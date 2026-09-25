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
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),4,"lawgen_v9 spec support out");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 let p:Value=serde_json::from_str(&fs::read_to_string(&a[2]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v9");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.4-P33");
 assert_eq!(p["schema"],"c3x-p33-parent-support-v1");
 assert_eq!(p["scientific_stage"],s["scientific_stage"]);
 assert_eq!(p["primary_case_count"],3);
 assert_eq!(p["repeat_control_count"],3);
 assert_eq!(s["closure_refinement"]["max_refinement_rounds"],8);
 assert_eq!(s["closure_refinement"]["max_addresses"],2048);
 assert_eq!(s["closure_refinement"]["max_replays_per_case"],160);
 assert_eq!(s["event_identity"]["classes"],json!(["EXACT_CONTINUATION","DRIFTED_CONTINUATION","EMERGENT","VANISHED"]));
 assert_eq!(s["implementation_roles"]["policy"],"CAPABILITY_FIRST_POLYGLOT_LANGUAGE_NONAUTHORITATIVE");
 assert_eq!(s["p33_selective_results_consulted"],false);
 let ss=sha(&s);let ps=sha(&p);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v9",
  "scientific_stage":s["scientific_stage"],"title":s["title"],
  "spec_sha256":ss,"parent_support_sha256":ps,
  "parent_authority":s["parent_authority"],"objective":s["objective"],"support":s["support"],
  "event_identity":s["event_identity"],"closure_refinement":s["closure_refinement"],
  "emergent_causation":s["emergent_causation"],"controls":s["controls"],
  "pv_counterfactual":s["pv_counterfactual"],"explanation_verification":s["explanation_verification"],
  "implementation_roles":s["implementation_roles"],"literature":s["literature"],
  "claim_ceiling":s["claim_ceiling"],"p33_selective_results_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[3]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("lineage-contract.json"),serde_json::to_string_pretty(&json!({
  "schema":"c3x-p33-lineage-contract-v1",
  "token_identity":s["event_identity"]["token_identity"],
  "hard_anchor":s["event_identity"]["lineage_hard_anchor"],
  "soft_coordinates":s["event_identity"]["lineage_soft_coordinates"],
  "correspondence_rule":s["event_identity"]["correspondence_rule"],
  "classes":s["event_identity"]["classes"],
  "split_merge_policy":s["event_identity"]["split_merge_policy"]
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("closure-contract.json"),serde_json::to_string_pretty(&json!({
  "schema":"c3x-p33-closure-contract-v1",
  "seed_universe":s["closure_refinement"]["seed_universe"],
  "parent_intervention":s["closure_refinement"]["parent_intervention"],
  "refinement_rule":s["closure_refinement"]["refinement_rule"],
  "fixed_point":s["closure_refinement"]["fixed_point"],
  "max_refinement_rounds":s["closure_refinement"]["max_refinement_rounds"],
  "max_addresses":s["closure_refinement"]["max_addresses"],
  "max_replays_per_case":s["closure_refinement"]["max_replays_per_case"],
  "max_final_leave_one_out":s["closure_refinement"]["max_final_leave_one_out"]
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
 "ordinal\tphase\n1\tconstitution\n2\trust_lineage_unit_tests\n3\tp32_parent_artifact_pin\n4\trepeat_identity_controls\n5\tp33_precommit\n6\tbaseline_catalogue\n7\tparent_baseline_seed_removal\n8\tlineage_correspondence\n9\tappend_only_closure_refinement\n10\tbranch_novel_minimal_removal\n11\tbranch_novel_retaining_sufficiency\n12\tproductive_trace_witness\n13\tpv_legality_and_chess_atoms\n14\tjavascript_independent_verification\n15\tadjudication\n").unwrap();
 println!("P33_LAWGEN_V9_PASS {} {} {}",ss,ps,cs);
}
