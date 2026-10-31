import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p21_source_move_legal_probe import inspect
P=Path(__file__).resolve().parents[1]/"c3x/cohorts/c3x-016-P4-Lichess-12-standalone-FEN-source-geometry-3x4-preoutcome.json"
class P21(unittest.TestCase):
 def test_actual_archived_twelve(self):
  rows=json.loads(P.read_text())["cases"]
  self.assertEqual(len(rows),12)
  for r in rows:
   with self.subTest(case=r["id"]):
    self.assertEqual(inspect(r["fen"],r["played_uci"]),"PASS_BOUNDED_NON_SPECIAL_MOVE_ONLY")
 def test_wrong_side(self):
  self.assertEqual(inspect("4k3/8/8/8/8/8/8/4K3 w - -","e8e7"),"FAIL_WRONG_SIDE")
 def test_nonexistent_piece(self):
  self.assertEqual(inspect("4k3/8/8/8/8/8/8/4K3 w - -","a1a2"),"FAIL_NO_SOURCE_PIECE")
 def test_self_check(self):
  self.assertEqual(inspect("k3r3/8/8/8/8/8/4R3/4K3 w - -","e2d2"),"FAIL_SELF_CHECK")
 def test_blocked(self):
  self.assertEqual(inspect("4k3/8/8/8/8/8/4P3/4RK2 w - -","e1e3"),"FAIL_BLOCKED")
 def test_unsupported_castling(self):
  self.assertEqual(inspect("4k3/8/8/8/8/8/8/4K2R w K -","e1g1"),"FAIL_BAD_GEOMETRY")
if __name__=="__main__":unittest.main()
