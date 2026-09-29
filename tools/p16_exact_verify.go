package main
import("encoding/json";"fmt";"os")
type Support struct{Pass bool `json:"pass"`}
type Cert struct{Schema string `json:"schema"`;Provenance string `json:"provenance_class"`;Concept any `json:"concept_label"`;Subset bool `json:"subset_reproduced"`;Sham bool `json:"sham_reproduced"`}
type Adj struct{Schema string `json:"schema"`;Stage string `json:"scientific_stage"`;Status string `json:"status"`;Verdict string `json:"verdict"`;Worlds int `json:"world_count"`;Raw bool `json:"raw_tt_key_emitted"`;Support Support `json:"support"`;Minimal int `json:"minimal_full_bridge_records"`;Exact []any `json:"replicated_exact_structural_signatures"`;Coarse []any `json:"replicated_coarse_full_bridge_signatures"`;Certs []Cert `json:"causal_explanation_certificates"`}
func die(s string){panic(s)}
func walk(v any){switch x:=v.(type){case map[string]any:for k,z:=range x{if k=="key"||k=="full_key"||k=="tt_key"{die("raw-key-field")};walk(z)};case []any:for _,z:=range x{walk(z)}}}
func main(){
 if len(os.Args)!=2{die("usage")}
 b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)}
 var x Adj;if json.Unmarshal(b,&x)!=nil{die("json")}
 if x.Schema!="c3x-g95-p16-adjudication-v1"||x.Stage!="C3X 0.7.0-G9.5-P16"||x.Worlds!=108||x.Raw{die("identity")}
 valid:=map[string]bool{"P16_REPLICATED_MINIMAL_STRUCTURAL_EQUIVALENCE_FULL_BRIDGE":true,"P16_REPLICATED_FULL_PREFERENCE_MEDIATION_NO_STABLE_MINIMAL_EQUIVALENCE":true,"P16_LOCAL_MINIMAL_FULL_BRIDGE_ONLY":true,"P16_REPLICATED_SUSCEPTIBILITY_ONLY":true,"P16_NO_FULL_BRIDGE_UNDER_FROZEN_MINIMIZATION_FAMILY":true,"P16_FRESH_SUPPORT_HOLD":true}
 if !valid[x.Verdict]{die("verdict")}
 if x.Status=="CLOSED_PASS"&&!x.Support.Pass{die("pass-support")}
 if x.Status=="HOLD"&&x.Support.Pass{die("hold-support")}
 for _,c:=range x.Certs{if c.Schema!="c3x-causal-contrast-certificate-v1"||c.Provenance!="C3X_CAUSAL_CONTRAST"||c.Concept!=nil||c.Subset||c.Sham{die("certificate")}}
 var raw any;if json.Unmarshal(b,&raw)!=nil{die("json2")};walk(raw)
 if x.Verdict=="P16_REPLICATED_MINIMAL_STRUCTURAL_EQUIVALENCE_FULL_BRIDGE"&&len(x.Exact)==0{die("exact")}
 if x.Verdict=="P16_REPLICATED_FULL_PREFERENCE_MEDIATION_NO_STABLE_MINIMAL_EQUIVALENCE"&&(len(x.Exact)!=0||len(x.Coarse)==0){die("coarse")}
 fmt.Printf("P16_GO_VERIFY_PASS %s minimal %d certificates %d\n",x.Verdict,x.Minimal,len(x.Certs))
}
