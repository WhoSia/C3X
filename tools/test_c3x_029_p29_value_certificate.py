import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p29_value_certificate import certify
def a(n,v,q):return dict(action=n,utility=v,plan=q)
class P29Certificate(unittest.TestCase):
 def test_strict_separation(self):
  x=certify({"r1":[a("x",.5,True)],"r2":[a("y",.3,True)]},
            {"u1":[a("x",.2,False)],"u2":[a("y",.1,False)]})
  self.assertEqual(x["status"],"FINITE_SEPARATION_RELATIVE_TO_DECLARED_UTILITY")
  self.assertAlmostEqual(x["strict_margin"],.2)
 def test_feasible_but_worse(self):
  x=certify({"r1":[a("x",.1,True)],"r2":[a("y",-.3,True)]},
            {"u1":[a("x",.15,False)],"u2":[a("y",.05,False)]})
  self.assertEqual(x["status"],"NO_VALUE_SEPARATION_CERTIFICATE")
 def test_no_tie_certification(self):
  self.assertEqual(certify({"r":[a("x",.1,True)]},{"u":[a("y",.1,False)]})["status"],"NO_VALUE_SEPARATION_CERTIFICATE")
 def test_missing_plan_hold(self):
  self.assertEqual(certify({"r":[a("x",1,False)]},{"u":[a("y",0,True)]})["status"],"HOLD_A_PLAN_NOT_GUARANTEED_OR_ORACLE")
if __name__=="__main__":unittest.main()
