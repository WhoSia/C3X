"""I10-P5 empirical search-PV -> chess-literate wording ceiling.

Actual ORIGINAL SF16 cold O/F/Z native words are source identity-checked;
this module never certifies a human STRATEGIC concept or upgrades P16.
Shows legal source PV SAN branching and straightforward board geometry
AFTER different hypothetical moves, not a human-intention theorem.
"""
from __future__ import annotations
import hashlib,json
from typing import Any
import chess

SOURCE_NATIVE_JSON_SHA="62513713811f9758c260d44a6902b52363c3ba33e260a4e5994742d15e819187"

def replay(fen:str,pv:list[str])->tuple[list[str],chess.Board]:
    b=chess.Board(fen)
    if not b.is_valid():raise ValueError("INVALID_ORIGINAL_CHESS_FEN")
    sans=[]
    for u in pv:
        m=chess.Move.from_uci(u)
        if m not in b.legal_moves:raise ValueError("NATIVE_PV_HAS_ILLEGAL_CHESS_MOVE")
        sans.append(b.san(m))
        b.push(m)
    return sans,b

def board_proxies(board:chess.Board,own:bool)->dict[str,int]:
    center=(chess.D4,chess.E4,chess.D5,chess.E5)
    opp_king=board.king(not own)
    if opp_king is None:raise ValueError("MISSING_KING")
    return {
      "own_center_attacked_count":sum(board.is_attacked_by(own,s) for s in center),
      "own_king_ring_pressure":sum(board.is_attacked_by(own,s)
          for s in [opp_king]+list(board.attacks(opp_king))),
      "own_material_on_board":sum(len(board.pieces(p,own)) for p in chess.PIECE_TYPES),
    }

