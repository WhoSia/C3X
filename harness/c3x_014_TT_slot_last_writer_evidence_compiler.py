#!/usr/bin/env python3
"""C3X 0.14 — fail-closed TT writer/consumer last-slot ancestry statement compiler.

Does NOT infer a full causal ancestry, causal pawn mediator, TT hash collision
solely from sidecar key mismatch, or causal mediation by LMR/history/NNUE.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import chess

LEGAL_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
PARENT_SHA="afd48ceb040668c53609d8d5bd78d7a9b781243044cd4187a87896929ef0dd6b"
WRITER_SITE={0:"출처 미확인",1:"테이블베이스",2:"정적 평가값 저장",
  3:"ProbCut",4:"메인 탐색 종료",5:"qsearch 스탠드패트",6:"qsearch 종료"}
class Reject(ValueError):pass
def check(x,label):
    if not x:raise Reject(label)
def file(path,sha):
    b=Path(path).read_bytes()
    check(hashlib.sha256(b).hexdigest()==sha,"WRONG_SOURCE_SHA256")
    return json.loads(b)
def verified(legal,parent,record):
    check(record["schema"]=="c3x-014-source-native-TT-physical-slot-last-writer-and-single-consumer-v1","WRONG_LINEAGE_SCHEMA")
    check(record["formal_research_unit"]=="C3X 0.14" and record["internal_checkpoint_only"],"NEW_STAGE_FORBIDDEN")
    check(record["actual_source_only_sha256"]==LEGAL_SHA and record["previous_exact_224_process_court_sha256"]==PARENT_SHA,"SOURCE_NOT_PINNED")
    check(record["source_game_groups"]==14 and record["legally_reached_worlds"]==28,"WRONG_SOURCE_GROUP_SCOPE")
    check(record["actual_engine_processes"]==224 and record["complete_all_four_arms_parent_native_exact_equivalence"]==224,"NOT_OBSERVATIONAL_SHAM_EQUIVALENT")
    check(record["technical_cold_repro_worlds"]==28 and record["all_ONE_MAIN_blocked_exactly_one_return"]==56,"FAILED_INTERVENTION_OR_REPRO")
    check(not record["P1_four_sealed_holdout_groups_opened"],"UNSEALED_HOLDOUT_NOT_AUTHORIZED")
    check(not record["causal_chess_concept_mediation_certified"],"UNSUPPORTED_CHESS_CAUSAL_CLAIM")
    check(not record["causal_history_lmr_NNUE_alpha_beta_mediators_independently_identified"],"UNSUPPORTED_RIVAL_MEDIATION_CLAIM")
    check(len(record["actual_raw_world_runs"])==56,"RAW_WORLD_CELL_COUNT")
    check(len(parent["all_raw_native_run_cells"])==56 and parent["source_game_groups"]==14,"WRONG_PARENT_N")
    source={c["source_group"]:c for c in legal["cases"] if c["concept_preserving_world"] and c["concept_changing_world"]}
    check(len(source)==14,"INVALID_SOURCE_WORLDS")
    pmap={(c["group"],c["world"],c["cold_repeat"]):c for c in parent["all_raw_native_run_cells"]}
    for r in record["actual_raw_world_runs"]:
        g=source.get(r["source_group"])
        check(g is not None and r["source_round"]==g["official_original_game_headers"]["Round"],"WRONG_SOURCE_ID")
        check(r["world"] in ("PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"),"UNFROZEN_WORLD")
        original_black=g["original_black18"]
        sham_black=g["concept_preserving_world"]["black18_uci"]
        end=original_black if r["world"]=="PLAYED_HISTORY" else sham_black
        hist=g["first_17_ply_path_uci"]+[end]
        check(r["history_18_plies"]==hist and len(hist)==18,"SOURCE_HISTORY_TAMPERED")
        b=chess.Board()
        try:
            for m in hist:b.push_uci(m)
        except ValueError as e:raise Reject("ILLEGAL_HISTORY") from e
        check(b.is_valid() and b.fen(en_passant="fen")==r["full_root_fen"],"WRONG_FEN")
        check(r["white_root_candidates"]==g["root_candidate_pair"] and all(chess.Move.from_uci(m) in b.legal_moves for m in r["white_root_candidates"]),"ILLEGAL_OR_SWITCHED_ROOT")
        p=pmap.get((r["source_group"],r["world"],r["cold_repeat"]))
        check(p is not None and r["all_four_arms_original_224_run_behavior_identical"],"PRIOR_224_REPLAY_NOT_EQUAL")
        check(r["white_cp_OFF_ONE_MAIN_MAIN"]==[p["arms"][x]["signed_white_cp_gap"] for x in ("OFF","ONE_MAIN","MAIN")],"CP_GAP_NOT_PARENT_NATIVE")
        check(r["bestmoves_OFF_ONE_MAIN_MAIN"]==[p["arms"][x]["bestmove"] for x in ("OFF","ONE_MAIN","MAIN")],"BESTMOVE_FRAUD")
        for typ,field in (("ONE_MAIN","one_first_blocked_consumer_and_last_writer"),("MAIN","main_family_first_blocked_consumer_and_last_writer")):
            d=r[field]
            check(d is not None,"MISSING_REAL_TT_CONSUMER")
            old=p["arms"][typ]["mechanism_path"]
            for k in ("first_blocked_key","first_blocked_ply","first_blocked_depth","first_blocked_bound","first_blocked_tt_value","first_blocked_beta"):
                check(d[k]==old[k],"CONSUMER_EVENT_ALTERED")
            check(d["first_writer_site"] in WRITER_SITE,"FORGED_WRITER_SITE")
            check(d["first_writer_known"] in (0,1) and d["first_writer_key_match"] in (0,1),"MALFORMED_WRITER_CLASS")
            check(d["first_writer_known"] or (not d["first_writer_key_match"] and d["first_writer_site"]==0),"UNKNOWN_WRITER_FALSE_PROMOTION")
            check(not d["first_writer_key_match"] or (d["first_writer_known"] and d["first_writer_full_key"]==d["first_blocked_key"]),"FALSE_FULL_64BIT_KEY_MATCH")
            check(d["first_writer_sequence"]>=0 and d["first_writer_slot_replacements"]>=0 and d["first_writer_slot_saves"]>=0,"IMPOSSIBLE_WRITER_COUNTS")
            check(d["first_writer_slot_saves"]>=d["first_writer_slot_replacements"],"MORE_REPLACEMENTS_THAN_SAVES")
            check(d["first_writer_site"]!=0 or not d["first_writer_key_match"],"UNKNOWN_SITE_CANNOT_FULLY_ATTRIBUTE")
        for arm in ("OFF","ONE_MAIN","MAIN"):
            payload=r["per_arm_mechanism_counter_payload"][arm]
            for k in ("picker_main_nodes","lmr_invoked","history_quiet_update",
                     "main_evaluate_calls","main_alpha_beta_move_cutoffs","main_tt_save_terminal"):
                check(payload[k]==p["arms"][arm]["mechanism_path"][k],"COMPETING_PATH_COUNTER_TAMPER")
        check(r["one_slot_summary"]["saves"]>0 and r["one_slot_summary"]["mapped_slots"]>0,"PROVENANCE_NOT_RUNNING")
    first=[r for r in record["actual_raw_world_runs"] if r["cold_repeat"]==1]
    check(len(first)==28,"NONINDEPENDENT_COLD_MULTIPLICITY")
    rows=[]
    for r in first:
        d=r["one_first_blocked_consumer_and_last_writer"]
        if not d["first_writer_known"]:
            verdict="WRITER_UNOBSERVED";detail="해당 TT 슬롯의 마지막 전체 저장자를 계측 자료에서 확인할 수 없었다."
        elif d["first_writer_key_match"]:
            verdict="LAST_WRITER_FULL_KEY_MATCH";detail="물리적 슬롯의 마지막 저장 전체 64비트 키와 이 TT 반환 요청 키가 일치했다."
        else:
            verdict="LAST_WRITER_KEY_MISMATCH";detail="물리적 슬롯에 마지막 저장된 전체 키와 소비 요청 키가 달랐다. 이 결과만으로 실제 해시 충돌의 원인을 확정할 수 없다."
        site=WRITER_SITE[d["first_writer_site"]]
        o,u,m=r["white_cp_OFF_ONE_MAIN_MAIN"]
        korean=(f"TCEC S29 {r['source_round']} 경기 {r['world']}: 합법적 전체 기보 이력을 고정한 채 최초 MAIN TT 반환 한 건만 억제했다. "
                f"소비 TT 키 {d['first_blocked_key']}, 탐색 깊이 {d['first_blocked_depth']}·ply {d['first_blocked_ply']}, "
                f"bound {d['first_blocked_bound']}, TT 값 {d['first_blocked_tt_value']}, β {d['first_blocked_beta']}. "
                f"이 물리 슬롯의 마지막 저장 경로는 {site}이며, 저장 순번 {d['first_writer_sequence']}, "
                f"기존과 다른 전체 키로 재사용된 횟수 {d['first_writer_slot_replacements']}이다. {detail} "
                f"백 후보 평가차 OFF {o}cp → 한 건 차단 {u}cp → 전체 MAIN 차단 {m}cp. "
                "마지막 저장자의 계측은 검색의 모든 선행 원인, 폰 전략의 인과 효과, LMR/history/NNUE의 개별 매개성을 입증하지 않는다.")
        rows.append({"source_game_group":r["source_group"],"round":r["source_round"],
           "world":r["world"],"physical_tt_last_writer_verdict":verdict,
           "last_writer_source_site_code":d["first_writer_site"],
           "last_writer_source_site":site,
           "last_writer_full_key_matched_consumer":bool(d["first_writer_key_match"]),
           "last_writer_slot_reuses_other_key":d["first_writer_slot_replacements"],
           "last_writer_record_sequence":d["first_writer_sequence"],
           "program_local_single_return_causal_test_performed":True,
           "chess_concept_mediation_certified":False,
           "full_TT_entry_causal_ancestry_certified":False,
           "mechanism_counter_changes_separately_causal_identified":False,
           "historical_source_anchored_korean_explanation":korean})
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--worlds",required=True);p.add_argument("--parent",required=True)
    p.add_argument("--lineage",required=True);p.add_argument("--lineage-sha",required=True)
    p.add_argument("--out-json",required=True);p.add_argument("--out-md",required=True)
    a=p.parse_args()
    worlds=file(a.worlds,LEGAL_SHA);parent=file(a.parent,PARENT_SHA);lineage=file(a.lineage,a.lineage_sha)
    rows=verified(worlds,parent,lineage)
    check(len(rows)==28,"INCOMPLETE_SOURCE_GROUNDED_EXPLANATIONS")
    n=0
    def must_fail(label,w=worlds,p=parent,l=lineage):
        nonlocal n
        try:verified(w,p,l)
        except Reject:n+=1;print("C3X014_LAST_TT_WRITER_CLAIM_FALSIFIER_PASS",label,flush=True)
        else:raise RuntimeError("TT_LAST_WRITER_CLAIM_FAIL_OPEN "+label)
    bad=copy.deepcopy(lineage);bad["causal_chess_concept_mediation_certified"]=True
    must_fail("FALSE_CAUSAL_CHESS_MEDIATOR",l=bad)
    bad=copy.deepcopy(lineage);bad["actual_raw_world_runs"][0]["one_first_blocked_consumer_and_last_writer"]["first_writer_key_match"]=1
    bad["actual_raw_world_runs"][0]["one_first_blocked_consumer_and_last_writer"]["first_writer_full_key"]=0
    must_fail("FALSE_FULL_KEY_MATCH",l=bad)
    bad=copy.deepcopy(lineage);bad["actual_raw_world_runs"][0]["one_first_blocked_consumer_and_last_writer"]["first_writer_site"]=99
    must_fail("INVENTED_TT_WRITER_SITE",l=bad)
    bad=copy.deepcopy(lineage);bad["actual_raw_world_runs"][0]["history_18_plies"]=["a1a8"]
    must_fail("FAKE_CHESS_HISTORY",l=bad)
    bad=copy.deepcopy(lineage);bad["actual_raw_world_runs"][0]["white_cp_OFF_ONE_MAIN_MAIN"]=[999,999,999]
    must_fail("FORGED_CANDIDATE_SCORES",l=bad)
    check(n==5,"UNRUN_OR_FAILED_FALSIFIERS")
    summary={
        "schema":"c3x-014-source-native-TT-physical-slot-writer-evidence-ledger-v1",
        "only_formal_research_unit":"C3X 0.14","P_checkpoints_are_internal_only":True,
        "lineage_native_raw_sha256":a.lineage_sha,"world_source_sha256":LEGAL_SHA,
        "prior_224_native_parent_sha256":PARENT_SHA,
        "independent_game_groups":14,"world_descriptions":28,
        "last_writer_match_world_count":sum(r["physical_tt_last_writer_verdict"]=="LAST_WRITER_FULL_KEY_MATCH" for r in rows),
        "last_writer_mismatch_world_count":sum(r["physical_tt_last_writer_verdict"]=="LAST_WRITER_KEY_MISMATCH" for r in rows),
        "last_writer_unknown_world_count":sum(r["physical_tt_last_writer_verdict"]=="WRITER_UNOBSERVED" for r in rows),
        "falsification_cases_rejected":n,"chess_concept_causal_certificates":0,
        "complete_search_ancestry_certificates":0,"human_learning_certificates":0,
        "rows":rows}
    Path(a.out_json).write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    md=["# C3X 0.14 — Stockfish16 Native Physical TT Entry Last Writer and Consumer",
        "ONE research unit C3X 0.14. Source-grounded lineage is limited to last writer of the actual physical TT slot."]
    for r in rows:
        md.extend([f"## TCEC {r['round']} / {r['world']}",r["historical_source_anchored_korean_explanation"]])
    Path(a.out_md).write_text("\n\n".join(md)+"\n")
    print("C3X014_LAST_TT_WRITER_CAUSAL_AUTHORITY_GATE_PASS",json.dumps({
        "games":14,"worlds":len(rows),"matched":summary["last_writer_match_world_count"],
        "mismatch":summary["last_writer_mismatch_world_count"],
        "unobserved":summary["last_writer_unknown_world_count"],"falsifiers":n}),flush=True)
if __name__=="__main__":main()
