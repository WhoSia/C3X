import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p18_cluster_uncertainty import bootstrap_game_macro as b
class Bootstrap(unittest.TestCase):
 def test_too_few_independent_games_hold(self):
  self.assertEqual(b([dict(game_id="a",error=True)]*100)["status"],"HOLD_TOO_FEW_GAMES")
 def test_constant_game_rates_have_zero_width(self):
  rows=[dict(game_id=str(i),error=False) for i in range(6)]
  z=b(rows,iterations=200);self.assertEqual(z["percentile_95"],[0,0])
 def test_reproducible_seed(self):
  rows=[dict(game_id=str(i),error=i%2==0) for i in range(8)]
  self.assertEqual(b(rows,iterations=150,seed=17),b(rows,iterations=150,seed=17))
 def test_unknown_error_abstain(self):
  rows=[dict(game_id=str(i),error=None) for i in range(8)]
  self.assertEqual(b(rows)["status"],"HOLD_UNVERIFIED_LABELS")
if __name__=="__main__":unittest.main()
