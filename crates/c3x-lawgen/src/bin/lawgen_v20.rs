use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};
const STAGE:&str="C3X 0.7.0-G9.5-P10";
fn canon(v:&Value)->Vec<u8>{serde_json::to_vec(v).unwrap()}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())}
fn write(p:&Path,v:&Value){fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3,"usage: lawgen_v20 spec.json outdir");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-g95-p10-constitution-v1");
 assert_eq!(s["scientific_stage"],STAGE);
 assert_eq!(s["p9_firewall"]["p9_target_labels_confirmatory_vote"],false);
 assert_eq!(s["p9_firewall"]["p9_regression_witnesses_confirmatory_vote"],false);
 assert_eq!(s["late_opening_worlds"]["engine_outcomes_consulted"],false);
 assert_eq!(s["lineage"]["no_post_target_archetype_refit"],true);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 write(&out.join("constitution.json"),&json!({"schema":"c3x-lawgen-constitution-v20","scientific_stage":STAGE,"spec_sha256":sha(&s),"constitution":s}));
 write(&out.join("anatomy-law.json"),&json!({"schema":"c3x-p10-anatomy-law-v1","scientific_stage":STAGE,
  "support_gate":s["support_gate"],"lineage":s["lineage"],"fresh_anatomy_verdicts":s["fresh_anatomy_verdicts"],
  "claim_ceiling":s["claim_ceiling"]}));
 write(&out.join("event-sampler.json"),&json!({"schema":"c3x-p10-event-sampler-law-v1","scientific_stage":STAGE,
  "event_sampler":s["event_sampler"],"execution":s["execution"]}));
 write(&out.join("regression-law.json"),&json!({"schema":"c3x-p10-regression-law-v1","scientific_stage":STAGE,
  "p9_regression_seed_lane":s["p9_regression_seed_lane"],"claim_ceiling":s["claim_ceiling"]}));
 write(&out.join("firewall.json"),&json!({"schema":"c3x-p10-firewall-v1","scientific_stage":STAGE,
  "p9_firewall":s["p9_firewall"],"harvest_bridge":s["harvest_bridge"]}));
 println!("G95_P10_LAWGEN_V20 {}",sha(&s));
}
