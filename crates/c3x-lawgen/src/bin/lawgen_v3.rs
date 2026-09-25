use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

fn canonical(v:&Value)->Value{
 match v{
  Value::Object(m)=>{
   let mut ks:Vec<_>=m.keys().cloned().collect();ks.sort();
   let mut o=serde_json::Map::new();
   for k in ks{o.insert(k.clone(),canonical(&m[&k]));}
   Value::Object(o)
  },
  Value::Array(a)=>Value::Array(a.iter().map(canonical).collect()),
  _=>v.clone()
 }
}
fn sha(v:&Value)->String{
 let b=serde_json::to_vec(&canonical(v)).unwrap();
 let mut h=Sha256::new();h.update(b);format!("{:x}",h.finalize())
}
fn req<'a>(v:&'a Value,k:&str)->&'a Value{v.get(k).unwrap_or_else(||panic!("missing {k}"))}
fn main(){
 let a:Vec<String>=env::args().collect();
 if a.len()!=3{eprintln!("usage: c3x-lawgen-v3 <spec.json> <out-dir>");std::process::exit(2);}
 let raw=fs::read_to_string(&a[1]).unwrap();
 let spec:Value=serde_json::from_str(&raw).unwrap();
 assert_eq!(req(&spec,"schema"),"c3x-lawgen-spec-v3");
 assert_eq!(req(&spec,"scientific_stage"),"C3X 0.7.0-G9.4-P27");
 let scope=req(&spec,"scope");
 assert_eq!(scope["anchor_budget_nodes"],80000);
 assert_eq!(scope["expected_cells"],128);
 assert_eq!(scope["selected_per_family_side_state"],1);
 let m=req(&spec,"manipulable_coordinate");
 assert_eq!(m["name"],"probe_refreshes_age_on_hit");
 assert_eq!(m["values"],json!([false,true]));
 let h=req(&spec,"history_instrument");
 assert_eq!(h["decoy_count"],3);
 assert_eq!(h["measurement_nodes"],80000);
 assert_eq!(h["threads"],1);
 assert_eq!(h["hash_mib"],64);
 let pred=req(&spec,"held_out_prediction");
 assert_eq!(pred["donor_architectures"],json!(["stockfish_19","berserk"]));
 assert_eq!(pred["held_out_architecture"],"ethereal");
 assert_eq!(pred["freeze_before_held_out_selective_outcomes"],true);
 let topo=req(&spec,"indexing_counterfactual");
 assert_eq!(topo["status"],"PRECOMMITTED_HOLD_UNLESS_TOPOLOGY_ISOMORPHISM_WITNESS");
 let spec_sha=sha(&spec);
 let constitution=json!({
  "schema":"c3x-lawgen-constitution-v3",
  "scientific_stage":spec["scientific_stage"],
  "title":spec["title"],
  "spec_sha256":spec_sha,
  "parent_authority":spec["parent_authority"],
  "scope":scope,
  "manipulation_contract":m,
  "history_instrument":h,
  "held_out_morphism_prediction":pred,
  "topology_counterfactual_gate":topo,
  "lawgen_v3":spec["lawgen_v3"],
  "literature_constraints":spec["literature_constraints"],
  "prospective_claims":spec["prospective_claims"],
  "claim_ceiling":spec["claim_ceiling"],
  "selective_outcomes_consulted":false
 });
 let csha=sha(&constitution);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({
   "constitution":constitution,"constitution_sha256":csha
 })).unwrap()+"\n").unwrap();
 let contract=json!({
  "schema":"c3x-mechanism-morphism-contract-v1",
  "scientific_stage":"C3X 0.7.0-G9.4-P27",
  "constitution_sha256":csha,
  "coordinate":"probe_refreshes_age_on_hit",
  "domain":[false,true],
  "estimand":"history-conditioned OFF->ON law-fingerprint transition",
  "donors":["stockfish_19","berserk"],
  "held_out":"ethereal",
  "prediction_capacity":"3-bit component-change mask only; donor exact-consensus required",
  "forbidden":[
   "post-heldout donor rule changes",
   "outcome-trained state remapping",
   "calling an indexing-family source swap a local coordinate intervention",
   "claiming a direct instantaneous age effect from the history-conditioned total effect"
  ]
 });
 fs::write(out.join("mechanism-morphism-contract.json"),serde_json::to_string_pretty(&contract).unwrap()+"\n").unwrap();
 let lattice=json!({
  "schema":"c3x-lawgen-claim-lattice-v3",
  "scientific_stage":"C3X 0.7.0-G9.4-P27",
  "constitution_sha256":csha,
  "nodes":[
   {"id":"S","requires":[],"meaning":"exact source locks and paired OFF/ON materialization"},
   {"id":"E","requires":["S"],"meaning":"native-policy off-target equivalence"},
   {"id":"H","requires":["E"],"meaning":"frozen persistent-TT history instrument and inherited support"},
   {"id":"D","requires":["H"],"meaning":"donor OFF/ON law-field execution"},
   {"id":"P","requires":["D"],"meaning":"sealed donor-consensus held-out prediction"},
   {"id":"X","requires":["P"],"meaning":"held-out Ethereal selective execution"},
   {"id":"M","requires":["X"],"meaning":"descriptor-to-causal-morphism adjudication"},
   {"id":"T","requires":[],"meaning":"indexing topology-isomorphism witness gate"}
  ],
  "non_implications":[
   "source locality does not imply nonzero causal effect",
   "within-engine age effect does not imply cross-engine morphism",
   "held-out match does not imply budget transport",
   "indexing gate failure does not imply indexing causal irrelevance"
  ]
 });
 fs::write(out.join("claim-lattice.json"),serde_json::to_string_pretty(&lattice).unwrap()+"\n").unwrap();
 let phases=[
  ("ontology_compile","outcome_blind"),
  ("source_pair_materialize","outcome_blind"),
  ("native_equivalence","outcome_blind"),
  ("history_precommit","outcome_blind"),
  ("donor_selective","post_precommit"),
  ("donor_prediction_seal","post_donor_before_heldout"),
  ("heldout_selective","post_prediction"),
  ("morphism_adjudication","post_heldout")
 ];
 let mut t="ordinal\tphase\tauthority\n".to_string();
 for (i,(p,a)) in phases.iter().enumerate(){t.push_str(&format!("{}\t{}\t{}\n",i+1,p,a));}
 fs::write(out.join("execution-matrix.tsv"),t).unwrap();
 println!("P27_LAWGEN_V3_PASS spec={} constitution={}",spec_sha,csha);
}
