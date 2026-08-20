/**
 * Contact duplicate scorecard + merge automation.
 *
 * Discovery mirrors the Plauti "Clone: Daily Contact Merge" job: contacts are
 * grouped on normalised FirstName + LastName + Email (all three present).
 * Every discovered group is scored against ALL configured scenarios
 * (Dedupe_Rule__mdt), guardrails are evaluated, and a Dedupe_Merge_Audit__c
 * scorecard row is written for every group whatever the outcome.
 *
 * A group auto-merges only when ALL of the following hold:
 *   - an auto-eligible scenario scores at/above its Auto_Merge_Score__c
 *     (ships as: Name and Email - Exact at 100)
 *   - ID points >= Contact_Id_Points_Required__c (ships as 2.5)
 *   - no guardrail blocks (portal users, active recurring conflicts, deceased)
 *   - group size <= Max_Group_Size__c and the run's merge cap is not exhausted
 *   - the run is not in dry-run mode and auto-merge is enabled
 *
 * Default shipped settings are dry-run ON / auto-merge OFF: the first runs
 * only produce scorecards.
 */
public with sharing class DedupeMergeBatch implements Database.Batchable<SObject>, Database.Stateful {

    static final List<String> FILL_FIELDS = new List<String>{
        'Phone', 'MobilePhone', 'HomePhone', 'OtherPhone',
        'MailingStreet', 'MailingCity', 'MailingState', 'MailingPostalCode', 'MailingCountry',
        'Birthdate'
    };

    final Boolean dryRun;
    final Boolean autoMergeEnabled;
    final DedupeConfig.Settings settings;
    final String runId;
    Integer mergesDone = 0;
    Integer groupsSeen = 0;

    static List<DedupeConfig.Scenario> contactScenarios;

    public DedupeMergeBatch() {
        this(null, null);
    }

    public DedupeMergeBatch(Boolean dryRunOverride, Boolean autoMergeOverride) {
        settings = DedupeConfig.settings();
        dryRun = dryRunOverride != null ? dryRunOverride : settings.dryRun;
        autoMergeEnabled = autoMergeOverride != null ? autoMergeOverride : settings.autoMergeEnabled;
        runId = 'RUN-' + Datetime.now().formatGmt('yyyyMMdd-HHmmss');
    }

    public Database.QueryLocator start(Database.BatchableContext bc) {
        String soql = 'SELECT ' + String.join(fieldList(), ', ')
            + ' FROM Contact'
            + ' WHERE Email != null AND FirstName != null AND LastName != null'
            + ' ORDER BY Email';
        return Database.getQueryLocator(soql);
    }

    public void execute(Database.BatchableContext bc, List<SObject> scope) {
        Set<Id> scopeIds = new Set<Id>();
        Set<String> emails = new Set<String>();
        for (SObject c : scope) {
            scopeIds.add((Id) c.get('Id'));
            emails.add((String) c.get('Email'));
        }

        // Re-query by email so a group split across batch scopes is always
        // seen whole; the anchor rule below stops double-processing.
        String soql = 'SELECT ' + String.join(fieldList(), ', ')
            + ' FROM Contact WHERE Email IN :emails'
            + ' AND FirstName != null AND LastName != null';
        List<SObject> candidates = Database.query(soql);

        Map<String, List<SObject>> groups = new Map<String, List<SObject>>();
        for (SObject c : candidates) {
            String key = DedupeEngine.normText((String) c.get('FirstName')) + '|'
                       + DedupeEngine.normText((String) c.get('LastName')) + '|'
                       + DedupeEngine.normEmail((String) c.get('Email'));
            if (!groups.containsKey(key)) {
                groups.put(key, new List<SObject>());
            }
            groups.get(key).add(c);
        }

        List<Dedupe_Merge_Audit__c> audits = new List<Dedupe_Merge_Audit__c>();
        for (String key : groups.keySet()) {
            List<SObject> grp = groups.get(key);
            if (grp.size() < 2) {
                continue;
            }
            Id anchor = grp[0].Id;
            for (SObject c : grp) {
                if (String.valueOf(c.Id) < String.valueOf(anchor)) {
                    anchor = c.Id;
                }
            }
            if (!scopeIds.contains(anchor)) {
                continue;   // this group is processed in the scope that holds its anchor
            }
            audits.add(processGroup(key, grp));
        }
        if (!audits.isEmpty()) {
            insert audits;
        }
    }

    public void finish(Database.BatchableContext bc) {
        System.debug(LoggingLevel.INFO, 'Dedupe run ' + runId + ': ' + groupsSeen
            + ' duplicate groups audited, ' + mergesDone + ' records merged'
            + (dryRun ? ' (dry run)' : ''));
    }

    // -----------------------------------------------------------------

    Dedupe_Merge_Audit__c processGroup(String key, List<SObject> grp) {
        groupsSeen++;
        List<DedupeConfig.Scenario> scenarios = scenarios();
        DedupeEngine.GroupScorecard card = DedupeEngine.scoreGroup('Contact', grp, scenarios);
        DedupeGuardrails.Result guard = DedupeGuardrails.evaluate(grp);

        Id masterId = guard.portalMasterId != null ? guard.portalMasterId : pickMaster(grp, guard);
        List<String> flags = new List<String>(guard.flags);

        List<String> loserIds = new List<String>();
        for (SObject c : grp) {
            if (c.Id != masterId) {
                loserIds.add(String.valueOf(c.Id));
            }
        }

        Dedupe_Merge_Audit__c audit = new Dedupe_Merge_Audit__c(
            Object__c = 'Contact',
            Group_Key__c = key.left(255),
            Master_Id__c = masterId,
            Merged_Ids__c = String.join(loserIds, ', '),
            Record_Count__c = grp.size(),
            Best_Scenario__c = card.bestScenario,
            Score__c = card.bestScore,
            Id_Points__c = card.idPoints,
            Run_Id__c = runId
        );

        Boolean scoreEligible = card.autoMergeEligible
            && card.idPoints >= settings.contactIdPointsRequired
            && grp.size() <= settings.maxGroupSize;

        if (grp.size() > settings.maxGroupSize) {
            flags.add('GROUP_TOO_LARGE: ' + grp.size() + ' records; review manually.');
        }

        if (scoreEligible && guard.blockAuto) {
            audit.Outcome__c = 'Blocked';
        } else if (scoreEligible) {
            if (dryRun || !autoMergeEnabled) {
                audit.Outcome__c = 'Dry Run - Would Merge';
            } else if (mergesDone + loserIds.size() > settings.maxMergesPerRun) {
                audit.Outcome__c = 'Review';
                flags.add('MAX_MERGES_REACHED: run cap of ' + settings.maxMergesPerRun + ' hit; group left for the next run.');
            } else {
                try {
                    doMerge(grp, masterId);
                    mergesDone += loserIds.size();
                    audit.Outcome__c = 'Auto-Merged';
                } catch (Exception e) {
                    audit.Outcome__c = 'Error';
                    audit.Error__c = e.getMessage().left(32000);
                }
            }
        } else {
            audit.Outcome__c = 'Review';
        }

        audit.Flags__c = String.join(flags, '\n').left(32000);
        audit.Scorecard_JSON__c = JSON.serialize(card).left(131000);
        return audit;
    }

    void doMerge(List<SObject> grp, Id masterId) {
        SObject master;
        List<SObject> losers = new List<SObject>();
        for (SObject c : grp) {
            if (c.Id == masterId) {
                master = c;
            } else {
                losers.add(c);
            }
        }

        if (settings.fillMasterBlanks) {
            Boolean changed = false;
            Map<String, Schema.SObjectField> fmap = Schema.SObjectType.Contact.fields.getMap();
            for (String f : FILL_FIELDS) {
                Schema.SObjectField tok = fmap.get(f);
                if (tok == null || !tok.getDescribe().isUpdateable()) {
                    continue;
                }
                if (master.get(f) != null) {
                    continue;
                }
                for (SObject loser : losers) {
                    Object v = loser.get(f);
                    if (v != null && String.valueOf(v) != '') {
                        master.put(f, v);
                        changed = true;
                        break;
                    }
                }
            }
            if (changed) {
                update master;
            }
        }

        // Apex merge requires contacts to share an account: pull losers into
        // the master's household first. NPSP cleans up emptied households.
        List<SObject> toReparent = new List<SObject>();
        for (SObject loser : losers) {
            if (loser.get('AccountId') != master.get('AccountId')) {
                loser.put('AccountId', master.get('AccountId'));
                toReparent.add(loser);
            }
        }
        if (!toReparent.isEmpty()) {
            update toReparent;
        }

        for (SObject loser : losers) {
            Database.MergeResult mr = Database.merge(master, loser.Id, false);
            if (!mr.isSuccess()) {
                String msg = 'merge failed for ' + loser.Id;
                for (Database.Error err : mr.getErrors()) {
                    msg += ': ' + err.getMessage();
                }
                throw new DedupeMergeException(msg);
            }
        }
    }

    Id pickMaster(List<SObject> grp, DedupeGuardrails.Result guard) {
        SObject best;
        Long bestRank = null;
        for (SObject c : grp) {
            Integer recurring = guard.activeRecurring.get(c.Id) == null ? 0 : guard.activeRecurring.get(c.Id);
            Integer opps = guard.oppCount.get(c.Id) == null ? 0 : guard.oppCount.get(c.Id);
            Long rank = (recurring > 0 ? 1000000L : 0L) + opps * 1000L;
            if (best == null || rank > bestRank
                || (rank == bestRank && olderThan(c, best))) {
                best = c;
                bestRank = rank;
            }
        }
        return best.Id;
    }

    static Boolean olderThan(SObject a, SObject b) {
        Datetime da = (Datetime) a.get('CreatedDate');
        Datetime db = (Datetime) b.get('CreatedDate');
        if (da == db) {
            return String.valueOf(a.Id) < String.valueOf(b.Id);
        }
        return da < db;
    }

    static List<DedupeConfig.Scenario> scenarios() {
        if (contactScenarios == null) {
            contactScenarios = DedupeConfig.scenariosFor('Contact');
        }
        return contactScenarios;
    }

    List<String> fieldList() {
        Set<String> fields = new Set<String>{
            'Id', 'FirstName', 'LastName', 'Email', 'AccountId',
            'CreatedDate', 'LastModifiedDate'
        };
        for (DedupeConfig.Scenario sc : scenarios()) {
            for (DedupeConfig.Rule r : sc.rules) {
                if (DedupeGuardrails.hasField('Contact', r.field)) {
                    fields.add(r.field);
                }
            }
        }
        for (String f : FILL_FIELDS) {
            if (DedupeGuardrails.hasField('Contact', f)) {
                fields.add(f);
            }
        }
        if (DedupeGuardrails.hasField('Contact', 'npsp__Deceased__c')) {
            fields.add('npsp__Deceased__c');
        }
        return new List<String>(fields);
    }

    public class DedupeMergeException extends Exception {}
}
