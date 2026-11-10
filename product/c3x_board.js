"use strict";
/* C3X P3: all visible chess data and decision scores come from the local API. */
const $ = id => document.getElementById(id);
const PIECES = {"K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙",
                "k":"♚","q":"♛","r":"♜","b":"♝","n":"♞","p":"♟"};
const INITIAL = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
let legal = [], currentFen = INITIAL, origin = null, selected = {a:"",b:""}, latest = null;

function status(text) { $("status").textContent = text; }
async function post(path, payload) {
  const res = await fetch(path, {method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(payload)});
  let body;
  try { body = await res.json(); } catch (_) {throw Error("서버의 JSON 응답을 해석할 수 없습니다.");}
  if(!res.ok) throw Error(body.error || "서버 오류: "+res.status);
  return body;
}
function parseFenBoard(fen) {
  const parts = fen.split(" ");
  if (parts.length < 2) throw Error("FEN 형식이 올바르지 않습니다.");
  const ranks = parts[0].split("/");
  if(ranks.length !== 8) throw Error("체스판 FEN의 행 수가 8이 아닙니다.");
  return ranks.map(line=>{
    let out=[];
    for(const c of line) {
      if(/[1-8]/.test(c)) for(let k=0;k<Number(c);k++) out.push("");
      else if(Object.hasOwn(PIECES,c)) out.push(c);
      else throw Error("FEN에 알 수 없는 기물 기호가 있습니다.");
    }
    if(out.length !== 8) throw Error("FEN의 각 행은 정확히 8칸이어야 합니다.");
    return out;
  });
}
function boardDraw(fen) {
  const ranks=parseFenBoard(fen), el=$("board"); el.replaceChildren();
  for(let r=0;r<8;r++)for(let f=0;f<8;f++){
    const sq=String.fromCharCode(97+f)+(8-r);
    const b=document.createElement("button");
    b.type="button";
    b.className="square "+((r+f)%2?"dark":"light");
    const piece=ranks[r][f];
    b.textContent=piece?PIECES[piece]:"";
    b.title=sq+(piece?" · "+piece:"");
    b.setAttribute("aria-label",sq+(piece?" 기물 "+piece:" 비어 있음"));
    if(sq===origin)b.classList.add("origin");
    if(selected.a.startsWith(sq))b.classList.add("pick-a");
    if(selected.b.startsWith(sq))b.classList.add("pick-b");
    b.addEventListener("click",()=>squareClick(sq));
    el.append(b);
  }
}
function activeTarget() {
  return document.querySelector('input[name="target"]:checked')?.value || "a";
}
function squareClick(sq) {
  if(!origin) {
    if(!legal.some(x=>x.uci.startsWith(sq))) {
      status("이 칸에서 둘 수 있는 합법 수가 없습니다."); return;
    }
    origin=sq; boardDraw(currentFen);status("도착 칸을 고르세요: "+sq);
    return;
  }
  const possible=legal.filter(x=>x.uci.slice(0,2)===origin &&
                                  x.uci.slice(2,4)===sq);
  if(possible.length) {
    const chosen=possible.find(x=>x.uci.endsWith("q")) || possible[0];
    const target=activeTarget();selected[target]=chosen.uci;
    $(target==="a"?"moveA":"moveB").value=chosen.uci;
    status("후보 "+target.toUpperCase()+": "+chosen.san+" ("+chosen.uci+")");
  } else status("합법 수가 아닙니다. 다시 출발 칸부터 선택하세요.");
  origin=null;boardDraw(currentFen);checkReady();
}
function checkReady() {
  $("analyze").disabled=!(selected.a && selected.b && selected.a!==selected.b);
  $("strategy").disabled=$("analyze").disabled;
}
function selectMenu(id, target) {
  const el=$(id);el.replaceChildren();
  const placeholder=document.createElement("option");
  placeholder.value=""; placeholder.textContent="후보 수를 선택하세요";el.append(placeholder);
  for(const {uci,san} of legal) {
    const opt=document.createElement("option");opt.value=uci;opt.textContent=san+" · "+uci;el.append(opt);
  }
  el.value="";
  el.addEventListener("change",()=>{
    selected[target]=el.value; origin=null;boardDraw(currentFen);checkReady();
  });
}
async function loadFen() {
  status("FEN과 합법 수를 확인하는 중입니다.");
  $("analyze").disabled=true;
  try {
    const result=await post("/api/legal",{fen:$("fen").value.trim()});
    currentFen=result.fen;$("fen").value=result.fen;legal=result.legal_moves;
    origin=null;selected={a:"",b:""};latest=null;
    $("strategyResult").classList.add("hidden");$("strategyResult").replaceChildren();
    selectMenu("moveA","a"); selectMenu("moveB","b");
    boardDraw(currentFen);
    $("results").classList.add("hidden");$("empty").classList.remove("hidden");
    status(legal.length+"개 합법 수 · "+(result.turn==="white"?"백":"흑")+" 차례");
  } catch(err) { status("국면 오류: "+err.message); }
}
function makeCell(text) {
  const td=document.createElement("td");td.textContent=String(text);return td;
}
function vstr(v) {return v===null||v===undefined?"메이트/미정":String(v);}
function appendText(parent,tag,content) {
  const el=document.createElement(tag);el.textContent=content;parent.append(el);return el;
}
function render(r) {
  latest=r;
  $("strategyResult").classList.add("hidden");$("strategyResult").replaceChildren();
  $("empty").classList.add("hidden");$("results").classList.remove("hidden");
  const e=r.engine_report, c=r.concept_report, roots=e.root_candidates;
  $("compareTitle").textContent=roots.map((x,i)=>(i?"B: ":"A: ")+x.facts.san+" ("+x.move_uci+")").join("   /   ");
  const gaps=e.candidate_A_minus_B_cp_by_depth_or_null;
  $("gap8").textContent=vstr(gaps["8"])+(gaps["8"]==null?"":" cp");
  $("gap10").textContent=vstr(gaps["10"])+(gaps["10"]==null?"":" cp");
  $("uncertainty").textContent=e.small_gap_or_mate_caution?
    "이 결과에는 근소한 점수 차이, 깊이 간 역전 또는 메이트 평가가 포함됩니다. 우열을 단정하지 않습니다.":
    "두 깊이에서의 우열이 유지되더라도 더 깊은 분석이나 독립 심판을 통한 확증은 없습니다.";
  const tbody=$("scores");tbody.replaceChildren();
  for(const depth of [8,10]) {
    const tr=document.createElement("tr");
    const k=String(depth);
    const vals=[depth,roots[0].forced_root_evaluations[k].mover_cp_or_null_if_mate,
      roots[1].forced_root_evaluations[k].mover_cp_or_null_if_mate,gaps[k]];
    vals.forEach(v=>tr.append(makeCell(vstr(v))));tbody.append(tr);
  }
  $("shared").textContent=Object.keys(c.concept_dimensions_shared_suppressed).length+
    "개 공통 지표는 차별 원인에서 제외했습니다.";
  const concepts=$("concepts");concepts.replaceChildren();
  const diff=Object.entries(c.concept_dimensions_different);
  if(!diff.length)appendText(concepts,"p","현재 측정한 7개 지표에는 차이가 없습니다.");
  for(const [name,x] of diff) {
    const item=document.createElement("div");item.className="tile";
    appendText(item,"strong",name.replaceAll("_"," "));
    appendText(item,"p","A: "+JSON.stringify(x.first)+" · B: "+JSON.stringify(x.second));
    concepts.append(item);
  }
  const branches=$("branches");branches.replaceChildren();
  for(let i=0;i<2;i++) {
    const root=roots[i],probe=root.opponent_reply_probe;
    const column=document.createElement("div");column.className="tile";
    appendText(column,"h3",(i===0?"후보 A ":"후보 B ")+root.facts.san);
    appendText(column,"p",probe.opponent_replies_total+"개 합법 응수 중 "+probe.sampled_reply_count+"개 검색");
    const ul=document.createElement("ul");
    for(const line of probe.reply_lines) {
      const li=document.createElement("li");
      const cp=line.after_opponent_reply_fresh_engine_value?.mover_cp_or_null_if_mate;
      li.textContent=line.opponent_reply_san+" → "+
        (line.measured_own_contingent_followup_uci_or_null||"종료")+
        " · "+vstr(cp)+(cp===null||cp===undefined?"":" cp");
      ul.append(li);
    }
    column.append(ul);branches.append(column);
  }
  $("raw").textContent=JSON.stringify(r,null,2);
}
function renderStrategy(data) {
  if(data.schema!=="c3x030-p4a-cui-inspired-two-opponent-layer-product-tree-v1")
    throw Error("전략나무 응답 스키마가 다릅니다.");
  if(!Array.isArray(data.roots) || data.roots.length!==2 ||
     data.roots[0].root_uci!==selected.a || data.roots[1].root_uci!==selected.b)
    throw Error("후보 수와 실제 전략나무가 일치하지 않습니다.");
  const panel=$("strategyResult");panel.replaceChildren();
  appendText(panel,"p","실제 원본 Stockfish 재검색 · 전체 "+data.total_leaf_paths+
    "개 말단 수순 · 독립 심판 없이 원본 엔진이 선택한 상대 응수만 검사");
  for(const [idx,root] of data.roots.entries()) {
    const area=document.createElement("div");area.className="tile";
    appendText(area,"h3",(idx===0?"후보 A ":"후보 B ")+root.root_san+
      " — "+root.leaf_count+"개 조건부 미래 계획");
    for(const first of root.tree) {
      if(first.terminal) {
        appendText(area,"p","종료 국면: "+first.terminal_result);
        continue;
      }
      const firstReply=first.opponent_move.action_san;
      const own=first.own_best_move_or_null?.action_san||"종료";
      const block=document.createElement("div");
      appendText(block,"p","상대 "+first.opponent_rank_1based+"순위: "+firstReply+
        " → 내 최선 대응 "+own);
      const second=document.createElement("ul");
      for(const deeper of first.next_opponent_replies) {
        const li=document.createElement("li");
        if(deeper.terminal){
          li.textContent="종료 국면: "+deeper.terminal_result;
        }else{
          li.textContent="다음 상대 "+deeper.opponent_rank_1based+"순위: "+
            deeper.opponent_move.action_san+" → 내 후속 대응 "+
            (deeper.own_best_move_or_null?.action_san||"종료")+
            " ("+deeper.trace_uci.join(" ")+")";
        }
        second.append(li);
      }
      block.append(second);area.append(block);
    }
    panel.append(area);
  }
  panel.classList.remove("hidden");
}
$("strategy").addEventListener("click",async()=>{
  const btn=$("strategy");btn.disabled=true;
  status("Cui 방식의 상대 응수 두 계층을 원본 Stockfish에서 실제 검색 중입니다.");
  try {
    const beforeA=selected.a,beforeB=selected.b,beforeFen=currentFen;
    const tree=await post("/api/strategy",{
      fen:beforeFen,move_a:beforeA,move_b:beforeB
    });
    if(currentFen!==beforeFen || selected.a!==beforeA || selected.b!==beforeB)
      throw Error("분석 도중 후보 수가 변경되었습니다. 다시 실행하세요.");
    renderStrategy(tree);
    status("두 번째 상대 응수까지 실제 전략나무 검색을 완료했습니다.");
  }catch(err){status("전략나무 검색 실패: "+err.message);}
  finally{checkReady();}
});
function exportMarkdown() {
  if(!latest)return;
  const blob=new Blob([latest.learner_markdown],{type:"text/markdown;charset=utf-8"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");a.href=url;a.download="C3X-two-move-explanation.md";
  document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url);
}
$("load").addEventListener("click",loadFen);
$("reset").addEventListener("click",()=>{$("fen").value=INITIAL;loadFen();});
$("analyze").addEventListener("click",async()=>{
  const btn=$("analyze");btn.disabled=true;status("원본 Stockfish가 두 후보와 상대 응수를 실제 분석 중입니다.");
  try{
    const data=await post("/api/analyze",{fen:currentFen,move_a:selected.a,move_b:selected.b});
    if(data.schema!=="c3x030-p3-local-interactive-product-v1")
      throw Error("예상과 다른 분석 프로토콜 응답입니다.");
    render(data);status("실제 Stockfish와 체스 규칙 분석이 완료되었습니다.");
  }catch(err){status("분석 실패: "+err.message);}
  finally{checkReady();}
});
$("export").addEventListener("click",exportMarkdown);
$("fen").value=INITIAL;loadFen();
