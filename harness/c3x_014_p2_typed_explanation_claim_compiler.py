#!/usr/bin/env python3
"""C3X 0.14 P2: evidence-rights compiler consuming ACTUAL native SF16 source data.

No freeform LLM. Claims stay typed. Fraud/poison regressions fail closed.
"""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
import chess
PERMITTED={"UCI_SCORE_OBSERVED","TT_PATH_INTERVENTION_WITH_NO_OBSERVED_CHANGE","TT_PATH_RESPONSE"}
EXPECTED_ENGINE_SOURCE="cb879eaa14bcbf3896c4d069dcb1cf543135c68c5b1fa0ea2eab942613332eeb"

class Refuse(ValueError):pass

def require(cond,msg):
    if not cond:raise Refuse(msg)

def locked_parse(raw,expected_sha):
    require(hashlib.sha256(raw).hexdigest()==expected_sha,"PANEL_SHA256_MISMATCH")
    p=json.loads(raw)
    require(p["schema"]=="c3x-014-p2-real-new16-group-typed-native-tt-score-choice-court-v1","BAD_SCHEMA")
    require(p["source_cohort_sha256"]==EXPECTED_ENGINE_SOURCE,"WRONG_SOURCE_COHORT")
    require(not p["p1_four_holdout_games_opened"],"HOLDOUT_EXPOSURE")
    require(p["independent_game_groups"]==16 and len(p["cases"])==64,"INVALID_GROUP_OR_CELL_COUNT")
    require(p["clean_vs_sham_exact_all"],"SHAM_FAILURE")
    require(all(z==32 for z in p["cold_pair_exact_by_arm_out_of_32"].values()),"UNSTABLE_COLD_RUNS")
    return p

def validate_result(cell):
    require(cell["sham_exact"],"SHAM_NOT_MATCHED")
    b=chess.Board(cell["fen"])
    require(b.is_valid() and b.turn==chess.WHITE,"INVALID_BOARD")
    pair=cell["pair"]
    require(len(pair)==2 and len(set(pair))==2,"BAD_ROOT_PAIR")
    try:
        moves=[chess.Move.from_uci(x) for x in pair]
    except ValueError:raise Refuse("BAD_MOVE_NOTATION")
    require(all(m in b.legal_moves for m in moves),"ILLEGAL_ROOT_MOVE")
    for name,obj in [("clean",cell["clean"]),("off",cell["off"]),*cell["arms"].items()]:
        require(name in ("clean","off","MAIN","QSEARCH","BOTH"),"UNKNOWN_ARM")
        require(obj["bestmove"] in pair,"BESTMOVE_OUTSIDE_ROOT")
        require(set(map(str,obj["final_MultiPV"].keys()))=={"1","2"},"INVALID_MULTIPV")
        values=list(obj["final_MultiPV"].values())
        require({v["root_move"] for v in values}==set(pair),"WRONG_RANK_MOVES")
        require(values[0]["root_move"]==obj["bestmove"],"BEST_NOT_RANK1")
        kinds=[v["score_kind"] for v in values]
        flags=[v["score_bound_flag"] for v in values]
        numeric=all(x=="cp" for x in kinds) and all(z=="exact_reported" for z in flags)
        require((obj["signed_white_cp_gap"] is not None)==numeric,"SCORE_TYPE_OR_BOUND_CONTAMINATION")
        if numeric:
            sc={v["root_move"]:v["score_value_white_perspective"] for v in values}
            require(obj["signed_white_cp_gap"]==sc[pair[0]]-sc[pair[1]],"SCORE_SIGN_OR_GAP_CORRUPTION")
        else:
            require(obj["numeric_gap_censored"],"BOUNDED_GAP_NOT_CENSORED")
        if name in ("MAIN","QSEARCH","BOTH"):
            tel=obj["tt"]
            require(tel.get("mode")=={"MAIN":1,"QSEARCH":2,"BOTH":3}[name],"TT_MODE_MISMATCH")
            require(tel.get("main_blocked",0)>=0 and tel.get("q_blocked",0)>=0,"TT_COUNTER_INVALID")
            if name=="MAIN":require(tel["q_blocked"]==0,"MAIN_WRONG_SITE")
            if name=="QSEARCH":require(tel["main_blocked"]==0,"QSEARCH_WRONG_SITE")
    require(cell["clean"]["bestmove"]==cell["off"]["bestmove"],"SHAM_BESTMOVE_DISAGREEMENT")

