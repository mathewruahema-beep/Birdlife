/**
 * Scoring engine for duplicate groups.
 *
 * Match methods reproduce the behaviour of the Plauti scenarios configured in
 * this org (EQUAL, PERSON_NAME, FUZZY_PERSON, COMPANY, EMAIL_EXACT, PHONE,
 * POSTAL_CODE, NOT_EQUAL). A scenario score is the weighted percentage of
 * matched field weight; a group's scenario score is the WEAKEST pair in the
 * group, so one bad member blocks the whole group from auto-merge.
 *
 * On top of the Plauti-style 0-100 score, each matched field contributes
 * "points of identification" (the manual dedupe SOP: Contacts need >= 2.5
 * points, Accounts >= 3 before a merge is considered safe).
 */
public with sharing class DedupeEngine {

    public class FieldScore {
        public String field;
        public String method;
        public Decimal weight;
        public Decimal score;      // 0..1
        public Boolean counted;    // false when both sides blank (weight excluded)
        public Decimal idPoints;
    }

    public class PairScore {
        public Id leftId;
        public Id rightId;
        public String scenarioKey;
        public Decimal score;      // 0..100
        public Decimal idPoints = 0;
        public List<FieldScore> fields = new List<FieldScore>();
    }

    public class ScenarioResult {
        public String key;
        public String label;
        public String scoreMethod;
        public Decimal threshold;
        public Decimal autoMergeScore;
        public Decimal groupScore;
        public Boolean meetsThreshold;
        public Boolean meetsAutoMerge;
    }

    public class GroupScorecard {
        public String objectApi;
        public List<Id> recordIds = new List<Id>();
        public List<ScenarioResult> scenarios = new List<ScenarioResult>();
        public List<PairScore> pairs = new List<PairScore>();
        public Decimal idPoints = 0;   // weakest pair's distinct-field ID points
        public Decimal bestScore = 0;
        public String bestScenario;
        public Boolean autoMergeEligible = false;
    }

    public static GroupScorecard scoreGroup(String objectApi, List<SObject> records,
                                            List<DedupeConfig.Scenario> scenarios) {
        GroupScorecard card = new GroupScorecard();
        card.objectApi = objectApi;
        for (SObject r : records) {
            card.recordIds.add((Id) r.get('Id'));
        }

        Map<String, Decimal> minScoreByScenario = new Map<String, Decimal>();
        Decimal minPairPoints = null;

        for (Integer i = 0; i < records.size(); i++) {
            for (Integer j = i + 1; j < records.size(); j++) {
                Map<String, Decimal> pairPointsByField = new Map<String, Decimal>();
                for (DedupeConfig.Scenario sc : scenarios) {
                    PairScore ps = scorePair(records[i], records[j], sc);
                    card.pairs.add(ps);
                    Decimal current = minScoreByScenario.get(sc.key);
                    if (current == null || ps.score < current) {
                        minScoreByScenario.put(sc.key, ps.score);
                    }
                    for (FieldScore fs : ps.fields) {
                        if (fs.idPoints > 0) {
                            Decimal prev = pairPointsByField.get(fs.field);
                            if (prev == null || fs.idPoints > prev) {
                                pairPointsByField.put(fs.field, fs.idPoints);
                            }
                        }
                    }
                }
                Decimal pairTotal = 0;
                for (Decimal p : pairPointsByField.values()) {
                    pairTotal += p;
                }
                if (minPairPoints == null || pairTotal < minPairPoints) {
                    minPairPoints = pairTotal;
                }
            }
        }
        card.idPoints = minPairPoints == null ? 0 : minPairPoints;

        for (DedupeConfig.Scenario sc : scenarios) {
            ScenarioResult res = new ScenarioResult();
            res.key = sc.key;
            res.label = sc.label;
            res.scoreMethod = sc.scoreMethod;
            res.threshold = sc.threshold;
            res.autoMergeScore = sc.autoMergeScore;
            res.groupScore = minScoreByScenario.containsKey(sc.key) ? minScoreByScenario.get(sc.key) : 0;
            res.meetsThreshold = res.groupScore >= sc.threshold;
            res.meetsAutoMerge = res.groupScore >= sc.autoMergeScore;
            card.scenarios.add(res);
            if (card.bestScenario == null || res.groupScore > card.bestScore) {
                card.bestScore = res.groupScore;
                card.bestScenario = res.label;
            }
            if (res.meetsAutoMerge) {
                card.autoMergeEligible = true;
            }
        }
        return card;
    }

    public static PairScore scorePair(SObject a, SObject b, DedupeConfig.Scenario sc) {
        PairScore ps = new PairScore();
        ps.leftId = (Id) a.get('Id');
        ps.rightId = (Id) b.get('Id');
        ps.scenarioKey = sc.key;
        Decimal num = 0;
        Decimal den = 0;
        for (DedupeConfig.Rule rule : sc.rules) {
            String va = str(a, rule.field);
            String vb = str(b, rule.field);
            FieldScore fs = new FieldScore();
            fs.field = rule.field;
            fs.method = rule.matchMethod;
            fs.weight = rule.weight;
            Boolean bothBlank = String.isBlank(va) && String.isBlank(vb);
            if (rule.matchMethod == 'NOT_EQUAL') {
                fs.counted = true;
                fs.score = (normText(va) != normText(vb)) ? 1 : 0;
            } else if (bothBlank) {
                fs.counted = false;
                fs.score = 0;
            } else {
                fs.counted = true;
                fs.score = fieldMatch(rule.matchMethod, va, vb);
            }
            if (fs.counted) {
                num += rule.weight * fs.score;
                den += rule.weight;
            }
            fs.idPoints = fs.score >= 0.99 ? rule.idPoints
                        : (fs.score >= 0.5 ? (rule.idPoints / 2).setScale(2) : 0);
            ps.idPoints += fs.idPoints;
            ps.fields.add(fs);
        }
        ps.score = den == 0 ? 0 : ((num / den) * 100).setScale(0, System.RoundingMode.HALF_UP);
        return ps;
    }

    public static Decimal fieldMatch(String method, String a, String b) {
        if (String.isBlank(a) || String.isBlank(b)) {
            return 0;
        }
        if (method == 'EQUAL') {
            return normText(a) == normText(b) ? 1 : 0;
        }
        if (method == 'PERSON_NAME' || method == 'FUZZY_PERSON') {
            return personName(a, b);
        }
        if (method == 'EMAIL_EXACT') {
            return tokenOverlap(a, b, 'email') ? 1 : 0;
        }
        if (method == 'PHONE') {
            return tokenOverlap(a, b, 'phone') ? 1 : 0;
        }
        if (method == 'COMPANY') {
            return tokenOverlap(a, b, 'auto') ? 1 : 0;
        }
        if (method == 'POSTAL_CODE') {
            return normState(a) == normState(b) ? 1 : 0;
        }
        return normText(a) == normText(b) ? 1 : 0;
    }

    // ---- normalisation --------------------------------------------------

    public static String normText(String s) {
        if (s == null) {
            return '';
        }
        String n = s.toLowerCase().trim()
                    .replace('’', '').replace('\'', '')
                    .replaceAll('\\s+', ' ');
        return n;
    }

    public static String normEmail(String s) {
        return s == null ? '' : s.toLowerCase().trim();
    }

    public static String normPhone(String s) {
        if (s == null) {
            return '';
        }
        String digits = s.replaceAll('[^0-9]', '');
        if (digits.startsWith('61') && digits.length() >= 11) {
            digits = '0' + digits.substring(2);
        }
        return digits;
    }

    static final Map<String, String> AU_STATES = new Map<String, String>{
        'victoria' => 'vic', 'new south wales' => 'nsw', 'queensland' => 'qld',
        'south australia' => 'sa', 'western australia' => 'wa', 'tasmania' => 'tas',
        'northern territory' => 'nt', 'australian capital territory' => 'act'
    };

    public static String normState(String s) {
        String n = normText(s).replace('.', '');
        return AU_STATES.containsKey(n) ? AU_STATES.get(n) : n;
    }

    static Decimal personName(String a, String b) {
        String na = normText(a);
        String nb = normText(b);
        if (na == nb) {
            return 1;
        }
        if (na == '' || nb == '') {
            return 0;
        }
        // one side is an initial of the other ("J" vs "Jane")
        if ((na.length() == 1 || nb.length() == 1) && na.left(1) == nb.left(1)) {
            return 0.8;
        }
        if (Math.abs(na.length() - nb.length()) <= 1
                && na.getLevenshteinDistance(nb) <= 1) {
            return 0.8;
        }
        return 0;
    }

    // Multi-value fields (AllEmail__c / AllPhone__c) hold several values;
    // any single shared value counts as a match, like Plauti's index groups.
    static Boolean tokenOverlap(String a, String b, String mode) {
        Set<String> ta = tokens(a, mode);
        Set<String> tb = tokens(b, mode);
        for (String t : ta) {
            if (t != '' && tb.contains(t)) {
                return true;
            }
        }
        return false;
    }

    static Set<String> tokens(String raw, String mode) {
        Set<String> result = new Set<String>();
        if (String.isBlank(raw)) {
            return result;
        }
        for (String part : raw.split('[;,/|\\s]+')) {
            String p = part.trim();
            if (p == '') {
                continue;
            }
            if (mode == 'email' || (mode == 'auto' && p.contains('@'))) {
                result.add(normEmail(p));
            } else if (mode == 'phone' || (mode == 'auto' && p.replaceAll('[^0-9]', '').length() >= 6)) {
                String d = normPhone(p);
                if (d != '') {
                    result.add(d);
                }
            } else {
                result.add(normText(p));
            }
        }
        return result;
    }

    static String str(SObject rec, String field) {
        try {
            Object o = rec.get(field);
            return o == null ? null : String.valueOf(o);
        } catch (Exception e) {
            return null;   // field not queried / not present in this org
        }
    }
}
