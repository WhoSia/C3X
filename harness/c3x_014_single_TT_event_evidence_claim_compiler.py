#!/usr/bin/env python3
"""C3X 0.14 — evidence-rights compiler for ONE actual TT return suppression.

Consumes SHA-pinned source-only legal worlds and actual C++ Stockfish16
pathway panel. Reports TT event provenance and rival path counters, not
a claim that history/LMR/NNUE or pawn strategy is separately causal.
"""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
import chess

SOURCE_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
PATH_COUNTERS=("picker_main_nodes","picker_main_ttmove","lmr_invoked","lmr_with_reduction",
  "history_quiet_update","history_continuation_update","main_evaluate_calls","main_tt_eval_reads",
  "main_alpha_beta_move_cutoffs","main_tt_save_terminal")
class Refuse(ValueError):pass
def require(x,msg):
    if not x:raise Refuse(msg)
def load(p,sha):
    raw=Path(p).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==sha,"ARTIFACT_SHA256_INVALID")
    return json.loads(raw)
def verify(source,p):
    require(source["schema"]=="c3x-014-legal-black18-alternative-chess-pawn-feature-court-v1","SOURCE_SCHEMA")
    require(source["groups_with_both_worlds"]==14 and not source["P1_sealed_holdout_read"],"SOURCE_HOLDOUT_OR_POPULATION")
    require(p["schema"]=="c3x-014-one-native-TT-return-vs-family-and-mechanism-rival-trace-v1","RAW_ENGINE_SCHEMA")
    require(p["formal_unit"]=="C3X 0.14" and p["one_formal_C3X_study_no_P_substage"],"UNAUTHORIZED_NEW_FORMAL_STAGE")
    require(p["source_worlds_sha256"]==SOURCE_SHA,"DIFFERENT_SOURCE_PANEL")
    require(p["source_game_groups"]==14 and len(p["all_raw_native_run_cells"])==56,"MISSING_ENGINE_CELLS")
    require(p["actual_engine_processes"]==224 and p["source_worlds_two_cold_identical_all_arms"]==28,"COLD_OR_PROCESS_COUNT_FAIL")
    require(p["clean_vs_OFF_control_exact_all_56"],"FAILED_NATIVE_OBSERVATIONAL_SHAM")
    require(not p["P1_sealed_four_games_opened"] and not p["causal_chess_concept_mediation_identified"],"FALSE_CAUSAL_CERT")
    games={c["source_group"]:c for c in source["cases"] if c["concept_preserving_world"] and c["concept_changing_world"]}
    require(len(games)==14,"SOURCE_GROUP_COUNT")
    first={}
    for cell in p["all_raw_native_run_cells"]:
        g=games.get(cell["group"])
        require(g is not None and cell["source_game"]==g["source_game_id"],"SOURCE_GROUP_MISMATCH")
        name=cell["world"];require(name in ("PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"),"BAD_WORLD_LABEL")
        pair=g["root_candidate_pair"];require(pair==cell["legal_white_root_pair"],"DIFFERENT_ROOT_CANDIDATES")
        hist=g["first_17_ply_path_uci"]+[g["original_black18"] if name=="PLAYED_HISTORY" else g["concept_preserving_world"]["black18_uci"]]
        require(hist==cell["full_history"],"HISTORY_NOT_SOURCE_GROUNDED")
        board=chess.Board()
        for move in hist:
            try:board.push_uci(move)
            except (ValueError,chess.IllegalMoveError) as e:raise Refuse("ILLEGAL_SOURCE_HISTORY") from e
        require(board.fen(en_passant="fen")==cell["root_FEN"],"FAKE_CHESS_POSITION")
        require(all(chess.Move.from_uci(m) in board.legal_moves for m in pair),"ILLEGAL_ROOT_MOVE")
        require(set(cell["arms"])=={"CLEAN","OFF","ONE_MAIN","MAIN"},"SOURCE_ARM_SET")
        require(cell["original_CLEAN_vs_OFF_sham_exact"],"SHAM_FALSE_FLAG")
        C,O,U,M=(cell["arms"][a] for a in ("CLEAN","OFF","ONE_MAIN","MAIN"))
        for a,z in (("OFF",O),("ONE_MAIN",U),("MAIN",M)):
            require(z["native_tt"]["mode"]=={"OFF":0,"ONE_MAIN":4,"MAIN":1}[a],"TT_INTERVENTION_MODE")
            require(z["native_tt"]["q_blocked"]==0,"QSEARCH_NOT_HELD_FIXED")
            require(z["native_completed"]["best_completed"]==12,"FIXED_DEPTH_NOT_COMPLETE")
            t=z["native_tt"]["main_blocked"]
            if a=="OFF":require(t==0,"OFF_BLOCKED_TT")
            if a=="ONE_MAIN":require(t==1,"SINGLE_EVENT_COUNT_NOT_ONE")
            if a=="MAIN":require(z["native_tt"]["main_taken"]==0,"FAMILY_INCOMPLETE_SUPPRESSION")
            mc=z["mechanism_path"]
            if a=="ONE_MAIN":
                require(mc["first_blocked_ply"]>=0 and mc["first_blocked_key"]!=0,"FIRST_TT_EVENT_UNPROVEN")
            for k in PATH_COUNTERS:require(mc[k]>=0,"NEGATIVE_MECHANISM_COUNTER")
            require(set(z["ranks"])=={"1","2"},"MISSING_FULL_DEPTH_RANKS")
            r=z["ranks"];require({v["root_move"] for v in r.values()}==set(pair),"WRONG_CANDIDATE_PV")
            require(z["bestmove"]==r["1"]["root_move"],"ROOT_BESTMOVE_RANK_DIVERGENCE")
            exact=all(v["score_kind"]=="cp" and v["score_flag"]=="exact_reported" for v in r.values())
            require((z["signed_white_cp_gap"] is not None)==exact,"BOUND_OR_MATE_AS_EXACT_CP")
            if exact:
                bymove={v["root_move"]:v["score_value_white"] for v in r.values()}
                require(z["signed_white_cp_gap"]==bymove[pair[0]]-bymove[pair[1]],"CP_GAP_SIGN_FRAUD")
        # What the additional instrumentation may NOT corrupt.
        for field in ("bestmove","ranks","signed_white_cp_gap","exact_numeric_cp"):
            require(C[field]==O[field],"CLEAN_VS_OFF_BROKEN")
        for kind,arm in (("one_return",U),("main_family",M)):
            g0=O["signed_white_cp_gap"];g1=arm["signed_white_cp_gap"]
            calc=g1-g0 if g0 is not None and g1 is not None else None
            require(cell[kind+"_gap_shift_cp"]==calc,"TT_SENSITIVITY_FRAUD")
            require(cell[kind+"_UCI_bestmove_changed"]==(O["bestmove"]!=arm["bestmove"]),"ROOT_FLIP_FRAUD")
        if cell["cold_repeat"]==1:
            require(name not in first.setdefault(cell["group"],{}),"DUPLICATE_GROUP_WORLD")
            first[cell["group"]][name]=cell
    require(len(first)==14 and all(set(x)=={"PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"} for x in first.values()),"GROUP_COVERAGE")
    rows=[]
    for g in sorted(first):
        worlds=first[g];c=games[g]
        require(c["original_root_concept"]["double_minus_single"]==
                c["concept_preserving_world"]["pawn_structure_concept"]["double_minus_single"],
                "CHESS_CONCEPT_WAS_NOT_PRESERVED")
        for name,row in sorted(worlds.items()):
            O,U,M=(row["arms"][a] for a in ("OFF","ONE_MAIN","MAIN"))
            deltas={key:{
                  "one_event":U["mechanism_path"][key]-O["mechanism_path"][key],
                  "full_family":M["mechanism_path"][key]-O["mechanism_path"][key]}
                    for key in PATH_COUNTERS}
            firstkey=U["mechanism_path"]
            text=(f"TCEC S29 {row['round']} 경기 {name}: 동일 합법적 기보·폰 개념에서 "
                  f"Stockfish16 TT 최초 조기 반환 단 1회를 차단했다. TT 사건 pos.key={firstkey['first_blocked_key']}, "
                  f"ply={firstkey['first_blocked_ply']}, depth={firstkey['first_blocked_depth']}, "
                  f"bound={firstkey['first_blocked_bound']}, TT 평가={firstkey['first_blocked_tt_value']}, "
                  f"β={firstkey['first_blocked_beta']}. 같은 두 폰 후보의 백 관점 차이 OFF {O['signed_white_cp_gap']}cp, "
                  f"첫 반환 1회 차단 {U['signed_white_cp_gap']}cp, 전체 MAIN 반환 차단 {M['signed_white_cp_gap']}cp. "
                  f"최선수 변경 여부는 첫 반환 {row['one_return_UCI_bestmove_changed']}, "
                  f"전체 반환 {row['main_family_UCI_bestmove_changed']}. "
                  f"MovePicker·history·LMR·정적 NNUE 평가·α–β 계측값은 탐색 경로의 연동 증거이지 "
                  "각각의 독립적 원인이나 체스 전략적 개념 인과 매개가 아니다.")
            rows.append({"source_game_group":g,"source_round":row["round"],"legal_world":name,
              "original_real_chess_position_FEN":row["root_FEN"],
              "ONE_MAIN_first_real_TT_return_key":firstkey["first_blocked_key"],
              "ONE_MAIN_first_TT_ply":firstkey["first_blocked_ply"],
              "ONE_MAIN_first_TT_depth":firstkey["first_blocked_depth"],
              "first_TT_site_event_static_identity_fixed_between_modes":False,
              "TT_ONE_MAIN_total_cutoffs_blocked":U["native_tt"]["main_blocked"],
              "score_OFF_ONE_MAIN_MAIN":[O["signed_white_cp_gap"],U["signed_white_cp_gap"],M["signed_white_cp_gap"]],
              "ONE_MAIN_categorical_root_label_change":row["one_return_UCI_bestmove_changed"],
              "full_MAIN_categorical_root_label_change":row["main_family_UCI_bestmove_changed"],
              "counter_deltas_relative_to_OFF":deltas,"chess_concept_changed_under_TT_intervention":False,
              "isolated_competing_mediator_causality_identified":False,
              "engine_source_verified_Korean_explanation":text})
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--legal-world-source",required=True);p.add_argument("--native-panel",required=True)
    p.add_argument("--native-sha",required=True);p.add_argument("--out-json",required=True);p.add_argument("--out-md",required=True)
    a=p.parse_args();source=load(a.legal_world_source,SOURCE_SHA);native=load(a.native_panel,a.native_sha)
    rows=verify(source,native)
    require(len(rows)==28,"MISSING_ALL_GENUINE_WORLD_EXPLANATIONS")
    tests=0
    def reject(name,src,panel):
        nonlocal tests
        try:verify(src,panel)
        except Refuse:tests+=1;print("C3X014_ONE_EVENT_CLAIM_FALSIFIER_PASS",name,flush=True)
        else:raise RuntimeError("TT_EVENT_AUTHORITY_FAIL_OPEN_"+name)
    bad=copy.deepcopy(native);bad["causal_chess_concept_mediation_identified"]=True
    reject("FAKE_CHESS_CAUSAL_CERT",source,bad)
    bad=copy.deepcopy(native);bad["all_raw_native_run_cells"][0]["arms"]["ONE_MAIN"]["native_tt"]["main_blocked"]=2
    reject("MORE_THAN_ONE_TT_RETURN_BLOCKED",source,bad)
    bad=copy.deepcopy(native);bad["all_raw_native_run_cells"][0]["full_history"]=["a1a8"]
    reject("ILLEGAL_SOURCE_CHESS_PATH",source,bad)
    bad=copy.deepcopy(native);bad["all_raw_native_run_cells"][0]["arms"]["ONE_MAIN"]["ranks"]["1"]["score_value_white"]=88888
    reject("SCORE_SIGN_OR_RANK_CORRUPTION",source,bad)
    bad=copy.deepcopy(source);one=next(z for z in bad["cases"] if z["concept_preserving_world"] is not None)
    one["concept_preserving_world"]["pawn_structure_concept"]["double_minus_single"]["passed_pawn"]=999
    reject("FALSE_CHESS_CONCEPT_PRESERVATION",bad,native)
    require(tests==5,"FALSIFIER_COURT_INCOMPLETE")
    summary={
      "schema":"c3x-014-single-real-TT-event-competing-pathway-explanation-ledger-v1",
      "one_formal_research_unit":"C3X 0.14","P_checkpoints_not_formal_substages":True,
      "legal_source_sha256":SOURCE_SHA,"native_panel_sha256":a.native_sha,
      "source_groups":14,"grounded_chess_worlds":28,"falsifiers_passed":tests,
      "chess_strategy_concept_mediation_certified":0,"separate_rival_path_causal_certificates":0,
      "human_educational_benefit_certified":0,"rows":rows}
    Path(a.out_json).write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    lines=["# C3X 0.14 — One Actual TT Return, Rival Search Path and Chess-Concept-Held-Fixed Evidence",
           "ONE formal research stage only; 14 development game groups and 28 historically legal boards."]
    for z in rows:lines.extend(["## TCEC "+z["source_round"]+" — "+z["legal_world"],z["engine_source_verified_Korean_explanation"]])
    Path(a.out_md).write_text("\n\n".join(lines)+"\n")
    print("C3X014_SINGLE_EVENT_TYPED_EVIDENCE_COURT_PASS",json.dumps({
      "groups":14,"worlds":28,"falsifiers":tests,
      "one_tt_root_label_changes":sum(z["ONE_MAIN_categorical_root_label_change"] for z in rows),
      "family_root_label_changes":sum(z["full_MAIN_categorical_root_label_change"] for z in rows)}),flush=True)
if __name__=="__main__":main()
