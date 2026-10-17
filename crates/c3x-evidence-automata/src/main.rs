//! C3X P7 development-only, fail-closed compiler of *observed* SF16 P8-P14 text events.
//! It never certifies natural mediation, independently adjudicated chess semantics,
//! or pedagogical benefit. Full source/raw-log authenticity remains external.
use serde::{Deserialize, Serialize};
use std::{collections::{BTreeMap, BTreeSet}, env, fs, process};

#[derive(Debug, Deserialize)]
struct Input {
    schema: String,
    run_id: String,
    #[serde(default)] source_receipt: Option<String>,
    lines: Vec<String>,
}
#[derive(Debug, Serialize)]
struct Event {
    line_number: usize,
    family: String,
    kind: String,
    call_id: Option<u64>,
    parent_id: Option<u64>,
    root_id: Option<u64>,
    serial: Option<u64>,
    child_id: Option<u64>,
    fields: BTreeMap<String, String>,
}
#[derive(Debug, Serialize)]
struct Verdict {
    schema: &'static str,
    run_id: String,
    source_receipt: Option<String>,
    source_authentication: &'static str,
    summary: BTreeMap<String, usize>,
    censored: bool,
    observed_linked_source_events: usize,
    observed_parent_assignments: usize,
    observed_best_assignments: usize,
    unlinked_parent_assignments: usize,
    joined_triples: usize,
    orphan_best_assignments: usize,
    evidence_level: &'static str,
    certified_claims: Vec<&'static str>,
    prohibited_claims: Vec<&'static str>,
    events: Vec<Event>,
}