def make_row(cell,arm="MAIN"):
    validate_result(cell)
    before=cell["off"];after=cell["arms"][arm]
    cutoff_counts=after["tt"]["main_blocked"] if arm=="MAIN" else after["tt"]["q_blocked"] if arm=="QSEARCH" else after["tt"]["main_blocked"]+after["tt"]["q_blocked"]
    delta=(after["signed_white_cp_gap"]-before["signed_white_cp_gap"]
           if after["signed_white_cp_gap"] is not None and before["signed_white_cp_gap"] is not None else None)
    response=before["bestmove"]!=after["bestmove"] or (delta is not None and delta!=0)
    claim=("TT_PATH_RESPONSE" if cutoff_counts>0 and response else
           "TT_PATH_INTERVENTION_WITH_NO_OBSERVED_CHANGE" if cutoff_counts>0 else "UCI_SCORE_OBSERVED")
    assert claim in PERMITTED
    origin=f"TCEC S29 회차 {cell['round']}, Stockfish 16 깊이 {cell['depth']}"
    observed=(f"{cell['pair'][0]}−{cell['pair'][1]} 백 관점 차이가 "
              f"{before['signed_white_cp_gap']:+d}cp에서 {after['signed_white_cp_gap']:+d}cp로 바뀌었다."
              if delta is not None else "하나 이상의 결과가 메이트 또는 경계형 점수라 정확한 cp 차이를 주장하지 않는다.")
    p=before["signed_white_cp_gap"];q=after["signed_white_cp_gap"]
    strict_inversion=(p is not None and q is not None and p*q<0)
    tie_transition=(p is not None and q is not None and (p==0 or q==0))
    if strict_inversion:
        move="두 후보 간 cp 평가차의 부호가 엄격히 역전됐다. "
    elif tie_transition:
        move="두 후보 간 cp 평가차 중 하나는 0으로, 엄격한 우열 역전이라고 말할 수 없다. "
    else:
        move=""
    move+=("UCI 최선수 표시는 달라졌다." if before["bestmove"]!=after["bestmove"] else "UCI 최선수 표시는 유지됐다.")
    language=(f"{origin}의 동일 원시 국면에서 {arm} TT 조기 반환 차단 {cutoff_counts}회가 계측됐다. "
              +observed+" "+move+
              " 이 수치는 탐색 구현에 대한 국소 반응이며, 폰 구조의 전략적 인과 설명이나 원래 체스의 최선수 증명이 아니다.")
    return {"source_group_hash":cell["group"],"source_game_id":cell["game"],
      "round":cell["round"],"depth":cell["depth"],"control_sham_exact":True,
      "arm":arm,"native_blocked_event_count":cutoff_counts,
      "before_bestmove":before["bestmove"],"after_bestmove":after["bestmove"],
      "before_signed_white_cp_gap":before["signed_white_cp_gap"],
      "after_signed_white_cp_gap":after["signed_white_cp_gap"],
      "numeric_cp_gap_shift":delta,
      "strict_signed_cp_preference_inversion":strict_inversion,
      "tie_endpoint_detected":tie_transition,
      "uci_bestmove_label_changed":before["bestmove"]!=after["bestmove"],
      "authority_label":claim,
      "chess_semantic_causal_claim_allowed":False,
      "human_learning_benefit_proven":False,
      "chess_explanation":language}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True)
    ap.add_argument("--sha256",required=True)
    ap.add_argument("--json-out",required=True)
    ap.add_argument("--markdown-out",required=True)
    a=ap.parse_args()
    payload=Path(a.panel).read_bytes()
    p=locked_parse(payload,a.sha256)
    rows=[]
    for c in p["cases"]:
        if c["repeat"]!=1:continue
        for mode in ("MAIN","QSEARCH","BOTH"):
            rows.append(make_row(c,mode))
    require(len(rows)==96,"EXPECTED_96_FIRST_COLD_ARM_CASES")
    # Mutation court: require refusal of a forged SHA, illegal board, swapped score sign,
    # invalid TT site and mate/cp crossing.
    sample=copy.deepcopy(p["cases"][0])
    ntests=0
    def expect_refusal(label,cell):
        nonlocal ntests
        try:make_row(cell)
        except Refuse:ntests+=1;print("P2_CLAIM_FALSIFIER_PASS",label,flush=True)
        else:raise RuntimeError("CLAIM_FALSIFIER_UNEXPECTEDLY_ACCEPTED "+label)
    try:locked_parse(payload,a.sha256[:4]+"0"*60)
    except Refuse:ntests+=1;print("P2_CLAIM_FALSIFIER_PASS","HASH",flush=True)
    else:raise RuntimeError("CLAIM_FALSIFIER_ACCEPTED_CORRUPTED_SHA")
    bad=copy.deepcopy(sample);bad["fen"]="8/8/8/8/8/8/8/8 w - - 0 1";expect_refusal("ILLEGAL_BOARD",bad)
    bad=copy.deepcopy(sample);bad["pair"][0]="e1e8";expect_refusal("ILLEGAL_ROOT",bad)
    bad=copy.deepcopy(sample);bad["off"]["signed_white_cp_gap"]=7654321;expect_refusal("SCORE_SIGN",bad)
    bad=copy.deepcopy(sample);bad["arms"]["MAIN"]["tt"]["mode"]=2;expect_refusal("TT_SITE",bad)
    bad=copy.deepcopy(sample);bad["off"]["final_MultiPV"]["1"]["score_bound_flag"]="lowerbound";expect_refusal("BOUND_SCORE",bad)
    require(ntests==6,"FALSIFIERS_MISSING")
    out={"schema":"c3x-014-p2-typed-chess-claim-ledger-v1",
      "authentic_source_sha256":a.sha256,
      "authority":"LOCAL_NATIVE_SF16_ENGINE_MECHANISM_ONLY",
      "number_of_actual_engine_arm_statements":len(rows),
      "falsification_tests_passed":ntests,
      "all_chess_semantic_claims_denied":all(not x["chess_semantic_causal_claim_allowed"] for x in rows),
      "rows":rows}
    for name,x in ((a.json_out,json.dumps(out,indent=2,ensure_ascii=False)+"\n"),):
        file=Path(name);file.parent.mkdir(parents=True,exist_ok=True);file.write_text(x)
    txt=["# C3X 0.14 P2 — Signed Native-Engine Explanation Ledger",
         "Source SHA256: "+a.sha256,
         "Exactly 96 arm-level sentences across 16 source groups × 2 depths × 3 interventions. No chess concept causation or student benefit certified.",
         "## One representative per authority level"]
    for label in sorted({r["authority_label"] for r in rows}):
        v=next(x for x in rows if x["authority_label"]==label)
        txt.extend(["### "+label,v["chess_explanation"]])
    txt.append("## Scope\nAll sentences are mechanically extracted from actual native engine data. Any independent chess-concept or learning-efficacy causal claim requires new tests.")
    Path(a.markdown_out).write_text("\n\n".join(txt)+"\n")
    print("P2_AUTHORITY_LEDGER_REAL_PANEL_PASS",len(rows),"mutation_falsifiers",ntests,
       "types",json.dumps({k:sum(x["authority_label"]==k for x in rows) for k in PERMITTED}),flush=True)
if __name__=="__main__":main()
