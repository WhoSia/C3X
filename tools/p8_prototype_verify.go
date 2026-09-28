package main
import("encoding/json";"fmt";"math";"os";"sort")

const eps=1e-12
type Block struct{Name string;Weight float64;Keys []string}
func read(p string)map[string]any{b,e:=os.ReadFile(p);if e!=nil{panic(e)};var x map[string]any;if json.Unmarshal(b,&x)!=nil{panic("json")};return x}
func sm(m map[string]any,k string)string{if v,ok:=m[k].(string);ok{return v};return ""}
func desc(r map[string]any)map[string]any{return r["descriptor"].(map[string]any)}
func blocks()[]Block{return []Block{
 {"board",.15,[]string{"side_to_move","in_check","phase","legal_moves_bucket","material_balance_bucket","castling_bucket","halfmove_bucket"}},
 {"current_event",.30,[]string{"scope","class","ply_bucket","depth_bucket","bound_bucket","window_relation","move_presence","payload_bucket"}},
 {"provenance_rates",.30,[]string{"cutoff_share","move_order_share","eval_share","pv_share","qsearch_share","current_scope_share","current_class_share","unique_key_ratio","repeated_key_event_share","current_key_share","same_key_gap_ratio","same_class_gap_ratio","depth_percentile","same_ply_share"}},
 {"temporal_shape",.20,[]string{"q1_class","q1_scope","q1_reuse","q2_class","q2_scope","q2_reuse","q3_class","q3_scope","q3_reuse","q4_class","q4_scope","q4_reuse"}},
 {"coarse_scale",.05,[]string{"prefix_size_bucket"}}}}
func dist(a,b map[string]any)float64{z:=0.0;for _,bl:=range blocks(){aa:=a[bl.Name].(map[string]any);bb:=b[bl.Name].(map[string]any);mis:=0;for _,k:=range bl.Keys{if fmt.Sprint(aa[k])!=fmt.Sprint(bb[k]){mis++}};z+=bl.Weight*float64(mis)/float64(len(bl.Keys))};return z}
func recs(p map[string]any)[]map[string]any{a:=p["records"].([]any);r:=make([]map[string]any,len(a));for i,z:=range a{r[i]=z.(map[string]any)};sort.Slice(r,func(i,j int)bool{return sm(r[i],"record_id")<sm(r[j],"record_id")});return r}
func farthest(xs []map[string]any,r float64)[]int{ps:=[]int{0};in:=map[int]bool{0:true};for{bi:=-1;bd:=-1.0;for i:=range xs{if in[i]{continue};nd:=math.Inf(1);for _,p:=range ps{d:=dist(desc(xs[i]),desc(xs[p]));if d<nd{nd=d}};if bi<0||nd>bd+eps||(math.Abs(nd-bd)<=eps&&sm(xs[i],"record_id")<sm(xs[bi],"record_id")){bi=i;bd=nd}};if bi<0||bd<=r+eps{break};ps=append(ps,bi);in[bi]=true};sort.Slice(ps,func(i,j int)bool{return sm(xs[ps[i]],"record_id")<sm(xs[ps[j]],"record_id")});return ps}
func nearest(xs []map[string]any,i int,ps []int)(int,float64){bp:=ps[0];bd:=dist(desc(xs[i]),desc(xs[bp]));for _,p:=range ps[1:]{d:=dist(desc(xs[i]),desc(xs[p]));if d<bd-eps||(math.Abs(d-bd)<=eps&&sm(xs[p],"record_id")<sm(xs[bp],"record_id")){bp=p;bd=d}};return bp,bd}
func main(){if len(os.Args)!=4{panic("usage: p8-prototype-verify profiles.json rust-index.json receipt.json")};p:=read(os.Args[1]);idx:=read(os.Args[2]);if fmt.Sprint(p["target_fields_consulted"])!="false"{panic("target firewall")};xs:=recs(p);rv,ok:=idx["selected_radius"].(float64);if !ok{out:=map[string]any{"schema":"c3x-p8-go-prototype-parity-v1","scientific_stage":"C3X 0.7.0-G9.5-P8","pass":true,"selected":false,"records_checked":len(xs)};b,_:=json.MarshalIndent(out,"","  ");os.WriteFile(os.Args[3],append(b,'\n'),0644);fmt.Println("P8_GO_PROTO_PARITY_PASS no-index",len(xs));return}
 ps:=farthest(xs,rv);want:=map[string]map[string]any{};for _,z:=range idx["assignments"].([]any){m:=z.(map[string]any);want[sm(m,"record_id")]=m}
 rustP:=idx["prototypes"].([]any);if len(ps)!=len(rustP){panic("prototype count mismatch")}
 for i,pidx:=range ps{rid:=sm(xs[pidx],"record_id");if sm(rustP[i].(map[string]any),"medoid_record_id")!=rid{panic("prototype identity mismatch")}}
 for i:=range xs{pidx,d:=nearest(xs,i,ps);rid:=sm(xs[i],"record_id");w:=want[rid];pid:="P8P:"+sm(xs[pidx],"record_id");if sm(w,"prototype_id")!=pid{panic("assignment mismatch "+rid)};wd:=w["distance"].(float64);if math.Abs(wd-d)>1e-10{panic("distance mismatch "+rid)}}
 out:=map[string]any{"schema":"c3x-p8-go-prototype-parity-v1","scientific_stage":"C3X 0.7.0-G9.5-P8","pass":true,"selected":true,"records_checked":len(xs),"prototypes_checked":len(ps),"radius":rv};b,_:=json.MarshalIndent(out,"","  ");os.WriteFile(os.Args[3],append(b,'\n'),0644);fmt.Println("P8_GO_PROTO_PARITY_PASS",len(xs),len(ps),rv)}