fn parse_uint(f: &BTreeMap<String,String>, key: &str) -> Option<u64> {
    f.get(key).and_then(|x| x.parse().ok())
}
fn parse_line(line: &str, number: usize) -> Result<Option<Event>, String> {
    let Some(body) = line.strip_prefix("info string ") else { return Ok(None); };
    let mut parts = body.split_whitespace();
    let family = parts.next().unwrap_or("");
    if !matches!(family, "c3x025_p8" | "c3x025_p11" | "c3x025_p12" | "c3x025_p13" | "c3x025_p14" | "c3x_p6" | "c3x_i10p6") { return Ok(None); }
    let mut fields = BTreeMap::new();
    for token in parts {
        let Some((k,v))=token.split_once('=') else { continue; };
        if fields.insert(k.to_string(),v.to_string()).is_some(){
            return Err(format!("DUPLICATE_FIELD at line {number}: {k}"));
        }
    }
    let kind = fields.get("kind").or_else(||fields.get("event")).cloned().unwrap_or_else(||"UNKNOWN".into());
    Ok(Some(Event {line_number:number, family:family.to_string(), kind,
        call_id:parse_uint(&fields,"call_id"), parent_id:parse_uint(&fields,"parent_id"),
        root_id:parse_uint(&fields,"root_id"), serial:parse_uint(&fields,"serial"),
        child_id:parse_uint(&fields,"child_id"), fields}))
}
fn compile(input: Input) -> Result<Verdict,String> {
    if input.schema != "c3x-p7-raw-uci-v1" || input.run_id.trim().is_empty() {
        return Err("SCHEMA_OR_RUN_ID_INVALID".into());
    }
    let mut events=Vec::new();let mut summary=BTreeMap::new();let mut seen=BTreeSet::new();
    let mut censored=false;
    for (i,line) in input.lines.iter().enumerate(){
        let Some(e)=parse_line(line,i+1)? else {continue};
        if e.kind.contains("CENSORED") || e.kind.contains("CENSOR") || line.contains("CENSORED") {
            censored=true;
        }
        *summary.entry(format!("{}:{}",e.family,e.kind)).or_insert(0)+=1;
        if e.family=="c3x025_p12" && e.kind=="SOURCE_EVENT" {
            let (Some(call),Some(root),Some(serial))=(e.call_id,e.root_id,e.serial) else {
                return Err(format!("SOURCE_EVENT_IDENTITY_MISSING line {}",e.line_number));
            };
            if call==0 || root==0 || serial==0 || !seen.insert((call,serial)) {
                return Err(format!("SOURCE_EVENT_IDENTITY_COLLISION line {}",e.line_number));
            }
        }
        events.push(e);
    }
    // Source event identity and structural parent links are typed as observed
    // facts only. Their occurrence alone never establishes a natural mediation.
    let linked=events.iter().filter(|e|e.family=="c3x025_p12" && e.kind=="SOURCE_EVENT"
        && e.call_id.is_some() && e.parent_id.is_some() && e.root_id.is_some()).count();
    let parents: Vec<_>=events.iter().filter(|e|e.family=="c3x025_p13" && e.kind=="Q_DIRECT_PARENT_ASSIGN").collect();
    let bests: Vec<_>=events.iter().filter(|e|e.family=="c3x025_p13" && e.kind=="Q_BEST_VALUE_ASSIGNED").collect();
    // A chain certificate requires exact child/parent/root identity across the
    // SOURCE_EVENT -> Q_DIRECT_PARENT_ASSIGN -> Q_BEST_VALUE_ASSIGNED edges.
    // Count-based co-occurrence alone is NEVER a linked chain.
    let mut keys=BTreeSet::new();
    for e in events.iter().filter(|e|e.family=="c3x025_p12" && e.kind=="SOURCE_EVENT") {
        if let (Some(c),Some(p),Some(r))=(e.call_id,e.parent_id,e.root_id) {
            if c!=0 && p!=0 && r!=0 && c!=p { keys.insert((c,p,r)); }
        }
    }
    let mut parent_keys=BTreeSet::new();
    let mut missing=0;
    for e in &parents {
        match (e.child_id,e.parent_id,e.root_id) {
            (Some(c),Some(p),Some(r)) if c!=0 && p!=0 && r!=0 && c!=p => {
                if !keys.contains(&(c,p,r)) {missing+=1;}
                if !parent_keys.insert((c,p,r)) {return Err(format!("DUPLICATE_PARENT_EDGE line {}",e.line_number));}
            },
            _ => missing+=1,
        }
    }
    let mut best_keys=BTreeSet::new();
    let mut orphan_best=0;
    for e in &bests {
        match (e.child_id,e.parent_id,e.root_id) {
            (Some(c),Some(p),Some(r)) if c!=0 && p!=0 && r!=0 && c!=p => {
                if !parent_keys.contains(&(c,p,r)) {orphan_best+=1;}
                if !best_keys.insert((c,p,r)) {return Err(format!("DUPLICATE_BEST_EDGE line {}",e.line_number));}
            },
            _ => orphan_best+=1,
        }
    }
    let joined=best_keys.iter().filter(|k|parent_keys.contains(k) && keys.contains(k)).count();
    let level=if events.is_empty(){"UNIDENTIFIED"}
        else if censored{"CENSORED"}
        else if joined>0 {"STRUCTURAL_CHAIN_OBSERVED"}
        else{"PARTIAL"};
    let mut permitted=vec!["RECORDED_SOURCE_EVENTS_ONLY"];
    if linked>0 {permitted.push("OBSERVED_FRAME_IDENTITIES");}
    if !parents.is_empty() {permitted.push("OBSERVED_PARENT_ASSIGNMENTS");}
    if !bests.is_empty() {permitted.push("OBSERVED_BEST_VALUE_ASSIGNMENTS");}
    if joined>0 {permitted.push("EXACT_IDENTITY_STRUCTURAL_TRIPLE");}
    Ok(Verdict {schema:"c3x-p7-evidence-automata-v1",run_id:input.run_id,
        source_receipt:input.source_receipt,source_authentication:"EXTERNAL_BYTE_AND_SOURCE_ATTESTATION_REQUIRED",
        summary,censored,observed_linked_source_events:linked,
        observed_parent_assignments:parents.len(),observed_best_assignments:bests.len(),
        unlinked_parent_assignments:missing,joined_triples:joined,orphan_best_assignments:orphan_best,evidence_level:level,certified_claims:permitted,
        prohibited_claims:vec!["NATURAL_TT_SEE_ROOT_MEDIATION", "CHESS_SEMANTIC_VALIDITY", "PEDAGOGICAL_UTILITY", "ELO_IMPROVEMENT", "P7_INDEPENDENT_VALIDATION", "C3X_0_26_PROMOTION"],events})
}
fn main(){
    let args:Vec<_>=env::args().collect();
    if args.len()!=3 {eprintln!("usage: c3x-evidence-automata INPUT.json OUTPUT.json");process::exit(2)}
    let result=(||->Result<(),String>{
        let bytes=fs::read(&args[1]).map_err(|e|e.to_string())?;
        let input:Input=serde_json::from_slice(&bytes).map_err(|e|e.to_string())?;
        let output=compile(input)?;
        let rendered=serde_json::to_string_pretty(&output).map_err(|e|e.to_string())?;
        fs::write(&args[2],format!("{rendered}\n")).map_err(|e|e.to_string())?;
        Ok(())
    })();
    if let Err(e)=result{eprintln!("EVIDENCE_COMPILER_HOLD: {e}");process::exit(1)}
}
#[cfg(test)]
mod tests {
    use super::*;
    fn inp(lines: &[&str])->Input{ Input{schema:"c3x-p7-raw-uci-v1".into(),run_id:"dev".into(),source_receipt:None,lines:lines.iter().map(|x|x.to_string()).collect()} }
    #[test] fn missing_events_never_promote(){let v=compile(inp(&["bestmove e2e4"])).unwrap();assert_eq!(v.evidence_level,"UNIDENTIFIED");assert!(v.prohibited_claims.contains(&"NATURAL_TT_SEE_ROOT_MEDIATION"));}
    #[test] fn observed_structural_chain_not_mediation(){let v=compile(inp(&["info string c3x025_p12 kind=SOURCE_EVENT serial=4 call_id=2 parent_id=1 root_id=1", "info string c3x025_p13 kind=Q_DIRECT_PARENT_ASSIGN child_id=2 parent_id=1 root_id=1", "info string c3x025_p13 kind=Q_BEST_VALUE_ASSIGNED child_id=2 parent_id=1 root_id=1 final_root_mediation=0"])).unwrap();assert_eq!(v.evidence_level,"STRUCTURAL_CHAIN_OBSERVED");assert!(v.prohibited_claims.contains(&"NATURAL_TT_SEE_ROOT_MEDIATION"));}
    #[test] fn censor_demotes(){let v=compile(inp(&["info string c3x025_p8 kind=CENSORED", "info string c3x025_p12 kind=SOURCE_EVENT serial=2 call_id=3 parent_id=1 root_id=1"])).unwrap();assert_eq!(v.evidence_level,"CENSORED");}
    #[test] fn collision_fails_closed(){let x="info string c3x025_p12 kind=SOURCE_EVENT serial=1 call_id=2 parent_id=1 root_id=1";assert!(compile(inp(&[x,x])).is_err());}
    #[test] fn disconnected_triples_are_not_observed_chain(){
        let v=compile(inp(&["info string c3x025_p12 kind=SOURCE_EVENT serial=4 call_id=2 parent_id=1 root_id=1", "info string c3x025_p13 kind=Q_DIRECT_PARENT_ASSIGN child_id=3 parent_id=1 root_id=1", "info string c3x025_p13 kind=Q_BEST_VALUE_ASSIGNED child_id=3 parent_id=1 root_id=1"])).unwrap();
        assert_eq!(v.evidence_level,"PARTIAL");assert_eq!(v.joined_triples,0);assert_eq!(v.unlinked_parent_assignments,1);
    }
    #[test] fn mismatched_best_edge_cannot_promote(){
        let v=compile(inp(&["info string c3x025_p12 kind=SOURCE_EVENT serial=4 call_id=2 parent_id=1 root_id=1", "info string c3x025_p13 kind=Q_DIRECT_PARENT_ASSIGN child_id=2 parent_id=1 root_id=1", "info string c3x025_p13 kind=Q_BEST_VALUE_ASSIGNED child_id=2 parent_id=5 root_id=1"])).unwrap();
        assert_eq!(v.evidence_level,"PARTIAL");assert_eq!(v.orphan_best_assignments,1);
    }
    #[test] fn duplicate_parent_rejected(){let x="info string c3x025_p13 kind=Q_DIRECT_PARENT_ASSIGN child_id=2 parent_id=1 root_id=1";assert!(compile(inp(&[x,x])).is_err());}
    #[test] fn duplicate_fields_fail(){assert!(compile(inp(&["info string c3x025_p12 kind=SOURCE_EVENT kind=OTHER"])).is_err());}
}
