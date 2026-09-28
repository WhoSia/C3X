package main

import(
 "crypto/sha256"
 "encoding/hex"
 "encoding/json"
 "fmt"
 "os"
 "sort"
 "strconv"
)

type Edge struct{Src,Dst int; T string}
func h(s string)string{z:=sha256.Sum256([]byte(s));return hex.EncodeToString(z[:])}
func sm(m map[string]any,k string)string{if v,ok:=m[k].(string);ok{return v};return ""}
func num(m map[string]any,k string)int{switch v:=m[k].(type){case float64:return int(v);case int:return v};return 0}
func pb(v int)string{if v<=0{return"0"};if v==1{return"1"};if v==2{return"2"};if v<=4{return"3_4"};if v<=8{return"5_8"};return"9_PLUS"}
func db(v int)string{if v<=0{return"LE0"};if v<=4{return"1_4"};if v<=8{return"5_8"};if v<=12{return"9_12"};if v<=16{return"13_16"};if v<=24{return"17_24"};return"25_PLUS"}
func pay(v int)string{if v==0{return"ZERO"};if v==1{return"ONE"};if v==-1{return"NEG_ONE"};if v>0{return"POS_OTHER"};return"NEG_OTHER"}
func win(e map[string]any)string{v,a,b:=num(e,"tt_value"),num(e,"alpha"),num(e,"beta");if v<=a{return"LE_ALPHA"};if v>=b{return"GE_BETA"};return"MID"}
func rootLabel(b map[string]any)string{
 return fmt.Sprintf("ROOT|stm=%s|check=%v|phase=%s|legal=%s|mat=%s|castle=%s|hm=%s",
  sm(b,"side_to_move"),b["in_check"],sm(b,"phase"),sm(b,"legal_moves_bucket"),sm(b,"material_balance_bucket"),sm(b,"castling_bucket"),sm(b,"halfmove_bucket"))
}
func eventLabel(e map[string]any,current bool)string{
 c:=0;if current{c=1};mv:="NONE";if num(e,"tt_move")!=0{mv="PRESENT"}
 return fmt.Sprintf("EVENT|scope=%s|class=%s|ply=%s|depth=%s|bound=%d|win=%s|move=%s|payload=%s|current=%d",
  sm(e,"scope"),sm(e,"class"),pb(num(e,"ply")),db(num(e,"depth")),num(e,"bound"),win(e),mv,pay(num(e,"payload")),c)
}
func graph(x map[string]any,ord int)([]string,[]Edge,int){
 ba:=x["board_atoms"].(map[string]any);evs:=x["events"].([]any)
 labels:=[]string{rootLabel(ba)}
 for i:=0;i<=ord;i++{labels=append(labels,eventLabel(evs[i].(map[string]any),i==ord))}
 edges:=[]Edge{};lastKey:=map[string]int{};lastClass:=map[string]int{};lastScope:=map[string]int{};lastPly:=map[int]int{}
 for i:=0;i<=ord;i++{
  n:=i+1;e:=evs[i].(map[string]any);edges=append(edges,Edge{0,n,"ROOT_EVENT"});if i>0{edges=append(edges,Edge{n-1,n,"NEXT"})}
  p:=num(e,"ply");if p>0{if q,ok:=lastPly[p-1];ok{edges=append(edges,Edge{q,n,"STACK_PARENT"})}}
  k:=sm(e,"key");if q,ok:=lastKey[k];ok{edges=append(edges,Edge{q,n,"SAME_KEY_PREV"})};lastKey[k]=n
  c:=sm(e,"class");if q,ok:=lastClass[c];ok{edges=append(edges,Edge{q,n,"SAME_CLASS_PREV"})};lastClass[c]=n
  s:=sm(e,"scope");if q,ok:=lastScope[s];ok{edges=append(edges,Edge{q,n,"SAME_SCOPE_PREV"})};lastScope[s]=n
  lastPly[p]=n;for z:=range lastPly{if z>p{delete(lastPly,z)}}
 }
 edges=append(edges,Edge{0,ord+1,"ROOT_CURRENT"});return labels,edges,ord+1
}
func refine(labels []string,edges []Edge,rounds int)[]string{
 c:=make([]string,len(labels));for i,z:=range labels{c[i]=h(z)}
 for r:=0;r<rounds;r++{
  in:=make([][]string,len(c));out:=make([][]string,len(c))
  for _,e:=range edges{out[e.Src]=append(out[e.Src],e.T+">"+c[e.Dst]);in[e.Dst]=append(in[e.Dst],e.T+"<"+c[e.Src])}
  n:=make([]string,len(c));for i:=range c{sort.Strings(in[i]);sort.Strings(out[i]);n[i]=h(c[i]+"|IN:"+join(in[i])+"|OUT:"+join(out[i]))};c=n
 };return c
}
func join(x []string)string{r:="";for i,z:=range x{if i>0{r+=","};r+=z};return r}
func stateID(labels []string,edges []Edge,current,rounds int)string{
 c:=refine(labels,edges,rounds);nh:=map[string]int{};eh:=map[string]int{}
 for _,z:=range c{nh[z]++};for _,e:=range edges{eh[e.T+"|"+c[e.Src]+"|"+c[e.Dst]]++}
 ks:=make([]string,0,len(nh));for k:=range nh{ks=append(ks,k)};sort.Strings(ks);ns:="";for i,k:=range ks{if i>0{ns+=","};ns+=k+":"+strconv.Itoa(nh[k])}
 ke:=make([]string,0,len(eh));for k:=range eh{ke=append(ke,k)};sort.Strings(ke);es:="";for i,k:=range ke{if i>0{es+=","};es+=k+":"+strconv.Itoa(eh[k])}
 return h(fmt.Sprintf("P7Q%d|ROOT=%s|CURRENT=%s|N=%s|E=%s",rounds,c[0],c[current],ns,es))
}
func main(){
 if len(os.Args)!=4{panic("usage: p7-cseg-verify input.json rust-output.json receipt.json")}
 ib,_:=os.ReadFile(os.Args[1]);rb,_:=os.ReadFile(os.Args[2]);var x map[string]any;var y map[string]any
 json.Unmarshal(ib,&x);json.Unmarshal(rb,&y)
 rows:=map[string]map[string]any{};for _,z:=range y["records"].([]any){m:=z.(map[string]any);rows[sm(m,"event_id")]=m}
 checked:=0
 for _,s0:=range x["selected"].([]any){
  s:=s0.(map[string]any);id:=sm(s,"event_id");ord:=num(s,"ordinal");labels,edges,current:=graph(x,ord);r:=rows[id];st:=r["state_ids"].(map[string]any)
  for q:=0;q<=3;q++{k:="Q"+strconv.Itoa(q);if st[k].(string)!=stateID(labels,edges,current,q){panic("P7_CSEG_DIGEST_MISMATCH "+id+" "+k)}}
  checked++
 }
 if containsKey(y,"key"){panic("P7_RAW_KEY_EMISSION")}
 out:=map[string]any{"schema":"c3x-p7-go-cseg-parity-v1","scientific_stage":"C3X 0.7.0-G9.5-P7","records_checked":checked,"q_levels_checked":4,"pass":true}
 b,_:=json.MarshalIndent(out,"","  ");os.WriteFile(os.Args[3],append(b,'\n'),0644);fmt.Println("P7_GO_CSEG_PARITY_PASS",checked)
}
func containsKey(v any,key string)bool{
 switch x:=v.(type){case map[string]any:for k,z:=range x{if k==key{return true};if containsKey(z,key){return true}};case []any:for _,z:=range x{if containsKey(z,key){return true}}};return false
}
