package main
import("encoding/json";"fmt";"os")
type Support struct{Pass bool `json:"pass"`;Sets int `json:"complete_matched_sets"`;Family map[string]int `json:"family_exposure_counts"`}
type Rep struct{Replicated bool `json:"replicated"`}
type Cert struct{Schema string `json:"schema"`;Provenance string `json:"provenance_class"`;Concept any `json:"concept_label"`}
type Adj struct{Schema string `json:"schema"`;Stage string `json:"scientific_stage"`;Status string `json:"status"`;Verdict string `json:"verdict"`;Worlds int `json:"world_count"`;Raw bool `json:"raw_tt_key_emitted"`;Upper bool `json:"upper_is_diagnostic_only"`;Support Support `json:"support"`;H Rep `json:"primary_hypothesis_replication"`;Rivals []string `json:"replicated_rival_families"`;Adv int `json:"h_lower_advantage_over_strongest_rival"`;Certs []Cert `json:"causal_explanation_certificates"`}
func die(s string){panic(s)}
func walk(v any){switch x:=v.(type){case map[string]any:for k,z:=range x{if k=="key"||k=="full_key"||k=="tt_key"{die("raw-key-field")};walk(z)};case []any:for _,z:=range x{walk(z)}}}
func main(){
 if len(os.Args)!=2{die("usage")};b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)}
 var x Adj;if json.Unmarshal(b,&x)!=nil{die("json")}
 if x.Schema!="c3x-g95-p17-adjudication-v1"||x.Stage!="C3X 0.7.0-G9.5-P17"||x.Worlds!=216||x.Raw||!x.Upper{die("identity")}
 valid:=map[string]bool{"P17_HYPOTHESIS_SURVIVES_FATAL_REPLICATION_SPECIFICALLY":true,"P17_HYPOTHESIS_REPLICATES_BUT_NOT_SPECIFIC":true,"P17_RIVAL_FAMILY_REPLICATES_HYPOTHESIS_DEFEATED":true,"P17_HYPOTHESIS_FAILS_UNDER_BALANCED_EXPOSURE":true,"P17_EXPOSURE_SUPPORT_HOLD":true}
 if !valid[x.Verdict]{die("verdict")}
 if x.Status=="CLOSED_PASS"&&!x.Support.Pass{die("support")}
 if x.Support.Pass{v:=-1;for _,n:=range x.Support.Family{if v<0{v=n}else if v!=n{die("balance")}}}
 if x.Verdict=="P17_HYPOTHESIS_SURVIVES_FATAL_REPLICATION_SPECIFICALLY"&&(!x.H.Replicated||len(x.Rivals)>0||x.Adv<2){die("survival")}
 if x.Verdict=="P17_RIVAL_FAMILY_REPLICATES_HYPOTHESIS_DEFEATED"&&len(x.Rivals)==0{die("rival")}
 if x.Verdict=="P17_HYPOTHESIS_FAILS_UNDER_BALANCED_EXPOSURE"&&x.H.Replicated{die("failure")}
 for _,c:=range x.Certs{if c.Schema!="c3x-causal-contrast-certificate-v1"||c.Provenance!="C3X_CAUSAL_CONTRAST"||c.Concept!=nil{die("certificate")}}
 var raw any;if json.Unmarshal(b,&raw)!=nil{die("json2")};walk(raw)
 fmt.Printf("P17_GO_VERIFY_PASS %s sets %d certs %d\n",x.Verdict,x.Support.Sets,len(x.Certs))
}
