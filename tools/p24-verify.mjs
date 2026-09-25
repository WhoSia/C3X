#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const [,, prePath, resultPath, reportPath] = process.argv;
if (!prePath || !resultPath || !reportPath) {
  console.error('usage: node tools/p24-verify.mjs <precommit.json> <adjudication.json> <report.md>');
  process.exit(2);
}

const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sortDeep = x => Array.isArray(x) ? x.map(sortDeep) : (x && typeof x === 'object')
  ? Object.fromEntries(Object.keys(x).sort().map(k => [k, sortDeep(x[k])])) : x;
const receiptHash = obj => {
  const copy = structuredClone(obj);
  delete copy.receipt_sha256;
  const bytes = JSON.stringify(sortDeep(copy));
  return crypto.createHash('sha256').update(bytes, 'utf8').digest('hex');
};
const assert = (ok, msg) => { if (!ok) throw new Error(msg); };

const pre = read(prePath);
const out = read(resultPath);
assert(pre.schema === 'c3x-p24-core-precommit-v1', 'precommit schema');
assert(out.schema === 'c3x-p24-adjudication-v1', 'adjudication schema');
assert(pre.scientific_stage === 'C3X 0.7.0-G9.4-P24', 'precommit stage');
assert(out.scientific_stage === pre.scientific_stage, 'stage mismatch');
assert(pre.selective_outcomes_consulted === false, 'precommit leakage flag');
assert(pre.cells.length === 384, 'precommit cell count');
assert(pre.receipt_sha256 === receiptHash(pre), 'precommit receipt hash');
assert(out.precommit_receipt_sha256 === pre.receipt_sha256, 'result/precommit lineage');
assert(out.receipt_sha256 === receiptHash(out), 'result receipt hash');
assert(out.inanis_pawn_q_negative_control.pass === true, 'Inanis PAWN_Q negative control');
for (const k of ['K1','K2','K4','K8']) assert(out.quotient_court[k], `missing ${k}`);

const lines = [
  '# C3X P24 independent verification',
  '',
  `- Verdict: \`${out.verdict}\``,
  `- Fresh cells: **${out.fresh_cells}**`,
  `- Precommit SHA-256: \`${pre.receipt_sha256}\``,
  `- Final SHA-256: \`${out.receipt_sha256}\``,
  `- Frozen-atlas refinement ceiling: **${out.quotient_refinement_ceiling}**`,
  `- Architecture-free K8 success: **${out.k8_intervention_response_bisimulation.architecture_free_success}**`,
  `- K8 architecture-free states: **${out.k8_intervention_response_bisimulation.architecture_free_states.length}/8**`,
  `- Architecture-indexed law nonconstant in every engine: **${out.architecture_indexed_law_nonconstant_each_engine}**`,
  `- Inanis PAWN_Q fine changes: **${out.inanis_pawn_q_negative_control.fine_changes}**`,
  '',
  '## Refinement court',
  '',
  '| Level | Strict universal | Natural universal | P20 recovery states |',
  '|---|---:|---:|---:|',
];
for (const k of ['K1','K2','K4','K8']) {
  const c = out.quotient_court[k];
  lines.push(`| ${k} | ${c.universal_strict_architecture_invariance} | ${c.universal_conditional_naturality} | ${c.p20_relation_recovery_states.length} |`);
}
lines.push('', '> This verifier checks lineage, canonical receipt hashes, fixed cardinalities, the negative control, and the presence of every frozen quotient level. It does not redefine the scientific court.');
fs.writeFileSync(reportPath, lines.join('\n') + '\n');
console.log('P24_JS_VERIFY_PASS', out.verdict, out.receipt_sha256);
