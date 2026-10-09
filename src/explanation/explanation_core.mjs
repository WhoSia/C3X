export const LEVEL = Object.freeze({GEOMETRY:"GEOMETRY",LEGAL:"LEGAL",FORCING:"FORCING",OPERATOR:"OPERATOR",CAUSAL:"CAUSAL"});
const known = new Set(["pin","skewer","interference","deflection","removal_of_defender","fork","clearance","decoy","pawn_structure","king_activity","space","king_safety","sacrifice","zugzwang","mating_net"]);
function gate(ok,why){if(!ok)throw Error("C3X017_FAIL_CLOSED_"+why);}
export function explain(e){
 gate(e && e.schema==="c3x017-explanation-v1","SCHEMA");
 gate(typeof e.case_id==="string" && /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(e.move),"MOVE");
 gate(Array.isArray(e.motifs),"MOTIFS");
 const result=["# Chess evidence: "+e.case_id,"Move: "+e.move,"## Candidate interpretation"];
 for(const m of e.motifs){
  gate(known.has(m.name),"UNKNOWN_MOTIF");
  gate([LEVEL.GEOMETRY,LEVEL.LEGAL,LEVEL.FORCING].includes(m.level),"MOTIF_LEVEL");
  if(m.level===LEVEL.FORCING)gate(m.certificate?.all_legal_replies===true && Number.isInteger(m.certificate?.horizon) && m.certificate.horizon>0 && Array.isArray(m.certificate?.refutations) && m.certificate.refutations.length===0,"FORCING_CERTIFICATE");
  result.push("- "+m.name+": "+(m.level===LEVEL.GEOMETRY?"geometry only, tactic not proved":m.level===LEVEL.LEGAL?"legal moves and replies observed, winning payoff not proved":"all legal replies audited for specified finite horizon"));
 }
 result.push("## Engine observation");
 if(e.engine){
  gate(e.engine.depth>0 && typeof e.engine.build==="string","ENGINE_BUILD");
  result.push("Stockfish build "+e.engine.build+" depth "+e.engine.depth+" selected "+e.engine.bestmove+".");
 }else result.push("No verified engine source result attached.");
 result.push("## Counterfactual search mechanism");
 if(e.counterfactual){
  const c=e.counterfactual;
  gate(c.source_site && c.actual_contact===true && c.sham_equal===true && c.cold_replay===true && c.original_source_baseline===true,"CAUSAL_GATE");
  const changes=[];
  if(c.before.bestmove!==c.after.bestmove)changes.push("bestmove");
  if(c.before.cp!==c.after.cp)changes.push("score");
  if(c.before.nodes!==c.after.nodes)changes.push("nodes");
  result.push("At "+c.source_site+": changed "+(changes.join(", ")||"no tracked final output")+"; exact source-site intervention with controls.");
 }else result.push("No source intervention certificate.");
 gate(!e.natural_tt_mediation || (e.natural_tt_mediation.writer && e.natural_tt_mediation.reader && e.natural_tt_mediation.path_specific_counterfactual),"TT_MEDIATION_UNPROVED");
 result.push("## What cannot yet be claimed");
 result.push("- A geometric motif proves a winning tactic or a brilliant move.");
 result.push("- A changed search result proves the engine internally represents a human tactical concept.");
 if(!e.natural_tt_mediation)result.push("- A single natural TT path necessarily mediated the move.");
 result.push("- This local effect transports across depth, engines or game histories.");
 return result.join("\n")+"\n";
}
