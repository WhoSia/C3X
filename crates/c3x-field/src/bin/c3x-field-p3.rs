use clap::{Parser,Subcommand};
use serde_json::{json,Value};
use std::{collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P3";

#[derive(Parser)]
#[command(name="c3x-field-p3",about="C3X P3 topology-field certificate kernel")]
struct Cli{#[command(subcommand)]cmd:Cmd}
#[derive(Subcommand)]
enum Cmd{
 Assess{#[arg(long)] input:PathBuf,#[arg(long)] schemas:PathBuf,#[arg(long)] out:PathBuf},
 Query{#[arg(long)] field:PathBuf,#[arg(long)] profiles:PathBuf,#[arg(long)] out:PathBuf},
 Diagnose{#[arg(long)] predictions:PathBuf,#[arg(long)] targets:PathBuf,#[arg(long)] out:PathBuf},
}

fn load(p:&PathBuf)->Value{serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()}
fn save(p:&PathBuf,v:&Value){if let Some(x)=p.parent(){fs::create_dir_all(x).unwrap();}fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn key(fiber:&str,ctx:&Value,coords:&[String])->String{
 let mut p=vec![fiber.to_string()];
 for c in coords{p.push(format!("{}={}",c,ctx[c].as_str().unwrap()));}
 p.join("||")
}
fn coords(v:&Value)->Vec<String>{v.as_array().unwrap().iter().map(|x|x.as_str().unwrap().to_string()).collect()}

fn assess(input:PathBuf,schemas:PathBuf,out:PathBuf){
 let x=load(&input);let ss=load(&schemas);
 assert_eq!(x["scientific_stage"],STAGE);
 let rows=x["records"].as_array().unwrap();
 let mut census=Vec::new();
 for s in ss.as_array().unwrap(){
  let cs=coords(&s["coordinates"]);let mut g:BTreeMap<String,Vec<&Value>>=BTreeMap::new();
  for r in rows{g.entry(key(r["fiber_id"].as_str().unwrap(),&r["context"],&cs)).or_default().push(r);}
  let mut col=0;let mut xp=0;let mut xe=0;
  for z in g.values(){
   if z.iter().map(|r|r["target"].as_bool().unwrap()).collect::<BTreeSet<_>>().len()>1{col+=1;}
   if z.iter().map(|r|r["position_id"].as_str().unwrap()).collect::<BTreeSet<_>>().len()>1{xp+=z.len();}
   if z.iter().map(|r|r["engine"].as_str().unwrap()).collect::<BTreeSet<_>>().len()>1{xe+=z.len();}
  }
  let n=rows.len();let d=g.len();let comp=if n==0{0.0}else{1.0-d as f64/n as f64};
  census.push(json!({"schema_id":s["id"],"rank":s["rank"],"added_coordinates":s["added_coordinates"],"coordinates":s["coordinates"],
    "records":n,"distinct_cells":d,"target_collisions":col,"compression":comp,"cross_position_records":xp,"cross_engine_records":xe}));
 }
 save(&out,&json!({"schema":"c3x-field-p3-assessment-v1","scientific_stage":STAGE,"census":census}));
}
fn query(field:PathBuf,profiles:PathBuf,out:PathBuf){
 let f=load(&field);let p=load(&profiles);let cs=coords(&f["coordinates"]);let cells=f["cells"].as_object().unwrap();let mut z=Vec::new();
 for r in p["records"].as_array().unwrap(){
  let k=key(r["fiber_id"].as_str().unwrap(),&r["context"],&cs);
  if let Some(c)=cells.get(&k){let lab=c["label"].as_str().unwrap();z.push(json!({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"cell_key":k,"status":if lab=="ROOT_CHANGE"{"CERTIFIED_ROOT_CHANGE"}else{"CERTIFIED_NO_ROOT_CHANGE"},"predicted_root_change":lab=="ROOT_CHANGE","support":c["support"]}));}
  else{z.push(json!({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"cell_key":k,"status":"ABSTAIN_UNSEEN_CONTEXT","predicted_root_change":Value::Null,"support":0}));}
 }
 save(&out,&json!({"schema":"c3x-field-p3-query-v1","scientific_stage":STAGE,"predictions":z,"target_fields_consulted":false}));
}
fn diagnose(predictions:PathBuf,targets:PathBuf,out:PathBuf){
 let p=load(&predictions);let t=load(&targets);let tm:BTreeMap<_,_>=t["records"].as_array().unwrap().iter().map(|r|(r["record_id"].as_str().unwrap(),r)).collect();
 let mut bad=Vec::new();let mut abst=0;
 for r in p["predictions"].as_array().unwrap(){
  if r["status"]=="ABSTAIN_UNSEEN_CONTEXT"{abst+=1;continue;}
  let q=r["predicted_root_change"].as_bool().unwrap();let y=tm[r["record_id"].as_str().unwrap()]["root_change"].as_bool().unwrap();
  if q!=y{bad.push(json!({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"cell_key":r["cell_key"],"predicted_root_change":q,"observed_root_change":y}));}
 }
 save(&out,&json!({"schema":"c3x-field-p3-diagnosis-v1","scientific_stage":STAGE,"authority":"POST_VERIFICATION_DIAGNOSTIC_ONLY","may_modify_field":false,"abstained":abst,"contradictions":bad}));
}
fn main(){let c=Cli::parse();match c.cmd{Cmd::Assess{input,schemas,out}=>assess(input,schemas,out),Cmd::Query{field,profiles,out}=>query(field,profiles,out),Cmd::Diagnose{predictions,targets,out}=>diagnose(predictions,targets,out)}}
