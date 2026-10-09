#!/usr/bin/env python3
"""Freeze source-game-disjoint TCEC S28 absolute king-pin worlds, NO engine data.

Same human chess law feature grammar as frozen original TCEC S29 classifier.
Predeclared quota (up to 8) for 4 prior legal law-type groups; 64 roots total.
"""
from __future__ import annotations
import argparse,collections,hashlib,io,json
from pathlib import Path
import chess,chess.pgn
from c3x_014_source_only_official_TCEC_pin_subtype_freeze import witnesses

SOURCE_BLOB="9c702d0e8f646f65f28f1555652937d58d397ad4"
SOURCE_COMMIT="3dd69a40b3cf6ccc74144df7411ef4e8e2140286"
S28_FILE="master-archive/TCEC_Season_28_-_Superfinal.pgn"
CAP=64
FOUR=[
 {"pinned_piece":"PAWN","pinning_piece":"QUEEN","axis":"DIAGONAL",
  "legal_pinned_piece_mobility":"ZERO","can_legally_capture_pinner":False},
 {"pinned_piece":"PAWN","pinning_piece":"QUEEN","axis":"FILE",
  "legal_pinned_piece_mobility":"NONZERO","can_legally_capture_pinner":False},
 {"pinned_piece":"ROOK","pinning_piece":"QUEEN","axis":"DIAGONAL",
  "legal_pinned_piece_mobility":"ZERO","can_legally_capture_pinner":False},
 {"pinned_piece":"PAWN","pinning_piece":"ROOK","axis":"FILE",
  "legal_pinned_piece_mobility":"NONZERO","can_legally_capture_pinner":False}
]
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def law(x):return json.dumps(x,sort_keys=True)
def must(x,m):
    if not x:raise RuntimeError(m)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pgn",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    raw=Path(a.pgn).read_bytes()
    must(blob(raw)==SOURCE_BLOB,"TCEC_S28_SOURCE_GIT_BLOB_MISMATCH")
    stream=io.StringIO(raw.decode("utf-8-sig"))
    games=0;actual_positions=0;witnesses_all=[]
    while True:
        g=chess.pgn.read_game(stream)
        if g is None:break
        games+=1
        must(not g.errors,"S28_OFFICIAL_PGN_ILLEGAL_"+str(games))
        bd=g.board();hist=[]
        header={k:g.headers.get(k,"") for k in ("Event","Site","Date","Round","White","Black")}
        for ply,m in enumerate(g.mainline_moves(),1):
            if ply>120:break
            must(m in bd.legal_moves,"S28_ILLEGAL_PLY")
            bd.push(m);hist.append(m.uci())
            if ply<18:continue
            actual_positions+=1
            for w in witnesses(bd,games,ply,hist,header):
                witnesses_all.append(w)
    must(games==100,"TCEC_S28_OFFICIAL_GAME_COUNT_NOT_100_"+str(games))
    dedup={}
    for w in witnesses_all:
        key=(w["game_index"],w["board_six_field_FEN"],w["pinned_square"])
        dedup.setdefault(key,w)
    all_distinct=list(dedup.values())
    selected=[];taken_games=set();origin={}
    def claim(w,stage):
        if w["game_index"] in taken_games:return False
        selected.append(w)
        taken_games.add(w["game_index"])
        origin[str(w["game_index"])]=stage
        return True
    for j,t in enumerate(FOUR):
        taken=0
        for w in all_distinct:
            if w["source_chess_law_subtype"]!=t:continue
            if claim(w,"PRESPEC_TARGET_LAW_"+str(j+1)):
                taken+=1
                if taken==8:break
    # Include 1st unseen source subtype before remaining positions (score blind).
    represented={law(w["source_chess_law_subtype"]) for w in selected}
    for w in all_distinct:
        if len(selected)>=CAP:break
        key=law(w["source_chess_law_subtype"])
        if key in represented:continue
        if claim(w,"NEW_CHESS_LAW_SUBTYPE_SOURCE_FIRST"):
            represented.add(key)
    for w in all_distinct:
        if len(selected)>=CAP:break
        claim(w,"CHRONOLOGICAL_SOURCE_GAME_FILL")
    must(len(selected)==CAP,"SOURCE_ONLY_FROZEN_WORLD_SHORTFALL_"+str(len(selected)))
    must(len(taken_games)==CAP,"MORE_THAN_ONE_ROOT_PER_ORIGINAL_SOURCE_GAME")
    # Full repeat of original chess rule witness checks, BEFORE engine output.
    for w in selected:
        b=chess.Board()
        for move in w["source_game_history_uci"]:
            must(chess.Move.from_uci(move) in b.legal_moves,"S28_ORIGINAL_MOVE_ILLEGAL")
            b.push_uci(move)
        must(b.fen(en_passant="fen")==w["board_six_field_FEN"],"S28_SOURCE_FEN_MISMATCH")
        sq=chess.parse_square(w["pinned_square"])
        must(b.is_pinned(b.turn,sq),"S28_NOT_ACTUALLY_KING_ABSOLUTE_PIN")
        actual=[m.uci() for m in b.generate_legal_moves(from_mask=chess.BB_SQUARES[sq])]
        must(actual==w["legal_moves_of_pinned_piece"],"S28_PIN_LAW_FULL_MOVE_MISMATCH")
    group_counts=collections.Counter(law(w["source_chess_law_subtype"]) for w in all_distinct)
    selected_counts=collections.Counter(law(w["source_chess_law_subtype"]) for w in selected)
    targets=[{"target_index":i+1,"law":t,
       "total_source_witnesses":group_counts[law(t)],
       "distinct_original_S28_games_with_a_witness":len({w["game_index"] for w in all_distinct if w["source_chess_law_subtype"]==t}),
       "frozen_sample_roots":selected_counts[law(t)]}
       for i,t in enumerate(FOUR)]
    result={"schema":"c3x-014-TCEC-season28-prescored-absolute-pin-law-transfer-corpus-sourceonly-v1",
      "formal_phase":"C3X 0.14","zero_Stockfish_outputs_used_for_source_selection":True,
      "upstream_original_commit":SOURCE_COMMIT,"upstream_original_path":S28_FILE,
      "upstream_original_PGN_git_blob_SHA1":SOURCE_BLOB,
      "upstream_original_PGN_sha256":hashlib.sha256(raw).hexdigest(),
      "source_provider":"TCEC","independent_season":28,
      "is_independent_provider":False,"is_same_source_as_S29":False,
      "official_source_game_count":games,"source_original_game_positions_ply18_to120":actual_positions,
      "actual_distinct_source_absolute_pin_witnesses":len(all_distinct),
      "actual_source_game_ids_with_king_pin":len({w["game_index"] for w in all_distinct}),
      "source_only_all_law_type_count":len(group_counts),
      "sample_size":len(selected),"source_game_distinctness":64,
      "primary_four_S29_prespecified_law_subtype_targets":targets,
      "actual_source_only_64_chess_pin_selected_worlds":selected,
      "source_only_selection_stage_by_game":origin,
      "all_S28_law_feature_counts":dict(group_counts),
      "selected_law_feature_counts":dict(selected_counts),
      "previous_40_S29_Stockfish_root_scores_were_not_consulted_for_source_order":True,
      "P1_four_game_sealed_holdout_accessed":False,
      "scientific_scope":[
          "Original TCEC Season28 distinct source season and different 100 games than S29; same TCEC provider, no claim of provider/engine family generality.",
          "64 frozen source games contain at most one root each, but the games share tournament/opening/players.",
          "Source roots selected using original S29 previously known law feature labels and score-blind chronological first-match quotas; not prospectively independent of the law hypothesis.",
          "All source chess legal move histories checked; classifying king pins before any stockfish run cannot prove stable learned Stockfish conceptual classes.",
          "The next 5-arm interventions alter whole-search SEE and WeakQueen source code, not the causal state of the particular root pinned object."
      ]}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_NEW_S28_SOURCE_ONLY_ABSOLUTE_PIN_FIBER_TRANSFER_FREEZE_PASS",json.dumps({
         "source_games":games,"source_positions":actual_positions,
         "source_legal_pin_witnesses":len(all_distinct),"distinct_game_pin_count":result["actual_source_game_ids_with_king_pin"],
         "S28_law_types":len(group_counts),"frozen_roots":len(selected),
         "targets":targets}),flush=True)
if __name__=="__main__":main()
