package main
import("encoding/json";"fmt";"os";"sort")
type Rec struct{Engine string `json:"engine"`;PositionID string `json:"position_id"`;SourceID string `json:"source_id"`;A0ID string `json:"a0_id"`;RootChange bool `json:"root_change"`}
type Merged struct{Schema string `json:"schema"`;Records []Rec `json:"records"`}
type Gate struct{MinTotalFiredRecords int `json:"min_total_fired_records"`;MinTotalRootChange int `json:"min_total_root_change"`;MinRecordsPerEngine int `json:"min_records_per_engine"`;MinPositiveEngines int `json:"min_positive_engines"`;MinPositiveSources int `json:"min_positive_sources"`;MinSensitivePositions int `json:"min_sensitive_positions"`;MinCrossEngineReplicatedPositions int `json:"min_cross_engine_replicated_positions"`}
type Rep struct{MinRootChangeEvents int `json:"min_root_change_events"`;MinPositiveEngines int `json:"min_positive_engines"`;MinPositivePositions int `json:"min_positive_positions"`;MinPositiveSources int `json:"min_positive_sources"`}
type Law struct{Schema string `json:"schema"`;SupportGate Gate `json:"support_gate"`;Lineage struct{Replicated Rep `json:"replicated_primary_archetype_rule"`} `json:"lineage"`}
type Out struct{Schema string `json:"schema"`;Support struct{Pass bool `json:"pass"`;Records int `json:"records"`;Root int `json:"root_change"`} `json:"support"`;Replicated []any `json:"replicated_a0_archetypes"`}
func read(p string,v any){b,e:=os.ReadFile(p);if e!=nil{panic(e)};if e=json.Unmarshal(b,v);e!=nil{panic(e)}}
func main(){
 if len(os.Args)!=5{panic("usage: p10-anatomy-verify merged law anatomy out")}
 var x Merged;var l Law;var o Out;read(os.Args[1],&x);read(os.Args[2],&l);read(os.Args[3],&o)
 engN:=map[string]int{};pEng:=map[string]bool{};pSrc:=map[string]bool{};pPos:=map[string]bool{};posEng:=map[string]map[string]bool{}
 type gdat struct{n int;eng,pos,src map[string]bool};gm:=map[string]*gdat{};root:=0
 for _,r:=range x.Records{engN[r.Engine]++;if r.RootChange{root++;pEng[r.Engine]=true;pSrc[r.SourceID]=true;pPos[r.PositionID]=true;if posEng[r.PositionID]==nil{posEng[r.PositionID]=map[string]bool{}};posEng[r.PositionID][r.Engine]=true
  if gm[r.A0ID]==nil{gm[r.A0ID]=&gdat{eng:map[string]bool{},pos:map[string]bool{},src:map[string]bool{}}};z:=gm[r.A0ID];z.n++;z.eng[r.Engine]=true;z.pos[r.PositionID]=true;z.src[r.SourceID]=true}}
 replPos:=0;for _,z:=range posEng{if len(z)>=2{replPos++}}
 pass:=len(x.Records)>=l.SupportGate.MinTotalFiredRecords&&root>=l.SupportGate.MinTotalRootChange&&len(pEng)>=l.SupportGate.MinPositiveEngines&&len(pSrc)>=l.SupportGate.MinPositiveSources&&len(pPos)>=l.SupportGate.MinSensitivePositions&&replPos>=l.SupportGate.MinCrossEngineReplicatedPositions
 for _,n:=range engN{if n<l.SupportGate.MinRecordsPerEngine{pass=false}}
 ids:=[]string{};if pass{for id,z:=range gm{if z.n>=l.Lineage.Replicated.MinRootChangeEvents&&len(z.eng)>=l.Lineage.Replicated.MinPositiveEngines&&len(z.pos)>=l.Lineage.Replicated.MinPositivePositions&&len(z.src)>=l.Lineage.Replicated.MinPositiveSources{ids=append(ids,id)}}};sort.Strings(ids)
 ok:=x.Schema=="c3x-p10-event-merged-v1"&&o.Schema=="c3x-g95-p10-anatomy-v1"&&o.Support.Pass==pass&&o.Support.Records==len(x.Records)&&o.Support.Root==root&&len(o.Replicated)==len(ids)
 out:=map[string]any{"schema":"c3x-g95-p10-go-anatomy-parity-v1","scientific_stage":"C3X 0.7.0-G9.5-P10","pass":ok,"support_pass":pass,"root_change":root,"replicated_a0_count":len(ids),"replicated_a0_ids":ids}
 b,_:=json.MarshalIndent(out,"","  ");_ = os.WriteFile(os.Args[4],append(b,'\n'),0644);fmt.Println("P10_GO_ANATOMY_PARITY",ok,"positive",root,"replicated",len(ids));if !ok{os.Exit(2)}
}
