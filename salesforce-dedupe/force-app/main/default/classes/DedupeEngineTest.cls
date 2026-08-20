@IsTest
private class DedupeEngineTest {

    static DedupeConfig.Scenario scenario(String key, Decimal threshold, Decimal autoScore) {
        DedupeConfig.Scenario sc = new DedupeConfig.Scenario();
        sc.key = key;
        sc.label = key;
        sc.objectApi = 'Contact';
        sc.scoreMethod = 'DEDUP';
        sc.threshold = threshold;
        sc.autoMergeScore = autoScore;
        return sc;
    }

    static void addRule(DedupeConfig.Scenario sc, String field, String method, Decimal weight, Decimal idPoints) {
        DedupeConfig.Rule r = new DedupeConfig.Rule();
        r.field = field;
        r.matchMethod = method;
        r.weight = weight;
        r.idPoints = idPoints;
        sc.rules.add(r);
    }

    static DedupeConfig.Scenario nameEmailExact() {
        DedupeConfig.Scenario sc = scenario('NAME_EMAIL_EXACT', 75, 100);
        addRule(sc, 'FirstName', 'EQUAL', 100, 0.5);
        addRule(sc, 'LastName', 'EQUAL', 100, 0.5);
        addRule(sc, 'Email', 'EQUAL', 100, 1.5);
        return sc;
    }

    @IsTest
    static void testNormalisers() {
        System.assertEquals('0412345678', DedupeEngine.normPhone('+61 412 345 678'));
        System.assertEquals('0412345678', DedupeEngine.normPhone('(04) 1234 5678'));
        System.assertEquals('obrien', DedupeEngine.normText(' O\'Brien '));
        System.assertEquals('vic', DedupeEngine.normState('Victoria'));
        System.assertEquals('vic', DedupeEngine.normState('VIC.'));
        System.assertEquals('jane smith', DedupeEngine.normText('Jane   SMITH'));
    }

    @IsTest
    static void testFieldMatchMethods() {
        System.assertEquals(1, DedupeEngine.fieldMatch('EQUAL', 'Jane', ' jane '));
        System.assertEquals(0, DedupeEngine.fieldMatch('EQUAL', 'Jane', 'Janet'));
        System.assertEquals(0.8, DedupeEngine.fieldMatch('PERSON_NAME', 'Jon', 'John'));
        System.assertEquals(0.8, DedupeEngine.fieldMatch('FUZZY_PERSON', 'J', 'Jane'));
        System.assertEquals(0, DedupeEngine.fieldMatch('PERSON_NAME', 'Jane', 'Mary'));
        System.assertEquals(1, DedupeEngine.fieldMatch('EMAIL_EXACT', 'a@b.com;c@d.com', 'C@D.com'));
        System.assertEquals(0, DedupeEngine.fieldMatch('EMAIL_EXACT', 'a@b.com', 'x@y.com'));
        System.assertEquals(1, DedupeEngine.fieldMatch('PHONE', '+61 412 345 678', '0412 345 678'));
        System.assertEquals(1, DedupeEngine.fieldMatch('COMPANY', 'a@b.com; 0412345678', '61412345678'));
        System.assertEquals(1, DedupeEngine.fieldMatch('POSTAL_CODE', 'Victoria', 'VIC'));
    }

    @IsTest
    static void testExactGroupScoresHundred() {
        Contact a = new Contact(FirstName = 'Jane', LastName = 'Doe', Email = 'jane@example.org');
        Contact b = new Contact(FirstName = 'JANE', LastName = 'doe', Email = 'Jane@Example.org');
        DedupeEngine.GroupScorecard card = DedupeEngine.scoreGroup(
            'Contact', new List<SObject>{ a, b },
            new List<DedupeConfig.Scenario>{ nameEmailExact() });

        System.assertEquals(100, card.bestScore);
        System.assertEquals(true, card.autoMergeEligible);
        System.assertEquals(2.5, card.idPoints);
    }

    @IsTest
    static void testMismatchedEmailBlocksAutoMerge() {
        Contact a = new Contact(FirstName = 'Jane', LastName = 'Doe', Email = 'jane@example.org');
        Contact b = new Contact(FirstName = 'Jane', LastName = 'Doe', Email = 'other@example.org');
        DedupeEngine.GroupScorecard card = DedupeEngine.scoreGroup(
            'Contact', new List<SObject>{ a, b },
            new List<DedupeConfig.Scenario>{ nameEmailExact() });

        System.assertEquals(67, card.bestScore);
        System.assertEquals(false, card.autoMergeEligible);
        System.assertEquals(1.0, card.idPoints);
    }

