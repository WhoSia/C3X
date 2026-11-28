import hashlib
import unittest
from collections import Counter
import chess
from c3x_031_r55_checkpoint_policy import CHECKPOINTS, choose_checkpoint, legal_checkpoints, distribution

def digest(i):
    return hashlib.sha256(str(i).encode()).hexdigest()

class PolicyTest(unittest.TestCase):
    def test_empty_singleton(self):
        self.assertIsNone(choose_checkpoint(digest(0), []))
        self.assertEqual(choose_checkpoint(digest(0), [(41,"key")]),(41,"key"))
    def test_order_and_coverage(self):
        candidates=[(p,str(p)) for p in CHECKPOINTS]
        counts=Counter()
        for i in range(2048):
            a=choose_checkpoint(digest(i), candidates)
            self.assertEqual(a,choose_checkpoint(digest(i),list(reversed(candidates))))
            counts[a[0]]+=1
        self.assertEqual(set(counts),set(CHECKPOINTS))
        self.assertGreater(sum(v for p,v in counts.items() if p%2),800)
        self.assertLess(sum(v for p,v in counts.items() if p%2),1248)
        print("synthetic checkpoint counts",dict(sorted(counts.items())))
    def test_rejects_bad_inputs(self):
        for d,r in [("bad",[]),(digest(0),[(40,"x"),(40,"y")]),(digest(0),[(42,"x")]),(digest(0),[(40,"")])]:
            with self.assertRaises(ValueError):
                choose_checkpoint(d,r)
    def test_real_legal_replay_no_mutation(self):
        b=chess.Board()
        replay=b.copy()
        # Use deterministic legal random walks rather than repeat a four-ply cycle.
        import random
        rng=random.Random(42)
        moves=[]
        for _ in range(81):
            if replay.is_game_over(): break
            m=rng.choice(sorted(replay.legal_moves,key=lambda m:m.uci()))
            moves.append(m);replay.push(m)
        rows=legal_checkpoints(b,moves,lambda board:board.fen())
        self.assertEqual(b.fen(),chess.STARTING_FEN)
        self.assertTrue(rows)
        for p,k in rows:
            verify=chess.Board()
            for m in moves[:p]: verify.push(m)
            self.assertEqual(k,verify.fen())
            self.assertEqual(verify.turn,p%2==0)
    def test_distribution(self):
        d=distribution([{"ply":40,"eligible_count":2},{"ply":41,"eligible_count":2}])
        self.assertEqual(d["side"],{"white":1,"black":1})
if __name__=="__main__":unittest.main()
