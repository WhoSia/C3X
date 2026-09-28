use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

const STAGE:&str="C3X 0.7.0-G9.5-P9";

fn canon(v:&Value)->Vec<u8>{serde_json::to_vec(v).unwrap()}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())}
fn write(p:&Path,v:&Value){fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}

fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3,"usage: lawgen_v19 spec.json outdir");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-g95-p9-constitution-v1");
 assert_eq!(s["scientific_stage"],STAGE);
 assert_eq!(s["p8_firewall"]["p8_target_labels_confirmatory_vote"],false);
 assert_eq!(s["p8_firewall"]["p8_positive_source_locations_confirmatory_vote"],false);
 assert_eq!(s["phase_matching"]["engine_outcomes_consulted"],false);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 write(&out.join("constitution.json"),&json!({"schema":"c3x-lawgen-constitution-v19","scientific_stage":STAGE,"spec_sha256":sha(&s),"constitution":s}));
 write(&out.join("phase-law.json"),&json!({"schema":"c3x-p9-phase-law-v1","scientific_stage":STAGE,
  "phase_matching":s["phase_matching"],"primary_estimands":s["primary_estimands"],"support_gate":s["support_gate"],
  "hotspot_rule":s["hotspot_rule"],"regression_suite":s["regression_suite"],"claim_ceiling":s["claim_ceiling"]}));
 write(&out.join("firewall.json"),&json!({"schema":"c3x-p9-firewall-v1","scientific_stage":STAGE,"p8_firewall":s["p8_firewall"],"harvest_bridge":s["harvest_bridge"]}));
 println!("G95_P9_LAWGEN_V19 {}",sha(&s));
}