    @IsTest
    static void testWeakestPairGovernsGroup() {
        Contact a = new Contact(FirstName = 'Jane', LastName = 'Doe', Email = 'jane@example.org');
        Contact b = new Contact(FirstName = 'Jane', LastName = 'Doe', Email = 'jane@example.org');
        Contact c = new Contact(FirstName = 'Jane', LastName = 'Doe', Email = 'different@example.org');
        DedupeEngine.GroupScorecard card = DedupeEngine.scoreGroup(
            'Contact', new List<SObject>{ a, b, c },
            new List<DedupeConfig.Scenario>{ nameEmailExact() });

        // pair (a,b) is 100 but the weakest pair drags the group below auto-merge
        System.assertEquals(false, card.autoMergeEligible);
    }

    @IsTest
    static void testNotEqualRule() {
        DedupeConfig.Scenario sc = scenario('SAME_ADDR_DIFF_HH', 75, 999);
        addRule(sc, 'MailingStreet', 'EQUAL', 85, 0.75);
        addRule(sc, 'MailingState', 'POSTAL_CODE', 60, 0.25);
        addRule(sc, 'AccountId', 'NOT_EQUAL', 100, 0);

        Contact a = new Contact(FirstName = 'A', LastName = 'X', MailingStreet = '1 Bird St', MailingState = 'Victoria');
        Contact b = new Contact(FirstName = 'B', LastName = 'Y', MailingStreet = '1 Bird St', MailingState = 'VIC');
        a.AccountId = '001000000000001AAA';
        b.AccountId = '001000000000002AAA';

        DedupeEngine.GroupScorecard card = DedupeEngine.scoreGroup(
            'Contact', new List<SObject>{ a, b }, new List<DedupeConfig.Scenario>{ sc });
        System.assertEquals(100, card.bestScore);

        // same household: NOT_EQUAL contributes nothing, score drops below threshold
        b.AccountId = a.AccountId;
        card = DedupeEngine.scoreGroup('Contact', new List<SObject>{ a, b },
                                       new List<DedupeConfig.Scenario>{ sc });
        System.assert(card.bestScore < 75, 'expected sub-threshold, got ' + card.bestScore);
    }

    @IsTest
    static void testBlankFieldsExcludedFromDenominator() {
        DedupeConfig.Scenario sc = scenario('FUZZY', 75, 999);
        addRule(sc, 'LastName', 'PERSON_NAME', 100, 0.5);
        addRule(sc, 'FirstName', 'PERSON_NAME', 90, 0.5);
        addRule(sc, 'Phone', 'COMPANY', 60, 1.0);

        // both phones blank: scenario still reaches 100 on names alone
        Contact a = new Contact(FirstName = 'Jane', LastName = 'Doe');
        Contact b = new Contact(FirstName = 'Jane', LastName = 'Doe');
        DedupeEngine.GroupScorecard card = DedupeEngine.scoreGroup(
            'Contact', new List<SObject>{ a, b }, new List<DedupeConfig.Scenario>{ sc });
        System.assertEquals(100, card.bestScore);

        // one side has a phone the other lacks: weight counts, score drops
        b.Phone = '0412345678';
        card = DedupeEngine.scoreGroup('Contact', new List<SObject>{ a, b },
                                       new List<DedupeConfig.Scenario>{ sc });
        System.assert(card.bestScore < 100);
    }

    @IsTest
    static void testConfigLoadsFromMetadataRows() {
        Dedupe_Rule__mdt row = new Dedupe_Rule__mdt(
            Object__c = 'Contact',
            Scenario_Key__c = 'TEST_SC',
            Scenario_Label__c = 'Test Scenario',
            Score_Method__c = 'DEDUP',
            Threshold__c = 75,
            Auto_Merge_Score__c = 100,
            Field__c = 'Email',
            Match_Method__c = 'EQUAL',
            Weight__c = 100,
            Id_Points__c = 1.5,
            Active__c = true
        );
        DedupeConfig.ruleOverride = new List<Dedupe_Rule__mdt>{ row };
        List<DedupeConfig.Scenario> scenarios = DedupeConfig.scenariosFor('Contact');
        System.assertEquals(1, scenarios.size());
        System.assertEquals('TEST_SC', scenarios[0].key);
        System.assertEquals(1, scenarios[0].rules.size());

        DedupeConfig.settingOverride = new Dedupe_Setting__mdt(
            Dry_Run__c = false, Auto_Merge_Enabled__c = true, Fill_Master_Blanks__c = true,
            Max_Merges_Per_Run__c = 10, Max_Group_Size__c = 4, Batch_Size__c = 10,
            Contact_Id_Points_Required__c = 2.5, Account_Id_Points_Required__c = 3.0
        );
        DedupeConfig.Settings s = DedupeConfig.settings();
        System.assertEquals(false, s.dryRun);
        System.assertEquals(10, s.maxMergesPerRun);
    }
}
