use clap::{Parser,Subcommand};
use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{collections::BTreeMap,fs,path::PathBuf};

#[derive(Parser)]
#[command(name="c3x-cseg-p7")]
struct Cli{#[command(subcommand)]cmd:Cmd}
#[derive(Subcommand)]
enum Cmd{Materialize{#[arg(long)]input:PathBuf,#[arg(long)]out:PathBuf}}

fn h(s:&str)->String{let mut x=Sha256::new();x.update(s.as_bytes());format!("{:x}",x.finalize())}
fn sval<'a>(v:&'a Value,k:&str)->&'a str{v[k].as_str().unwrap_or("")}
fn ibucket(v:i64)->&'static str{if v<=0{"LE0"}else if v<=4{"1_4"}else if v<=8{"5_8"}else if v<=12{"9_12"}else if v<=16{"13_16"}else if v<=24{"17_24"}else{"25_PLUS"}}
fn pbucket(v:i64)->&'static str{if v<=0{"0"}else if v==1{"1"}else if v==2{"2"}else if v<=4{"3_4"}else if v<=8{"5_8"}else{"9_PLUS"}}
fn payload(v:i64)->&'static str{if v==0{"ZERO"}else if v==1{"ONE"}else if v==-1{"NEG_ONE"}else if v>0{"POS_OTHER"}else{"NEG_OTHER"}}
fn win(e:&Value)->&'static str{
 let v=e["tt_value"].as_i64().unwrap();let a=e["alpha"].as_i64().unwrap();let b=e["beta"].as_i64().unwrap();
 if v<=a{"LE_ALPHA"}else if v>=b{"GE_BETA"}else{"MID"}
}
fn root_label(b:&Value)->String{
 format!("ROOT|stm={}|check={}|phase={}|legal={}|mat={}|castle={}|hm={}",
  sval(b,"side_to_move"),b["in_check"].as_bool().unwrap(),sval(b,"phase"),sval(b,"legal_moves_bucket"),
  sval(b,"material_balance_bucket"),sval(b,"castling_bucket"),sval(b,"halfmove_bucket"))
}
fn event_label(e:&Value,current:bool)->String{
 format!("EVENT|scope={}|class={}|ply={}|depth={}|bound={}|win={}|move={}|payload={}|current={}",
  sval(e,"scope"),sval(e,"class"),pbucket(e["ply"].as_i64().unwrap()),ibucket(e["depth"].as_i64().unwrap()),
  e["bound"].as_i64().unwrap(),win(e),if e["tt_move"].as_i64().unwrap()!=0{"PRESENT"}else{"NONE"},
  payload(e["payload"].as_i64().unwrap()),if current{1}else{0})
}
#[derive(Clone)]
struct Edge{src:usize,dst:usize,t:String}

fn graph(x:&Value,ord:usize)->(Vec<String>,Vec<Edge>,usize){
 let ev=x["events"].as_array().unwrap();let mut labels=vec![root_label(&x["board_atoms"])];
 for (i,e) in ev.iter().take(ord+1).enumerate(){labels.push(event_label(e,i==ord));}
 let mut edges=Vec::new();let mut last_key=BTreeMap::<String,usize>::new();let mut last_class=BTreeMap::<String,usize>::new();
 let mut last_scope=BTreeMap::<String,usize>::new();let mut last_ply=BTreeMap::<i64,usize>::new();
 for i in 0..=ord{
  let n=i+1;let e=&ev[i];edges.push(Edge{src:0,dst:n,t:"ROOT_EVENT".into()});
  if i>0{edges.push(Edge{src:n-1,dst:n,t:"NEXT".into()});}
  let p=e["ply"].as_i64().unwrap();
  if p>0{if let Some(&q)=last_ply.get(&(p-1)){edges.push(Edge{src:q,dst:n,t:"STACK_PARENT".into()});}}
  let k=sval(e,"key").to_string();if let Some(&q)=last_key.get(&k){edges.push(Edge{src:q,dst:n,t:"SAME_KEY_PREV".into()});}last_key.insert(k,n);
  let c=sval(e,"class").to_string();if let Some(&q)=last_class.get(&c){edges.push(Edge{src:q,dst:n,t:"SAME_CLASS_PREV".into()});}last_class.insert(c,n);
  let s=sval(e,"scope").to_string();if let Some(&q)=last_scope.get(&s){edges.push(Edge{src:q,dst:n,t:"SAME_SCOPE_PREV".into()});}last_scope.insert(s,n);
  last_ply.insert(p,n);let kill:Vec<i64>=last_ply.keys().copied().filter(|z|*z>p).collect();for z in kill{last_ply.remove(&z);}
 }
 edges.push(Edge{src:0,dst:ord+1,t:"ROOT_CURRENT".into()});
 (labels,edges,ord+1)
}
fn refine(labels:&[String],edges:&[Edge],rounds:usize)->Vec<String>{
 let mut c:Vec<String>=labels.iter().map(|z|h(z)).collect();
 for _ in 0..rounds{
  let mut inc=vec![Vec::<String>::new();c.len()];let mut out=vec![Vec::<String>::new();c.len()];
  for e in edges{out[e.src].push(format!("{}>{}",e.t,c[e.dst]));inc[e.dst].push(format!("{}<{}",e.t,c[e.src]));}
  let mut n=Vec::new();
  for i in 0..c.len(){inc[i].sort();out[i].sort();n.push(h(&format!("{}|IN:{}|OUT:{}",c[i],inc[i].join(","),out[i].join(","))));}
  c=n;
 }c
}
fn state_id(labels:&[String],edges:&[Edge],current:usize,rounds:usize)->String{
 let c=refine(labels,edges,rounds);let mut nh=BTreeMap::<String,usize>::new();for z in &c{*nh.entry(z.clone()).or_default()+=1;}
 let mut eh=BTreeMap::<String,usize>::new();for e in edges{*eh.entry(format!("{}|{}|{}",e.t,c[e.src],c[e.dst])).or_default()+=1;}
 let ns=nh.iter().map(|(k,v)|format!("{}:{}",k,v)).collect::<Vec<_>>().join(",");
 let es=eh.iter().map(|(k,v)|format!("{}:{}",k,v)).collect::<Vec<_>>().join(",");
 h(&format!("P7Q{}|ROOT={}|CURRENT={}|N={}|E={}",rounds,c[0],c[current],ns,es))
}
fn materialize(input:PathBuf,out:PathBuf){
 let x:Value=serde_json::from_str(&fs::read_to_string(input).unwrap()).unwrap();
 assert_eq!(x["schema"],"c3x-cseg-input-v1");assert_eq!(x["target_fields_consulted"],false);assert_eq!(x["counterfactual_trace_consulted"],false);
 let mut rows=Vec::new();
 for s in x["selected"].as_array().unwrap(){
  let ord=s["ordinal"].as_u64().unwrap() as usize;let (labels,edges,current)=graph(&x,ord);
  let mut states=serde_json::Map::new();for q in 0..=3{states.insert(format!("Q{}",q),Value::String(state_id(&labels,&edges,current,q)));}
  let e=&x["events"][ord];
  rows.push(json!({"event_id":s["event_id"],"sampling_stratum":s["sampling_stratum"],"state_ids":states,
   "graph_census":{"nodes":labels.len(),"edges":edges.len(),"prefix_events":ord+1},
   "current_event":{"scope":e["scope"],"class":e["class"],"ply":e["ply"],"depth":e["depth"],"bound":e["bound"],
      "window_relation":win(e),"move_presence":if e["tt_move"].as_i64().unwrap()!=0{"PRESENT"}else{"NONE"}},
   "board_atoms":x["board_atoms"],"raw_tt_key_emitted":false,"counterfactual_information_consulted":false,"fiber_id_consulted":false}));
 }
 let z=json!({"schema":"c3x-cseg-state-batch-p7-v1","scientific_stage":"C3X 0.7.0-G9.5-P7","records":rows,
   "target_fields_consulted":false,"raw_tt_key_emitted":false,"counterfactual_information_consulted":false,"fiber_id_consulted":false});
 fs::write(out,serde_json::to_string_pretty(&z).unwrap()+"\n").unwrap();
}
fn main(){let c=Cli::parse();match c.cmd{Cmd::Materialize{input,out}=>materialize(input,out)}}
