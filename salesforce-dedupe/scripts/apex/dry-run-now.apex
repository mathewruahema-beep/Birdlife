// Scorecard-only pass over all contacts. No records are changed.
Database.executeBatch(new DedupeMergeBatch(true, false), 25);
