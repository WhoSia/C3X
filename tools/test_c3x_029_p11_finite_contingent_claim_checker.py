import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p11_finite_contingent_claim_checker import check_claim,compare_candidates

class ContingentClaimTests(unittest.TestCase):
    def test_single_policy_true(self):
        r=check_claim({"r1":["a","b"],"r2":["b","c"]},
            {"safe":{"r1":["b"],"r2":["b"]},"active":{"r1":["a","b"],"r2":["b"]}},["r1","r2"])
        self.assertEqual(r["status"],"CERTIFIED_RELATIVE_TO_DECLARED_LEGALITY")
        self.assertEqual(r["witness"],{"r1":"b","r2":"b"})
    def test_conjunction_false_even_when_each_independently_true(self):
        r=check_claim({"r":["left","right"]},
            {"P":{"r":["left"]},"Q":{"r":["right"]}},["r"])
        self.assertEqual(r["status"],"REFUTED_COMMON_WITNESS")
        self.assertTrue(r["separate_properties_satisfiable"])
    def test_all_legal_domain_missing(self):
        r=check_claim({"capture":["re"],"quiet":["wait"]},
            {"P":{"capture":["re"],"quiet":["wait"]}},["capture"])
        self.assertEqual(r["status"],"HOLD_INCOMPLETE_LEGAL_REPLY_DOMAIN")
    def test_no_vacuous_success(self):
        self.assertEqual(check_claim({},{"P":{}},[])["status"],"ABSTAIN_EMPTY_DOMAIN")
    def test_absent_property_is_not_success(self):
        self.assertEqual(check_claim({"r":["a"]},{"P":{}},["r"])["status"],"HOLD_INCOMPLETE_PROPERTY_COVERAGE")
    def test_no_response_is_hold(self):
        self.assertEqual(check_claim({"r":[]},{"P":{"r":[]}},["r"])["status"],"HOLD_NO_LEGAL_RESPONSE")
    def test_competitor_refuter(self):
        a=check_claim({"r":["a"]},{"P":{"r":["a"]}},["r"])
        b=check_claim({"r":["a"]},{"P":{"r":[]}},["r"])
        self.assertEqual(compare_candidates(a,b,"P|H2|all","P|H2|all")["status"],"CONTRASTIVE_WITNESS_WITH_REFUTER_NOT_CHESS_PREFERENCE")
    def test_mismatched_claim_abstains(self):
        a=check_claim({"r":["a"]},{"P":{"r":["a"]}},["r"])
        b=check_claim({"r":["a"]},{"Q":{"r":[]}},["r"])
        self.assertEqual(compare_candidates(a,b,"P|H2|all","Q|H2|all")["status"],"ABSTAIN_MISMATCHED_OR_UNFROZEN_CLAIM")
    def test_both_true_not_contrastive(self):
        a=check_claim({"r":["a"]},{"P":{"r":["a"]}},["r"])
        self.assertEqual(compare_candidates(a,a,"P|H2|all","P|H2|all")["status"],"ABSTAIN_NO_CONTRASTIVE_CERTIFICATE")

if __name__=="__main__":unittest.main()
