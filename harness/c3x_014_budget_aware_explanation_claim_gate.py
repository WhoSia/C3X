#!/usr/bin/env python3
"""Budget-aware native-chess explanation gate inside ONE formal C3X 0.14 study.

Feeds on real fixed-depth and node-cap panels; does not certify chess concepts.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import chess

NODE_SHA="37d6b3bde44e971ee88ae5fbababd63ba88980ce6b48e0bfa80234cebccdbdf1"
class Reject(ValueError):pass
def chk(ok,why):
    if not ok:raise Reject(why)
def read(path,hashval):
    b=Path(path).read_bytes()
    chk(hashlib.sha256(b).hexdigest()==hashval,"SOURCE_SHA256_CORRUPT")
    return json.loads(b)
def validate(c):
    board=chess.Board(c["full_root_fen"])
    chk(board.is_valid() and board.turn,"BAD_FEN")
    pair=c["legal_pair"]
    chk(len(set(pair))==2 and all(chess.Move.from_uci(m) in board.legal_moves for m in pair),"ILLEGAL_ROOT")
    chk(c["requested_equal_depth"] in (11,12,13),"INVALID_DEPTH")
    chk(c["clean_vs_instrumented_off_sham_exact"],"BROKEN_SHAM")
    chk(c["main"]["tt"]["mode"]==1 and c["main"]["tt"]["q_blocked"]==0,"WRONG_INTERVENTION")
    chk(c["observed_native_MAIN_cutoffs_blocked"]==c["main"]["tt"]["main_blocked"],"FAKE_TT_COUNT")
    for arm in ("off","main"):
        v=c[arm];pv=v["final_MultiPV"]
        chk(set(pv)=={"1","2"},"BAD_MULTIPV")
        chk({p["root_move"] for p in pv.values()}==set(pair),"PV_WRONG_ROOT")
        chk(pv["1"]["root_move"]==v["bestmove"],"BESTMOVE_RANK_MISMATCH")
        exact=all(p["score_kind"]=="cp" and p["score_bound_flag"]=="exact_reported" for p in pv.values())
        chk((v["signed_white_cp_gap"] is not None)==exact,"BOUND_CP_PRETENDED_EXACT")
        if exact:
            score={z["root_move"]:z["score_value_white_perspective"] for z in pv.values()}
            chk(v["signed_white_cp_gap"]==score[pair[0]]-score[pair[1]],"CP_SIGN_CORRUPTION")
        chk(c["rank1_reported_nodes_"+arm]==pv["1"]["nodes"],"NODE_COUNT_CORRUPT")
    x,y=c["off"]["signed_white_cp_gap"],c["main"]["signed_white_cp_gap"]
    chk(x==c["off_root_white_cp_gap"] and y==c["main_root_white_cp_gap"],"GAP_VALUE_FORGED")
    if x is not None and y is not None:
        chk(c["strict_nonzero_cp_sign_inversion"]==(x*y<0),"STRICT_SIGN_FORGED")
        chk(c["zero_margin_endpoint"]==(x==0 or y==0),"TIE_ENDPOINT_FORGED")
    chk(c["bestmove_label_changed"]==(c["off"]["bestmove"]!=c["main"]["bestmove"]),"LABEL_CHANGE_FORGED")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--depth",required=True);p.add_argument("--depth-sha",required=True)
    p.add_argument("--node",required=True);p.add_argument("--json-out",required=True);p.add_argument("--md-out",required=True)
    a=p.parse_args()
    d=read(a.depth,a.depth_sha);n=read(a.node,NODE_SHA)
    chk(d["one_formal_research_stage"]=="C3X 0.14" and d["P3_is_internal_not_formal_stage"],"WRONG_STUDY_IDENTITY")
    chk(d["sham_exact_every_cell"] and d["two_cold_runs_equal_group_depth_out_of_48"]==48,"FAILED_CONTROLS")
    chk(len(d["samples"])==96 and not d["P1_holdout_opened"],"HOLDOUT_OR_SAMPLE_ERROR")
    chk(n["schema"]=="c3x-014-p2-node-cap-order-hash-postdiscovery-actual-native-court-v1" and len(n["cells"])==128,"BAD_NODE_STRESS_SOURCE")
    sources=[x for x in d["samples"] if x["cold_repeat"]==1]
    group={}
    for x in sources:group.setdefault(x["source_group_hash"],[]).append(x)
    chk(len(group)==16,"SIXTEEN_GROUPS_REQUIRED")
    node={}
    for x in n["cells"]:
        if x["original_order"] and x["hash_mib"]==16 and x["repeat"]==1:
            chk(x["group"] not in node,"NODE_DUPLICATE")
            node[x["group"]]=x
    chk(set(group)==set(node),"ORIGIN_GROUP_MISMATCH")
    rows=[]
    for key in sorted(group):
        cs=sorted(group[key],key=lambda x:x["requested_equal_depth"])
        chk([x["requested_equal_depth"] for x in cs]==[11,12,13],"MISSING_DEPTH")
        for x in cs:validate(x)
        z=node[key]
        chk(cs[0]["full_root_fen"]==z["fen"] and cs[0]["legal_pair"]==z["pair"],"NODE_ROOT_MISMATCH")
        sr=[x["requested_equal_depth"] for x in cs if x["strict_nonzero_cp_sign_inversion"]]
        labels=[x["requested_equal_depth"] for x in cs if x["bestmove_label_changed"]]
        complete=[z["mode_off"]["max_completed_both_pv_depth"],z["mode_main"]["max_completed_both_pv_depth"]]
        chk(all(isinstance(x,int) for x in complete),"INCOMPLETE_NODE_BUDGET")
        summary="; ".join(f"d{x['requested_equal_depth']}: {x['off_root_white_cp_gap']}→{x['main_root_white_cp_gap']} cp" for x in cs)
        label="THREE_DEPTH_LOCAL_SIGN_INVERSION" if len(sr)==3 else "DEPTH_CONDITIONAL_ENGINE_RESPONSE" if sr else "NO_STRICT_SIGN_INVERSION"
        msg=(f"Stockfish16, TCEC S29 {cs[0]['round']} 경기 후보 {cs[0]['legal_pair'][0]} / {cs[0]['legal_pair'][1]}; "
             f"동일 요청 깊이 비교 {summary}. 엄격한 부호 역전 d={sr}, UCI 최선수 변경 d={labels}. "
             f"동일 요청 노드 한도 실험의 양쪽 완료 깊이는 {complete[0]} 대 {complete[1]}. "
             "이는 내부 탐색 경로의 국소적 반응이며 전략적 체스 개념의 인과성이 입증된 것은 아니다.")
        rows.append({"round":cs[0]["round"],"group":key,"authority":label,"strict_sign_depths":sr,
            "uci_label_change_depths":labels,"node_cap_completed_depths":complete,
            "node_cap_depth_discordant":complete[0]!=complete[1],
            "chess_concept_causality_certified":False,"language_ko":msg})
    tests=0
    def must_reject(name,x):
        nonlocal tests
        try:validate(x)
        except Reject:tests+=1;print("P3_BUDGET_FALSIFIER_PASS",name,flush=True)
        else:raise RuntimeError("FAIL_OPEN "+name)
    x=copy.deepcopy(sources[0]);x["full_root_fen"]="8/8/8/8/8/8/8/8 w - - 0 1";must_reject("ILLEGAL_FEN",x)
    x=copy.deepcopy(sources[0]);x["off_root_white_cp_gap"]=99999;must_reject("SCORE_SIGN",x)
    x=copy.deepcopy(sources[0]);x["requested_equal_depth"]=99;must_reject("UNAUTHORIZED_DEPTH",x)
    x=copy.deepcopy(sources[0]);x["main"]["tt"]["mode"]=2;must_reject("WRONG_TT_SITE",x)
    x=copy.deepcopy(sources[0]);x["off"]["final_MultiPV"]["1"]["score_bound_flag"]="lowerbound";must_reject("CP_BOUND",x)
    chk(tests==5,"MUTATION_TESTS_MISSING")
    result={"schema":"c3x-014-single-study-budget-aware-chess-engine-explanation-v1",
            "formal_stage":"C3X 0.14","P3_internal_only":True,"source_depth_sha256":a.depth_sha,
            "source_node_stress_sha256":NODE_SHA,"game_groups":16,"mutations_rejected":tests,
            "chess_concept_causal_claims_certified":0,"user_learning_benefit_proven":False,"rows":rows}
    Path(a.json_out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    lines=["# C3X 0.14 — Budget-Aware Search Explanation (Internal P3)"]
    for x in rows:lines.extend(["## TCEC "+x["round"]+" — "+x["authority"],x["language_ko"]])
    Path(a.md_out).write_text("\n\n".join(lines)+"\n")
    print("C3X014_BUDGET_EXPLANATION_REAL_PANEL_PASS",json.dumps({
        "n":len(rows),"rejected":tests,"strata":{k:sum(x["authority"]==k for x in rows) for k in set(z["authority"] for z in rows)},
        "source_96":next(x for x in rows if x["round"]=="96.1")}),flush=True)
if __name__=="__main__":main()
