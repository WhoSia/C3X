use clap::{Parser,Subcommand};
use serde_json::{json,Map,Value};
use std::{cmp::Ordering,collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P6";

#[derive(Parser)]
#[command(name="c3x-repr-p6",about="Bounded relational/interactions representation learner for C3X P6")]
struct Cli{#[command(subcommand)]cmd:Cmd}

#[derive(Subcommand)]
enum Cmd{
 Learn{#[arg(long)] input:PathBuf,#[arg(long)] grammar:PathBuf,#[arg(long)] out:PathBuf},
 QueryShortlist{#[arg(long)] shortlist:PathBuf,#[arg(long)] profiles:PathBuf,#[arg(long)] out:PathBuf},
 QueryField{#[arg(long)] field:PathBuf,#[arg(long)] profiles:PathBuf,#[arg(long)] out:PathBuf},
}

fn load(p:&PathBuf)->Value{serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()}
fn save(p:&PathBuf,v:&Value){if let Some(x)=p.parent(){fs::create_dir_all(x).unwrap();}fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn sval<'a>(v:&'a Value,k:&str)->&'a str{v[k].as_str().unwrap_or("")}

fn ref_value(r:&Value,rf:&str)->String{
 if let Some(k)=rf.strip_prefix("C."){return r["context"][k].as_str().expect("missing context ref").to_string();}
 if let Some(k)=rf.strip_prefix("R."){return r["relations"][k].as_str().expect("missing relation ref").to_string();}
 panic!("bad field ref {rf}")
}

fn term_value(r:&Value,t:&Value)->String{
 match sval(t,"type"){
  "CONTEXT_ATOM"=>r["context"][sval(t,"field")].as_str().expect("missing context atom").to_string(),
  "RELATIONAL_ATOM"=>r["relations"][sval(t,"field")].as_str().expect("missing relational atom").to_string(),
  "INTERACTION"=>format!("{}&{}",ref_value(r,sval(t,"left")),ref_value(r,sval(t,"right"))),
  x=>panic!("bad term type {x}")
 }
}

fn key(r:&Value,terms:&[Value])->String{
 let mut p=vec![sval(r,"fiber_id").to_string()];
 for t in terms{p.push(format!("{}={}",sval(t,"id"),term_value(r,t)));}
 p.join("||")
}

fn combos(n:usize,k:usize,start:usize,cur:&mut Vec<usize>,out:&mut Vec<Vec<usize>>){
 if cur.len()==k{out.push(cur.clone());return}
 for i in start..n{cur.push(i);combos(n,k,i+1,cur,out);cur.pop();}
}

fn metrics(rows:&[Value],terms:&[Value])->Value{
 let mut g:BTreeMap<String,Vec<&Value>>=BTreeMap::new();
 for r in rows{g.entry(key(r,terms)).or_default().push(r);}
 let mut collisions=0usize;let mut xp=0usize;let mut xe=0usize;let mut reused_pos=0usize;let mut reused_pos_cells=0usize;
 for z in g.values(){
  let labs=z.iter().map(|r|r["target"].as_bool().unwrap()).collect::<BTreeSet<_>>();
  let posset=z.iter().map(|r|sval(r,"position_id")).collect::<BTreeSet<_>>();
  let engset=z.iter().map(|r|sval(r,"engine")).collect::<BTreeSet<_>>();
  if labs.len()>1{collisions+=1;}
  if posset.len()>1{xp+=z.len();}
  if engset.len()>1{xe+=z.len();}
  if labs.len()==1 && labs.contains(&true) && (posset.len()>1 || engset.len()>1){
   reused_pos+=z.len();reused_pos_cells+=1;
  }
 }
 let n=rows.len();let d=g.len();
 json!({"records":n,"distinct_cells":d,"target_collisions":collisions,
  "compression":if n==0{0.0}else{1.0-d as f64/n as f64},
  "cross_position_records":xp,"cross_engine_records":xe,
  "reused_positive_records":reused_pos,"reused_positive_cells":reused_pos_cells,
  "positive_records":rows.iter().filter(|r|r["target"].as_bool()==Some(true)).count(),
  "negative_records":rows.iter().filter(|r|r["target"].as_bool()==Some(false)).count()})
}

fn cells(rows:&[Value],terms:&[Value])->Map<String,Value>{
 let mut g:BTreeMap<String,Vec<&Value>>=BTreeMap::new();
 for r in rows{g.entry(key(r,terms)).or_default().push(r);}
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
 assert_eq!(x["schema"],"c3x-field-p6-train-input-v1");assert_eq!(x["scientific_stage"],STAGE);
 assert_eq!(g["schema"],"c3x-p6-relational-grammar-v1");assert_eq!(g["scientific_stage"],STAGE);
 assert_eq!(g["forbid_engine_identity"],true);assert_eq!(g["forbid_architecture_identity"],true);
 let rows=x["records"].as_array().unwrap();
 let pool=g["terms"].as_array().unwrap();
 for r in rows{for t in pool{let _=term_value(r,t);}}
 let maxk=g["max_terms"].as_u64().unwrap() as usize;
 let maxi=g["max_interaction_terms"].as_u64().unwrap() as usize;
 let maxdesc=g["max_description_bits"].as_f64().unwrap();
 let maxshort=g["max_shortlist"].as_u64().unwrap() as usize;
 let cell_cost=g["cell_cost_bits"].as_f64().unwrap();
 let ad=&g["train_admissibility"];
 let mincomp=ad["min_compression"].as_f64().unwrap();
 let minxp=ad["min_cross_position_records"].as_u64().unwrap() as usize;
 let minxe=ad["min_cross_engine_records"].as_u64().unwrap() as usize;
 let minrp=ad["min_reused_positive_records"].as_u64().unwrap() as usize;
 let maxcol=ad["max_target_collisions"].as_u64().unwrap() as usize;
 let mut raw=Vec::<Vec<usize>>::new();
 for k in 1..=maxk{combos(pool.len(),k,0,&mut Vec::new(),&mut raw);}
 let mut searched=0usize;let mut admissible_total=0usize;let mut good=Vec::<Value>::new();
 for idxs in raw{
  let terms:Vec<Value>=idxs.iter().map(|i|pool[*i].clone()).collect();
  let ints=terms.iter().filter(|t|sval(t,"type")=="INTERACTION").count();
  if ints>maxi{continue}
  let desc: f64=terms.iter().map(|t|t["cost_bits"].as_f64().unwrap()).sum();
  if desc>maxdesc+1e-12{continue}
  searched+=1;
  let m=metrics(rows,&terms);let pos=m["positive_records"].as_u64().unwrap();let neg=m["negative_records"].as_u64().unwrap();
  let ok=m["target_collisions"].as_u64().unwrap() as usize<=maxcol &&
   m["compression"].as_f64().unwrap()+1e-12>=mincomp &&
   m["cross_position_records"].as_u64().unwrap() as usize>=minxp &&
   m["cross_engine_records"].as_u64().unwrap() as usize>=minxe &&
   m["reused_positive_records"].as_u64().unwrap() as usize>=minrp && pos>0 && neg>0;
  if !ok{continue}
  admissible_total+=1;
  let mdl=desc+cell_cost*m["distinct_cells"].as_u64().unwrap() as f64;
  let ids:Vec<String>=terms.iter().map(|t|sval(t,"id").to_string()).collect();
  let id=format!("RB[{}]",ids.join("+"));
  good.push(json!({"id":id,"basis_terms":terms,"term_ids":ids,"metrics":m,"description_bits":desc,"mdl_bits":mdl}));
 }
 good.sort_by(|a,b|{
  a["mdl_bits"].as_f64().unwrap().partial_cmp(&b["mdl_bits"].as_f64().unwrap()).unwrap_or(Ordering::Equal)
   .then_with(||a["description_bits"].as_f64().unwrap().partial_cmp(&b["description_bits"].as_f64().unwrap()).unwrap_or(Ordering::Equal))
   .then_with(||a["basis_terms"].as_array().unwrap().len().cmp(&b["basis_terms"].as_array().unwrap().len()))
   .then_with(||b["metrics"]["compression"].as_f64().unwrap().partial_cmp(&a["metrics"]["compression"].as_f64().unwrap()).unwrap_or(Ordering::Equal))
   .then_with(||sval(a,"id").cmp(sval(b,"id")))
 });
 if good.len()>maxshort{good.truncate(maxshort);}
 for z in &mut good{
  let ts=z["basis_terms"].as_array().unwrap().clone();
  z.as_object_mut().unwrap().insert("cells".into(),Value::Object(cells(rows,&ts)));
 }
 let count=good.len();
 save(&out,&json!({"schema":"c3x-p6-train-shortlist-v1","scientific_stage":STAGE,
  "searched_candidates":searched,"admissible_candidates_total_before_truncation":admissible_total,
  "shortlist":good,"shortlist_count":count,"target_fields_consulted":true,
  "p5_selection_labels_consulted":false,"selection_targets_consulted":false,"transport_targets_consulted":false}));
}

fn predict_one(c:&Value,rows:&[Value])->Vec<Value>{
 let terms=c["basis_terms"].as_array().unwrap();
 let cells=c["cells"].as_object().unwrap();
 rows.iter().map(|r|{
  let k=key(r,terms);let cc=cells.get(&k);
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
 save(&out,&json!({"schema":"c3x-p6-shortlist-query-v1","scientific_stage":STAGE,"queries":q,
   "target_fields_consulted":false,"p5_selection_labels_consulted":false}));
}

fn query_field(field:PathBuf,profiles:PathBuf,out:PathBuf){
 let f=load(&field);let p=load(&profiles);let rows=p["records"].as_array().unwrap();
 let c=&f["selected_candidate"];
 let pr=if c.is_null(){Vec::new()}else{predict_one(c,rows)};
 save(&out,&json!({"schema":"c3x-p6-field-query-v1","scientific_stage":STAGE,"predictions":pr,
   "target_fields_consulted":false,"p5_selection_labels_consulted":false}));
}

fn main(){let c=Cli::parse();match c.cmd{
 Cmd::Learn{input,grammar,out}=>learn(input,grammar,out),
 Cmd::QueryShortlist{shortlist,profiles,out}=>query_shortlist(shortlist,profiles,out),
 Cmd::QueryField{field,profiles,out}=>query_field(field,profiles,out),
}}
