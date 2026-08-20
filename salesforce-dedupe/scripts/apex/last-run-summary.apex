// Outcome counts for the most recent run.
List<Dedupe_Merge_Audit__c> latest = [SELECT Run_Id__c FROM Dedupe_Merge_Audit__c ORDER BY CreatedDate DESC LIMIT 1];
if (!latest.isEmpty()) {
    String runId = latest[0].Run_Id__c;
    for (AggregateResult ar : [SELECT Outcome__c o, COUNT(Id) c FROM Dedupe_Merge_Audit__c
                               WHERE Run_Id__c = :runId GROUP BY Outcome__c]) {
        System.debug(runId + '  ' + ar.get('o') + ': ' + ar.get('c'));
    }
}
