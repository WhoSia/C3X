package main
import("encoding/json";"fmt";"os")
type Rep struct{Replicated bool `json:"replicated"`}
type Support struct{Pass bool `json:"pass"`; Complete int `json:"complete_matched_sets"`}
type X struct{Schema string `json:"schema"`; Verdict string `json:"verdict"`; Upper bool `json:"upper_is_diagnostic_only"`; Raw bool `json:"raw_tt_key_emitted"`; Support Support `json:"confirmation_support"`; Primary Rep `json:"primary_hypothesis_replication"`; Rivals []string `json:"replicated_rival_families"`; Advantage int `json:"h_lower_advantage_over_strongest_rival"`; Certs []map[string]any `json:"causal_explanation_certificates"`}
func main(){if len(os.Args)!=2{panic("arg")};b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var x X;if json.Unmarshal(b,&x)!=nil{panic("json")}
 if x.Schema!="c3x-g95-p18-adjudication-v1"||!x.Upper||x.Raw{panic("contract")}
 if x.Verdict=="P18_HYPOTHESIS_SURVIVES_SUPPORT_REALIZED_FATAL_REPLICATION"&&(!x.Support.Pass||!x.Primary.Replicated||len(x.Rivals)>0||x.Advantage<2){panic("survival")}
 fmt.Println("P18_GO_VERIFY_PASS",x.Verdict,"sets",x.Support.Complete,"certs",len(x.Certs))}