def audit(native:dict[str,Any])->dict[str,Any]:
    if native.get("schema")!="c3x-i10-p5-new-Olympiad-original-SF16-eight-game-source-order-O-F-Z-native-v1":
        raise ValueError("SOURCE_NATIVE_SCHEMA_OR_PROVENANCE_MISSING")
    if len(native.get("worlds",[]))!=8:raise ValueError("HISTORIC_SOURCE_WORLD_COUNT_WRONG")
    worlds=[]
    for x in native["worlds"]:
        cells=x["source_world_cells"]
        if set(cells)!=set(["O","F","Z"]) or cells["O"]["uci"]!=cells["Z"]["uci"]:
            raise ValueError("NO_CONTACT_SHAM_COMPARISON_BROKEN")
        if cells["F"]["physical_source"]["source_reorder"]!=1:
            raise ValueError("SOURCE_INTERVENTION_NO_CONTACT")
        o=cells["O"]["uci"];f=cells["F"]["uci"]
        if o["bestmove"]!=f["bestmove"]:
            raise ValueError("UNEXPECTED_ROOT_BESTMOVE_FLIP_NOT_IN_FROZEN_EIGHT")
        O=o["pv"];F=f["pv"]
        san_O,_=replay(x["fen"],O);san_F,_=replay(x["fen"],F)
        if not O or not F or O[0]!=o["bestmove"] or F[0]!=f["bestmove"]:
            raise ValueError("ROOT_PV_BESTMOVE_NOT_LEGAL_OR_SAME")
        n=0
        for a,b in zip(O,F):
            if a!=b:break
            n+=1
        if O==F and n!=len(O):raise ValueError("COMMON_PREFIX_INCONSISTENCY")
        if len(O)>1 and len(F)>1 and O[1]!=F[1]:
            raise ValueError("FROZEN_NATIVE_FIRST_OPPONENT_REPLY_CHANGED_UNEXPECTEDLY")
        original=chess.Board(x["fen"]);own=original.turn
        baseline_proxy=board_proxies(original,own)
        # Read hypothetical board after the two lines' first distinguishable
        # move, not after their full depth (different line lengths confound).
        horizon=min(n+1,len(O),len(F))
        b1=chess.Board(x["fen"]);b2=chess.Board(x["fen"])
        for u in O[:horizon]:b1.push_uci(u)
        for u in F[:horizon]:b2.push_uci(u)
        proxies_O=board_proxies(b1,own)
        proxies_F=board_proxies(b2,own)
        deltas={k:proxies_F[k]-proxies_O[k] for k in proxies_O}
        if O!=F:
            text=(f"원본 Stockfish 16에서 {san_O[0]} 선택은 유지됐지만, "
                  f"루트 탐색 순서 개입 뒤 출력된 탐색 변형은 "
                  f"{n+1}번째 반수부터 달라졌습니다. "
                  f"원본 변형: {' '.join(san_O[:min(n+3,len(san_O))])}; "
                  f"개입 변형: {' '.join(san_F[:min(n+3,len(san_F))])}. "
                  "이는 특정 깊이의 탐색 경로가 달라진 관측이며, "
                  "체스 전략적 원인이나 상대의 필연적 응수를 증명하지 않습니다.")
        else:
            text=(f"기록된 원본 엔진 분석에서 {san_O[0]}의 루트 순서 개입은 "
                  "실제로 실행됐지만, 표시된 주 변형과 최종 추천 수는 동일했습니다. "
                  "전략적 인과 효과가 입증된 것은 아닙니다.")
        worlds.append({
            "game_id":x["game_id"],"original_ply":x["ply"],"played_move":x["played_san"],
            "native_source_root_reordered":True,
            "root_bestmove_original":o["bestmove"],"root_bestmove_after_intervention":f["bestmove"],
            "source_PV_legal_replay_original_san":san_O,
            "source_PV_legal_replay_intervened_san":san_F,
            "source_PV_common_prefix_halfmoves":n,
            "first_opponent_reply_changed":len(O)>1 and len(F)>1 and O[1]!=F[1],
            "hypothetical_chess_board_compare_horizon_halfmoves":horizon,
            "source_original_board_proxies":baseline_proxy,
            "hypothetical_branch_difference_proxies":deltas,
            "human_readable_korean_bounded_report":text,
            "source_intervention_causal_observation":"ROOT_ORDER_TO_DISPLAYED_PV_ONLY",
            "human_semantic_chess_concept_caused":False,
            "true_opponent_response_inferred":False,
            "chess_causing_engine_preference_identified":False,
            "source_event_mechanism_specificity":"EXACT_ROOT_ORDER_NOT_TT_SEE_CAUSAL_PATH",
        })
    pvs=sum(x["source_PV_legal_replay_original_san"]!=x["source_PV_legal_replay_intervened_san"] for x in worlds)
    return {
      "schema":"c3x-i10-p5-original-source-native-search-PV-chess-semantics-ceiling-v1",
      "source_original_game_groups":len(worlds),
      "native_source_root_reordered":8,
      "bestmove_unchanged":8,
      "first_opponent_reply_unchanged":sum(not x["first_opponent_reply_changed"] for x in worlds),
      "later_hypothetical_PV_changed":pvs,
      "source_intervention_supported_claim":"EXACT_ORIGINAL_ENGINE_ROOT_ORDER_CAUSED_LOCAL_PV_TEXT_DIFFERENCE_WHERE_OBSERVED",
      "not_admissible_claims":[
         "strategic_concept_caused_actual_bestmove",
         "a_line_of_play_is_forced",
         "verified_high_level_source_concept_alignment",
         "engines_true_objective_optimal_chess_move",
         "general_human_instructional_transfer"
      ],
      "new_public_C3X_certificate":None,
      "independent_new_engine_source_causal_chess_semantics":False,
      "samples":worlds
    }

def audit_from_raw(raw:bytes):
    if hashlib.sha256(raw).hexdigest()!=SOURCE_NATIVE_JSON_SHA:
        raise ValueError("ORIGINAL_NATIVE_RESULT_JSON_SHA256_WRONG")
    return audit(json.loads(raw))
