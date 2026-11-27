// C3X R36: independently written finite reference model of single-slot SF16 save/probe semantics.
// Upstream GPL-3.0-or-later: https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/tt.cpp
// This tests source-derived transition semantics, NOT native engine or empirical mediator effects.
"use strict";
function tag(k){return Number(BigInt(k)&65535n)}

function cluster(k,n){return Number((BigInt(k)*BigInt(n))>>64n)}

function empty(){return {key16:0,depth8:0,gen:0,pv:0,bound:0,move:0,value:0,ev:0,writers:{move:null,score:null,generation:null}}}

function save(s,e){const t={...s,writers:{...s.writers}};const different=tag(e.key)!==s.key16;const moveWrite=e.move!==0||different;const full=e.bound===3||different||e.depth8+2*e.pv>s.depth8-4;
if(moveWrite){t.move=e.move;t.writers.move={id:e.id,key:e.key}}
if(full){Object.assign(t,{key16:tag(e.key),depth8:e.depth8,gen:e.gen,pv:e.pv,bound:e.bound,value:e.value,ev:e.ev});t.writers.score={id:e.id,key:e.key};t.writers.generation={id:e.id,key:e.key,kind:"save"}}
return {state:t,moveWrite,full}}

function probeRefresh(s,key,gen,id){if(s.key16!==tag(key)&&s.depth8!==0)return {state:s,found:false,refresh:false};return {state:{...s,gen,writers:{...s.writers,generation:{id,key,kind:"probe"}}},found:s.depth8!==0,refresh:true}}

function run(){const A="0x123456780000beef",B="0x123456780001beef",C="0x123456780001cafe",n=524288;
const event=(id,key,extra={})=>({id,key,depth8:50,gen:8,pv:0,bound:2,move:100,value:40,ev:20,...extra});let passed=[];const check=(name,ok)=>{if(!ok)throw Error(name);passed.push(name)};
check("distinct full keys share tag and physical cluster",A!==B&&tag(A)===tag(B)&&cluster(A,n)===cluster(B,n));
const a=save(empty(),event("A",A)).state;const b=save(a,event("B",B,{depth8:1,move:200,value:99}));check("move-only write preserves score author",b.moveWrite&&!b.full&&b.state.writers.move.key===B&&b.state.writers.score.key===A&&b.state.value===40);
const c=save(b.state,event("C",A,{bound:3,move:0,value:90}));check("full overwrite may preserve a different-key move",c.full&&!c.moveWrite&&c.state.move===200&&c.state.writers.move.key===B&&c.state.writers.score.key===A);
const p=probeRefresh(c.state,B,16,"P");check("tag hit refreshes generation despite mismatched score writer",p.found&&p.refresh&&p.state.gen===16&&p.state.writers.score.key!==B&&p.state.writers.move.key===B);
const q=probeRefresh(empty(),A,16,"Q");check("empty probe miss can write generation",!q.found&&q.refresh&&q.state.gen===16);
const d=save(c.state,event("D",C,{move:0}));check("different tag resets move even when no move supplied",d.full&&d.moveWrite&&d.state.move===0&&d.state.writers.move.key===C);
const e=save(a,event("E",A,{depth8:46,pv:0,move:0}));check("strict depth boundary does not overwrite",!e.full&&!e.moveWrite);
const f=save(a,event("F",A,{depth8:46,pv:1,move:0}));check("pv bonus changes overwrite eligibility",f.full&&!f.moveWrite);
const g=probeRefresh(a,C,24,"G");check("different-tag occupied-slot nonmatch has no refresh",!g.found&&!g.refresh&&g.state===a);
const h=probeRefresh(a,A,8,"H");check("equal-byte refresh still records a write event",h.refresh&&h.state.gen===a.gen&&h.state.writers.generation.id==="H");
return {tests:passed,example:{A,B,cluster:cluster(A,n),tag:tag(A),moveWriter:c.state.writers.move,scoreWriter:c.state.writers.score,generationWriter:p.state.writers.generation}}}
console.log(JSON.stringify(run(),null,2));
