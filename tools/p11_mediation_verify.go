package main
import("encoding/json";"fmt";"os")
type Support struct{Pass bool `json:"pass"`;Targets int `json:"targets"`;Exact int `json:"exact_parent_replays"`;Engines []string `json:"valid_engines"`;Bounds []string `json:"valid_bound_variants"`;CutoffObserved int `json:"cases_with_cutoff_observed"`;CutoffDiverged int `json:"cases_with_first_cutoff_divergence"`;Classes []string `json:"observed_semantic_classes"`}
type Adj struct{Schema string `json:"schema"`;Stage string `json:"scientific_stage"`;Fresh bool `json:"fresh_confirmatory_vote"`;Status string `json:"status"`;Verdict string `json:"verdict"`;Support Support `json:"support"`;Raw bool `json:"raw_tt_key_emitted"`;Cases []map[string]any `json:"cases"`}
func die(s string){panic(s)}
func main(){
 if len(os.Args)!=2{die("usage: p11_mediation_verify adjudication.json")}
 b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)}
 var x Adj;if json.Unmarshal(b,&x)!=nil{die("json")}
 if x.Schema!="c3x-g95-p11-adjudication-v1"||x.Stage!="C3X 0.7.0-G9.5-P11"{die("identity")}
 if x.Fresh||x.Raw{die("authority")}
 if len(x.Cases)!=17||x.Support.Targets!=17||x.Support.Exact!=17{die("target-count")}
 if len(x.Support.Engines)<2||len(x.Support.Bounds)<2{die("support-spread")}\n if x.Support.CutoffObserved<1{die("cutoff-unobserved")}\n foundCutoff:=false;for _,c:=range x.Support.Classes{if c=="CUTOFF"{foundCutoff=true}};if !foundCutoff{die("cutoff-class-missing")}
 if !x.Support.Pass||x.Status!="CLOSED_PASS"||x.Verdict!="P11_BOUNDED_MEDIATION_AND_PATCH_DIAGNOSTIC_CLOSED"{die("verdict")}
 for _,c:=range x.Cases{
   if _,ok:=c["raw_tt_key"];ok{die("raw-key-field")}
   if v,ok:=c["raw_tt_key_emitted"];ok&&v!=false{die("raw-key")}
   if c["status"]!="PASS"{die("case-hold")}
 }
 fmt.Println("P11_GO_VERIFY_PASS",x.Verdict,"targets",len(x.Cases))
}
