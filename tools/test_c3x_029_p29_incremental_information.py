import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p29_incremental_information import compare
def row(i,y,plan,base,game=None,split="heldout"):
 return dict(case_id=str(i),game_id=str(game or i),y=y,plan_p=plan,baseline_p=base,split=split)
class P29Info(unittest.TestCase):
 def test_plan_improves(self):
  x=compare([row(i,True,.9,.6) for i in range(6)])
  self.assertEqual(x["direction"],"PLAN_IMPROVES")
  self.assertAlmostEqual(x["game_macro_brier_gain"],.15)
 def test_plan_worse(self):
  self.assertEqual(compare([row(i,True,.6,.9) for i in range(6)])["direction"],"PLAN_WORSE")
 def test_many_rows_one_game(self):
  self.assertEqual(compare([row(i,True,.9,.5,"same") for i in range(100)])["status"],"HOLD_INSUFFICIENT_INDEPENDENT_GAMES")
 def test_development_leakage(self):
  z=[row(i,True,.9,.5) for i in range(6)];z[-1]["split"]="development"
  self.assertEqual(compare(z)["status"],"HOLD_NOT_HELDOUT")
 def test_duplicate_case(self):
  z=[row(i,True,.9,.5) for i in range(6)];z[-1]["case_id"]="0"
  self.assertEqual(compare(z)["status"],"FAIL_DUPLICATE_CASE")
 def test_bad_probability(self):
  z=[row(i,True,.9,.5) for i in range(6)];z[-1]["plan_p"]=1.1
  self.assertEqual(compare(z)["status"],"HOLD_PROBABILITY")
if __name__=="__main__":unittest.main()
