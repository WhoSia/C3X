#!/usr/bin/env node
import fs from 'node:fs';

const [,, prePath, resultPath, reportPath] = process.argv;
if (!prePath || !resultPath || !reportPath) {
  console.error('usage: node tools/p24-verify.mjs <precommit.json> <adjudication.json> <report.md>');
  process.exit(2);
}

const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const assert = (ok, msg) => { if (!ok) throw new Error(msg); };
const sha256Hex = x => typeof x === 'string' && /^[0-9a-f]{64}$/.test(x);

const pre = read(prePath);
const out = read(resultPath);
assert(pre.schema === 'c3x-p24-core-precommit-v1', 'precommit schema');
assert(out.schema === 'c3x-p24-adjudication-v1', 'adjudication schema');
assert(pre.scientific_stage === 'C3X 0.7.0-G9.4-P24', 'precommit stage');
assert(out.scientific_stage === pre.scientific_stage, 'stage mismatch');
assert(pre.selective_outcomes_consulted === false, 'precommit leakage flag');
assert(pre.cells.length === 384, 'precommit cell count');
assert(out.fresh_cells === 384, 'result cell count');
assert(sha256Hex(pre.receipt_sha256), 'precommit receipt syntax');
assert(sha256Hex(out.receipt_sha256), 'result receipt syntax');
assert(out.precommit_receipt_sha256 === pre.receipt_sha256, 'result/precommit lineage');
assert(out.inanis_pawn_q_negative_control.pass === true, 'Inanis PAWN_Q negative control');
assert(out.inanis_pawn_q_negative_control.fine_changes === 0, 'Inanis PAWN_Q fine-change count');

const levels = ['K1','K2','K4','K8'];
for (const k of levels) assert(out.quotient_court[k], `missing ${k}`);

// Recompute the scientific branch decision independently from the Python court.
const anyStrict = levels.some(k => out.quotient_court[k].universal_strict_architecture_invariance === true);
const anyNatural = levels.some(k => out.quotient_court[k].universal_conditional_naturality === true);
const common = out.k8_intervention_response_bisimulation.architecture_free_states;
assert(Array.isArray(common), 'architecture-free state list');
const architectureFree = common.length === 8;
const architectureIndexNecessary = !architectureFree;
assert(out.k8_intervention_response_bisimulation.architecture_free_success === architectureFree, 'architecture-free flag');
assert(out.k8_intervention_response_bisimulation.architecture_index_necessary === architectureIndexNecessary, 'architecture-index flag');
const ceiling = !anyStrict && !anyNatural && architectureIndexNecessary;
assert(out.quotient_refinement_ceiling === ceiling, 'refinement ceiling recomputation');

const distinct = out.quotient_court.K8.distinct_response_laws_by_engine;
const targets = ['stockfish_19','berserk','ethereal'];
const nonconstant = targets.every(t => Number(distinct[t]) > 1);
assert(out.architecture_indexed_law_nonconstant_each_engine === nonconstant, 'nonconstant architecture-law flag');

let expected;
if (!out.inanis_pawn_q_negative_control.pass) expected = 'NEGATIVE_CONTROL_FAILURE';
else if (architectureFree) expected = 'ARCHITECTURE_FREE_INTERVENTION_RESPONSE_BISIMULATION_RECONSTITUTED';
else if (ceiling && nonconstant) expected = 'FROZEN_ATLAS_QUOTIENT_REFINEMENT_CEILING_REACHED__ARCHITECTURE_INDEXED_CAUSAL_LAW_CONSTITUTED';
else if (ceiling) expected = 'FROZEN_ATLAS_QUOTIENT_REFINEMENT_CEILING_REACHED__NO_STABLE_LAW_CONSTITUTION';
else expected = 'PARTIAL_ATLAS_TRANSPORT__SUCCESSOR_CONFIRMATION_REQUIRED';
assert(out.verdict === expected, `verdict mismatch: expected ${expected}`);

const lines = [
  '# C3X P24 independent verification',
  '',
  `- Verdict: \`${out.verdict}\``,
  `- Fresh cells: **${out.fresh_cells}**`,
  `- Precommit SHA-256 identifier: \`${pre.receipt_sha256}\``,
  `- Final SHA-256 identifier: \`${out.receipt_sha256}\``,
  `- Frozen-atlas refinement ceiling: **${out.quotient_refinement_ceiling}**`,
  `- Architecture-free K8 success: **${architectureFree}**`,
  `- K8 architecture-free states: **${common.length}/8**`,
  `- Architecture-indexed law nonconstant in every engine: **${nonconstant}**`,
  `- Inanis PAWN_Q fine changes: **${out.inanis_pawn_q_negative_control.fine_changes}**`,
  '',
  '## Refinement court',
  '',
  '| Level | Strict universal | Natural universal | P20 recovery states |',
  '|---|---:|---:|---:|',
];
for (const k of levels) {
  const c = out.quotient_court[k];
  lines.push(`| ${k} | ${c.universal_strict_architecture_invariance} | ${c.universal_conditional_naturality} | ${c.p20_relation_recovery_states.length} |`);
}
lines.push('', '> The JavaScript verifier independently recomputes the branch logic, refinement ceiling, architecture-index necessity, and final verdict from the sealed JSON fields. It deliberately does not recompute Python receipt hashes because Python and ECMAScript number serialization are not byte-identical without a shared canonical-number standard.');
fs.writeFileSync(reportPath, lines.join('\n') + '\n');
console.log('P24_JS_VERIFY_PASS', out.verdict, out.receipt_sha256);
