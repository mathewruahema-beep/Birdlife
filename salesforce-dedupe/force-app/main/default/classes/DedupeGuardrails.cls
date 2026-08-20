/**
 * Safety checks the merge automation runs before any auto-merge — the parts
 * of the BirdLife dedupe SOP that Plauti does not enforce by itself:
 *
 *  - the record with an active portal login must be the merge master; two or
 *    more active portal logins in one group blocks auto-merge entirely
 *  - a group where more than one record holds ACTIVE recurring giving
 *    (NPSP Recurring Donations, Payments2Us Recurring Payments, or a current
 *    Payments2Us Subscription/membership) goes to human review, because a
 *    merge would stack live payment schedules on one supporter
 *  - deceased flag conflicts go to review
 *
 * Child-object checks are describe-guarded dynamic SOQL so staging/production
 * schema drift degrades to "not checked" instead of a crash.
 */
public with sharing class DedupeGuardrails {

    public class Result {
        public Boolean blockAuto = false;
        public List<String> flags = new List<String>();
        public Id portalMasterId;
        public Map<Id, Integer> activeRecurring = new Map<Id, Integer>();
        public Map<Id, Integer> oppCount = new Map<Id, Integer>();
    }

    @TestVisible static List<User> portalUsersOverride;

    public static Result evaluate(List<SObject> grp) {
        Result res = new Result();
        Set<Id> ids = new Set<Id>();
        for (SObject r : grp) {
            ids.add((Id) r.get('Id'));
        }

        List<User> portalUsers = portalUsersOverride != null
            ? portalUsersOverride
            : [SELECT Id, ContactId FROM User WHERE ContactId IN :ids AND IsActive = true];
        Set<Id> portalContacts = new Set<Id>();
        for (User u : portalUsers) {
            portalContacts.add(u.ContactId);
        }
        if (portalContacts.size() > 1) {
            res.blockAuto = true;
            res.flags.add('MULTIPLE_PORTAL_USERS: more than one record in this group has an active portal login. Run "Disable Customer User" on the losers first.');
        } else if (portalContacts.size() == 1) {
            res.portalMasterId = new List<Id>(portalContacts)[0];
            res.flags.add('PORTAL_USER_MASTER: portal login record forced as merge master.');
        }

        addCounts(res.activeRecurring, 'npe03__Recurring_Donation__c', 'npe03__Contact__c',
                  'npsp__Status__c', 'npsp__Status__c = \'Active\'', ids);
        addCounts(res.activeRecurring, 'AAkPay__Recurring_Payment__c', 'AAkPay__Contact__c',
                  'AAkPay__Recurring_Payment_Status__c', 'AAkPay__Recurring_Payment_Status__c = \'Active\'', ids);
        addCounts(res.activeRecurring, 'AAkPay__Subscription__c', 'AAkPay__Contact__c',
                  'AAkPay__End_Date__c', 'AAkPay__End_Date__c >= TODAY', ids);
        addCounts(res.oppCount, 'Opportunity', 'npsp__Primary_Contact__c', null, null, ids);

        Integer holdersOfActiveRecurring = 0;
        for (Id cid : ids) {
            Integer n = res.activeRecurring.get(cid);
            if (n != null && n > 0) {
                holdersOfActiveRecurring++;
            }
        }
        if (holdersOfActiveRecurring > 1) {
            res.blockAuto = true;
            res.flags.add('MULTIPLE_ACTIVE_RECURRING: ' + holdersOfActiveRecurring
                + ' records hold active recurring donations/payments/memberships. Merge manually and consolidate the schedules.');
        }

        Boolean anyFinancials = !res.oppCount.isEmpty() || !res.activeRecurring.isEmpty();
        if (anyFinancials) {
            res.flags.add('HAS_FINANCIALS: group carries donations or recurring records; they will transfer to the master on merge.');
        }

        if (hasField('Contact', 'npsp__Deceased__c')) {
            Boolean anyDeceased = false;
            Boolean anyLiving = false;
            for (SObject r : grp) {
                Object v = null;
                try { v = r.get('npsp__Deceased__c'); } catch (Exception e) { break; }
                if (v == null) {
                    anyLiving = true;
                } else if ((Boolean) v) {
                    anyDeceased = true;
                } else {
                    anyLiving = true;
                }
            }
            if (anyDeceased && anyLiving) {
                res.blockAuto = true;
                res.flags.add('DECEASED_CONFLICT: group mixes deceased and living records.');
            }
        }
        return res;
    }

    static void addCounts(Map<Id, Integer> acc, String objectApi, String lookupField,
                          String filterField, String filterExpr, Set<Id> ids) {
        if (!hasField(objectApi, lookupField)) {
            return;
        }
        String soql = 'SELECT ' + lookupField + ' lk, COUNT(Id) c FROM ' + objectApi
                    + ' WHERE ' + lookupField + ' IN :ids';
        if (filterField != null && hasField(objectApi, filterField)) {
            soql += ' AND ' + filterExpr;
        }
        soql += ' GROUP BY ' + lookupField;
        try {
            for (AggregateResult ar : Database.query(soql)) {
                Id cid = (Id) ar.get('lk');
                Integer n = (Integer) ar.get('c');
                Integer prev = acc.get(cid);
                acc.put(cid, (prev == null ? 0 : prev) + (n == null ? 0 : n));
            }
        } catch (Exception e) {
            // schema drift or FLS: treat as not-checked rather than failing the run
        }
    }

    static Map<String, Set<String>> fieldCache = new Map<String, Set<String>>();

    public static Boolean hasField(String objectApi, String fieldApi) {
        Set<String> fields = fieldCache.get(objectApi);
        if (fields == null) {
            Schema.SObjectType t = Schema.getGlobalDescribe().get(objectApi);
            if (t == null) {
                fieldCache.put(objectApi, new Set<String>());
                return false;
            }
            fields = new Set<String>();
            for (String f : t.getDescribe().fields.getMap().keySet()) {
                fields.add(f.toLowerCase());
            }
            fieldCache.put(objectApi, fields);
        }
        return fields.contains(fieldApi.toLowerCase());
    }
}
