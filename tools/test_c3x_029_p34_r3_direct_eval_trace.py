import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_029_p34_r3_direct_nnue_classical_eval_trace import parse_trace

class DirectEvalTrace(unittest.TestCase):
 def test_extract_identical_board_raw_evaluations(self):
  s="""Contributing terms
 Classical evaluation   +0.32 (white side)
 NNUE evaluation        -0.11 (white side)
 Final evaluation       +0.08 (white side) [with scaled NNUE]
 """
  x=parse_trace(s)
  self.assertEqual(x["status"],"DIRECT_STATIC_TRACE_OK")
  self.assertAlmostEqual(x["raw_nnue_minus_classical_white_pawns"],-.43)
 def test_in_check_no_eval_is_hold(self):
  self.assertEqual(parse_trace("Final evaluation: none (in check)")["status"],"IN_CHECK_EVAL_NOT_AVAILABLE")
 def test_missing_nnue_trace_is_hold(self):
  self.assertEqual(parse_trace("Final evaluation +0.12 (white side)")["status"],"HOLD_EVAL_TRACE_MISSING")
if __name__=="__main__":unittest.main()
