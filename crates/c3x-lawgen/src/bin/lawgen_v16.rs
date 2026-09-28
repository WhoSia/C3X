use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

const STAGE:&str="C3X 0.7.0-G9.5-P6";

fn canonical(v:&Value)->Vec<u8>{serde_json::to_vec(v).unwrap()}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canonical(v));format!("{:x}",h.finalize())}
fn write(path:&Path,v:&Value){fs::write(path,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}

fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3,"usage: lawgen_v16 spec.json outdir");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-g95-p6-constitution-v1");
 assert_eq!(s["scientific_stage"],STAGE);
 assert_eq!(s["counterexample_sequestration"]["p5_selection_labels_confirmatory_vote"],false);
 assert_eq!(s["counterexample_sequestration"]["p5_selection_target_artifacts_may_be_downloaded"],false);
 assert_eq!(s["temporal_firewall"]["causal_availability"],"STRICT_EVENT_PREFIX_ONLY");
 assert_eq!(s["temporal_firewall"]["future_parent_trace_allowed"],false);
 assert_eq!(s["representation_grammar"]["max_interaction_terms"],1);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 let constitution=json!({"schema":"c3x-lawgen-constitution-v16","scientific_stage":STAGE,"spec_sha256":sha(&s),"constitution":s});
 let c=&constitution["constitution"];
 write(&out.join("constitution.json"),&constitution);
 let mut terms=Vec::<Value>::new();
 for x in c["representation_grammar"]["ordinary_context_atoms"].as_array().unwrap(){
  terms.push(json!({"id":format!("C.{}",x.as_str().unwrap()),"type":"CONTEXT_ATOM","field":x,"cost_bits":c["representation_grammar"]["atomic_term_cost_bits"]}));
 }
 for x in c["representation_grammar"]["relational_atoms"].as_array().unwrap(){
  terms.push(json!({"id":format!("R.{}",x.as_str().unwrap()),"type":"RELATIONAL_ATOM","field":x,"cost_bits":c["representation_grammar"]["atomic_term_cost_bits"]}));
 }
 for x in c["representation_grammar"]["interaction_templates"].as_array().unwrap(){
  terms.push(json!({"id":x["id"],"type":"INTERACTION","left":x["left"],"right":x["right"],"cost_bits":c["representation_grammar"]["interaction_term_cost_bits"]}));
 }
 write(&out.join("representation-grammar.json"),&json!({
   "schema":"c3x-p6-relational-grammar-v1","scientific_stage":STAGE,
   "mandatory_anchor":c["representation_grammar"]["mandatory_anchor"],
   "max_terms":c["representation_grammar"]["max_terms"],
   "max_interaction_terms":c["representation_grammar"]["max_interaction_terms"],
   "max_description_bits":c["representation_grammar"]["max_description_bits"],
   "max_shortlist":c["representation_grammar"]["max_shortlist"],
   "cell_cost_bits":c["representation_grammar"]["cell_cost_bits"],
   "terms":terms,
   "train_admissibility":c["representation_grammar"]["train_admissibility"],
   "ranking":c["representation_grammar"]["ranking"],
   "forbid_engine_identity":true,"forbid_architecture_identity":true,"forbid_sampling_stratum":true
 }));
 write(&out.join("split-gates.json"),&json!({
   "schema":"c3x-p6-split-gates-v1","scientific_stage":STAGE,
   "train_support_gate":c["train_support_gate"],"selection_support_gate":c["selection_support_gate"],
   "selection_gate":c["selection_gate"],"transport_gate":c["transport_gate"]
 }));
 write(&out.join("counterexample-firewall.json"),&json!({
   "schema":"c3x-p6-counterexample-firewall-v1","scientific_stage":STAGE,
   "firewall":c["counterexample_sequestration"]
 }));
 println!("G95_P6_LAWGEN_V16 {}",constitution["spec_sha256"]);
}
