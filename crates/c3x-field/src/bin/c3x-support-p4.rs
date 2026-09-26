use clap::{Parser,Subcommand};
use serde_json::{json,Value};
use std::{collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P4";

#[derive(Parser)]
#[command(name="c3x-support-p4",about="Outcome-blind mechanism-stratified exact-event sampler for C3X P4")]
struct Cli{#[command(subcommand)]cmd:Cmd}
#[derive(Subcommand)]
enum Cmd{
 Sample{#[arg(long)] trace:PathBuf,#[arg(long)] plan:PathBuf,#[arg(long,default_value_t=16)] max_events:usize,#[arg(long)] out:PathBuf},
}
fn load(p:&PathBuf)->Value{serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()}
fn save(p:&PathBuf,v:&Value){if let Some(x)=p.parent(){fs::create_dir_all(x).unwrap();}fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn i64v(v:&Value,k:&str)->i64{v[k].as_i64().unwrap_or(0)}
fn s<'a>(v:&'a Value,k:&str)->&'a str{v[k].as_str().unwrap_or("")}
fn qualifies(kind:&str,e:&Value,reused:bool)->bool{
 if i64v(e,"ply")>1{return false}
 match kind{
  "CUTOFF_NEAR_ROOT"=>s(e,"class")=="CUTOFF",
  "MOVE_ORDER_NEAR_ROOT"=>s(e,"class")=="MOVE_ORDER_SEED" && i64v(e,"tt_move")!=0,
  "EVAL_NEAR_ROOT"=>matches!(s(e,"class"),"EVAL_REUSE"|"TT_VALUE_AS_EVAL"),
  "PREFIX_KEY_REUSE"=>reused,
  "ANY_PREFIX"=>true,
  _=>panic!("unknown P4 stratum kind {kind}")
 }
}
fn sample(trace:PathBuf,plan:PathBuf,max_events:usize,out:PathBuf){
 let t=load(&trace);let p=load(&plan);
 assert_eq!(p["schema"],"c3x-p4-sampling-plan-v1");assert_eq!(p["scientific_stage"],STAGE);
 assert_eq!(p["target_fields_consulted"],false);
 let es=t["events"].as_array().expect("events");
 let mut previous:BTreeMap<String,usize>=BTreeMap::new();
 let mut reused=vec![false;es.len()];
 for (i,e) in es.iter().enumerate(){
  let k=s(e,"key").to_string();reused[i]=previous.get(&k).copied().unwrap_or(0)>0;
  *previous.entry(k).or_default()+=1;
 }
 let mut selected:Vec<Value>=Vec::new();let mut used:BTreeSet<String>=BTreeSet::new();
 let mut census=Vec::new();
 for st in p["strata"].as_array().unwrap(){
  let id=st["id"].as_str().unwrap();let kind=st["kind"].as_str().unwrap();let quota=st["quota"].as_u64().unwrap() as usize;
  let mut cand:Vec<(String,usize)>=es.iter().enumerate().filter_map(|(i,e)|{
   if !qualifies(kind,e,reused[i]){return None}
   let aid=s(e,"address_id");if aid.is_empty(){return None}
   Some((aid.to_string(),i))
  }).collect();
  cand.sort_by(|a,b|a.0.cmp(&b.0));cand.dedup_by(|a,b|a.0==b.0);
  let mut taken=0;
  for (aid,i) in &cand{
   if selected.len()>=max_events||taken>=quota{break}
   if used.insert(aid.clone()){
    selected.push(json!({"event_id":aid,"ordinal":i,"sampling_stratum":id}));
    taken+=1;
   }
  }
  census.push(json!({"id":id,"kind":kind,"quota":quota,"eligible":cand.len(),"selected":taken}));
 }
 if selected.len()<max_events{
  let mut all:Vec<(String,usize)>=es.iter().enumerate().filter_map(|(i,e)|{
   if i64v(e,"ply")>1{return None} let aid=s(e,"address_id");if aid.is_empty(){return None} Some((aid.to_string(),i))
  }).collect();
  all.sort_by(|a,b|a.0.cmp(&b.0));all.dedup_by(|a,b|a.0==b.0);
  for (aid,i) in all{
   if selected.len()>=max_events{break}
   if used.insert(aid.clone()){selected.push(json!({"event_id":aid,"ordinal":i,"sampling_stratum":"QUOTA_FILL"}));}
  }
 }
 save(&out,&json!({
  "schema":"c3x-p4-sampling-selection-v1","scientific_stage":STAGE,
  "selected":selected,"selected_count":selected.len(),"max_events":max_events,
  "stratum_census":census,"target_fields_consulted":false,"raw_full_key_emitted":false,
  "selection_semantics":"parent-trace only; ply<=1; frozen stratum quotas; lexicographic exact-address tie break"
 }));
}
fn main(){let c=Cli::parse();match c.cmd{Cmd::Sample{trace,plan,max_events,out}=>sample(trace,plan,max_events,out)}}
