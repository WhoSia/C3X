use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

fn canon(v:&Value)->Vec<u8>{
 let mut x=v.clone();
 fn sort(v:&mut Value){match v{
  Value::Object(m)=>{let old=std::mem::take(m);let mut kv:Vec<_>=old.into_iter().collect();kv.sort_by(|a,b|a.0.cmp(&b.0));for(k,mut z)in kv{sort(&mut z);m.insert(k,z);}},
  Value::Array(a)=>for z in a{sort(z)}, _=>{}
 }}
 sort(&mut x);serde_json::to_vec(&x).unwrap()
}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())}

fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),4,"lawgen_v11 spec support out");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 let p:Value=serde_json::from_str(&fs::read_to_string(&a[2]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v11");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.5-P1");
 assert_eq!(p["schema"],"c3x-g95-p1-support-v1");
 assert_eq!(p["scientific_stage"],s["scientific_stage"]);
 assert_eq!(p["counts"]["discovery"],2);
 assert_eq!(p["counts"]["binding_holdout"],1);
 assert_eq!(p["counts"]["historical_transport"],4);
 assert_eq!(p["counts"]["fresh_engine_worlds"],6);
 assert_eq!(s["discovery_and_freeze"]["refinement_order"],json!(["F0","F1","F2","F3"]));
 assert_eq!(s["candidate_selection"]["max_exact_events_per_world"],8);
 assert_eq!(s["execution_budgets"]["max_candidates_per_world"],8);
 assert_eq!(s["execution_budgets"]["max_world_replays"],12);
 assert_eq!(s["implementation_roles"]["policy"],"CAPABILITY_FIRST_POLYGLOT_LANGUAGE_NONAUTHORITATIVE");
 assert_eq!(s["g95_p1_selective_results_consulted"],false);
 assert_eq!(p["g95_p1_selective_results_consulted"],false);
 let ss=sha(&s);let ps=sha(&p);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v11",
  "scientific_stage":s["scientific_stage"],"title":s["title"],
  "spec_sha256":ss,"parent_support_sha256":ps,
  "parent_authority":s["parent_authority"],"objective":s["objective"],
  "causal_fiber":s["causal_fiber"],"candidate_selection":s["candidate_selection"],
  "parent_contexts":s["parent_contexts"],"discovery_and_freeze":s["discovery_and_freeze"],
  "holdout_gate":s["holdout_gate"],"transport":s["transport"],"verdict_ladder":s["verdict_ladder"],
  "execution_budgets":s["execution_budgets"],"exact_event_explanation":s["exact_event_explanation"],
  "implementation_roles":s["implementation_roles"],"external_code_study":s["external_code_study"],
  "literature":s["literature"],"claim_ceiling":s["claim_ceiling"],
  "g95_p1_selective_results_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[3]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("fiber-levels.json"),serde_json::to_string_pretty(&s["causal_fiber"]["levels"]).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
 "ordinal\tphase\n1\tconstitution\n2\tsource_locked_corpus\n3\tprecommit_and_binary_hash_inheritance\n4\tdiscovery_singleton_diagnostics\n5\tdiscovery_level_freeze\n6\tbinding_stockfish_holdout\n7\thistorical_transport\n8\tfresh_cross_engine_transport\n9\tlegal_move_and_pv_replay\n10\trust_signature_recomputation\n11\tjavascript_firewall_verification\n12\tadjudication\n").unwrap();
 println!("G95_P1_LAWGEN_V11_PASS {} {} {}",ss,ps,cs);
}
