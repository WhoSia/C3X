package main
import("encoding/json";"fmt";"os";"strings")
type Support struct{Pass bool `json:"pass"`;Pairs int `json:"admitted_pair_positions"`;Active int `json:"active_engine_worlds"`;Fired int `json:"fired_target_records"`;Misses int `json:"address_misses"`}
type Adj struct{Schema string `json:"schema"`;Stage string `json:"scientific_stage"`;Status string `json:"status"`;Verdict string `json:"verdict"`;Support Support `json:"support"`;Worlds int `json:"world_count"`;Raw bool `json:"raw_tt_key_emitted"`;Records []map[string]any `json:"records"`;Rep []map[string]any `json:"replicated_orientation_free_reversal_signatures"`;RepRecip []map[string]any `json:"replicated_reciprocal_signatures"`}
func die(s string){panic(s)}
func walk(v any){switch x:=v.(type){case map[string]any:for k,z:=range x{if k=="key"||k=="full_key"||k=="tt_key"{die("raw-key-field")};walk(z)};case []any:for _,z:=range x{walk(z)}}}
func main(){if len(os.Args)!=2{die("usage p14_verify adjudication.json")};b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var x Adj;if json.Unmarshal(b,&x)!=nil{die("json")}
 if x.Schema!="c3x-g95-p14-adjudication-v1"||x.Stage!="C3X 0.7.0-G9.5-P14"{die("identity")}
 if x.Raw||x.Worlds!=72{die("authority")}
 valid:=map[string]bool{"P14_REPLICATED_RECIPROCAL_CROSS_ENGINE_PAIR_GEOMETRY":true,"P14_REPLICATED_ORIENTATION_FREE_PAIR_REVERSAL_TRANSPORT":true,"P14_LOCAL_MULTIENGINE_UNORDERED_PAIR_TRANSPORT_ONLY":true,"P14_LOCAL_UNORDERED_PAIR_EDGE_CAUSALITY_ONLY":true,"P14_NO_PAIR_EDGE_REVERSAL_UNDER_FROZEN_EXACT_EVENT_INTERVENTION":true,"P14_FRESH_SUPPORT_HOLD":true}
 if !valid[x.Verdict]{die("verdict")}
 if x.Verdict=="P14_REPLICATED_RECIPROCAL_CROSS_ENGINE_PAIR_GEOMETRY"&&len(x.RepRecip)==0{die("reciprocal-replication")}
 if x.Verdict=="P14_REPLICATED_ORIENTATION_FREE_PAIR_REVERSAL_TRANSPORT"&&len(x.Rep)==0{die("event-replication")}
 if x.Support.Pass&&x.Status!="CLOSED_PASS"{die("pass-status")};if !x.Support.Pass&&x.Status!="HOLD"{die("hold-status")}
 var raw any;if json.Unmarshal(b,&raw)!=nil{die("json2")};walk(raw)
 for _,r:=range x.Records{
  if r["raw_tt_key_emitted"]!=false{die("record-key")}
  rel:=fmt.Sprint(r["target_relation"]);if rel!="BASELINE_PREFERRED"&&rel!="BASELINE_DISPREFERRED"{die("relation")}
  eff:=fmt.Sprint(r["effect_category"])
  if eff=="EDGE_REVERSAL"{
   if r["edge_reversed"]!=true{die("reversal-flag")}
   p:=r["pair"].(map[string]any);a:=p["A"].(map[string]any);bb:=p["B"].(map[string]any);base:=r["baseline_preferred"].(map[string]any);to:=r["t_only_root"].(map[string]any)
   bu:=fmt.Sprint(base["uci"]);tu:=fmt.Sprint(to["uci"]);au:=fmt.Sprint(a["uci"]);bbu:=fmt.Sprint(bb["uci"])
   if !((bu==au&&tu==bbu)||(bu==bbu&&tu==au)){die("reversal-pair")}
  }
 }
 if strings.Contains(string(b),"\"key\":"){die("serialized-key")}
 fmt.Println("P14_GO_VERIFY_PASS",x.Verdict,"records",len(x.Records),"pairs",x.Support.Pairs,"active",x.Support.Active)
}
