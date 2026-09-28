package main

import (
 "encoding/json"
 "fmt"
 "os"
 "sort"
)

type Rec struct {
 RecordID string `json:"record_id"`
 Engine string `json:"engine"`
 PositionID string `json:"position_id"`
 Phase string `json:"phase"`
 SourceID string `json:"source_id"`
 RootChange bool `json:"root_change"`
}
type Merged struct{Schema string `json:"schema"`; ScientificStage string `json:"scientific_stage"`; Records []Rec `json:"records"`}
type Req struct{
 MinRootChangeEvents int `json:"min_root_change_events"`
 MinSensitiveWorlds int `json:"min_sensitive_worlds"`
 MinSensitivePositions int `json:"min_sensitive_positions"`
 MinPositiveEngines int `json:"min_positive_engines"`
 MinPositiveSources int `json:"min_positive_sources"`
 MinCrossEngineReplicatedPositions int `json:"min_cross_engine_replicated_positions"`
}
type Law struct{Schema string `json:"schema"`; HotspotRule struct{Requirements Req `json:"requirements"`} `json:"hotspot_rule"`}
type PhaseOut struct{Phase string `json:"phase"`; Records int `json:"records"`; Root int `json:"root_change_events"`; Hot bool `json:"operational_hotspot"`}
type Map struct{Schema string `json:"schema"`; PhaseMap []PhaseOut `json:"phase_map"`}

func read(path string, v any){b,e:=os.ReadFile(path);if e!=nil{panic(e)};if e=json.Unmarshal(b,v);e!=nil{panic(e)}}
func add(set map[string]bool,k string){set[k]=true}
func main(){
 if len(os.Args)!=5{panic("usage: p9-map-verify merged.json phase-law.json map.json out.json")}
 var x Merged;var law Law;var m Map
 read(os.Args[1],&x);read(os.Args[2],&law);read(os.Args[3],&m)
 if x.Schema!="c3x-p9-event-merged-v1"||law.Schema!="c3x-p9-phase-law-v1"||m.Schema!="c3x-g95-p9-map-v1"{panic("schema")}
 phases:=map[string][]Rec{}
 for _,r:=range x.Records{phases[r.Phase]=append(phases[r.Phase],r)}
 got:=map[string]PhaseOut{}
 req:=law.HotspotRule.Requirements
 for p,rs:=range phases{
  root:=0;worlds:=map[string]bool{};sw:=map[string]bool{};positions:=map[string]bool{};eng:=map[string]bool{};src:=map[string]bool{}
  posEng:=map[string]map[string]bool{}
  for _,r:=range rs{
   wk:=r.Engine+"|"+r.PositionID;worlds[wk]=true
   if r.RootChange{
    root++;sw[wk]=true;add(positions,r.PositionID);add(eng,r.Engine);add(src,r.SourceID)
    if posEng[r.PositionID]==nil{posEng[r.PositionID]=map[string]bool{}}
    posEng[r.PositionID][r.Engine]=true
   }
  }
  repl:=0;for _,es:=range posEng{if len(es)>=2{repl++}}
  hot:=root>=req.MinRootChangeEvents&&len(sw)>=req.MinSensitiveWorlds&&len(positions)>=req.MinSensitivePositions&&len(eng)>=req.MinPositiveEngines&&len(src)>=req.MinPositiveSources&&repl>=req.MinCrossEngineReplicatedPositions
  got[p]=PhaseOut{Phase:p,Records:len(rs),Root:root,Hot:hot}
 }
 exp:=map[string]PhaseOut{};for _,z:=range m.PhaseMap{exp[z.Phase]=z}
 pass:=true;diff:=[]string{}
 keys:=make([]string,0,len(got));for k:=range got{keys=append(keys,k)};sort.Strings(keys)
 for _,k:=range keys{
  a:=got[k];b,ok:=exp[k]
  if !ok||a.Records!=b.Records||a.Root!=b.Root||a.Hot!=b.Hot{pass=false;diff=append(diff,k)}
 }
 out:=map[string]any{"schema":"c3x-g95-p9-go-map-parity-v1","scientific_stage":"C3X 0.7.0-G9.5-P9","pass":pass,"phase_differences":diff,"phases_checked":len(got)}
 b,_:=json.MarshalIndent(out,"","  ");_ = os.WriteFile(os.Args[4],append(b,'\n'),0644)
 fmt.Println("P9_GO_MAP_PARITY",pass,"phases",len(got))
 if !pass{os.Exit(2)}
}
