/**
 * Nightly entry point. Behaviour (dry-run vs live merge) comes from the
 * Dedupe_Setting__mdt "Default" record, so flipping to live needs a metadata
 * change, not a code change.
 *
 * Schedule (see scripts/apex/schedule-nightly.apex):
 *   System.schedule('BirdLife Dedupe Nightly', '0 0 21 * * ?', new DedupeScheduler());
 * 9pm org time keeps clear of the 7pm Conga receipting batch.
 */
public with sharing class DedupeScheduler implements Schedulable {
    public void execute(SchedulableContext sc) {
        DedupeConfig.Settings s = DedupeConfig.settings();
        Database.executeBatch(new DedupeMergeBatch(), s.batchSize);
    }
}
