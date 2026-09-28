use clap::{Parser,Subcommand};
use serde_json::{json,Value};
use std::{collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P9";

#[derive(Parser)]
#[command(name="c3x-p9-map")]
struct Cli{#[command(subcommand)]cmd:Cmd}
#[derive(Subcommand)]
enum Cmd{Compile{#[arg(long)]input:PathBuf,#[arg(long)]law:PathBuf,#[arg(long)]out:PathBuf}}

fn load(p:&PathBuf)->Value{serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()}
fn save(p:&PathBuf,v:&Value){if let Some(q)=p.parent(){fs::create_dir_all(q).unwrap();}fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn s<'a>(v:&'a Value,k:&str)->&'a str{v[k].as_str().unwrap_or("")}
fn b(v:&Value,k:&str)->bool{v[k].as_bool().unwrap_or(false)}
fn u(v:&Value,k:&str)->usize{v[k].as_u64().unwrap_or(0) as usize}

fn summarize_phase(rows:&[&Value],phase:&str,req:&Value)->Value{
 let rs:Vec<&Value>=rows.iter().copied().filter(|r|s(r,"phase")==phase).collect();
 let pos:Vec<&Value>=rs.iter().copied().filter(|r|b(r,"root_change")).collect();
 let mut worlds:BTreeMap<String,Vec<&Value>>=BTreeMap::new();
 for r in &rs{worlds.entry(format!("{}|{}",s(r,"engine"),s(r,"position_id"))).or_default().push(*r);}
 let sensitive_worlds:Vec<&String>=worlds.iter().filter(|(_,v)|v.iter().any(|r|b(r,"root_change"))).map(|(k,_)|k).collect();
 let positive_positions:BTreeSet<&str>=pos.iter().map(|r|s(r,"position_id")).collect();
 let engines:BTreeSet<&str>=pos.iter().map(|r|s(r,"engine")).collect();
 let sources:BTreeSet<&str>=pos.iter().map(|r|s(r,"source_id")).collect();
 let mut pos_eng_by_position:BTreeMap<&str,BTreeSet<&str>>=BTreeMap::new();
 for r in &pos{pos_eng_by_position.entry(s(r,"position_id")).or_default().insert(s(r,"engine"));}
 let replicated:Vec<&str>=pos_eng_by_position.iter().filter(|(_,e)|e.len()>=2).map(|(p,_)|*p).collect();
 let pass=pos.len()>=u(req,"min_root_change_events")
  && sensitive_worlds.len()>=u(req,"min_sensitive_worlds")
  && positive_positions.len()>=u(req,"min_sensitive_positions")
  && engines.len()>=u(req,"min_positive_engines")
  && sources.len()>=u(req,"min_positive_sources")
  && replicated.len()>=u(req,"min_cross_engine_replicated_positions");
 json!({
  "phase":phase,"records":rs.len(),"root_change_events":pos.len(),
  "event_sensitivity_rate":if rs.is_empty(){0.0}else{pos.len() as f64/rs.len() as f64},
  "worlds":worlds.len(),"sensitive_worlds":sensitive_worlds.len(),
  "sensitive_world_fraction":if worlds.is_empty(){0.0}else{sensitive_worlds.len() as f64/worlds.len() as f64},
  "sensitive_positions":positive_positions,"positive_engines":engines,"positive_sources":sources,
  "cross_engine_replicated_positions":replicated,"operational_hotspot":pass
 })
}

fn group_counts(rows:&[&Value],keys:&[&str])->Value{
 let mut g:BTreeMap<String,(usize,usize)>=BTreeMap::new();
 for r in rows{
  let k=keys.iter().map(|x|s(r,x)).collect::<Vec<_>>().join("|");
  let e=g.entry(k).or_insert((0,0));e.0+=1;if b(r,"root_change"){e.1+=1;}
 }
 Value::Array(g.into_iter().map(|(k,(n,p))|json!({"key":k,"records":n,"root_change":p,"rate":if n==0{0.0}else{p as f64/n as f64}})).collect())
}

fn control_for<'a>(positive:&Value,rows:&[&'a Value])->Option<&'a Value>{
 let eng=s(positive,"engine");let pos=s(positive,"position_id");let cls=s(positive,"semantic_class");
 let traj=s(positive,"trajectory_id");let phase=s(positive,"phase");
 let mut a:Vec<&Value>=rows.iter().copied().filter(|r|!b(r,"root_change")&&s(r,"engine")==eng&&s(r,"position_id")==pos&&s(r,"semantic_class")==cls).collect();
 a.sort_by(|x,y|s(x,"record_id").cmp(s(y,"record_id")));if let Some(x)=a.first(){return Some(*x)}
 let mut bset:Vec<&Value>=rows.iter().copied().filter(|r|!b(r,"root_change")&&s(r,"engine")==eng&&s(r,"trajectory_id")==traj&&s(r,"phase")==phase&&s(r,"semantic_class")==cls).collect();
 bset.sort_by(|x,y|s(x,"record_id").cmp(s(y,"record_id")));bset.first().copied()
}
fn case_view(r:&Value)->Value{
 json!({"record_id":r["record_id"],"engine":r["engine"],"engine_binary_sha256":r["engine_binary_sha256"],
  "trajectory_id":r["trajectory_id"],"phase":r["phase"],"source_id":r["source_id"],"source_ply":r["source_ply"],
  "position_id":r["position_id"],"fen_sha256":r["candidate_sha256"],"event_address_id":r["event_id"],
  "event_address":r["event_address"],"semantic_class":r["semantic_class"],"scope":r["scope"],"ply":r["ply"],"depth":r["depth"],
  "sampling_stratum":r["sampling_stratum"],"baseline":r["baseline"],"counterfactual":r["counterfactual"],
  "first_pv_divergence":r["first_pv_divergence"],"chess_phenotype":r["chess_phenotype"]})
}

fn compile(input:PathBuf,lawp:PathBuf,out:PathBuf){
 let x=load(&input);let law=load(&lawp);
 assert_eq!(x["schema"],"c3x-p9-event-merged-v1");assert_eq!(x["scientific_stage"],STAGE);
 assert_eq!(law["schema"],"c3x-p9-phase-law-v1");assert_eq!(law["scientific_stage"],STAGE);
 let mut rows:Vec<&Value>=x["records"].as_array().unwrap().iter().collect();
 rows.sort_by(|a,b|s(a,"record_id").cmp(s(b,"record_id")));
 let sg=&law["support_gate"];
 let total=rows.len();let pos=rows.iter().filter(|r|b(r,"root_change")).count();let neg=total-pos;
 let phases:Vec<String>=law["phase_matching"]["phase_windows"].as_array().unwrap().iter().map(|z|s(z,"id").to_string()).collect();
 let by_phase_counts:Vec<(String,usize)>=phases.iter().map(|p|(p.clone(),rows.iter().filter(|r|s(r,"phase")==p).count())).collect();
 let engines:BTreeSet<&str>=rows.iter().filter(|r|b(r,"root_change")).map(|r|s(r,"engine")).collect();
 let sources:BTreeSet<&str>=rows.iter().filter(|r|b(r,"root_change")).map(|r|s(r,"source_id")).collect();
 let posph:BTreeSet<&str>=rows.iter().filter(|r|b(r,"root_change")).map(|r|s(r,"phase")).collect();
 let mut per_engine:BTreeMap<&str,usize>=BTreeMap::new();for r in &rows{*per_engine.entry(s(r,"engine")).or_default()+=1;}
 let mut reasons=Vec::new();
 if total<u(sg,"min_total_fired_records"){reasons.push("TOTAL_FIRED_RECORDS");}
 if by_phase_counts.iter().any(|(_,n)|*n<u(sg,"min_fired_records_per_phase")){reasons.push("PHASE_FIRED_RECORDS");}
 if per_engine.values().any(|n|*n<u(sg,"min_records_per_engine")){reasons.push("ENGINE_RECORDS");}
 if pos<u(sg,"min_total_root_change"){reasons.push("ROOT_CHANGE_RECORDS");}
 if engines.len()<u(sg,"min_positive_engines"){reasons.push("POSITIVE_ENGINES");}
 if sources.len()<u(sg,"min_positive_sources"){reasons.push("POSITIVE_SOURCES");}
 if posph.len()<u(sg,"min_positive_phases"){reasons.push("POSITIVE_PHASES");}
 let support_pass=reasons.is_empty();
 let req=&law["hotspot_rule"]["requirements"];
 let phase_map:Vec<Value>=phases.iter().map(|p|summarize_phase(&rows,p,req)).collect();
 let hotspot_phases:BTreeSet<String>=phase_map.iter().filter(|z|support_pass&&z["operational_hotspot"].as_bool().unwrap()).map(|z|s(z,"phase").to_string()).collect();

 let maxpp=law["regression_suite"]["max_positive_cases_per_phase_engine"].as_u64().unwrap() as usize;
 let mut selected_positive=Vec::<&Value>::new();
 for phase in &hotspot_phases{
  for eng in ["stockfish_19","berserk","ethereal"]{
   let mut z:Vec<&Value>=rows.iter().copied().filter(|r|b(r,"root_change")&&s(r,"phase")==phase&&s(r,"engine")==eng).collect();
   z.sort_by(|a,b|s(a,"record_id").cmp(s(b,"record_id")));z.truncate(maxpp);selected_positive.extend(z);
  }
 }
 let mut regression=Vec::new();
 for p in selected_positive{
  let ctrl=control_for(p,&rows);
  regression.push(json!({"positive":case_view(p),"matched_control":ctrl.map(case_view)}));
 }
 let z=json!({"schema":"c3x-g95-p9-map-v1","scientific_stage":STAGE,
  "status":if support_pass{"CARTOGRAPHY_COMPLETE"}else{"SUPPORT_HOLD"},
  "support":{"records":total,"root_change":pos,"negative":neg,"pass":support_pass,"failure_reasons":reasons,
    "positive_engines":engines,"positive_sources":sources,"positive_phases":posph,
    "records_by_phase":by_phase_counts.into_iter().map(|(p,n)|json!({"phase":p,"records":n})).collect::<Vec<_>>(),
    "records_by_engine":per_engine},
  "phase_map":phase_map,"operational_hotspot_phases":hotspot_phases,
  "engine_phase_map":group_counts(&rows,&["phase","engine"]),
  "source_phase_map":group_counts(&rows,&["phase","source_id"]),
  "semantic_class_phase_map":group_counts(&rows,&["phase","semantic_class"]),
  "regression_suite":regression,
  "winner_selected":false,"post_target_threshold_refit":false,"p8_target_labels_consulted":false,
  "claim_ceiling":law["claim_ceiling"]});
 save(&out,&z);
 println!("P9_MAP {} records={} positive={} hotspots={}",z["status"],total,pos,z["operational_hotspot_phases"].as_array().unwrap().len());
}
fn main(){let c=Cli::parse();match c.cmd{Cmd::Compile{input,law,out}=>compile(input,law,out)}}
