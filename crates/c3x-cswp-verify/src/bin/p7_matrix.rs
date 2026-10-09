//! C3X 0.15 P7 independent categorical-outcome verifier.
//! Separate Rust implementation, audited against original P6 native reference.
use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,process};
const P7_SHA:&str="01ea31dcb1d900925ff38ec3d6d5da4afe63bba6c87eccc2eb8563d9440d8c77";
const P6_SHA:&str="c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11";
fn guard(ok:bool,reason:impl Into<String>)->Result<(),String>{if ok{Ok(())}else{Err(reason.into())}}
fn read(path:&str,sha:&str)->Result<Value,String>{
 let b=fs::read(path).map_err(|e|format!("READ {path}: {e}"))?;
 let digest=format!("{:x}",Sha256::digest(&b));
 guard(digest==sha,format!("INPUT_SHA_NOT_FROZEN {path} actual={digest}"))?;
 serde_json::from_slice(&b).map_err(|e|e.to_string())
}
fn arr<'a>(v:&'a Value,k:&str)->Result<&'a [Value],String>{
 v.get(k).and_then(Value::as_array).map(|a|a.as_slice()).ok_or_else(||format!("MISSING_ARRAY {k}"))
}
fn v<'a>(x:&'a Value,key:&str)->Result<&'a Value,String>{
 x.get(key).ok_or_else(||format!("MISSING {key}"))
}
fn arm<'a>(x:&'a Value,arm:&str)->Result<&'a Value,String>{
 v(v(x,"cells")?,arm)
}
fn mv(x:&Value)->Result<&str,String>{
 v(v(x,"UCI")?,"bestmove")?.as_str().ok_or_else(||"MISSING_MOVE".to_owned())
}
fn rule(p7:&Value,p6:&Value)->Result<Value,String>{
 guard(v(p7,"native_search_processes")?.as_u64()==Some(24),"NOT_24_NATIVE_SEARCHES")?;
 guard(v(p7,"cold_pairs")?.as_u64()==Some(12),"COLD_REPEAT_COUNT_BAD")?;
 let rows=arr(p7,"cases")?;
 let olds=arr(p6,"all_64_native_four_cell_interventions")?;
 guard(rows.len()==2 && olds.len()==64,"P7_P6_COURT_DENOMINATOR_BAD")?;
 let mut report=Vec::new();
 for (idx,x) in rows.iter().enumerate(){
  let ordinal=[2usize,29][idx];let original=&olds[ordinal-1];
  guard(v(x,"ordinal")?.as_u64()==Some(ordinal as u64),"CASE_ORDER_CHANGED")?;
  guard(v(original,"ordinal")?.as_u64()==Some(ordinal as u64),"P6_CASE_CHANGED")?;
  guard(v(x,"root_fen_sha256")?==v(original,"fen_sha256")?,"ORIGINAL_FEN_CHANGED")?;
  guard(v(x,"frozen_target")?==v(original,"presealed_tt_target")?,"P7_TARGET_NOT_P6_PRESELECTED")?;
  guard(v(x,"source_law")?==v(original,"law")?,"SOURCE_CHESS_LAW_CHANGED")?;
  let mut matrix=Vec::new();
  for see in ["OFF","ROOT_OBJECT_SEE_UNMASK"] {
   for (mode,p6mode) in [("IDENTITY",Some("ALLOW")),("RETURN_ALPHA",None),("BLOCK_EXACT_ONCE",Some("BLOCK_EXACT_ONCE"))] {
    let key=format!("{see}__{mode}");
    let p7arm=arm(x,&key)?;
    let answer=mv(p7arm)?;
    let pv=v(v(p7arm,"UCI")?,"pv")?.as_array().ok_or("PV_NOT_ARRAY")?;
    guard(pv.first().and_then(Value::as_str)==Some(answer),format!("BESTMOVE_PV_NOT_ALIGNED {ordinal} {key}"))?;
    let p7value=v(p7arm,"p7_value")?;
    let tt=v(p7arm,"p6s1")?;
    guard(v(tt,"target_valid")?.as_u64()==Some(1),"PRESELECTED_EDGE_NOT_VALID")?;
    guard(v(tt,"suppressed")?.as_u64().unwrap_or(999)<=1,"MULTIPLE_TT_SUPPRESSIONS")?;
    if let Some(prior_mode)=p6mode {
      let prior_name=format!("{see}__{prior_mode}");
      let baseline=v(v(original,"four_native_cold_conditions")?,&prior_name)?;
      guard(v(p7arm,"UCI")?==v(baseline,"UCI")?,format!("P6_NATIVE_CATEGORICAL_SCORE_PV_NODE_DRIFT {ordinal} {key}"))?;
      guard(v(p7arm,"p6s1")?==v(baseline,"target")?,format!("P6_EXACT_TT_TARGET_CONTINUITY_DRIFT {ordinal} {key}"))?;
      guard(v(p7value,"matched_score_deliveries")?.as_u64()==Some(0),"CONTROL_DELIVERED_P7_SCORE")?;
    } else {
      guard(v(p7value,"mode")?.as_u64()==Some(1),"P7_VALUE_MODE_WRONG")?;
      guard(v(p7value,"matched_score_deliveries")?.as_u64()==Some(1),"RETURN_ALPHA_NOT_DELIVERED_EXACTLY_ONCE")?;
      guard(v(p7value,"numeric_changes")?.as_u64()==Some(1),"NUMERIC_REPLACEMENT_WAS_NULL")?;
      guard(v(p7value,"delivered_value")?.as_i64()==Some(130),"RETURN_VALUE_NOT_ALPHA_130")?;
      guard(v(p7value,"alpha")?.as_i64()==Some(130)&&v(p7value,"beta")?.as_i64()==Some(131),"READER_AB_WINDOW_CHANGED")?;
      let orig=if ordinal==2{14}else{29};
      guard(v(p7value,"old_value")?.as_i64()==Some(orig),"ORIGINAL_TT_RETURN_VALUE_DIFFERENT")?;
      guard(v(tt,"suppressed")?.as_u64()==Some(0),"SCORE_ONLY_ARM_ACTUALLY_BLOCKED_RETURN")?;
    }
    matrix.push(json!({"see":see,"regime":mode,"move":answer}));
   }
  }
  let off=|regime:&str|->Result<&str,String>{mv(arm(x,&format!("OFF__{regime}"))?)};
  let on=|regime:&str|->Result<&str,String>{mv(arm(x,&format!("ROOT_OBJECT_SEE_UNMASK__{regime}"))?)};
  let actual=[off("IDENTITY")?!=on("IDENTITY")?,
              off("RETURN_ALPHA")?!=on("RETURN_ALPHA")?,
              off("BLOCK_EXACT_ONCE")?!=on("BLOCK_EXACT_ONCE")?];
  let expected=if ordinal==2{[false,true,true]}else{[true,false,false]};
  guard(actual==expected,format!("BINARY_PROJECTION_DRIFT {ordinal}"))?;
  if ordinal==2{
   guard(off("IDENTITY")?==on("IDENTITY")?
      && off("RETURN_ALPHA")?==on("BLOCK_EXACT_ONCE")?
      && on("RETURN_ALPHA")?==off("BLOCK_EXACT_ONCE")?
      && off("RETURN_ALPHA")?!=off("BLOCK_EXACT_ONCE")?,
      "P7_CASE2_ARM_DIRECTION_REVERSAL_NOT_PRESENT")?;
  } else {
   for see in ["OFF","ROOT_OBJECT_SEE_UNMASK"] {
    guard(mv(arm(x,&format!("{see}__RETURN_ALPHA"))?)?
         ==mv(arm(x,&format!("{see}__BLOCK_EXACT_ONCE"))?)?,
         "P7_CASE29_VALUE_CONTINUATION_ROOT_RESULTS_NOT_EQUAL")?;
   }
  }
  report.push(json!({"ordinal":ordinal,"root_fen_sha256":v(x,"root_fen_sha256")?,
       "same_binary_projection_but_different_arm_local_outcomes":ordinal==2,
       "binary_response":[actual[0] as u8,actual[1] as u8,actual[2] as u8],
       "categorical_outcomes":matrix}));
 }
 Ok(json!({"schema":"c3x015-P7-independent-Rust-categorical-potential-outcome-court-v1",
  "status":"P7_24_NATIVE_CAT_OUTCOME_ROWS_AND_P6_REGRESSION_SCOPED_PASS",
  "P7_original_byte_sha256":P7_SHA,"P6_original_byte_sha256":P6_SHA,
  "original_source_game_worlds":2,"native_processes":24,"cold_pairs":12,
  "categorical_response_projection_nonidentifiability_world":2,
  "opposite_S_response_but_same_binary_state":true,
  "cases":report,"not_proven":["Natural indirect mediation","Other engine transfer","NNUE latent concept"]}))
}
fn run()->Result<(),String>{
 let args:Vec<String>=env::args().collect();
 guard(args.len()==4,"USAGE: p7_matrix P7_RESULT.json P6_RESULT.json OUT.json")?;
 let p7=read(&args[1],P7_SHA)?;
 let p6=read(&args[2],P6_SHA)?;
 let out=rule(&p7,&p6)?;
 // A bounded semantic mutation after SHA verification MUST be rejected.
 let mut corrupt=p7.clone();
 corrupt["cases"][0]["cells"]["OFF__RETURN_ALPHA"]["UCI"]["bestmove"]=json!("a1a1");
 guard(rule(&corrupt,&p6).is_err(),"IN_MEMORY_P7_CATEGORICAL_TAMPER_ACCEPTED")?;
 fs::write(&args[3],format!("{}\n",serde_json::to_string_pretty(&out).unwrap()))
   .map_err(|e|e.to_string())?;
 println!("C3X015_RUST_P7_CATEGORICAL_DIRECTIONAL_OUTCOME_INDEPENDENT_PASS");
 println!("{}",serde_json::to_string(&out).unwrap());
 Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("C3X015_RUST_P7_COURT_FAIL {e}");process::exit(2)}}
