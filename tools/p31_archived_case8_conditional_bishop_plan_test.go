package main
import "testing"

// C3X historical exposed DEVELOPMENT case 8; source board from frozen P4 cohort.
// Independent chess-law experiment: separate each candidate's opponent reply domain.
// This is a full single-ply reply enumeration, NOT value/engine preference proof.
func TestP31BishopCaptureReplyRobustness(t *testing.T) {
 base,err:=Parse("2k2r2/pp1rp2p/1bp1b1p1/4p1Pn/4P2P/1PP2P1B/P1K5/R1B2N1R b - -")
 if err!=nil {t.Fatal(err)}
 root:=map[string]Board{}
 for _,m:=range base.Legal() {
  if m.UCI()=="e6h3" || m.UCI()=="h5g7" {root[m.UCI()]=base.Do(m)}
 }
 if len(root)!=2 {t.Fatal("missing root moves")}
 // After 1...Bxh3, one of White's twenty legal replies is 2.Rxh3.
 took:=root["e6h3"]
 if took.sq[sq(7,2)]!='b' {t.Fatal("Bxh3 must capture White's bishop")}
 totalTake, bishopSurvives:=0,0
 recapture:=[]string{}
 for _,reply:=range took.Legal(){
  totalTake++;next:=took.Do(reply)
  if next.sq[sq(7,2)]=='b' {bishopSurvives++} else {recapture=append(recapture,reply.UCI())}
 }
 if totalTake!=20 || bishopSurvives!=19 || len(recapture)!=1 || recapture[0]!="h1h3"{
  t.Fatalf("take: replies=%d survive=%d recaptures=%v",totalTake,bishopSurvives,recapture)
 }
 // After 1...Ng7, opponent controls whether White bishop remains on h3;
 // enumerate 24 distinct White legal replies, not equated to ...Bxh3 world.
 wait:=root["h5g7"]
 totalWait,stillCanCapture:=0,0
 denials:=map[string]bool{}
 for _,reply:=range wait.Legal(){
  totalWait++;next:=wait.Do(reply)
  feasible:=false
  if next.sq[sq(7,2)]=='B' {
   for _,m:=range next.Legal(){if m.UCI()=="e6h3"{feasible=true;break}}
  }
  if feasible {stillCanCapture++} else {denials[reply.UCI()]=true}
 }
 expected:=[]string{"h3g4","h3f5","h3e6","h3g2"}
 if totalWait!=24 || stillCanCapture!=20 || len(denials)!=4 {
  t.Fatalf("wait: replies=%d conditional_capture=%d denials=%v",totalWait,stillCanCapture,denials)
 }
 for _,x:=range expected {if !denials[x]{t.Errorf("expected refusal by bishop relocation %s",x)}}
 t.Logf("Bxh3: %d/%d black bishop survives White reply; recapture Rxh3. Ng7: %d/%d legal White replies allow subsequent Bxh3; four move bishop away.",bishopSurvives,totalTake,stillCanCapture,totalWait)
}
