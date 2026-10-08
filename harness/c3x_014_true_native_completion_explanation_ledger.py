#!/usr/bin/env python3
"""True Stockfish16 completedDepth-aware 16-game explanation ledger, C3X 0.14.

Joins pinned real depth-panel and source-native postsearch telemetry. Does NOT
equate reported UCI MultiPV depth with completedDepth or chess strategic truth.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import chess

DEPTH_SHA="868b70e5311e2d9cc51f01e8ef50fc78127b1544dd9198c335f7877af335a24b"
NATIVE_SHA="cf6f4e5703a3250e7694049978fa3fa541107217a079997674f324f11d254978"

class Refuse(ValueError):pass
def require(c,msg):
    if not c:raise Refuse(msg)
def load(p,expected):
    raw=Path(p).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==expected,"SOURCE_BYTES_TAMPERED")
    return json.loads(raw)
def check_native(n):
    require(n["mode"] in ("OFF","MAIN"),"MODE")
    k=n["native"]
    require(0<=k["best_completed"]<=k["best_root_depth"],"FAKE_NATIVE_DEPTH")
    require(k["best_completed"]==k["main_completed"],"THREAD1_COMPLETION_DISAGREEMENT")
    require(n["max_pv_reported_rank12_depth"]>=k["best_completed"],"PV_DEPTH_BELOW_COMPLETION")
    require(n["fixed_source_node_cap"]>=1024,"INVALID_NODE_CAP")
    require(n["matches_original_previous_native_PV_and_nodes"],"NOT_SOURCE_EQUIVALENT")
def compile_sources(depth,native):
    require(depth["schema"]=="c3x-014-internal-p3-equal-requested-depth-budget-response-surface-v1","BAD_DEPTH_PANEL")
    require(depth["one_formal_research_stage"]=="C3X 0.14" and depth["P3_is_internal_not_formal_stage"],"NEW_FORMAL_SUBSTAGE_FORBIDDEN")
    require(depth["sham_exact_every_cell"] and depth["two_cold_runs_equal_group_depth_out_of_48"]==48,"INVALID_SHAM")
    require(depth["source_game_groups"]==16 and len(depth["samples"])==96 and not depth["P1_holdout_opened"],"BAD_SAMPLE_COUNT")
    require(native["schema"]=="c3x-014-native-stockfish16-completed-depth-vs-UCI-PV-court-v1","BAD_NATIVE_SOURCE")
    require(native["source_games"]==16 and native["engine_runs"]==64,"INCOMPLETE_NATIVE_PROBE")
    require(native["cold_pair_equal_out_of32"]==32 and native["exact_same_parent_stress_uci_output_count_out_of64"]==64,"LOGGER_PERTURBED_SEARCH")
    require(native["native_completedDepth_disagrees_with_max_two_PV_reported_depth_out_of64"]==46,"UNEXPECTED_COMPLETION_PANEL_CHANGED")
    d={}
    for c in depth["samples"]:
        if c["cold_repeat"]==1:d.setdefault(c["source_group_hash"],[]).append(c)
    n={}
    for x in native["all_runs"]:
        check_native(x)
        if x["repeat"]==1:n.setdefault(x["source_group"],{})[x["mode"]]=x
    require(len(d)==len(n)==16 and set(d)==set(n),"GAME_GROUP_MIXUP")
    out=[]
    for key in sorted(d):
        cs=sorted(d[key],key=lambda x:x["requested_equal_depth"])
        require([x["requested_equal_depth"] for x in cs]==[11,12,13],"DEPTH_GRID_CHANGED")
        require(set(n[key])=={"OFF","MAIN"},"MISSING_NATIVE_ARMS")
        b=chess.Board(cs[0]["full_root_fen"])
        require(b.is_valid() and b.turn,"INVALID_CHESS_BOARD")
        pair=cs[0]["legal_pair"]
        require(len(pair)==2 and all(chess.Move.from_uci(x) in b.legal_moves for x in pair),"ILLEGAL_CANDIDATE")
        nativeOff=n[key]["OFF"];nativeMain=n[key]["MAIN"]
        require(nativeOff["source_round"]==cs[0]["round"]==nativeMain["source_round"],"PROVENANCE_ROUND_MISMATCH")
        require(nativeOff["legal_pair"]==pair==nativeMain["legal_pair"],"PROVENANCE_ROOT_MISMATCH")
        inversion=[x["requested_equal_depth"] for x in cs if x["strict_nonzero_cp_sign_inversion"]]
        label_changes=[x["requested_equal_depth"] for x in cs if x["bestmove_label_changed"]]
        white_gaps={str(x["requested_equal_depth"]):{"off":x["off_root_white_cp_gap"],"main":x["main_root_white_cp_gap"]} for x in cs}
        completed=[nativeOff["native"]["best_completed"],nativeMain["native"]["best_completed"]]
        reported=[nativeOff["max_pv_reported_rank12_depth"],nativeMain["max_pv_reported_rank12_depth"]]
        claim=("DEPTH_RESTRICTED_SIGN_INVERSION" if inversion else "NO_STRICT_SIGN_INVERSION_WITHIN_TESTED_DEPTHS")
        human=(f"TCEC S29 {cs[0]['round']} 경기, 후보 {pair[0]} / {pair[1]}: "
              + "; ".join(f"깊이 {x['requested_equal_depth']} 평가차 {x['off_root_white_cp_gap']}→{x['main_root_white_cp_gap']}cp" for x in cs)
              + f". 엄격한 평가차 부호 역전 깊이: {inversion or '없음'}, UCI 최선수 변경 깊이: {label_changes or '없음'}. "
              + f"기존 노드 한도 재실험에서 C++ 내부 실제 완료 깊이 OFF {completed[0]} / MAIN {completed[1]}, "
              + f"UCI 두 후보 PV 정보에 나타난 최대 표기 깊이 OFF {reported[0]} / MAIN {reported[1]}. "
              + "이 관찰은 특정 Stockfish16 검색 구현의 반응이다. 동일 계산량, 체스 개념의 전략적 원인 또는 교육 효과를 증명하지 않는다.")
        out.append({"round":cs[0]["round"],"group":key,"root_pair":pair,"authority":claim,
            "strict_cp_inversion_depths":inversion,"UCI_bestmove_change_depths":label_changes,
            "fixed_depth_white_cp_gaps":white_gaps,
            "native_true_completedDepth_OFF_MAIN":completed,
            "max_PV_reported_depth_OFF_MAIN":reported,
            "UCI_PV_depth_is_not_proof_of_native_completion":True,
            "chess_strategy_causal_certified":False,
            "human_teaching_effect_certified":False,
            "korean_evidence_bound_explanation":human})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixed-depth",required=True)
    p.add_argument("--native",required=True)
    p.add_argument("--json-out",required=True)
    p.add_argument("--md-out",required=True)
    a=p.parse_args()
    depth=load(a.fixed_depth,DEPTH_SHA)
    native=load(a.native,NATIVE_SHA)
    rows=compile_sources(depth,native)
    require(len(rows)==16,"WRONG_GROUP_OUTPUT")
    # Falsification of source integrity, native state, and legal/identity transport.
    checks=0
    def refusal(tag,f):
        nonlocal checks
        try:f()
        except Refuse:checks+=1;print("P3_TRUE_COMPLETION_CLAIM_FALSIFIER_PASS",tag,flush=True)
        else:raise RuntimeError("CLAIM_GATE_FAIL_OPEN "+tag)
    refusal("SHA",lambda:load(a.native,"0"*64))
    bad=copy.deepcopy(native);bad["all_runs"][0]["native"]["best_completed"]=999
    refusal("NATIVE_DEPTH",lambda:compile_sources(depth,bad))
    bad=copy.deepcopy(native);bad["all_runs"][0]["matches_original_previous_native_PV_and_nodes"]=False
    refusal("SOURCE_EXACT",lambda:compile_sources(depth,bad))
    bad=copy.deepcopy(depth);bad["samples"][0]["full_root_fen"]="8/8/8/8/8/8/8/8 w - - 0 1"
    # replace all first-cold? first case is repeat1 in frozen source ordering
    refusal("ILLEGAL_BOARD",lambda:compile_sources(bad,native))
    bad=copy.deepcopy(native);bad["all_runs"][0]["source_group"]="bogus"
    refusal("SOURCE_IDENTITY",lambda:compile_sources(depth,bad))
    require(checks==5,"INCOMPLETE_MUTATION_COURT")
    out={"schema":"c3x-014-single-formal-stage-native-budget-aware-explanation-v2",
         "research_unit":"C3X 0.14","P3_internal_only":True,"first_source_sha256":DEPTH_SHA,
         "native_probe_sha256":NATIVE_SHA,"games":16,"native_completions_not_equal_PV_reports":46,
         "falsifiers_passed":checks,"strategic_causal_claims_allowed":0,"user_learning_effect_certified":False,
         "source_game_explanations":rows}
    Path(a.json_out).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    words=["# C3X 0.14 — Native-Completed-Depth-Aware Engine Explanation Ledger",
           "Internal P3 only. One formal research unit. Sixteen source-game-bound comments, no chess strategy causal certification."]
    for r in sorted(rows,key=lambda x:x["round"]):
        words.extend(["## TCEC "+r["round"]+" — "+r["authority"],r["korean_evidence_bound_explanation"]])
    Path(a.md_out).write_text("\n\n".join(words)+"\n")
    print("C3X014_TRUE_NATIVE_COMPLETION_EXPLANATIONS_PASS",json.dumps({
        "games":len(rows),"strict":sum(bool(r["strict_cp_inversion_depths"]) for r in rows),
        "five_false_claims_rejected":checks,
        "round96":next(r for r in rows if r["round"]=="96.1")}),flush=True)
if __name__=="__main__":main()
