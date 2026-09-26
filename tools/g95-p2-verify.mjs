import fs from 'node:fs';

const [,,path]=process.argv;
if(!path)throw new Error('usage: node g95-p2-verify.mjs adjudication.json');
const x=JSON.parse(fs.readFileSync(path,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error(m)};

ok(x.schema==='c3x-g95-p2-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P2','stage');
ok(x.explanation_verification.unsupported_rendered_claims===0,'unsupported');
ok(x.explanation_verification.failed===0,'explanation-verification');

const allowed=new Set([
 'DISCOVERY_CONTEXT_SUPPORT_LIMITED_HOLD',
 'NO_PORTABLE_CONTEXT_BASIS_HOLD',
 'PORTABLE_FIELD_HOLD_ARCHITECTURE_DIAGNOSTIC_ONLY',
 'PORTABLE_CONTEXT_FIELD_SCOPE_INSUFFICIENT_HOLD',
 'PORTABLE_CONTEXT_FIELD_HELDOUT_FALSIFIED',
 'PORTABLE_CONTEXT_INDEXED_CAUSAL_FIELD_HELDOUT_CERTIFIED',
 'EXPLANATION_SCOPE_VERIFICATION_FAIL'
]);
ok(allowed.has(x.verdict),'verdict');

const mins=new Set(x.minimal_portable_basis_ids||[]);
if(x.selected_basis_id!==null&&x.selected_basis_id!==undefined){
  ok(mins.has(x.selected_basis_id),'selected-not-discovery-minimal');
  ok((x.selected_coordinates||[]).every(c=>!String(c).startsWith('arch:')),'architecture-in-primary-basis');
}
ok(x.heldout_scope.target_fields_consulted===false,'scope-target-leak');

const forbiddenProfileKeys=new Set([
 'root_change','counterfactual_bestmove','counterfactual_score','counterfactual_wdl','counterfactual_pv',
 'parent_bestmove','parent_score','parent_wdl','parent_pv','target'
]);
const forbiddenContextKeys=/^(engine_id|fen|position_hash|case_role|address_id|full_key|root_change|counterfactual_|learned_|world_id)/i;
for(const z of x.certificates||[]){
  const p=z.profile;
  for(const k of Object.keys(p))ok(!forbiddenProfileKeys.has(k),'profile-target-field:'+k);
  for(const k of Object.keys(p.context||{}))ok(!forbiddenContextKeys.test(k),'forbidden-context:'+k);
  for(const k of Object.keys(p.architecture_context||{}))ok(/^arch_/.test(k),'bad-architecture-key:'+k);

  const st=z.status;
  const target=!!z.target.root_change;
  if(st==='CERTIFIED_ROOT_CHANGE')ok(target,'cert-root-target');
  if(st==='CERTIFIED_NO_ROOT_CHANGE')ok(!target,'cert-no-root-target');
  if(st==='ABSTAIN_UNSEEN_CONTEXT')ok(z.prediction.status==='ABSTAIN_UNSEEN_CONTEXT','abstain-support');
  if(st==='CONTRADICTED_CONTEXT_CELL')ok(z.prediction.status!=='ABSTAIN_UNSEEN_CONTEXT','contradiction-seen');
}

const d=x.discovery_support||{};
const hasPortable=(x.minimal_portable_basis_ids||[]).length>0;
const hasArch=(x.architecture_diagnostic_basis_ids||[]).length>0;
const scopePass=!!x.heldout_scope.coverage?.gate_pass;
const hv=x.heldout_transport||{};
const contradictions=(hv.contradictions||[]).length;
const mixed=(hv.mixed_heldout_cells||[]).length;
let expected;
if(!d.pass) expected='DISCOVERY_CONTEXT_SUPPORT_LIMITED_HOLD';
else if(!hasPortable) expected=hasArch?'PORTABLE_FIELD_HOLD_ARCHITECTURE_DIAGNOSTIC_ONLY':'NO_PORTABLE_CONTEXT_BASIS_HOLD';
else if(!scopePass) expected='PORTABLE_CONTEXT_FIELD_SCOPE_INSUFFICIENT_HOLD';
else if(contradictions||mixed||hv.verdict==='CONTEXT_FIELD_TRANSPORT_FALSIFIED') expected='PORTABLE_CONTEXT_FIELD_HELDOUT_FALSIFIED';
else expected='PORTABLE_CONTEXT_INDEXED_CAUSAL_FIELD_HELDOUT_CERTIFIED';
ok(x.verdict===expected,'verdict-ladder:'+expected+' got '+x.verdict);

if(hasPortable){
  ok(Number.isInteger(x.minimum_portable_cardinality),'minimum-cardinality');
  for(const bid of x.minimal_portable_basis_ids)ok(String(bid).startsWith('P:'),'portable-basis-id');
}
console.log('G95_P2_JS_VERIFY_PASS',x.verdict,'basis',x.selected_basis_id);
