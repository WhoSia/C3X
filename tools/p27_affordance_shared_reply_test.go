package main
import "testing"
// Intended to be run alongside the historical Go chess engine recovered in P22.
// This is a one-reply non-discrimination control, not a full policy or value test.
func p27LegalApply(t *testing.T,b Board,uci string) Board {
 t.Helper()
 for _,m:=range b.Legal(){if m.UCI()==uci{return b.Do(m)}}
 t.Fatalf("illegal sequence step %s",uci);return b
}
func TestP27SharedPlanDoesNotDiscriminate(t *testing.T){
 base,e:=Parse("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
 if e!=nil{t.Fatal(e)}
 for _,a:=range []string{"e2e4","d2d4"}{
  b:=p27LegalApply(t,base,a)
  b=p27LegalApply(t,b,"e7e5")
  _=p27LegalApply(t,b,"g1f3")
 }
}
