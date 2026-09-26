use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

fn canon(v:&Value)->Vec<u8>{
 let mut x=v.clone();
 fn sort(v:&mut Value){match v{
  Value::Object(m)=>{let old=std::mem::take(m);let mut kv:Vec<_>=old.into_iter().collect();kv.sort_by(|a,b|a.0.cmp(&b.0));for(k,mut z)in kv{sort(&mut z);m.insert(k,z);}},
  Value::Array(a)=>for z in a{sort(z)},_=>{}
 }}
 sort(&mut x);serde_json::to_vec(&x).unwrap()
}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())}

fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),4,"lawgen_v13 spec support out");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 let p:Value=serde_json::from_str(&fs::read_to_string(&a[2]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v13");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.5-P3");
 assert_eq!(p["schema"],"c3x-g95-p3-support-v1");
 assert_eq!(p["scientific_stage"],s["scientific_stage"]);
 assert_eq!(p["parent_closure_commit"],"07591db34ee6af830efc5736ad397a7e1a577247");
 assert_eq!(s["p3_selective_results_consulted"],false);
 assert_eq!(p["p3_selective_results_consulted"],false);
 assert_eq!(s["schema_families"].as_array().unwrap().len(),5);
 assert_eq!(s["development_derived_rivals"].as_array().unwrap().len(),2);
 assert!(s["schema_families"].as_array().unwrap().iter().all(|x|x["role"]=="PRIMARY_CANDIDATE"));
 assert!(s["development_derived_rivals"].as_array().unwrap().iter().all(|x|x["role"]=="DEVELOPMENT_DERIVED_RIVAL_ONLY"));
 assert_eq!(s["context_measurement"]["causal_availability"],"EVENT_PREFIX_ONLY");
 assert_eq!(s["context_measurement"]["future_of_candidate_parent_trace_features_allowed"],false);
 assert_eq!(s["context_measurement"]["raw_full_key_emitted"],false);
 assert_eq!(s["corpus"]["discovery"]["positions"],8);
 assert_eq!(s["corpus"]["heldout"]["positions"],8);
 assert_eq!(s["discovery_court"]["support_gate"]["min_fired_records"],96);
 assert_eq!(s["heldout_firewall"]["pre_target_scope_gate"]["min_seen_fraction"],0.25);
 assert_eq!(s["implementation_object"]["rust_cli"],"c3x-field-p3");
 assert_eq!(s["implementation_object"]["rust_commands"],json!(["assess","query","diagnose"]));
 let ss=sha(&s);let ps=sha(&p);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v13","scientific_stage":s["scientific_stage"],"title":s["title"],
  "spec_sha256":ss,"parent_support_sha256":ps,"parent_authority":s["parent_authority"],
  "development_firewall":s["development_firewall"],"formal_object":s["formal_object"],
  "context_schema_version":s["context_schema_version"],"base_coordinates":s["base_coordinates"],
  "new_coordinate_vocabulary":s["new_coordinate_vocabulary"],"schema_families":s["schema_families"],
  "development_derived_rivals":s["development_derived_rivals"],
  "context_measurement":s["context_measurement"],"corpus":s["corpus"],"execution":s["execution"],
  "discovery_court":s["discovery_court"],"heldout_firewall":s["heldout_firewall"],
  "heldout_transport_gate":s["heldout_transport_gate"],"diagnose_surface":s["diagnose_surface"],
  "explanation_service":s["explanation_service"],"verdict_ladder":s["verdict_ladder"],
  "implementation_object":s["implementation_object"],"literature":s["literature"],
  "source_code_study":s["source_code_study"],"claim_ceiling":s["claim_ceiling"],
  "p3_selective_results_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[3]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 let mut all_schemas=s["schema_families"].as_array().unwrap().clone();
 all_schemas.extend(s["development_derived_rivals"].as_array().unwrap().clone());
 fs::write(out.join("schema-families.json"),serde_json::to_string_pretty(&Value::Array(all_schemas)).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
"ordinal\tphase\n1\tconstitution\n2\tp2_development_failure_diagnosis\n3\tfresh_corpus_freeze\n4\tprecommit_and_executable_inheritance\n5\tfresh_discovery_profiles_and_targets\n6\ttopology_schema_discovery\n7\theldout_profile_target_split\n8\ttarget_blind_scope\n9\theldout_target_opening\n10\tglobal_and_engine_specific_transport\n11\tpost_verification_diagnosis\n12\texplanation_service_compilation\n13\tindependent_firewall\n14\treproducible_toolkit\n15\tdurable_custody\n").unwrap();
 println!("G95_P3_LAWGEN_V13_PASS {} {} {}",ss,ps,cs);
}