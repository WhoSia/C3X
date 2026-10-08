#!/usr/bin/env python3
"""C3X 0.14 — Legal-history chess concept vs native TT typed evidence gate.

This compiler describes true chess board features and source-native engine
responses, but rejects the unjustified leap to isolated causal mediation.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import chess
from c3x_014_legal_black_reply_concept_source_freeze import vector

SOURCE_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
class Refuse(ValueError):pass

def require(x,why):
    if not x:raise Refuse(why)
def load(path,sha):
    b=Path(path).read_bytes()
    require(hashlib.sha256(b).hexdigest()==sha,"RAW_BYTE_SHA_INVALID")
    return json.loads(b)
def auth(source,panel):
    require(source["schema"]=="c3x-014-legal-black18-alternative-chess-pawn-feature-court-v1","BAD_CONCEPT_SCHEMA")
    require(panel["schema"]=="c3x-014-historical-legal-concept-black-response-native-tt-challenge-v1","BAD_ENGINE_SCHEMA")
    require(panel["source_json_sha256"]==SOURCE_SHA,"NOT_SAME_CONCEPT_SOURCE")
    require(not source["P1_sealed_holdout_read"] and not panel["P1_sealed_holdout_accessed"],"HOLDOUT_TAMPER")
    require(panel["source_groups"]==16 and len(panel["all_cells"])==120,"NOT_THE_COMPLETE_COURT")
    require(panel["original_vs_OFF_sham_exact_out_of120"]==120,"FAILED_NATIVE_SHAMS")
    require(panel["cold_exact_pairs_out_of60"]==60,"NONDETERMINISTIC_NATIVE_OUTPUT")
    require(panel["chess_domain_mediation_causally_identified"] is False,"FALSE_CAUSAL_CERTIFICATE")
    require(len(source["cases"])==16 and len(panel["all_game_concept_and_mechanism_details"])==16,"MISSING_SOURCE_GROUP")
    srcs={r["source_group"]:r for r in source["cases"]}
    psummary={r["source_group"]:r for r in panel["all_game_concept_and_mechanism_details"]}
    require(set(srcs)==set(psummary),"SOURCE_GROUP_JOIN_INCOMPLETE")
    first={}
    for cell in panel["all_cells"]:
        require(cell["sham_exact"],"INVALID_NATIVE_SHAM_CELL")
        require(cell["source_game_id"]==srcs[cell["group"]]["source_game_id"],"GAME_PROVENANCE_MISMATCH")
        require(cell["main"]["native_tt"]["mode"]==1,"MAIN_NATIVE_MODE_WRONG")
        require(cell["main_masked_TT_cutoffs"]==cell["main"]["native_tt"]["main_blocked"],"TT_MASK_COUNT_WRONG")
        require(cell["off"]["native_tt"]["mode"]==0,"OFF_NATIVE_MODE_WRONG")
        require(cell["off"]["native_tt"]["main_blocked"]==0,"NATIVE_SHAM_TT_MASKED")
        require(cell["main"]["native_completed"]["best_completed"]==12,"MAIN_NOT_COMPLETED_DEPTH12")
        require(cell["off"]["native_completed"]["best_completed"]==12,"OFF_NOT_COMPLETED_DEPTH12")
        pair=cell["world_source"]["pair"]; fen=cell["world_source"]["root_fen"]
        chess_b=chess.Board()
        for m in cell["world_source"]["full_18_ply_history"]:
            try:chess_b.push_uci(m)
            except (ValueError,chess.IllegalMoveError) as e:raise Refuse("ILLEGAL_HISTORICAL_PATH") from e
        require(chess_b.fen(en_passant="fen")==fen,"FALSE_HISTORICAL_FEN")
        require(chess_b.is_valid() and chess_b.turn==chess.WHITE,"INVALID_CHESS_ROOT")
        require(len(pair)==2 and all(chess.Move.from_uci(m) in chess_b.legal_moves for m in pair),"ILLEGAL_PAWN_CANDIDATE")
        for side in ("off","main"):
            z=cell[side]
            require(z["depth"]==12 and set(z["ranks"])=={"1","2"},"INVALID_DEPTH_SCORE")
            scores=list(z["ranks"].values())
            require({x["move"] for x in scores}==set(pair),"INVALID_RANKING_MOVES")
            require(z["bestmove"]==z["ranks"]["1"]["move"],"BESTMOVE_RANK_MISMATCH")
            numerical=all(x["kind"]=="cp" and x["bound"]=="exact_reported" for x in scores)
            require((z["signed_white_gap_cp"] is not None)==numerical,"MATE_OR_BOUND_CP_MISUSE")
            if numerical:
                bymove={x["move"]:x["value_white"] for x in scores}
                require(z["signed_white_gap_cp"]==bymove[pair[0]]-bymove[pair[1]],"WRONG_SIGNED_CP_GAP")
        x,y=cell["off"]["signed_white_gap_cp"],cell["main"]["signed_white_gap_cp"]
        if x is not None and y is not None:
            require(cell["gap_shift_white_cp"]==y-x,"WRONG_TREATMENT_SHIFT")
            require(cell["strict_white_cp_gap_sign_inverted"]==(x*y<0),"MISLABELED_INVERSION")
        require(cell["UCI_bestmove_changed"]==(cell["off"]["bestmove"]!=cell["main"]["bestmove"]),"MISLABELED_ROOT_FLIP")
        if cell["cold_repeat"]==1:first.setdefault(cell["group"],{})[cell["world"]]=cell
    require(len(first)==16,"INCOMPLETE_COLD_FIRST_PANEL")
    rows=[]
    for g,src in srcs.items():
        worlds=first[g]
        require(set(worlds)>={"PLAYED_HISTORY","PLAYED_FEN_ONLY"},"ORIGINAL_CONTEXT_MISSING")
        pre=chess.Board()
        for move in src["first_17_ply_path_uci"]:pre.push_uci(move)
        require(pre.fen(en_passant="fen")==src["first_17_ply_fen"],"PREDECESSOR_FEN_CORRUPT")
        for key,label in (("concept_changing_world","CONCEPT_CHANGE_HISTORY"),
                          ("concept_preserving_world","CONCEPT_SHAM_HISTORY")):
            w=src[key]
            if w is None:
                require(label not in worlds,"GHOST_WORLD")
                continue
            require(label in worlds,"MISSING_WORLD")
            b=pre.copy(stack=True);b.push_uci(w["black18_uci"])
            require(b.fen(en_passant="fen")==w["root_full_FEN"],"BAD_COUNTERFACTUAL_FEN")
            require(vector(b,src["root_candidate_pair"])==w["pawn_structure_concept"],"FORGED_CHESS_CONCEPT_FEATURE")
        true=worlds["PLAYED_HISTORY"]
        change=worlds.get("CONCEPT_CHANGE_HISTORY")
        sham=worlds.get("CONCEPT_SHAM_HISTORY")
        pair=src["root_candidate_pair"]
        d1=change["gap_shift_white_cp"]-true["gap_shift_white_cp"] if change and change["gap_shift_white_cp"] is not None and true["gap_shift_white_cp"] is not None else None
        d0=sham["gap_shift_white_cp"]-true["gap_shift_white_cp"] if sham and sham["gap_shift_white_cp"] is not None and true["gap_shift_white_cp"] is not None else None
        did=d1-d0 if d1 is not None and d0 is not None else None
        feats=src["targeted_concept_delta"] or {}
        sentence=(f"TCEC S29 {src['official_original_game_headers']['Round']} 경기, 같은 실제 17반수수순에서 "
          f"흑의 실제 수 {src['original_black18']}과 합법 대안 "
          f"{src['concept_changing_world']['black18_uci'] if src['concept_changing_world'] else '없음'}을 비교했다. "
          f"백 후보 {pair[0]} / {pair[1]}의 폰 응수 개념 대비를 바꾼 항목은 {', '.join(feats.keys()) if feats else '해당 없음'}이다. "
          f"실제 이력 세계의 MAIN TT 차단 평가차 변화는 {true['gap_shift_white_cp']}cp, "
          f"개념 변화 대안은 {change['gap_shift_white_cp'] if change else '대안 없음'}cp, "
          f"개념 유지 대조 대안은 {sham['gap_shift_white_cp'] if sham else '대안 없음'}cp였다. "
          f"두 대안의 TT 반응 차이는 {did if did is not None else '계산 불가'}cp로 관측됐다. "
          "그러나 다른 흑의 수는 전술, NNUE, 검색 순서 및 TT 키도 바꾸므로 체스 개념 하나의 인과 매개 효과라고 인정할 수 없다.")
        rows.append({"group":g,"round":src["official_original_game_headers"]["Round"],
          "chess_concept_changed":bool(change),"concept_sham_available":bool(sham),
          "changed_feature_names":sorted(feats),"original_TT_gap_shift":true["gap_shift_white_cp"],
          "concept_changed_world_TT_gap_shift":change["gap_shift_white_cp"] if change else None,
          "semantic_sham_world_TT_gap_shift":sham["gap_shift_white_cp"] if sham else None,
          "concept_changed_minus_sham_response_cp":did,
          "history_dropped_changes_OFF_output":not psummary[g]["history_vs_FEN_OFF_same_output"],
          "isolated_mediator_causal_certificate":False,
          "engine_evidence_bounded_Korean_description":sentence})
    return sorted(rows,key=lambda r:r["round"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--concepts",required=True);p.add_argument("--native-panel",required=True);p.add_argument("--native-sha",required=True)
    p.add_argument("--out-json",required=True);p.add_argument("--out-md",required=True)
    a=p.parse_args()
    s=load(a.concepts,SOURCE_SHA)
    e=load(a.native_panel,a.native_sha)
    rows=auth(s,e)
    require(len(rows)==16,"EXPLANATION_SOURCE_COUNT_WRONG")
    tests=0
    def reject(label,source,panel):
        nonlocal tests
        try:auth(source,panel)
        except Refuse:tests+=1;print("C3X014_CHESS_CONCEPT_AUTHORITY_FALSIFIER_PASS",label,flush=True)
        else:raise RuntimeError("FALSE_CONCEPT_CAUSATION_ALLOWED "+label)
    fake=copy.deepcopy(e);fake["chess_domain_mediation_causally_identified"]=True
    reject("FALSE_CAUSAL_PROMOTION",s,fake)
    fake=copy.deepcopy(e);fake["all_cells"][0]["gap_shift_white_cp"]=999999
    reject("TREATMENT_GAP_CORRUPTION",s,fake)
    fake=copy.deepcopy(e);fake["all_cells"][0]["world_source"]["full_18_ply_history"]=["a1a8"]
    reject("ILLEGAL_HISTORICAL_CHESS_PATH",s,fake)
    fake=copy.deepcopy(s)
    example=next(c for c in fake["cases"] if c["concept_changing_world"])
    example["concept_changing_world"]["pawn_structure_concept"]["single"]["passed_pawn"]=99
    reject("FORGED_PAWN_CONCEPT",fake,e)
    fake=copy.deepcopy(e);fake["all_cells"][0]["main"]["native_tt"]["mode"]=2
    reject("WRONG_NATIVE_TT_SITE",s,fake)
    require(tests==5,"REQUIRED_FALSE_CLAIM_TESTS_MISSING")
    ledger={"schema":"c3x-014-legally-reached-chess-concept-vs-TT-source-grounded-ledger-v1",
       "formal_stage":"C3X 0.14","P_labels_are_internal_checkpoints_only":True,
       "concept_source_sha256":SOURCE_SHA,"engine_native_source_sha256":a.native_sha,
       "game_groups":16,"cases_with_concept_changes":sum(x["chess_concept_changed"] for x in rows),
       "tampering_and_causal_promotion_rejections":tests,
       "isolated_chess_concept_causality_established":False,"educational_benefit_demonstrated":False,
       "rows":rows}
    Path(a.out_json).write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n")
    md=["# C3X 0.14 — Genuine Legal Chess-History Concept and Native TT Evidence",
       "This is an internal work section of ONE C3X 0.14 project. Observed chess features are proxies, not identified causal mediators."]
    for r in rows:md.extend(["## Official TCEC S29 "+r["round"],r["engine_evidence_bounded_Korean_description"]])
    Path(a.out_md).write_text("\n\n".join(md)+"\n")
    print("C3X014_LEGAL_CHESS_CONCEPT_TYPED_PRODUCT_PASS",json.dumps({
        "games":len(rows),"changed":ledger["cases_with_concept_changes"],
        "tamper_falsifiers":tests,
        "history_sensitive_groups":sum(x["history_dropped_changes_OFF_output"] for x in rows)}),flush=True)
if __name__=="__main__":main()
