import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p29_value_probe import adjudicate,compare
def a(name,val,plan):return {"action":name,"utility":val,"plan":plan}
class P29Value(unittest.TestCase):
 def test_guaranteed_plan_can_have_worse_value(self):
  x=compare({"r1":[a("x",.1,True)],"r2":[a("y",-.3,True)]},
            {"u1":[a("x",.15,False)],"u2":[a("y",.05,False)]})
  self.assertEqual(x["status"],"DESCRIPTIVE_PLAN_SCOPE_ONLY")
  self.assertAlmostEqual(x["value_difference_a_minus_b"],-.35)
 def test_plan_can_impose_worst_case_cost(self):
  x=adjudicate({"r1":[a("safe",3,False),a("plan",-1,True)],
                "r2":[a("safe",2,False),a("plan",0,True)]})
  self.assertEqual(x["plan_opportunity_cost"],3)
 def test_zero_cost(self):
  self.assertEqual(adjudicate({"r":[a("q",1,True)]})["plan_opportunity_cost"],0)
 def test_missing_plan(self):
  self.assertEqual(adjudicate({"r":[a("no",0,False)]})["status"],"PLAN_NOT_GUARANTEED")
 def test_nan_refused(self):
  self.assertEqual(adjudicate({"r":[a("q",float("nan"),True)]})["status"],"HOLD_INVALID_ORACLE")
 def test_duplicate_action_refused(self):
  self.assertEqual(adjudicate({"r":[a("q",1,True),a("q",2,False)]})["status"],"FAIL_DUPLICATE_ACTION")
 def test_empty_reply_refused(self):
  self.assertEqual(adjudicate({"r":[]})["status"],"HOLD_MISSING_ACTIONS")
if __name__=="__main__":unittest.main()
