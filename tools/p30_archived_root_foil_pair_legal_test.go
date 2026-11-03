package main

import "testing"

// A historical SOURCE-BACKED FEN-only DEVELOPMENT pairing, not a new
// Stockfish result and not a verified full-game-history state.
func TestP30ArchivedOrderSensitiveCandidatePairsAreLegal(t *testing.T) {
 cases := []struct{ id string; fen string; original string; reordered string }{
  {"6", "6k1/1b2bppp/p3p3/2p4n/2PnN3/2NB3P/PP3PPB/6K1 w - -", "c3a4", "e4d6"},
  {"8", "2k2r2/pp1rp2p/1bp1b1p1/4p1Pn/4P2P/1PP2P1B/P1K5/R1B2N1R b - -", "e6h3", "h5g7"},
 }
 for _,tc := range cases {
  board,err:=Parse(tc.fen)
  if err!=nil { t.Fatalf("case %s FEN: %v",tc.id,err) }
  legal:=map[string]bool{}
  for _,m:=range board.Legal(){legal[m.UCI()]=true}
  if !legal[tc.original] || !legal[tc.reordered] {
   t.Errorf("case %s: original %s legal %v, order-changed %s legal %v",tc.id,tc.original,legal[tc.original],tc.reordered,legal[tc.reordered])
  }
  t.Logf("case %s root legal moves %d; recorded bestmoves %s / %s both legal",tc.id,len(legal),tc.original,tc.reordered)
 }
}
