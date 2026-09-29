package main
import("encoding/json";"fmt";"os";"strings")
type Support struct{Pass bool `json:"pass"`;Qualified int `json:"qualified_worlds"`;Fired int `json:"fired_target_records"`;Misses int `json:"address_misses"`}
type Adj struct{Schema string `json:"schema"`;Stage string `json:"scientific_stage"`;Status string `json:"status"`;Verdict string `json:"verdict"`;Support Support `json:"support"`;Worlds int `json:"world_count"`;Raw bool `json:"raw_tt_key_emitted"`;Records []map[string]any `json:"records"`;Rep []map[string]any `json:"replicated_direct_pair_flip_signatures"`}
func die(s string){panic(s)}
func walk(v any){switch x:=v.(type){case map[string]any:for k,z:=range x{if k=="key"||k=="full_key"||k=="tt_key"{die("raw-key-field")};walk(z)};case []any:for _,z:=range x{walk(z)}}}
func main(){if len(os.Args)!=2{die("usage p13_verify adjudication.json")};b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var x Adj;if json.Unmarshal(b,&x)!=nil{die("json")}
 if x.Schema!="c3x-g95-p13-adjudication-v1"||x.Stage!="C3X 0.7.0-G9.5-P13"{die("identity")}
 if x.Raw||x.Worlds!=48{die("authority")}
 valid:=map[string]bool{"P13_REPLICATED_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY":true,"P13_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY_LOCAL_ONLY":true,"P13_ROOT_CANDIDATE_COMPETITION_REDIRECTION_WITHOUT_PAIRWISE_BOUNDARY_REPLICATION":true,"P13_NO_ROOT_PREFERENCE_BOUNDARY_EFFECT_UNDER_FROZEN_EXACT_EVENT_INTERVENTION":true,"P13_FRESH_SUPPORT_HOLD":true}
 if !valid[x.Verdict]{die("verdict")}
 if x.Verdict=="P13_REPLICATED_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY"&&len(x.Rep)==0{die("replication")}
 if x.Support.Pass&&x.Status!="CLOSED_PASS"{die("pass-status")};if !x.Support.Pass&&x.Status!="HOLD"{die("hold-status")}
 var raw any;if json.Unmarshal(b,&raw)!=nil{die("json2")};walk(raw)
 for _,r:=range x.Records{if r["raw_tt_key_emitted"]!=false{die("record-key")};eff,_:=r["effect_category"].(string);if eff=="DIRECT_PAIR_FLIP"{p,ok:=r["preference_boundary_crossed"].(bool);if !ok||!p{die("flip-flag")};pair,_:=r["isolated_pair"].(map[string]any);rr,_:=pair["rival"].(map[string]any);to,_:=r["t_only_root"].(map[string]any);if fmt.Sprint(rr["uci"])!=fmt.Sprint(to["uci"]){die("flip-rival")}}}
 if strings.Contains(string(b),"\"key\":"){die("serialized-key")}
 fmt.Println("P13_GO_VERIFY_PASS",x.Verdict,"records",len(x.Records),"qualified",x.Support.Qualified)
}
