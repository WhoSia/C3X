package main
import "testing"

// The recorded source-order-sensitive case 8 is DEVELOPMENT data.
// "Captures White's h3 bishop" is a board-true candidate discriminator,
// not a proof that it is the reason for a stable root preference.
func TestP30CandidateCaptureIsTrueButNotSourceStableExplanation(t *testing.T) {
 b,err:=Parse("2k2r2/pp1rp2p/1bp1b1p1/4p1Pn/4P2P/1PP2P1B/P1K5/R1B2N1R b - -")
 if err!=nil { t.Fatal(err) }
 h3:=sq(7,2)
 if b.sq[h3]!='B' {t.Fatalf("original h3 expected white Bishop, got %c",b.sq[h3])}
 branches:=map[string]Board{}
 for _,m:=range b.Legal(){
   if m.UCI()=="e6h3" || m.UCI()=="h5g7" {branches[m.UCI()]=b.Do(m)}
 }
 if len(branches)!=2 {t.Fatalf("missing recorded candidate; got %d",len(branches))}
 if branches["e6h3"].sq[h3]!='b' { t.Errorf("bishop-capture candidate must occupy h3 with black bishop") }
 if branches["h5g7"].sq[h3]!='B' { t.Errorf("knight retreat candidate must leave White bishop at h3") }
}
