// C3X 0.17 source-event alignment court. Does not infer mediation from chronology.
export function parseEvent(line) {
  if (typeof line !== "string" || !line.startsWith("info string c3x017_root_event ")) throw Error("C3X017_WRONG_EVENT");
  const pairs=line.trim().split(/\s+/).slice(3);
  const e={};
  for (const p of pairs) {
    const at=p.indexOf("="); if(at<1) throw Error("C3X017_MALFORMED_EVENT");
    const k=p.slice(0,at),v=p.slice(at+1);
    if(k in e) throw Error("C3X017_DUPLICATE_FIELD");
    e[k]=k==="kind"?v:Number(v);
    if(k!=="kind" && (!Number.isSafeInteger(e[k]) || !Number.isFinite(e[k]))) throw Error("C3X017_NONINTEGER_EVENT");
  }
  if(!["candidate","window_enter","window_exit","after_sort"].includes(e.kind) || !Number.isInteger(e.seq) || !Number.isInteger(e.depth)) throw Error("C3X017_BAD_EVENT_SHAPE");
  const required=e.kind==="candidate"?["move","child_return","before","after","alpha","beta"]:["alpha","beta"];
  if(required.some(k=>!Number.isInteger(e[k])))throw Error("C3X017_INCOMPLETE_EVENT");
  return Object.freeze(e);
}
const eq=(a,b,k)=>a[k]===b[k];
export function compareRootEvents(a,b){
  if(!Array.isArray(a)||!Array.isArray(b))throw Error("C3X017_EXPECT_EVENT_ARRAYS");
  const baseline=a.map(x=>typeof x==="string"?parseEvent(x):x);
  const treated=b.map(x=>typeof x==="string"?parseEvent(x):x);
  const n=Math.min(baseline.length,treated.length);
  for(let i=0;i<n;i++){
    const x=baseline[i],y=treated[i];
    if(x.kind!==y.kind||x.depth!==y.depth||(x.kind==="candidate" && x.move!==y.move))
      return {first_retained_index:i,classification:"EVENT_ALIGNMENT_AMBIGUOUS",baseline:x,treatment:y,necessary_mediator_proven:false};
    for(const k of ["alpha","beta"])if(!eq(x,y,k))
      return {first_retained_index:i,classification:"ALPHA_BETA_WINDOW_CHANGED",baseline:x,treatment:y,necessary_mediator_proven:false};
    if(x.kind==="candidate"){
      if(x.child_return!==y.child_return)
        return {first_retained_index:i,classification:"CHILD_RETURN_CHANGED",rootStoredScoreChanged:x.after!==y.after,baseline:x,treatment:y,necessary_mediator_proven:false};
      if(x.after!==y.after||x.before!==y.before)
        return {first_retained_index:i,classification:"ROOT_STORED_SCORE_CHANGED",baseline:x,treatment:y,necessary_mediator_proven:false};
    } else if(x.kind==="after_sort"&& (x.first_move!==y.first_move||x.first_score!==y.first_score))
      return {first_retained_index:i,classification:"ROOT_RANKING_CHANGED",baseline:x,treatment:y,necessary_mediator_proven:false};
    else if(x.kind==="window_exit" && x.value!==y.value)
      return {first_retained_index:i,classification:"WINDOW_SEARCH_VALUE_CHANGED",baseline:x,treatment:y,necessary_mediator_proven:false};
  }
  return {first_retained_index:baseline.length===treated.length?null:n,
    classification:baseline.length===treated.length?"NO_RETAINED_DIFFERENCE":"ONE_SIDE_RETAINED_EVENT",
    necessary_mediator_proven:false};
}
export function ttMediationClaim(t){
 if(t?.writer_contact!==true || t?.reader_contact!==true || t?.path_specific_counterfactual!==true || t?.cold_sham_pass!==true)
  return {warrant:"HOLD",reason:"writer_reader_path_specific_intervention_not_complete"};
 return {warrant:"EVENT_SPECIFIC_PATH_EFFECT_SUPPORTED",reason:"path_specific_scope_only_not_universal"};
}
