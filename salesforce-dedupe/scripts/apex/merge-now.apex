// LIVE MERGE RUN — merges every group that passes the scorecard and guardrails.
// Run dry-run first and review the Dedupe_Merge_Audit__c rows before using this.
Database.executeBatch(new DedupeMergeBatch(false, true), 25);
