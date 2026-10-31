import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p17_risk_coverage import evaluate
def r(i,g,e,error):return dict(case_id=i,game_id=g,emitted=e,error=error)
class Risk(unittest.TestCase):
 def test_abstain_is_not_free_accuracy(self):
  a=evaluate([r("1","a",False,None),r("2","b",False,None)])
  self.assertEqual(a["status"],"ZERO_COVERAGE");self.assertIsNone(a["risk"])
 def test_risk_is_conditioned_on_emission(self):
  a=evaluate([r("1","a",True,True),r("2","a",True,False),r("3","b",False,None)])
  self.assertEqual(a["coverage"],2/3);self.assertEqual(a["risk"],.5)
 def test_macro_game_differs_from_item_weighted(self):
  a=evaluate([r(str(i),"a",True,False) for i in range(9)]+[r("9","b",True,True)])
  self.assertAlmostEqual(a["risk"],.1);self.assertAlmostEqual(a["macro_game_risk"],.5)
 def test_unlabeled_emission_hold(self):
  self.assertEqual(evaluate([r("1","a",True,None)])["status"],"HOLD_UNKNOWN_ERROR")
 def test_no_forced_labels_for_refusal(self):
  self.assertEqual(evaluate([r("1","a",False,False)])["status"],"HOLD_REFUSAL_HAS_ERROR_LABEL")
if __name__=="__main__":unittest.main()
