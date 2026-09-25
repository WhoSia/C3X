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
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3);
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v7");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.4-P31");
 assert_eq!(s["support"]["worlds"],16);
 assert_eq!(s["support"]["hash_mib"],1);
 assert_eq!(s["intervention_family"]["modes"],json!(["BASE","NO_CUTOFF","NO_MOVE","NO_EVAL","NO_CUTOFF_MOVE","NO_CUTOFF_EVAL","NO_MOVE_EVAL","NO_ALL"]));
 let ss=sha(&s);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v7",
  "scientific_stage":s["scientific_stage"],"title":s["title"],"spec_sha256":ss,
  "parent_authority":s["parent_authority"],"objective":s["objective"],"support":s["support"],
  "normalized_semantics":s["normalized_semantics"],"intervention_family":s["intervention_family"],
  "root_provenance":s["root_provenance"],"attribution_graph":s["attribution_graph"],
  "explanation_certificate":s["explanation_certificate"],"architecture_sources":s["architecture_sources"],
  "literature":s["literature"],"claim_ceiling":s["claim_ceiling"],"selective_results_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("semantic-event-schema.json"),serde_json::to_string_pretty(&json!({
  "schema":"c3x-p31-semantic-use-events-v1",
  "summary":"Z,CUTOFF,MOVE_ORDER_SEED,EVAL_REUSE,TT_VALUE_AS_EVAL,PV_PROMOTION",
  "witness":"U,scope,class,key,ply,depth,alpha,beta,tt_value,tt_eval,bound,tt_move,payload",
  "witness_gate":"measurement search only, ply<=4, deterministic first 128 events"
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("compiler-contract.json"),serde_json::to_string_pretty(&json!({
  "schema":"c3x-p31-explainer-compiler-v1",
  "single_class_claims":["root_move","pv","score","search_path"],
  "interaction_claims":"compound masks only; never rewrite as single-class cause",
  "language_ceiling":"engine-computation provenance only; no strategic-intent anthropomorphism"
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
 "ordinal\tphase\n1\tcompile_constitution\n2\tbuild_native_semantic_variants\n3\ttransparency_gate\n4\tprecommit_16_worlds\n5\tbaseline_semantic_trace\n6\tsingle_class_counterfactuals\n7\tcompound_counterfactuals\n8\tattribution_graph\n9\texplanation_compiler\n10\tadjudication\n").unwrap();
 println!("P31_LAWGEN_V7_PASS {} {}",ss,cs);
}