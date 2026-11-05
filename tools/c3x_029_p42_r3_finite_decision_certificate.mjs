#!/usr/bin/env node
/**
 * C3X P42/R3: finite three-ply certificate and omitted-third-candidate refuter.
 * Synthetic mathematical regression only: NOT chess, external referee, or novelty.
 */
"use strict";

function evaluate(values, planIndices) {
  let Q = Infinity, W = Infinity, R = 0;
  for (let r = 0; r < values.length; r++) {
    const v = Math.max(...values[r]);
    const w = Math.max(...planIndices[r].map(i => values[r][i]));
    Q = Math.min(Q, v);
    W = Math.min(W, w);
    R = Math.max(R, v - w);
  }
  return {Q, W, R};
}
function rng(seed = 20261105) {
  let x = seed >>> 0;
  return () => { x = (Math.imul(1664525, x) + 1013904223) >>> 0; return x / 2**32; };
}
function audit(iterations = 20000) {
  const random = rng();
  let failures = 0, pairwise = 0, thirdBeatsPlan = 0;
  for (let i = 0; i < iterations; i++) {
    const v = Array.from({length:3},()=>Array.from({length:2},
      ()=>Array.from({length:4},()=>Math.floor(random()*201)-100)));
    const p = v.map(()=>Array.from({length:2},()=>[Math.floor(random()*4)]));
    const cases = v.map((candidate,k)=>evaluate(candidate,p[k]));
    for (const c of cases) {
      if (!(c.Q-c.R <= c.W && c.W <= c.Q && c.R >= 0)) failures++;
    }
    if (cases[0].Q-cases[0].R > cases[1].Q) {
      pairwise++;
      if (!(cases[0].W > cases[1].Q)) failures++;
      if (cases[2].Q > cases[0].W) thirdBeatsPlan++;
    }
  }
  return {
    synthetic_worlds:iterations, assertion_failures:failures,
    pairwise_certificates:pairwise,
    third_candidate_higher_than_certified_plan:thirdBeatsPlan,
    status:failures?"FAIL":"PASS_SYNTHETIC_MATH_ONLY"
  };
}
const result = audit();
if (result.assertion_failures) process.exitCode = 1;
console.log(JSON.stringify(result,null,2));
