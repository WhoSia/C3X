use clap::{Parser,Subcommand};
use serde_json::{json,Value};
use std::{collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P10";
#[derive(Parser)]struct Cli{#[command(subcommand)]cmd:Cmd}
#[derive(Subcommand)]enum Cmd{Compile{#[arg(long)]input:PathBuf,#[arg(long)]law:PathBuf,#[arg(long)]out:PathBuf}}
fn load(p:&PathBuf)->Value{serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()}
fn save(p:&PathBuf,v:&Value){if let Some(q)=p.parent(){fs::create_dir_all(q).unwrap();}fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn s<'a>(v:&'a Value,k:&str)->&'a str{v[k].as_str().unwrap_or("")}
fn b(v:&Value,k:&str)->bool{v[k].as_bool().unwrap_or(false)}
fn u(v:&Value,k:&str)->usize{v[k].as_u64().unwrap_or(0) as usize}
fn group(rows:&[&Value],idfield:&str)->Vec<Value>{
 let mut g:BTreeMap<&str,Vec<&Value>>=BTreeMap::new();
 for r in rows{g.entry(s(r,idfield)).or_default().push(*r);}
 g.into_iter().map(|(id,z)|{
  let pos:Vec<&Value>=z.iter().copied().filter(|r|b(r,"root_change")).collect();
  let eng:BTreeSet<&str>=pos.iter().map(|r|s(r,"engine")).collect();
  let positions:BTreeSet<&str>=pos.iter().map(|r|s(r,"position_id")).collect();
  let sources:BTreeSet<&str>=pos.iter().map(|r|s(r,"source_id")).collect();
  json!({"archetype_id":id,"records":z.len(),"root_change":pos.len(),
    "root_change_rate":if z.is_empty(){0.0}else{pos.len() as f64/z.len() as f64},
    "positive_engines":eng,"positive_positions":positions,"positive_sources":sources,
    "example":z.first().map(|r|r[idfield.replace("_id","_archetype").as_str()].clone()).unwrap_or(Value::Null)})
 }).collect()
}
fn compile(input:PathBuf,lawp:PathBuf,out:PathBuf){
 let x=load(&input);let law=load(&lawp);
 assert_eq!(x["schema"],"c3x-p10-event-merged-v1");assert_eq!(x["scientific_stage"],STAGE);
 assert_eq!(law["schema"],"c3x-p10-anatomy-law-v1");
 assert_eq!(x["p9_target_labels_consulted"],false);assert_eq!(x["raw_tt_key_emitted"],false);
 let rows:Vec<&Value>=x["records"].as_array().unwrap().iter().collect();
 let sg=&law["support_gate"];let n=rows.len();let pos=rows.iter().filter(|r|b(r,"root_change")).count();
 let neg=n-pos;
 let mut per_eng:BTreeMap<&str,usize>=BTreeMap::new();for r in &rows{*per_eng.entry(s(r,"engine")).or_default()+=1;}
 let peng:BTreeSet<&str>=rows.iter().filter(|r|b(r,"root_change")).map(|r|s(r,"engine")).collect();
 let psrc:BTreeSet<&str>=rows.iter().filter(|r|b(r,"root_change")).map(|r|s(r,"source_id")).collect();
 let ppos:BTreeSet<&str>=rows.iter().filter(|r|b(r,"root_change")).map(|r|s(r,"position_id")).collect();
 let mut poseng:BTreeMap<&str,BTreeSet<&str>>=BTreeMap::new();
 for r in rows.iter().filter(|r|b(r,"root_change")){poseng.entry(s(r,"position_id")).or_default().insert(s(r,"engine"));}
 let replpos:Vec<&str>=poseng.iter().filter(|(_,e)|e.len()>=2).map(|(p,_)|*p).collect();
 let mut reasons=Vec::<&str>::new();
 if n<u(sg,"min_total_fired_records"){reasons.push("TOTAL_FIRED")}
 if pos<u(sg,"min_total_root_change"){reasons.push("ROOT_CHANGE")}
 if per_eng.values().any(|z|*z<u(sg,"min_records_per_engine")){reasons.push("ENGINE_RECORDS")}
 if peng.len()<u(sg,"min_positive_engines"){reasons.push("POSITIVE_ENGINES")}
 if psrc.len()<u(sg,"min_positive_sources"){reasons.push("POSITIVE_SOURCES")}
 if ppos.len()<u(sg,"min_sensitive_positions"){reasons.push("SENSITIVE_POSITIONS")}
 if replpos.len()<u(sg,"min_cross_engine_replicated_positions"){reasons.push("CROSS_ENGINE_POSITION_REPLICATION")}
 let support_pass=reasons.is_empty();

 let a0=group(&rows,"a0_id");let a1=group(&rows,"a1_id");let rr=&law["lineage"]["replicated_primary_archetype_rule"];
 let mut replicated=Vec::new();
 if support_pass{
  for z in &a0{
   if u(z,"root_change")>=u(rr,"min_root_change_events")
    && z["positive_engines"].as_array().map(|x|x.len()).unwrap_or(0)>=u(rr,"min_positive_engines")
    && z["positive_positions"].as_array().map(|x|x.len()).unwrap_or(0)>=u(rr,"min_positive_positions")
    && z["positive_sources"].as_array().map(|x|x.len()).unwrap_or(0)>=u(rr,"min_positive_sources"){
     replicated.push(z.clone());
   }
  }
 }
 let mut samepos=Vec::new();
 for p in &replpos{
  let zs:Vec<&Value>=rows.iter().copied().filter(|r|b(r,"root_change")&&s(r,"position_id")==*p).collect();
  samepos.push(json!({"position_id":p,"engines":zs.iter().map(|r|s(r,"engine")).collect::<BTreeSet<_>>(),
    "witnesses":zs.iter().map(|r|json!({"record_id":r["record_id"],"engine":r["engine"],"a0_id":r["a0_id"],
      "baseline_bestmove":r["baseline"]["bestmove"],"counterfactual_bestmove":r["counterfactual"]["bestmove"],
      "first_pv_divergence":r["first_pv_divergence"]})).collect::<Vec<_>>()}));
 }
 let verdicts=&law["fresh_anatomy_verdicts"];
 let status=if !support_pass{s(verdicts,"support_fail")}else if replicated.is_empty(){s(verdicts,"support_pass_no_replicated_archetype")}else{s(verdicts,"support_pass_replicated_archetype")};
 let z=json!({"schema":"c3x-g95-p10-anatomy-v1","scientific_stage":STAGE,"status":status,
  "support":{"records":n,"root_change":pos,"negative":neg,"pass":support_pass,"failure_reasons":reasons,
    "records_by_engine":per_eng,"positive_engines":peng,"positive_sources":psrc,"sensitive_positions":ppos,
    "cross_engine_replicated_positions":replpos},
  "a0_map":a0,"a1_diagnostic_map":a1,"replicated_a0_archetypes":replicated,
  "same_position_cross_engine_witnesses":samepos,
  "p9_target_labels_consulted":false,"p9_regression_witnesses_confirmatory_vote":false,
  "a1_may_rescue_a0":false,"post_target_archetype_refit":false,"raw_tt_key_emitted":false,
  "claim_ceiling":law["claim_ceiling"]});
 save(&out,&z);
 println!("P10_ANATOMY {} records={} positive={} replicated_a0={}",status,n,pos,z["replicated_a0_archetypes"].as_array().unwrap().len());
}
fn main(){let c=Cli::parse();match c.cmd{Cmd::Compile{input,law,out}=>compile(input,law,out)}}
