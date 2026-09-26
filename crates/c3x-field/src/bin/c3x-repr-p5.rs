use clap::{Parser,Subcommand};
use serde_json::{json,Map,Value};
use std::{cmp::Ordering,collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P5";

#[derive(Parser)]
#[command(name="c3x-repr-p5",about="Exhaustive bounded representation learner/query kernel for C3X P5")]
struct Cli{#[command(subcommand)]cmd:Cmd}
#[derive(Subcommand)]
enum Cmd{
 Learn{#[arg(long)] input:PathBuf,#[arg(long)] grammar:PathBuf,#[arg(long)] out:PathBuf},
 QueryShortlist{#[arg(long)] shortlist:PathBuf,#[arg(long)] profiles:PathBuf,#[arg(long)] out:PathBuf},
 QueryField{#[arg(long)] field:PathBuf,#[arg(long)] profiles:PathBuf,#[arg(long)] out:PathBuf},
 Diagnose{#[arg(long)] predictions:PathBuf,#[arg(long)] targets:PathBuf,#[arg(long)] out:PathBuf},
}
fn load(p:&PathBuf)->Value{serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()}
fn save(p:&PathBuf,v:&Value){if let Some(x)=p.parent(){fs::create_dir_all(x).unwrap();}fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn sval<'a>(v:&'a Value,k:&str)->&'a str{v[k].as_str().unwrap_or("")}
fn key(r:&Value,cs:&[String])->String{
 let mut p=vec![sval(r,"fiber_id").to_string()];
 let ctx=&r["context"];
 for c in cs{p.push(format!("{}={}",c,ctx[c].as_str().expect("context atom must be string")));}
 p.join("||")
}
fn combos(atoms:&[String],k:usize,start:usize,cur:&mut Vec<String>,out:&mut Vec<Vec<String>>){
 if cur.len()==k{out.push(cur.clone());return}
 for i in start..atoms.len(){cur.push(atoms[i].clone());combos(atoms,k,i+1,cur,out);cur.pop();}
}
fn metrics(rows:&[Value],cs:&[String])->Value{
 let mut g:BTreeMap<String,Vec<&Value>>=BTreeMap::new();
 for r in rows{g.entry(key(r,cs)).or_default().push(r);}
 let mut collisions=0usize;let mut xp=0usize;let mut xe=0usize;
 for z in g.values(){
  if z.iter().map(|r|r["target"].as_bool().unwrap()).collect::<BTreeSet<_>>().len()>1{collisions+=1;}
  if z.iter().map(|r|sval(r,"position_id")).collect::<BTreeSet<_>>().len()>1{xp+=z.len();}
  if z.iter().map(|r|sval(r,"engine")).collect::<BTreeSet<_>>().len()>1{xe+=z.len();}
 }
 let n=rows.len();let d=g.len();
 json!({"records":n,"distinct_cells":d,"target_collisions":collisions,
  "compression":if n==0{0.0}else{1.0-d as f64/n as f64},
  "cross_position_records":xp,"cross_engine_records":xe,
  "positive_records":rows.iter().filter(|r|r["target"].as_bool()==Some(true)).count(),
  "negative_records":rows.iter().filter(|r|r["target"].as_bool()==Some(false)).count()})
}
fn cells(rows:&[Value],cs:&[String])->Map<String,Value>{
 let mut g:BTreeMap<String,Vec<&Value>>=BTreeMap::new();
 for r in rows{g.entry(key(r,cs)).or_default().push(r);}
 let mut out=Map::new();
 for (k,z) in g{
  let labs=z.iter().map(|r|r["target"].as_bool().unwrap()).collect::<BTreeSet<_>>();
  if labs.len()!=1{continue}
  let y=*labs.iter().next().unwrap();
  out.insert(k,json!({"label":if y{"ROOT_CHANGE"}else{"NO_ROOT_CHANGE"},"support":z.len(),
   "engines":z.iter().map(|r|sval(r,"engine")).collect::<BTreeSet<_>>(),
   "positions":z.iter().map(|r|sval(r,"position_id")).collect::<BTreeSet<_>>(),
   "source_strata":z.iter().map(|r|sval(r,"source_stratum")).collect::<BTreeSet<_>>() }));
 }
 out
}
fn learn(input:PathBuf,grammar:PathBuf,out:PathBuf){
 let x=load(&input);let g=load(&grammar);
 assert_eq!(x["schema"],"c3x-field-p5-train-input-v1");assert_eq!(x["scientific_stage"],STAGE);
 assert_eq!(g["schema"],"c3x-p5-representation-grammar-v1");assert_eq!(g["scientific_stage"],STAGE);
 assert_eq!(g["forbid_engine_identity"],true);assert_eq!(g["forbid_architecture_identity"],true);
 let rows=x["records"].as_array().unwrap();let atoms:Vec<String>=g["atoms"].as_array().unwrap().iter().map(|v|v.as_str().unwrap().to_string()).collect();
 for r in rows{
  for a in &atoms{assert!(r["context"].get(a).and_then(|v|v.as_str()).is_some(),"missing atom {a}");}
 }
 let maxk=g["max_coordinates"].as_u64().unwrap() as usize;let maxshort=g["max_shortlist"].as_u64().unwrap() as usize;
 let ad=&g["train_admissibility"];let mincomp=ad["min_compression"].as_f64().unwrap();
 let minxp=ad["min_cross_position_records"].as_u64().unwrap() as usize;let minxe=ad["min_cross_engine_records"].as_u64().unwrap() as usize;
 let maxcol=ad["max_target_collisions"].as_u64().unwrap() as usize;
 let coord_cost=g["complexity"]["coordinate_cost_bits"].as_f64().unwrap();let cell_cost=g["complexity"]["cell_cost_bits"].as_f64().unwrap();
 let mut all=Vec::<Vec<String>>::new();
 for k in 1..=maxk{combos(&atoms,k,0,&mut Vec::new(),&mut all);}
 let searched=all.len();let mut good=Vec::<Value>::new();
 for cs in all{
  let m=metrics(rows,&cs);let pos=m["positive_records"].as_u64().unwrap();let neg=m["negative_records"].as_u64().unwrap();
  let ok=m["target_collisions"].as_u64().unwrap() as usize<=maxcol &&
    m["compression"].as_f64().unwrap()+1e-12>=mincomp &&
    m["cross_position_records"].as_u64().unwrap() as usize>=minxp &&
    m["cross_engine_records"].as_u64().unwrap() as usize>=minxe && pos>0 && neg>0;
  if !ok{continue}
  let mdl=coord_cost*cs.len() as f64+cell_cost*m["distinct_cells"].as_u64().unwrap() as f64;
  let id=format!("R[{}]",cs.join("+"));
  good.push(json!({"id":id,"coordinates":cs,"metrics":m,"mdl_bits":mdl}));
 }
 good.sort_by(|a,b|{
  a["mdl_bits"].as_f64().unwrap().partial_cmp(&b["mdl_bits"].as_f64().unwrap()).unwrap_or(Ordering::Equal)
   .then_with(||a["coordinates"].as_array().unwrap().len().cmp(&b["coordinates"].as_array().unwrap().len()))
   .then_with(||b["metrics"]["compression"].as_f64().unwrap().partial_cmp(&a["metrics"]["compression"].as_f64().unwrap()).unwrap_or(Ordering::Equal))
   .then_with(||sval(a,"id").cmp(sval(b,"id")))
 });
 if good.len()>maxshort{good.truncate(maxshort);}
 for z in &mut good{
  let cs:Vec<String>=z["coordinates"].as_array().unwrap().iter().map(|v|v.as_str().unwrap().to_string()).collect();
  z.as_object_mut().unwrap().insert("cells".into(),Value::Object(cells(rows,&cs)));
 }
 save(&out,&json!({"schema":"c3x-p5-train-shortlist-v1","scientific_stage":STAGE,
  "searched_candidates":searched,"admissible_candidates_total_before_truncation":null,
  "shortlist":good,"shortlist_count":good.len(),"target_fields_consulted":true,
  "selection_targets_consulted":false,"transport_targets_consulted":false}));
}
fn predict_one(c:&Value,rows:&[Value])->Vec<Value>{
 let cs:Vec<String>=c["coordinates"].as_array().unwrap().iter().map(|v|v.as_str().unwrap().to_string()).collect();
 let cells=c["cells"].as_object().unwrap();
 rows.iter().map(|r|{
  let k=key(r,&cs);let cc=cells.get(&k);
  if let Some(z)=cc{
   let lab=sval(z,"label");
   json!({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"source_stratum":r["source_stratum"],
    "candidate_id":c["id"],"cell_key":k,"status":if lab=="ROOT_CHANGE"{"CERTIFIED_ROOT_CHANGE"}else{"CERTIFIED_NO_ROOT_CHANGE"},
    "predicted_root_change":lab=="ROOT_CHANGE","discovery_support":z["support"]})
  }else{
   json!({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"source_stratum":r["source_stratum"],
    "candidate_id":c["id"],"cell_key":k,"status":"ABSTAIN_UNSEEN_CONTEXT","predicted_root_change":Value::Null,"discovery_support":0})
  }
 }).collect()
}
fn query_shortlist(shortlist:PathBuf,profiles:PathBuf,out:PathBuf){
 let s=load(&shortlist);let p=load(&profiles);let rows=p["records"].as_array().unwrap();
 let mut q=Vec::new();
 for c in s["shortlist"].as_array().unwrap(){q.push(json!({"candidate_id":c["id"],"predictions":predict_one(c,rows)}));}
 save(&out,&json!({"schema":"c3x-p5-shortlist-query-v1","scientific_stage":STAGE,"queries":q,"target_fields_consulted":false}));
}
fn query_field(field:PathBuf,profiles:PathBuf,out:PathBuf){
 let f=load(&field);let p=load(&profiles);let rows=p["records"].as_array().unwrap();
 let c=&f["selected_candidate"];
 let pr=if c.is_null(){Vec::new()}else{predict_one(c,rows)};
 save(&out,&json!({"schema":"c3x-p5-field-query-v1","scientific_stage":STAGE,"predictions":pr,"target_fields_consulted":false}));
}
fn diagnose(predictions:PathBuf,targets:PathBuf,out:PathBuf){
 let p=load(&predictions);let t=load(&targets);
 let tm:BTreeMap<_,_>=t["records"].as_array().unwrap().iter().map(|r|(sval(r,"record_id"),r)).collect();
 let mut bad=Vec::new();let mut abst=0usize;
 for r in p["predictions"].as_array().unwrap(){
  if r["status"]=="ABSTAIN_UNSEEN_CONTEXT"{abst+=1;continue;}
  let q=r["predicted_root_change"].as_bool().unwrap();let y=tm[sval(r,"record_id")]["root_change"].as_bool().unwrap();
  if q!=y{bad.push(json!({"record_id":r["record_id"],"candidate_id":r["candidate_id"],"cell_key":r["cell_key"],"predicted_root_change":q,"observed_root_change":y}));}
 }
 save(&out,&json!({"schema":"c3x-p5-diagnosis-v1","scientific_stage":STAGE,"authority":"POST_TARGET_DIAGNOSTIC_ONLY","may_modify_field":false,"abstained":abst,"contradictions":bad}));
}
fn main(){let c=Cli::parse();match c.cmd{
 Cmd::Learn{input,grammar,out}=>learn(input,grammar,out),
 Cmd::QueryShortlist{shortlist,profiles,out}=>query_shortlist(shortlist,profiles,out),
 Cmd::QueryField{field,profiles,out}=>query_field(field,profiles,out),
 Cmd::Diagnose{predictions,targets,out}=>diagnose(predictions,targets,out),
}}
