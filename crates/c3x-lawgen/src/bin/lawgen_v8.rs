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
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),4,"lawgen_v8 spec support out");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 let p:Value=serde_json::from_str(&fs::read_to_string(&a[2]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v8");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.4-P32");
 assert_eq!(p["schema"],"c3x-p32-parent-support-v1");
 assert_eq!(p["scientific_stage"],s["scientific_stage"]);
 assert_eq!(p["selected_engine_worlds"],14);
 assert_eq!(p["single_family_cases"],17);
 assert_eq!(s["frontier_localization"]["ply_frontiers"],json!([0,1,2,4,8]));
 assert_eq!(s["minimality"]["budget"]["max_replays_per_case"],96);
 assert_eq!(s["intervention_address"]["event_types"],json!(["CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL"]));
 let ss=sha(&s);let ps=sha(&p);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v8",
  "scientific_stage":s["scientific_stage"],"title":s["title"],
  "spec_sha256":ss,"parent_support_sha256":ps,
  "parent_authority":s["parent_authority"],"objective":s["objective"],"support":s["support"],
  "intervention_address":s["intervention_address"],"frontier_localization":s["frontier_localization"],
  "minimality":s["minimality"],"pv_counterfactual":s["pv_counterfactual"],
  "chess_concept_grounding":s["chess_concept_grounding"],
  "explanation_verification":s["explanation_verification"],"literature":s["literature"],
  "claim_ceiling":s["claim_ceiling"],"p32_event_results_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[3]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("address-contract.json"),serde_json::to_string_pretty(&json!({
   "schema":"c3x-p32-event-address-v1",
   "fields":s["intervention_address"]["address_fields"],
   "event_types":s["intervention_address"]["event_types"],
   "unreached":"requested targets that never match are explicit counterfactual outcomes"
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("minimality-contract.json"),serde_json::to_string_pretty(&json!({
   "schema":"c3x-p32-minimality-v1",
   "removal":s["minimality"]["removal"],"retaining":s["minimality"]["retaining"],
   "budget":s["minimality"]["budget"],"nonmonotonicity":s["minimality"]["nonmonotonicity"]
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("explanation-contract.json"),serde_json::to_string_pretty(&json!({
   "schema":"c3x-p32-explanation-verification-v1",
   "grounding":s["chess_concept_grounding"],"verification":s["explanation_verification"]
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
 "ordinal\tphase\n1\tconstitution\n2\tnative_event_build\n3\tbase_transparency\n4\tp32_precommit\n5\tcase_catalog\n6\tfrontier_localization\n7\tminimal_removal\n8\tminimal_retaining\n9\tleave_one_out_certificate\n10\tpv_reconstruction\n11\tchess_grounding\n12\texplanation_ast\n13\tindependent_verification\n14\tadjudication\n").unwrap();
 println!("P32_LAWGEN_V8_PASS {} {} {}",ss,ps,cs);
}