/**
 * Relies on the Dedupe_Rule__mdt / Dedupe_Setting__mdt records that deploy
 * with this package (custom metadata is visible to tests without SeeAllData).
 */
@IsTest
private class DedupeMergeBatchTest {

    static Contact make(String first, String last, String email) {
        return new Contact(FirstName = first, LastName = last, Email = email);
    }

    @IsTest
    static void testDryRunWritesScorecardOnly() {
        insert new List<Contact>{
            make('Jane', 'Doe', 'jane.doe@example.org'),
            make('Jane', 'Doe', 'jane.doe@example.org'),
            make('Solo', 'Person', 'solo@example.org')
        };

        Test.startTest();
        Database.executeBatch(new DedupeMergeBatch(true, false), 200);
        Test.stopTest();

        List<Dedupe_Merge_Audit__c> audits = [SELECT Outcome__c, Score__c, Id_Points__c,
                                                     Record_Count__c, Best_Scenario__c
                                              FROM Dedupe_Merge_Audit__c];
        System.assertEquals(1, audits.size(), 'one duplicate group expected');
        System.assertEquals('Dry Run - Would Merge', audits[0].Outcome__c);
        System.assertEquals(100, audits[0].Score__c);
        System.assert(audits[0].Id_Points__c >= 2.5);
        System.assertEquals(2, audits[0].Record_Count__c);

        System.assertEquals(3, [SELECT COUNT() FROM Contact], 'dry run must not merge');
    }

    @IsTest
    static void testAutoMergeMergesGroupAndFillsBlanks() {
        Contact keeper = make('Alex', 'Wren', 'alex.wren@example.org');
        Contact dupe1 = make('Alex', 'Wren', 'alex.wren@example.org');
        dupe1.Phone = '0412345678';
        Contact dupe2 = make('alex', 'wren', 'Alex.Wren@example.org');
        insert new List<Contact>{ keeper, dupe1, dupe2 };

        Test.startTest();
        Database.executeBatch(new DedupeMergeBatch(false, true), 200);
        Test.stopTest();

        List<Contact> remaining = [SELECT Id, Phone FROM Contact];
        System.assertEquals(1, remaining.size(), 'group should merge to one record');
        System.assertEquals('0412345678', remaining[0].Phone, 'master blanks filled from losers');

        List<Dedupe_Merge_Audit__c> audits = [SELECT Outcome__c, Merged_Ids__c, Master_Id__c
                                              FROM Dedupe_Merge_Audit__c];
        System.assertEquals(1, audits.size());
        System.assertEquals('Auto-Merged', audits[0].Outcome__c);
        System.assertEquals(remaining[0].Id, (Id) audits[0].Master_Id__c);
        System.assertEquals(2, audits[0].Merged_Ids__c.split(',').size());
    }

    @IsTest
    static void testDifferentEmailsAreNotGrouped() {
        insert new List<Contact>{
            make('Kim', 'Lee', 'kim.a@example.org'),
            make('Kim', 'Lee', 'kim.b@example.org')
        };

        Test.startTest();
        Database.executeBatch(new DedupeMergeBatch(false, true), 200);
        Test.stopTest();

        System.assertEquals(2, [SELECT COUNT() FROM Contact]);
        System.assertEquals(0, [SELECT COUNT() FROM Dedupe_Merge_Audit__c]);
    }

    @IsTest
    static void testGuardrailBlocksOnMultiplePortalUsers() {
        Contact a = make('Pat', 'Finch', 'pat@example.org');
        Contact b = make('Pat', 'Finch', 'pat@example.org');
        insert new List<Contact>{ a, b };

        User u1 = new User(ContactId = a.Id);
        User u2 = new User(ContactId = b.Id);
        DedupeGuardrails.portalUsersOverride = new List<User>{ u1, u2 };

        DedupeGuardrails.Result res = DedupeGuardrails.evaluate(
            new List<SObject>{ a, b });
        System.assertEquals(true, res.blockAuto);
        System.assert(String.join(res.flags, ' ').contains('MULTIPLE_PORTAL_USERS'));
    }

    @IsTest
    static void testGuardrailForcesPortalMaster() {
        Contact a = make('Sam', 'Egret', 'sam@example.org');
        Contact b = make('Sam', 'Egret', 'sam@example.org');
        insert new List<Contact>{ a, b };

        DedupeGuardrails.portalUsersOverride = new List<User>{ new User(ContactId = b.Id) };
        DedupeGuardrails.Result res = DedupeGuardrails.evaluate(new List<SObject>{ a, b });
        System.assertEquals(false, res.blockAuto);
        System.assertEquals(b.Id, res.portalMasterId);
    }

    @IsTest
    static void testSchedulerSchedulesAndRuns() {
        Test.startTest();
        String jobId = System.schedule('DedupeSchedulerTest', '0 0 21 * * ?', new DedupeScheduler());
        new DedupeScheduler().execute(null);
        Test.stopTest();

        System.assertNotEquals(null, jobId);
        System.assertEquals(1, [SELECT COUNT() FROM CronTrigger WHERE Id = :jobId]);
    }
}
