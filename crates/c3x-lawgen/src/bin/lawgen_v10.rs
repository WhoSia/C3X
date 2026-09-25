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
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),4,"lawgen_v10 spec support out");
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 let p:Value=serde_json::from_str(&fs::read_to_string(&a[2]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v10");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.4-P34");
 assert_eq!(p["schema"],"c3x-p34-parent-support-v1");
 assert_eq!(p["scientific_stage"],s["scientific_stage"]);
 assert_eq!(p["primary_case_count"],3);
 assert_eq!(s["quotient_lattice"]["refinement_order"],json!(["Q0","Q1","Q2","Q3"]));
 assert_eq!(s["closure_or_divergence"]["max_refinement_rounds_per_level"],6);
 assert_eq!(s["closure_or_divergence"]["max_observed_cones_per_level"],256);
 assert_eq!(s["closure_or_divergence"]["max_replays_per_case_level"],128);
 assert_eq!(s["collision_falsification"]["max_exact_members_per_selected_cone"],12);
 assert_eq!(s["implementation_roles"]["policy"],"CAPABILITY_FIRST_POLYGLOT_LANGUAGE_NONAUTHORITATIVE");
 assert_eq!(s["p34_selective_results_consulted"],false);
 assert_eq!(p["p34_selective_outcomes_consulted"],false);
 let ss=sha(&s);let ps=sha(&p);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v10",
  "scientific_stage":s["scientific_stage"],"title":s["title"],
  "spec_sha256":ss,"parent_support_sha256":ps,
  "parent_authority":s["parent_authority"],"objective":s["objective"],
  "quotient_lattice":s["quotient_lattice"],"intervention_semantics":s["intervention_semantics"],
  "closure_or_divergence":s["closure_or_divergence"],"causal_gates":s["causal_gates"],
  "collision_falsification":s["collision_falsification"],
  "explanation_verification":s["explanation_verification"],
  "implementation_roles":s["implementation_roles"],
  "external_code_study":s["external_code_study"],"literature":s["literature"],
  "data_policy":s["data_policy"],"claim_ceiling":s["claim_ceiling"],
  "p34_selective_results_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[3]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("quotient-lattice.json"),serde_json::to_string_pretty(&s["quotient_lattice"]).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
 "ordinal\tphase\n1\tconstitution\n2\tengine_dynamic_cone_build\n3\tbase_transparency\n4\tparent_seed_replay\n5\tQ0_closure_and_collision\n6\tQ1_refinement_if_required\n7\tQ2_refinement_if_required\n8\tQ3_refinement_if_required\n9\texact_member_drilldown\n10\tpv_legality\n11\tjavascript_independent_verification\n12\tadjudication\n").unwrap();
 println!("P34_LAWGEN_V10_PASS {} {} {}",ss,ps,cs);
}
