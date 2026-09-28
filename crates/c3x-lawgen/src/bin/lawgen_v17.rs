use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};
const STAGE:&str="C3X 0.7.0-G9.5-P7";
fn canon(v:&Value)->Vec<u8>{serde_json::to_vec(v).unwrap()}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())}
fn write(p:&Path,v:&Value){fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3);
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-g95-p7-constitution-v1");assert_eq!(s["scientific_stage"],STAGE);
 assert_eq!(s["label_firewall"]["p6_target_labels_confirmatory_vote"],false);
 assert_eq!(s["label_firewall"]["fiber_id_allowed_in_p7_state"],false);
 assert_eq!(s["cseg"]["counterfactual_information_allowed"],false);
 assert_eq!(s["cseg"]["raw_tt_key_emitted"],false);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 write(&out.join("constitution.json"),&json!({"schema":"c3x-lawgen-constitution-v17","scientific_stage":STAGE,"spec_sha256":sha(&s),"constitution":s}));
 let c=&s["cseg"];write(&out.join("cseg-schema.json"),&json!({"schema":"c3x-p7-cseg-law-v1","scientific_stage":STAGE,
  "root_node_atoms":c["root_node_atoms"],"event_node_atoms":c["event_node_atoms"],"edge_types":c["edge_types"],
  "raw_tt_key_emitted":false,"counterfactual_information_allowed":false,"fiber_id_allowed":false}));
 write(&out.join("quotient-ladder.json"),&json!({"schema":"c3x-p7-quotient-ladder-v1","scientific_stage":STAGE,
  "ladder":s["quotient_ladder"],"state_gate":s["state_gate"]}));
 write(&out.join("split-gates.json"),&json!({"schema":"c3x-p7-split-gates-v1","scientific_stage":STAGE,
  "train_support_gate":s["train_support_gate"],"selection_support_gate":s["selection_support_gate"],
  "selection_gate":s["selection_gate"],"transport_gate":s["transport_gate"]}));
 write(&out.join("label-firewall.json"),&json!({"schema":"c3x-p7-label-firewall-v1","scientific_stage":STAGE,"firewall":s["label_firewall"]}));
 println!("G95_P7_LAWGEN_V17 {}",sha(&s));
}
