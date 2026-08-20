/**
 * Loads the dedupe scorecard configuration from custom metadata.
 * Rules mirror the live Plauti Duplicate Check scenarios (see docs/ALIGNMENT.md)
 * so that one rule set drives both the scorecard and the merge automation.
 */
public with sharing class DedupeConfig {

    public class Rule {
        public String field;
        public String matchMethod;
        public Decimal weight;
        public Decimal idPoints;
    }

    public class Scenario {
        public String key;
        public String label;
        public String objectApi;
        public String scoreMethod;
        public String plautiId;
        public Decimal threshold;
        public Decimal autoMergeScore;
        public List<Rule> rules = new List<Rule>();
    }

    public class Settings {
        public Boolean dryRun = true;
        public Boolean autoMergeEnabled = false;
        public Boolean fillMasterBlanks = true;
        public Integer maxMergesPerRun = 200;
        public Integer maxGroupSize = 6;
        public Integer batchSize = 25;
        public Decimal contactIdPointsRequired = 2.5;
        public Decimal accountIdPointsRequired = 3.0;
    }

    @TestVisible static List<Dedupe_Rule__mdt> ruleOverride;
    @TestVisible static Dedupe_Setting__mdt settingOverride;

    public static List<Scenario> scenariosFor(String objectApi) {
        Map<String, Scenario> byKey = new Map<String, Scenario>();
        for (Dedupe_Rule__mdt r : queryRules()) {
            if (r.Object__c != objectApi || r.Active__c != true) {
                continue;
            }
            Scenario sc = byKey.get(r.Scenario_Key__c);
            if (sc == null) {
                sc = new Scenario();
                sc.key = r.Scenario_Key__c;
                sc.label = r.Scenario_Label__c;
                sc.objectApi = r.Object__c;
                sc.scoreMethod = r.Score_Method__c;
                sc.plautiId = r.Plauti_Scenario_Id__c;
                sc.threshold = r.Threshold__c == null ? 75 : r.Threshold__c;
                sc.autoMergeScore = r.Auto_Merge_Score__c == null ? 999 : r.Auto_Merge_Score__c;
                byKey.put(sc.key, sc);
            }
            Rule rule = new Rule();
            rule.field = r.Field__c;
            rule.matchMethod = r.Match_Method__c;
            rule.weight = r.Weight__c == null ? 100 : r.Weight__c;
            rule.idPoints = r.Id_Points__c == null ? 0 : r.Id_Points__c;
            sc.rules.add(rule);
        }
        return byKey.values();
    }

    static List<Dedupe_Rule__mdt> queryRules() {
        if (ruleOverride != null) {
            return ruleOverride;
        }
        return [SELECT Object__c, Scenario_Key__c, Scenario_Label__c, Plauti_Scenario_Id__c,
                       Score_Method__c, Threshold__c, Auto_Merge_Score__c,
                       Field__c, Match_Method__c, Weight__c, Id_Points__c, Active__c
                FROM Dedupe_Rule__mdt];
    }

    public static Settings settings() {
        Settings s = new Settings();
        Dedupe_Setting__mdt row = settingOverride;
        if (row == null) {
            List<Dedupe_Setting__mdt> rows =
                [SELECT Dry_Run__c, Auto_Merge_Enabled__c, Fill_Master_Blanks__c,
                        Max_Merges_Per_Run__c, Max_Group_Size__c, Batch_Size__c,
                        Contact_Id_Points_Required__c, Account_Id_Points_Required__c
                 FROM Dedupe_Setting__mdt
                 WHERE DeveloperName = 'Default'
                 LIMIT 1];
            if (rows.isEmpty()) {
                return s;
            }
            row = rows[0];
        }
        s.dryRun = row.Dry_Run__c;
        s.autoMergeEnabled = row.Auto_Merge_Enabled__c;
        s.fillMasterBlanks = row.Fill_Master_Blanks__c;
        if (row.Max_Merges_Per_Run__c != null) {
            s.maxMergesPerRun = row.Max_Merges_Per_Run__c.intValue();
        }
        if (row.Max_Group_Size__c != null) {
            s.maxGroupSize = row.Max_Group_Size__c.intValue();
        }
        if (row.Batch_Size__c != null) {
            s.batchSize = row.Batch_Size__c.intValue();
        }
        if (row.Contact_Id_Points_Required__c != null) {
            s.contactIdPointsRequired = row.Contact_Id_Points_Required__c;
        }
        if (row.Account_Id_Points_Required__c != null) {
            s.accountIdPointsRequired = row.Account_Id_Points_Required__c;
        }
        return s;
    }
}
