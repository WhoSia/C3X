import unittest
from tools.c3x_027_game14_root_boundary_court import parse_boundary_lines,compare_worlds
def fixture(score=4):
 return "\n".join(
   f"event=ROOT_BOUNDARY depth={d} leader={17+d} score={score+d} average={score+d-1}"
   for _ in range(2) for d in (1,2,3))
class SourceBoundaryCourtTests(unittest.TestCase):
 def test_replay_parity(self):
  self.assertEqual(parse_boundary_lines(fixture())["status"],
                   "PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS")
 def test_change_across_runs_is_hold(self):
  s=fixture();s=s.replace("score=7 average=6","score=8 average=6",1)
  self.assertEqual(parse_boundary_lines(s.splitlines())["status"],
                   "HOLD_COLD_BOUNDARIES_MISSING_OR_CHANGED")
 def test_three_worlds(self):
  x=compare_worlds({"A":fixture(4),"B":fixture(7),"C":fixture(4)})
  self.assertEqual(x["status"],"PASS_OBSERVATIONAL_DEPTH_COMPARISON")
  self.assertEqual(x["first_B_C_boundary_difference"]["depth"],1)
  self.assertFalse(x["causal_parent_to_root_certified"])
 def test_absence_is_hold(self):
  self.assertEqual(compare_worlds({})["status"],"HOLD_INCOMPLETE_NATIVE_DEPTH_DATA")
if __name__=="__main__":unittest.main()
