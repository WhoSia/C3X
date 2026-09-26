use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

const STAGE:&str="C3X 0.7.0-G9.5-P4";

fn canonical(v:&Value)->Vec<u8>{serde_json::to_vec(v).unwrap()}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canonical(v));format!("{:x}",h.finalize())}
fn write(path:&Path,v:&Value){fs::write(path,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}

fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3,"usage: lawgen_v14 spec.json outdir");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-g95-p4-constitution-v1");assert_eq!(s["scientific_stage"],STAGE);
 assert_eq!(s["selective_firewall"]["p2_p3_root_change_labels_used_to_choose_sampling_strata"],false);
 assert_eq!(s["selective_firewall"]["p2_p3_heldout_targets_confirmatory_vote"],false);
 assert_eq!(s["sampling"]["target_fields_consulted"],false);
 assert_eq!(s["context_field"]["feature_expansion_allowed"],false);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 let constitution=json!({"schema":"c3x-lawgen-constitution-v14","scientific_stage":STAGE,"spec_sha256":sha(&s),"constitution":s});
 let c=&constitution["constitution"];
 write(&out.join("constitution.json"),&constitution);
 write(&out.join("sampling-strata.json"),&json!({"schema":"c3x-p4-sampling-plan-v1","scientific_stage":STAGE,"strata":c["sampling"]["strata"],"target_fields_consulted":false,"raw_key_policy":c["sampling"]["raw_key_policy"]}));
 write(&out.join("schema-families.json"),&c["context_field"]["schema_families"]);
 write(&out.join("power-plan.json"),&json!({"schema":"c3x-p4-power-plan-v1","scientific_stage":STAGE,"power_gate":c["power_gate"],"positive_control_lane":c["positive_control_lane"]}));
 println!("G95_P4_LAWGEN_V14 {}",constitution["spec_sha256"]);
}
