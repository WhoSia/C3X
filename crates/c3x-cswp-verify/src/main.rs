//! Independent C3X 0.15 P6 native TT single-edge evidence verifier.
//! Does not execute or trust the experiment's Python verdicts.
//! Checks byte-identical source receipts and row-level counters and outcomes.
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::HashSet;
use std::env;
use std::fs;
use std::process;

const P2_SHA: &str = "e930f0b489301c656690d09f4821583a28eead04e43382b545bda35b71279256";
const P6S0_SHA: &str = "0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1";
const P6S1_SHA: &str = "c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11";
const R2_SHA: &str = "1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534";

fn need(condition: bool, message: impl Into<String>) -> Result<(), String> {
    if condition { Ok(()) } else { Err(message.into()) }
}
fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str, String> {
    v.get(key).and_then(Value::as_str).ok_or_else(|| format!("missing string: {key}"))
}
fn num(v: &Value, key: &str) -> Result<u64, String> {
    v.get(key).and_then(Value::as_u64).ok_or_else(|| format!("missing unsigned integer: {key}"))
}
fn array<'a>(v: &'a Value, key: &str) -> Result<&'a [Value], String> {
    v.get(key).and_then(Value::as_array).map(|a| a.as_slice())
        .ok_or_else(|| format!("missing array: {key}"))
}
fn open_sha(path: &str, expected: &str) -> Result<Value, String> {
    let raw = fs::read(path).map_err(|e| format!("cannot read {path}: {e}"))?;
    let hash = format!("{:x}", Sha256::digest(&raw));
    need(hash == expected, format!("BYTE_SHA_MISMATCH {path}: {hash} expected {expected}"))?;
    serde_json::from_slice(&raw).map_err(|e| format!("JSON_PARSE_FAIL {path}: {e}"))
}
fn best(row: &Value, name: &str) -> Result<String, String> {
    let condition = row.get("four_native_cold_conditions")
        .and_then(|v| v.get(name)).ok_or_else(|| format!("missing arm {name}"))?;
    let uci = condition.get("UCI").ok_or_else(|| format!("missing UCI {name}"))?;
    let answer = text(uci, "bestmove")?.to_owned();
    let pv = array(uci, "pv")?;
    need(pv.first().and_then(Value::as_str) == Some(answer.as_str()),
        format!("BESTMOVE_NOT_FIRST_PV {name}"))?;
    need(num(uci,"nodes")? > 0, format!("ZERO_NODES {name}"))?;
    Ok(answer)
}
fn arm<'a>(row: &'a Value, name: &str) -> Result<&'a Value, String> {
    row.get("four_native_cold_conditions")
        .and_then(|a| a.get(name))
        .ok_or_else(||format!("ARM_MISSING {name}"))
}
fn verify(p2: &Value, target: &Value, p6: &Value) -> Result<Value,String> {
    need(text(p2,"source_SHA256")? == R2_SHA,"P2_SOURCE_NOT_R2")?;
    need(text(target,"source_sha256")? == R2_SHA,"P6S0_SOURCE_NOT_R2")?;
    need(text(p6,"source_r2_sha256")? == R2_SHA,"P6S1_SOURCE_NOT_R2")?;
    need(text(p6,"P2_prior_SHA256")? == P2_SHA,"P6S1_PRIOR_P2_ID_MISMATCH")?;
    need(text(p6,"P6S0_target_sha256")? == P6S0_SHA,"P6S1_PRESEALED_TARGET_ID_MISMATCH")?;
    let p2rows=array(p2,"pin_worlds")?;
    let targets=array(target,"all64_targets")?;
    let p6rows=array(p6,"all_64_native_four_cell_interventions")?;
    need(p2rows.len()==64 && targets.len()==64 && p6rows.len()==64,"NOT_64_GAME_ROWS")?;
    let mut seen_fens=HashSet::new();
    let mut seen_games=HashSet::new();
    let mut originally_flipped=0u64;
    let mut blocked_flipped=0u64;
    let mut flip_effect_mismatch=0u64;
    let mut off_suppressed=0u64;
    let mut see_suppressed=0u64;
    let mut joint_exposed=0u64;
    let mut no_target=0u64;
    let mut target_eligible=0u64;
    let mut off_root_changes=0u64;
    let mut see_root_changes=0u64;
    let mut cases=Vec::new();
    let mut negative=Vec::new();
    let pairs=[
        ("OFF__ALLOW","OFF__BLOCK_EXACT_ONCE"),
        ("ROOT_OBJECT_SEE_UNMASK__ALLOW","ROOT_OBJECT_SEE_UNMASK__BLOCK_EXACT_ONCE")
    ];
    for i in 0..64 {
        let a=&p2rows[i];let t=&targets[i];let b=&p6rows[i];
        let ordinal=(i+1) as u64;
        for d in [a,t,b] {
            need(num(d,"ordinal")?==ordinal,format!("ORDINAL_CHANGED {ordinal}"))?;
            need(text(d,"fen_sha256")?==text(a,"fen_sha256")?,format!("FEN_CHANGED {ordinal}"))?;
        }
        need(text(t,"game_sha256")?==text(a,"game_sha256")?
          && text(b,"source_game_sha256")?==text(a,"game_sha256")?,
          format!("GAME_HISTORY_ID_CHANGED {ordinal}"))?;
        need(a["law"]==t["original_pin_law"] && a["law"]==b["law"],
           format!("CHESS_LAW_TYPE_DRIFT {ordinal}"))?;
        need(seen_fens.insert(text(a,"fen_sha256")?.to_owned()),"REPEATED_FEN")?;
        need(seen_games.insert(text(a,"game_sha256")?.to_owned()),"REPEATED_GAME")?;
        need(b["presealed_tt_target"]==t["target"],format!("TARGET_REWRITTEN_AFTER_OUTCOME {ordinal}"))?;
        let eligible=num(&t["target"],"eligible")?;
        need(eligible <= 1,"BAD_TARGET_ELIGIBLE")?;
        target_eligible+=eligible;
        if eligible==0 {no_target+=1}
        need(b["four_native_cold_conditions"].as_object().map(|x|x.len())==Some(4),
            format!("MISSING_NATIVE_ARM {ordinal}"))?;
        for (allow,blocked) in pairs {
            let ac=arm(b,allow)?;let bc=arm(b,blocked)?;
            let at=&ac["target"];let bt=&bc["target"];
            need(num(at,"mode")?==0 && num(bt,"mode")?==1,format!("REGIME_SWAP {ordinal}"))?;
            need(num(at,"suppressed")?==0 && num(bt,"suppressed")?<=1,
                 format!("MORE_THAN_ONE_TT_RETURN_BLOCKED {ordinal}"))?;
            need(num(bt,"suppressed")?<=eligible,
                 format!("BLOCKED_UNREGISTERED_TT_RETURN {ordinal}"))?;
            need(num(at,"target_valid")?==eligible && num(bt,"target_valid")?==eligible,
                 format!("TARGET_NOT_SAME_IN_ARMS {ordinal}"))?;
            if eligible==1 {
                let expected_key=num(&t["target"],"key")?;
                let expected_seq=num(&t["target"],"writer_seq")?;
                need(num(at,"target_key")?==expected_key && num(bt,"target_key")?==expected_key
                    && num(at,"target_seq")?==expected_seq && num(bt,"target_seq")?==expected_seq,
                    format!("WRITER_TARGET_ID_DRIFT {ordinal}"))?;
            }
            need(num(ac,"pre_source_first_key")?==num(bc,"pre_source_first_key")?,
                 format!("SOURCE_PREFIX_FIRST_CANDIDATE_KEY_CHANGED {ordinal}"))?;
            if eligible==0 {
                need(ac["UCI"]==bc["UCI"], format!("NEGATIVE_NO_TARGET_CHANGED {ordinal}"))?;
            }
        }
        let normal_off=best(b,"OFF__ALLOW")?;
        let normal_see=best(b,"ROOT_OBJECT_SEE_UNMASK__ALLOW")?;
        let block_off=best(b,"OFF__BLOCK_EXACT_ONCE")?;
        let block_see=best(b,"ROOT_OBJECT_SEE_UNMASK__BLOCK_EXACT_ONCE")?;
        need(arm(b,"OFF__ALLOW")?["UCI"]==a["native_pristine_OFF"],
             format!("P2_PRISTINE_OFF_NATIVE_UCI_CHANGED {ordinal}"))?;
        need(arm(b,"ROOT_OBJECT_SEE_UNMASK__ALLOW")?["UCI"]==a["native_ROOT_SEE_UNMASK"],
             format!("P2_GUARDED_SEE_NATIVE_UCI_CHANGED {ordinal}"))?;
        need(arm(b,"OFF__ALLOW")?["UCI"]==t["original_OFF_native_UCI"],
             format!("P6S0_BASELINE_OFF_CHANGED {ordinal}"))?;
        let norm=u64::from(normal_off!=normal_see);
        let blocked=u64::from(block_off!=block_see);
        need(num(b,"original_p2_SEE_root_flip")?==norm &&
             num(b,"regime_OFF_rootflip")?==norm &&
             num(b,"regime_SEE_rootflip")?==blocked &&
             num(b,"SEEsensitivity_under_one_edge_block")?==blocked,
             format!("UNTRUSTED_ROW_CAUSAL_EFFECT_SUMMARY {ordinal}"))?;
        let off_del=num(arm(b,"OFF__BLOCK_EXACT_ONCE")?.get("target").unwrap(),"suppressed")?;
        let see_del=num(arm(b,"ROOT_OBJECT_SEE_UNMASK__BLOCK_EXACT_ONCE")?.get("target").unwrap(),"suppressed")?;
        need(num(b,"OFF_delivered")?==off_del && num(b,"SEE_delivered")?==see_del,
             format!("DISAGREE_ACTUAL_SUPPRESSION_COUNT {ordinal}"))?;
        off_suppressed+=off_del;
        see_suppressed+=see_del;
        joint_exposed+=u64::from(off_del==1 && see_del==1);
        originally_flipped+=norm;blocked_flipped+=blocked;
        flip_effect_mismatch+=u64::from(norm!=blocked);
        off_root_changes+=u64::from(normal_off!=block_off);
        see_root_changes+=u64::from(normal_see!=block_see);
        if norm!=blocked {
            cases.push(json!({"ordinal":ordinal,"law":a["law"],
                "normal_off":normal_off,"normal_see":normal_see,
                "one_TT_block_off":block_off,"one_TT_block_see":block_see,
                "off_edge_delivered":off_del,"see_edge_delivered":see_del,
                "selected_writer_class":num(&t["target"],"writer_tag")?,
                "selected_stored_bound":num(&t["target"],"stored_bound")?,
                "selected_full_key":num(&t["target"],"key")?}));
        }
        if eligible==0 {negative.push(ordinal)}
    }
    let check_counts=[
      ("presealed_target_eligible",target_eligible),("exact_matching_OFF_suppressed_worlds",off_suppressed),
      ("exact_matching_SEE_suppressed_worlds",see_suppressed),
      ("same_presealed_edge_suppressed_in_both_worlds",joint_exposed),
      ("original_SEE_root_change_count",originally_flipped),
      ("exact_edge_block_SEE_root_change_count",blocked_flipped),
      ("one_edge_changes_OFF_root_move",off_root_changes),
      ("one_edge_changes_SEE_root_move",see_root_changes)];
    for (name,actual) in check_counts {
       need(num(p6,name)?==actual,format!("TOPLINE_TAMPER_{name}: recomputed={actual}"))?;
    }
    need(target_eligible==51 && no_target==13 && off_suppressed==51 && see_suppressed==44
         && joint_exposed==44,"EXPECTED_PRESEALED_TARGET_DELIVERY_COUNTS_CHANGED")?;
    need(originally_flipped==11 && blocked_flipped==11 && flip_effect_mismatch==2
         && off_root_changes==1 && see_root_changes==1,"CAUSAL_CONTRAST_NO_LONGER_TWO_OPPOSING_CASES")?;
    need(cases.iter().map(|v|v["ordinal"].as_u64().unwrap()).collect::<Vec<_>>()==vec![2,29],
        "TARGETED_CAUSAL_CASES_NOT_2_AND_29")?;
    need(num(p6,"original_native_processes")?==512 &&
         text(p6,"all_256_cold_conditions_exact")?=="256/256" &&
         text(p6,"all_P2_allow_conditions_identical")?=="64/64",
         "TECHNICAL_REPEAT_COUNTS_CHANGED")?;
    Ok(json!({
      "schema":"c3x-015-independent-rust-p6s1-verifier-v1",
      "source_of_truth":"original native JSON bytes, crossmatched P2 and P6S0; never trusts P6S1 summary alone",
      "status":"INDEPENDENT_ROWS_AND_SHA_PASS_SCOPED",
      "prior_p2_sha256":P2_SHA,"prior_p6s0_source_only_sha256":P6S0_SHA,
      "p6s1_native_json_sha256":P6S1_SHA,"original_r2_source_sha256":R2_SHA,
      "rows_checked":64,"distinct_games":seen_games.len(),"distinct_fens":seen_fens.len(),
      "original_SEE_root_flips":originally_flipped,
      "single_edge_block_SEE_root_flips":blocked_flipped,
      "change_in_SEE_response_identity_worlds":flip_effect_mismatch,
      "targeted_TT_return_eligible":target_eligible,"no_target_negative_controls":no_target,
      "exactly_once_suppressed_off":off_suppressed,"exactly_once_suppressed_see":see_suppressed,
      "edge_delivered_in_both":joint_exposed,
      "TT_block_changed_OFF_root_moves":off_root_changes,
      "TT_block_changed_SEE_root_moves":see_root_changes,
      "opposing_bounded_cases":cases,
      "negative_no_target_ordinals":negative,
      "limitations":["Only original P2/P6S0/P6S1 data consistency independently verified",
           "Native experiment correctness and exact four-way cold duplicates cannot be inferred from summarized JSON alone",
           "One exact return influences two bounded software runs; natural mediation and general chess strategy remain unproven",
           "Frozen P1 C1 accuracy failure is not changed by this verifier"]}))
}
fn run() -> Result<(),String> {
    let a:Vec<String>=env::args().collect();
    need(a.len()==5,"usage: c3x-cswp-verify P2.json P6S0.json P6S1.json OUTPUT_RECEIPT.json")?;
    let p2=open_sha(&a[1],P2_SHA)?;
    let t=open_sha(&a[2],P6S0_SHA)?;
    let p6=open_sha(&a[3],P6S1_SHA)?;
    let receipt=verify(&p2,&t,&p6)?;
    fs::write(&a[4],format!("{}\n",serde_json::to_string_pretty(&receipt).unwrap()))
         .map_err(|e|format!("writing receipt: {e}"))?;
    println!("C3X015_RUST_INDEPENDENT_P6S1_ROW_BY_ROW_SHA_AND_NEGATIVE_CONTROL_PASS");
    println!("C3X015_RUST_SUMMARY {}",serde_json::to_string(&receipt).unwrap());
    Ok(())
}
fn main() {
  if let Err(e)=run(){eprintln!("C3X015_RUST_COURT_FAIL {e}");process::exit(2)}
}
#[cfg(test)]
mod tests {
 use super::*;
 #[test] fn checksum_known_vector(){
  assert_eq!(format!("{:x}",Sha256::digest(b"abc")),
   "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
 }
 #[test] fn test_row_guard(){
   assert!(need(false,"negative control").is_err());
   assert!(need(true,"okay").is_ok());
 }
 #[test] fn absent_arm_is_fail_closed(){
    let a=json!({"four_native_cold_conditions":{}});
    assert!(arm(&a,"OFF__ALLOW").is_err());
 }
}
