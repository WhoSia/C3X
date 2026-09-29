package main
import("encoding/json";"fmt";"os")
type Support struct{Pass bool `json:"pass"`;Fired int `json:"fired_target_records"`;Root int `json:"root_change_targets"`;Engines []string `json:"positive_engines"`;Sources []string `json:"positive_sources"`;Positions int `json:"sensitive_positions"`;Pairs int `json:"exact_cutoff_pairs"`;Mediated int `json:"mediated_targets"`}
type Adj struct{Schema string `json:"schema"`;Stage string `json:"scientific_stage"`;Status string `json:"status"`;Verdict string `json:"verdict"`;Support Support `json:"support"`;Worlds int `json:"world_count"`;Raw bool `json:"raw_tt_key_emitted"`;Records []map[string]any `json:"records"`}
func die(s string){panic(s)}
func main(){if len(os.Args)!=2{die("usage p12_verify adjudication.json")};b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var x Adj;if json.Unmarshal(b,&x)!=nil{die("json")}
 if x.Schema!="c3x-g95-p12-adjudication-v1"||x.Stage!="C3X 0.7.0-G9.5-P12"{die("identity")}
 if x.Raw||x.Worlds!=36{die("authority")}
 valid:=map[string]bool{"P12_FRESH_SUPPORT_HOLD":true,"P12_REPLICATED_EXACT_CUTOFF_MEDIATION":true,"P12_EXACT_CUTOFF_MEDIATION_IDENTIFIED_REPLICATION_HOLD":true,"P12_CUTOFF_COLOCATION_ONLY":true}
 if !valid[x.Verdict]{die("verdict")}
 if x.Support.Pass && x.Status!="CLOSED_PASS"{die("pass-status")}
 if !x.Support.Pass && x.Status!="HOLD"{die("hold-status")}
 for _,r:=range x.Records{if v,ok:=r["raw_tt_key_emitted"];!ok||v!=false{die("record-key")}}
 fmt.Println("P12_GO_VERIFY_PASS",x.Verdict,"records",len(x.Records),"root",x.Support.Root)
}
