package main
import("encoding/json";"fmt";"os")
type Support struct{Pass bool `json:"pass"`;Active int `json:"factorial_active_engine_worlds"`}
type Rec struct{Kind string `json:"kind"`;Bound string `json:"target_bound"`;Role string `json:"target_relation_delta_role"`}
type Adj struct{Schema string `json:"schema"`;Stage string `json:"scientific_stage"`;Status string `json:"status"`;Verdict string `json:"verdict"`;Worlds int `json:"world_count"`;Raw bool `json:"raw_tt_key_emitted"`;Support Support `json:"support"`;Records []Rec `json:"records"`;RepFull []any `json:"replicated_full_bridge_signatures"`;RepMod []any `json:"replicated_susceptibility_signatures"`}
func die(s string){panic(s)}
func walk(v any){switch x:=v.(type){case map[string]any:for k,z:=range x{if k=="key"||k=="full_key"||k=="tt_key"{die("raw-key-field")};walk(z)};case []any:for _,z:=range x{walk(z)}}}
func main(){
 if len(os.Args)!=2{die("usage p15_verify adjudication.json")}
 b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)}
 var x Adj;if json.Unmarshal(b,&x)!=nil{die("json")}
 if x.Schema!="c3x-g95-p15-adjudication-v1"||x.Stage!="C3X 0.7.0-G9.5-P15"||x.Worlds!=96||x.Raw{die("identity")}
 valid:=map[string]bool{
  "P15_REPLICATED_CHESS_STRUCTURE_SEARCH_PREFERENCE_FULL_BRIDGE":true,
  "P15_REPLICATED_CHESS_STRUCTURE_SUSCEPTIBILITY_MODULATION":true,
  "P15_LOCAL_CHESS_STRUCTURE_SEARCH_BRIDGE_ONLY":true,
  "P15_BOARD_DIRECT_PREFERENCE_EFFECT_WITHOUT_SEARCH_MEDIATION":true,
  "P15_NO_CHESS_STRUCTURE_SEARCH_BRIDGE_UNDER_FROZEN_GRAMMAR":true,
  "P15_FRESH_SUPPORT_HOLD":true}
 if !valid[x.Verdict]{die("verdict")}
 if x.Status=="CLOSED_PASS"&&!x.Support.Pass{die("pass-support")}
 if x.Status=="HOLD"&&x.Support.Pass{die("hold-support")}
 for _,r:=range x.Records{
  if r.Kind!="FULL_BRIDGE"&&r.Kind!="SUSCEPTIBILITY_MODULATION"{die("record-kind")}
  if r.Bound!="UPPER"&&r.Bound!="LOWER"{die("bound")}
  if r.Role!="ANCHOR_DISPREFERRED_DOMINANT"&&r.Role!="ANCHOR_PREFERRED_DOMINANT"&&r.Role!="BALANCED"{die("role")}
 }
 var raw any;if json.Unmarshal(b,&raw)!=nil{die("json2")};walk(raw)
 if x.Verdict=="P15_REPLICATED_CHESS_STRUCTURE_SEARCH_PREFERENCE_FULL_BRIDGE"&&len(x.RepFull)==0{die("rep-full")}
 if x.Verdict=="P15_REPLICATED_CHESS_STRUCTURE_SUSCEPTIBILITY_MODULATION"&&len(x.RepMod)==0{die("rep-mod")}
 fmt.Printf("P15_GO_VERIFY_PASS %s records %d active %d\n",x.Verdict,len(x.Records),x.Support.Active)
}
