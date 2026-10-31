import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p19_paired_method_comparison import paired
def r(i,emitted,error,game=None):return dict(case_id=str(i),game_id=str(game or i),emitted=emitted,error=error)
class Paired(unittest.TestCase):
 def test_no_nonoverlapping_false_superiority(self):
  a=[r(1,True,False),r(2,False,None)]
  b=[r(1,False,None),r(2,True,True)]
  self.assertEqual(paired(a,b)["status"],"HOLD_NO_COMMON_COVERAGE")
 def test_paired_risk_only_on_common_cases(self):
  a=[r(1,True,False),r(2,True,True),r(3,False,None)]
  b=[r(1,True,True),r(2,True,True),r(3,True,False)]
  x=paired(a,b)
  self.assertEqual(x["both_emitted"],2);self.assertEqual(x["a_risk"],.5);self.assertEqual(x["b_risk"],1.0)
 def test_unmatched_case_universe(self):
  self.assertEqual(paired([r(1,True,False)],[r(2,True,False)])["status"],"HOLD_UNMATCHED_CASE_UNIVERSE")
 def test_source_mismatch(self):
  self.assertEqual(paired([r(1,True,False)],[r(1,True,False,game="other")])["status"],"HOLD_SOURCE_MISMATCH")
 def test_nonboolean_error_hold(self):
  self.assertEqual(paired([r(1,True,1)],[r(1,True,False)])["status"],"HOLD_INVALID_LABEL")
if __name__=="__main__":unittest.main()
