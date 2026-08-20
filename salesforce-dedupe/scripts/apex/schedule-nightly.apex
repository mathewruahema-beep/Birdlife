// 9pm org time (AEST) — clear of the 7pm Conga receipting batch.
// Behaviour (dry run vs live) is controlled by Dedupe_Setting__mdt.Default.
System.schedule('BirdLife Dedupe Nightly', '0 0 21 * * ?', new DedupeScheduler());
