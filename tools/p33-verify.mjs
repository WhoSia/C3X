import fs from 'node:fs';
const [,,path]=process.argv;
if(!path) throw new Error('usage: node p33-verify.mjs adjudication.json');
const x=JSON.parse(fs.readFileSync(path,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error(m)};
ok(x.schema==='c3x-p33-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.4-P33','stage');
ok(x.repeat_controls.passed===x.repeat_controls.total,'repeat-controls');
ok(x.explanation_verification.unsupported_rendered_claims===0,'unsupported-claim-count');
let nec=0,both=0,prod=0;
const allowed=new Set(['LINEAGE_CORRESPONDENCE','CONDITIONAL_NECESSITY','CONDITIONAL_SUFFICIENCY','PRODUCTIVE_SEARCH_TRACE','PV_DIVERGENCE','CHESS_ATOMIC_CONTRAST','LIMITATION']);
for(const z of x.certificates){
  ok(z.verification?.pass===true,'certificate-verification');
  const c=z.case;let n=false,s=false,p=false;
  for(const a of z.ast){
    ok(allowed.has(a.type),'unknown-ast');
    if(a.type==='CONDITIONAL_NECESSITY'){n=true;ok(c.minimal_branch_novel_removal.status==='CERTIFIED','necessity-support');ok(a.set_size===c.minimal_branch_novel_removal.address_ids.length,'necessity-size')}
    if(a.type==='CONDITIONAL_SUFFICIENCY'){s=true;ok(c.minimal_branch_novel_retaining.status==='CERTIFIED','sufficiency-support');ok(a.set_size===c.minimal_branch_novel_retaining.address_ids.length,'sufficiency-size')}
    if(a.type==='PRODUCTIVE_SEARCH_TRACE'){p=true;ok(c.productive_search_trace_witness===true,'productive-support');ok(a.operational_only===true,'productive-boundary')}
  }
  if(n)nec++;if(n&&s)both++;if(p)prod++;
}
ok(nec===x.certified.conditional_necessity,'necessity-count');
ok(both===x.certified.conditional_necessity_and_sufficiency,'both-count');
ok(prod===x.certified.productive_search_trace_witnesses,'productive-count');
console.log('P33_JS_VERIFY_PASS',x.verdict,'cases',x.primary_cases,'both',both,'productive',prod);
