use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{env,fs,path::Path};

#[derive(Debug,Deserialize)]
struct Spec{
 schema:String, scientific_stage:String, title:String,
 parent_authority:Value, fresh_worlds:FreshWorlds, axes:Axes,
 state_correspondence:StateCorrespondence,
 descriptor_authority:Value, product_space:Value,
 prediction_authority:Value, literature_constraints:Vec<Value>,
 prospective_claims:Vec<Value>, claim_ceiling:Vec<String>
}
#[derive(Debug,Deserialize)]
struct FreshWorlds{
 lane:String,generation_index_offset:u64,families:Vec<String>,
 worlds_per_family:usize,worlds_per_side_per_family:usize,
 engine_outcomes_consulted:bool
}
#[derive(Debug,Deserialize,Serialize)]
struct Axes{
 architecture:Vec<String>,budget_nodes:Vec<u64>,anchor_budget_nodes:u64,
 state_levels:Vec<usize>,interventions:Vec<String>,squares:Vec<String>,
 response_fingerprint:Vec<String>
}
#[derive(Debug,Deserialize,Serialize)]
struct StateCorrespondence{
 family:String,fit_data:String,capacity:String,anchor_budget_nodes:u64,
 objective:String,composition:String,selection_after_alignment:String,
 support_gate:String
}
#[derive(Debug,Serialize)]
struct Row{
 ordinal:usize,phase:String,family:Option<String>,budget:Option<u64>,authority:String
}
fn canonical(v:&Value)->Value{
 match v{
  Value::Object(m)=>{
   let mut ks:Vec<_>=m.keys().cloned().collect();ks.sort();
   let mut o=serde_json::Map::new();
   for k in ks{o.insert(k.clone(),canonical(&m[&k]));}
   Value::Object(o)
  },
  Value::Array(a)=>Value::Array(a.iter().map(canonical).collect()),
  _=>v.clone()
 }
}
fn sha(v:&Value)->String{
 let b=serde_json::to_vec(&canonical(v)).unwrap();
 let mut h=Sha256::new();h.update(b);format!("{:x}",h.finalize())
}
fn validate(s:&Spec){
 assert_eq!(s.schema,"c3x-lawgen-spec-v2");
 assert_eq!(s.scientific_stage,"C3X 0.7.0-G9.4-P26");
 assert!(!s.fresh_worlds.engine_outcomes_consulted);
 assert_eq!(s.fresh_worlds.families.len(),8);
 assert_eq!(s.fresh_worlds.worlds_per_family,48);
 assert_eq!(s.fresh_worlds.worlds_per_side_per_family*2,s.fresh_worlds.worlds_per_family);
 assert!(s.fresh_worlds.generation_index_offset>620000);
 assert_eq!(s.axes.architecture,vec!["stockfish_19","berserk","ethereal"]);
 assert_eq!(s.axes.budget_nodes,vec![40000,80000,160000,300000]);
 assert!(s.axes.budget_nodes.contains(&s.axes.anchor_budget_nodes));
 assert_eq!(s.axes.anchor_budget_nodes,s.state_correspondence.anchor_budget_nodes);
 assert_eq!(s.axes.state_levels,vec![2,4,8]);
 assert_eq!(s.axes.interventions,vec!["SHAM","MASK_MAIN","MASK_QSEARCH","MASK_MAIN_QSEARCH","MASK_ALL"]);
 assert_eq!(s.axes.squares,vec!["HEAVY_HEAVY","MINOR_MINOR"]);
 assert_eq!(s.axes.response_fingerprint.len(),3);
 assert_eq!(s.state_correspondence.family,"finite_permutation_to_shared_anchor");
 assert!(s.state_correspondence.fit_data.contains("SHAM"));
 assert!(s.state_correspondence.capacity.contains("permutation"));
}
fn matrix(s:&Spec)->Vec<Row>{
 let mut out=Vec::new();let mut n=0usize;
 let mut push=|phase:&str,f:Option<String>,b:Option<u64>,auth:&str|{
  n+=1;out.push(Row{ordinal:n,phase:phase.into(),family:f,budget:b,authority:auth.into()})
 };
 push("ontology_compile",None,None,"outcome_blind");
 for f in &s.fresh_worlds.families{push("world_compile",Some(f.clone()),None,"outcome_blind");}
 push("world_merge",None,None,"outcome_blind");
 for b in &s.axes.budget_nodes{
  for f in &s.fresh_worlds.families{push("sham_census",Some(f.clone()),Some(*b),"outcome_blind");}
  push("atlas_build",None,Some(*b),"outcome_blind");
 }
 push("state_correspondence_fit",None,None,"outcome_blind");
 push("support_optimized_selection",None,None,"outcome_blind");
 push("precommit_roundtrip",None,None,"outcome_blind");
 for f in &s.fresh_worlds.families{push("product_field_selective",Some(f.clone()),None,"post_precommit");}
 push("product_field_adjudication",None,None,"post_precommit");
 push("independent_semantic_verification",None,None,"post_adjudication");
 out
}
fn main(){
 let a:Vec<String>=env::args().collect();
 if a.len()!=3{eprintln!("usage: c3x-lawgen-v2 <spec.json> <out-dir>");std::process::exit(2);}
 let raw=fs::read_to_string(&a[1]).unwrap();
 let val:Value=serde_json::from_str(&raw).unwrap();
 let s:Spec=serde_json::from_value(val.clone()).unwrap();validate(&s);
 let rows=matrix(&s);let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 let spec_sha=sha(&val);
 let constitution=json!({
  "schema":"c3x-lawgen-constitution-v2",
  "scientific_stage":s.scientific_stage,
  "title":s.title,
  "spec_sha256":spec_sha,
  "parent_authority":s.parent_authority,
  "fresh_worlds":{
   "lane":s.fresh_worlds.lane,
   "generation_index_offset":s.fresh_worlds.generation_index_offset,
   "families":s.fresh_worlds.families,
   "worlds_per_family":s.fresh_worlds.worlds_per_family,
   "outcome_blind":true
  },
  "axes":s.axes,
  "state_correspondence":s.state_correspondence,
  "descriptor_authority":s.descriptor_authority,
  "product_space":s.product_space,
  "prediction_authority":s.prediction_authority,
  "literature_constraints":s.literature_constraints,
  "prospective_claims":s.prospective_claims,
  "claim_ceiling":s.claim_ceiling,
  "execution_matrix_rows":rows.len(),
  "selective_outcomes_consulted":false
 });
 let csha=sha(&constitution);
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":constitution,"constitution_sha256":csha})).unwrap()+"\n").unwrap();
 let mut t="ordinal\tphase\tfamily\tbudget\tauthority\n".to_string();
 for r in &rows{t.push_str(&format!("{}\t{}\t{}\t{}\t{}\n",r.ordinal,r.phase,r.family.as_deref().unwrap_or(""),r.budget.map(|x|x.to_string()).unwrap_or_default(),r.authority));}
 fs::write(out.join("execution-matrix.tsv"),t).unwrap();
 let field=json!({
  "schema":"c3x-product-field-contract-v1",
  "scientific_stage":"C3X 0.7.0-G9.4-P26",
  "constitution_sha256":csha,
  "axes":["architecture","budget","mapped_state","intervention"],
  "state_map_capacity":"finite permutation through 80k anchor",
  "forbidden":["outcome-trained correspondence","post-hoc budget deletion","post-hoc descriptor invention"],
  "removability_tests":{"architecture":"exact fingerprint equality at every budget×state×square","budget":"exact fingerprint equality at every architecture×state×square"}
 });
 fs::write(out.join("product-field-contract.json"),serde_json::to_string_pretty(&field).unwrap()+"\n").unwrap();
 let lattice=json!({
  "schema":"c3x-lawgen-claim-lattice-v2",
  "scientific_stage":"C3X 0.7.0-G9.4-P26",
  "constitution_sha256":csha,
  "nodes":[
   {"id":"W","requires":[],"meaning":"fresh exact-world constitution"},
   {"id":"A","requires":["W"],"meaning":"multi-budget SHAM atlas family"},
   {"id":"S","requires":["A"],"meaning":"low-capacity cross-budget state correspondence"},
   {"id":"P","requires":["S"],"meaning":"sealed product-space intervention field"},
   {"id":"R_A","requires":["P"],"meaning":"architecture-index removability test"},
   {"id":"R_B","requires":["P"],"meaning":"budget-index removability test"},
   {"id":"D","requires":[],"meaning":"descriptor intervention feasibility audit"}
  ],
  "non_implications":[
   "state correspondence does not imply causal-law transport",
   "architecture index necessity does not imply engine-name fundamentality",
   "budget index necessity does not imply time-control transport",
   "descriptor feasibility does not imply descriptor effect identification"
  ]
 });
 fs::write(out.join("claim-lattice.json"),serde_json::to_string_pretty(&lattice).unwrap()+"\n").unwrap();
 println!("P26_LAWGEN_V2_PASS spec={} constitution={} rows={}",spec_sha,csha,rows.len());
}
