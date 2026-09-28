use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};
const STAGE:&str="C3X 0.7.0-G9.5-P8";
fn canon(v:&Value)->Vec<u8>{serde_json::to_vec(v).unwrap()}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())}
fn write(p:&Path,v:&Value){fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3);
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-g95-p8-constitution-v1");assert_eq!(s["scientific_stage"],STAGE);
 assert_eq!(s["label_firewall"]["p7_q_state_ids_allowed_in_p8_descriptor"],false);
 assert_eq!(s["label_firewall"]["engine_identity_allowed_in_primary_descriptor"],false);
 assert_eq!(s["label_firewall"]["counterfactual_information_allowed_before_train_prototype_freeze"],false);
 assert_eq!(s["prototype_labeling"]["no_deterministic_causal_state_claim"],true);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 write(&out.join("constitution.json"),&json!({"schema":"c3x-lawgen-constitution-v18","scientific_stage":STAGE,"spec_sha256":sha(&s),"constitution":s}));
 write(&out.join("descriptor-law.json"),&json!({"schema":"c3x-p8-descriptor-law-v1","scientific_stage":STAGE,
  "descriptor":s["descriptor"],"label_firewall":s["label_firewall"]}));
 write(&out.join("prototype-law.json"),&json!({"schema":"c3x-p8-prototype-law-v1","scientific_stage":STAGE,
  "prototype_cover":s["prototype_cover"],"prototype_labeling":s["prototype_labeling"]}));
 write(&out.join("retrieval-gates.json"),&json!({"schema":"c3x-p8-retrieval-gates-v1","scientific_stage":STAGE,
  "train_support_gate":s["train_support_gate"],"selection_support_gate":s["selection_support_gate"],
  "retrieval_gate":s["retrieval_gate"],"transport_gate":s["transport_gate"]}));
 write(&out.join("developer-diagnostic-law.json"),&json!({"schema":"c3x-p8-developer-diagnostic-law-v1","scientific_stage":STAGE,
  "developer_diagnostic":s["developer_diagnostic"],"claim_ceiling":s["claim_ceiling"]}));
 println!("G95_P8_LAWGEN_V18 {}",sha(&s));
}
