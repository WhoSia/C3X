package main
import "testing"
// Works with archived Go chess rules from P22. All legal immediate replies
// after each candidate are enumerated; this does NOT claim strategy value.
func p28Apply(t *testing.T,b Board,uci string) Board {
 t.Helper()
 for _,m:=range b.Legal(){if m.UCI()==uci{return b.Do(m)}}
 t.Fatalf("illegal move %s",uci)
 return b
}
func TestP28Nf3AllReplies(t *testing.T){
 base,e:=Parse("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
 if e!=nil{t.Fatal(e)}
 for _,a:=range []string{"e2e4","d2d4"}{
  b:=p28Apply(t,base,a)
  replies:=b.Legal()
  available:=0
  failures:=[]string{}
  for _,r:=range replies {
   next:=b.Do(r)
   found:=false
   for _,m:=range next.Legal(){if m.UCI()=="g1f3"{found=true;break}}
   if found {available++} else {failures=append(failures,r.UCI())}
  }
  if len(replies)!=20 || available!=20 || len(failures)!=0 {
   t.Fatalf("%s: replies=%d available=%d failure=%v",a,len(replies),available,failures)
  }
  t.Logf("candidate=%s replies=%d Nf3_available=%d",a,len(replies),available)
 }
}
