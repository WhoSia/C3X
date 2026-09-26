use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

const STAGE:&str="C3X 0.7.0-G9.5-P5";

fn canonical(v:&Value)->Vec<u8>{serde_json::to_vec(v).unwrap()}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canonical(v));format!("{:x}",h.finalize())}
fn write(path:&Path,v:&Value){fs::write(path,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}

fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3,"usage: lawgen_v15 spec.json outdir");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-g95-p5-constitution-v1");
 assert_eq!(s["scientific_stage"],STAGE);
 assert_eq!(s["temporal_repair"]["causal_availability"],"STRICT_EVENT_PREFIX_ONLY");
 assert_eq!(s["temporal_repair"]["future_parent_trace_allowed"],false);
 assert_eq!(s["selective_firewall"]["schema_selection_targets_visible_during_representation_learning"],false);
 assert_eq!(s["selective_firewall"]["transport_targets_visible_before_field_and_scope_seal"],false);
 assert_eq!(s["representation_grammar"]["forbid_engine_identity"],true);
 assert_eq!(s["representation_grammar"]["forbid_architecture_identity"],true);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 let constitution=json!({"schema":"c3x-lawgen-constitution-v15","scientific_stage":STAGE,"spec_sha256":sha(&s),"constitution":s});
 let c=&constitution["constitution"];
 write(&out.join("constitution.json"),&constitution);
 write(&out.join("representation-grammar.json"),&json!({
   "schema":"c3x-p5-representation-grammar-v1","scientific_stage":STAGE,
   "mandatory_anchor":c["representation_grammar"]["mandatory_anchor"],
   "max_coordinates":c["representation_grammar"]["max_coordinates"],
   "max_shortlist":c["representation_grammar"]["max_shortlist"],
   "atoms":c["representation_grammar"]["atoms"],
   "train_admissibility":c["representation_grammar"]["train_admissibility"],
   "complexity":c["representation_grammar"]["complexity"],
   "forbid_engine_identity":true,"forbid_architecture_identity":true,"forbid_sampling_stratum":true
 }));
 write(&out.join("split-gates.json"),&json!({
   "schema":"c3x-p5-split-gates-v1","scientific_stage":STAGE,
   "support_gate":c["support_gate"],"selection_gate":c["selection_gate"],"transport_gate":c["transport_gate"]
 }));
 println!("G95_P5_LAWGEN_V15 {}",constitution["spec_sha256"]);
}
