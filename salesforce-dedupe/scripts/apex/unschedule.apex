for (CronTrigger ct : [SELECT Id FROM CronTrigger WHERE CronJobDetail.Name = 'BirdLife Dedupe Nightly']) {
    System.abortJob(ct.Id);
}
