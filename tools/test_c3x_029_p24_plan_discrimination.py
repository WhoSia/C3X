import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p24_plan_discrimination import score
def r(i,a,b,v=True):return {"reply_id":str(i),"a_plan":a,"b_plan":b,"verified":v}
class P24(unittest.TestCase):
 def test_shared_is_not_discriminating(self):
  x=score([r(1,True,True),r(2,True,True)])
  self.assertEqual(x["a_only_reply_fraction"],0)
 def test_one_vs_two(self):
  x=score([r(1,True,False),r(2,True,True)])
  self.assertEqual(x["a_only_reply_fraction"],.5)
 def test_unverified_oracle_is_hold(self):
  self.assertEqual(score([r(1,True,False,False)])["status"],"HOLD_ORACLE")
 def test_duplicate_reply_rejected(self):
  self.assertEqual(score([r(1,True,False),r(1,True,False)])["status"],"FAIL_DUPLICATE_REPLY")
 def test_empty(self):
  self.assertEqual(score([])["status"],"HOLD_EMPTY")
if __name__=="__main__":unittest.main()
