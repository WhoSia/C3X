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
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),4,"lawgen_v12 spec support out");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 let p:Value=serde_json::from_str(&fs::read_to_string(&a[2]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v12");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.5-P2");
 assert_eq!(p["schema"],"c3x-g95-p2-support-v1");
 assert_eq!(p["scientific_stage"],s["scientific_stage"]);
 assert_eq!(p["parent_closure_commit"],"5641751979adb562a381177323c56d8262d62cc6");
 assert_eq!(s["p2_selective_results_consulted"],false);
 assert_eq!(p["p2_selective_results_consulted"],false);
 assert_eq!(s["context_vocabulary"]["portable"].as_array().unwrap().len(),15);
 assert_eq!(s["context_vocabulary"]["architecture_secondary"].as_array().unwrap().len(),4);
 assert_eq!(s["discovery_basis_court"]["max_portable_cardinality"],3);
 assert_eq!(s["discovery_basis_court"]["support_gate"]["min_fired_records"],96);
 assert_eq!(s["heldout_firewall"]["pre_target_scope_gate"]["min_seen_fraction"],0.25);
 assert_eq!(s["corpus"]["discovery"]["positions"],8);
 assert_eq!(s["corpus"]["heldout"]["positions"],8);
 assert_eq!(s["execution_budgets"]["discovery_engine_worlds"],24);
 assert_eq!(s["execution_budgets"]["heldout_engine_worlds"],24);
 assert_eq!(s["implementation_object"]["rust_cli"],"c3x-field");
 assert_eq!(s["implementation_object"]["rust_commands"],json!(["discover","scope","verify","query"]));
 let ss=sha(&s);let ps=sha(&p);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v12","scientific_stage":s["scientific_stage"],"title":s["title"],
  "spec_sha256":ss,"parent_support_sha256":ps,
  "parent_authority":s["parent_authority"],"objective":s["objective"],"formal_object":s["formal_object"],
  "context_vocabulary":s["context_vocabulary"],"context_measurement":s["context_measurement"],
  "corpus":s["corpus"],"discovery_basis_court":s["discovery_basis_court"],
  "heldout_firewall":s["heldout_firewall"],"heldout_transport_gate":s["heldout_transport_gate"],"verdict_ladder":s["verdict_ladder"],
  "explanation_scope":s["explanation_scope"],"implementation_object":s["implementation_object"],
  "execution_budgets":s["execution_budgets"],"literature":s["literature"],"claim_ceiling":s["claim_ceiling"],
  "p2_selective_results_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[3]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("context-vocabulary.json"),serde_json::to_string_pretty(&s["context_vocabulary"]).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
"ordinal\tphase\n1\tconstitution\n2\tpinned_discovery_and_heldout_corpus\n3\tprecommit_and_executable_inheritance\n4\tdiscovery_profiles_and_targets\n5\tminimal_portable_basis_discovery\n6\theldout_profile_generation\n7\ttarget_blind_scope_selection\n8\theldout_target_opening\n9\ttransport_verification\n10\tengine_specific_basis_comparison\n11\texplanation_scope_compilation\n12\tindependent_javascript_firewall\n13\tdurable_custody\n").unwrap();
 println!("G95_P2_LAWGEN_V12_PASS {} {} {}",ss,ps,cs);
}
