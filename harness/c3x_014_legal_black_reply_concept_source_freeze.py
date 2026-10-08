#!/usr/bin/env python3
"""C3X 0.14 legal concept contrast census: same prior 17 plies, alternate 18th black move.

Completely independent of engine evaluation. Every counterfactual reaches its
root by an actual legal prior history, not arbitrary editing of a chess FEN.
"""
import argparse,hashlib,io,json
from pathlib import Path
import chess
import chess.pgn

COHORT_SHA="cb879eaa14bcbf3896c4d069dcb1cf543135c68c5b1fa0ea2eab942613332eeb"
OFFICIAL_COMMIT="3dd69a40b3cf6ccc74144df7411ef4e8e2140286"
BLOB="68141d7a9afad301c237106c3b2a3324cb35b130"

def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob_hash(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def jhash(s):return hashlib.sha256(s.encode()).hexdigest()

def features_at(board,move):
    chess_move=chess.Move.from_uci(move)
    assert chess_move in board.legal_moves
    assert board.piece_at(chess_move.from_square).piece_type==chess.PAWN
    assert board.piece_at(chess_move.from_square).color==chess.WHITE
    b=board.copy(stack=True);b.push(chess_move)
    assert b.turn==chess.BLACK and b.is_valid()
    target=chess_move.to_square
    tr=chess.square_rank(target)
    f=chess.square_file(target)
    black_pawns=list(b.pieces(chess.PAWN,chess.BLACK))
    white_pawns=list(b.pieces(chess.PAWN,chess.WHITE))
    pawn_attackers_black=list(b.attackers(chess.BLACK,target)&b.pieces(chess.PAWN,chess.BLACK))
    pawn_defenders_white=list(b.attackers(chess.WHITE,target)&b.pieces(chess.PAWN,chess.WHITE))
    passed=not any(abs(chess.square_file(sq)-f)<=1 and chess.square_rank(sq)>=tr for sq in black_pawns)
    legal_ep=[m.uci() for m in b.legal_moves if b.is_en_passant(m) and m.to_square+8==target]
    cap=[m.uci() for m in b.legal_moves
         if b.is_capture(m) and (m.to_square==target or (b.is_en_passant(m) and m.to_square+8==target))]
    attacks=[sq for sq in b.attacks(target) if (b.piece_at(sq) is not None
                  and b.piece_at(sq).color==chess.BLACK and b.piece_at(sq).piece_type!=chess.PAWN)]
    isolated=not any(abs(chess.square_file(sq)-f)==1 for sq in white_pawns if sq!=target)
    doubled=any(chess.square_file(sq)==f for sq in white_pawns if sq!=target)
    return {
      "passed_pawn":int(passed),
      "enemy_pawn_attacks_square":int(bool(pawn_attackers_black)),
      "friendly_pawn_defends_square":int(bool(pawn_defenders_white)),
      "black_legal_immediate_capture_reply":int(bool(cap)),
      "black_legal_en_passant_reply":int(bool(legal_ep)),
      "white_pawn_attacks_enemy_nonpawn_piece":int(bool(attacks)),
      "isolated_white_pawn":int(isolated),
      "doubled_white_pawn":int(doubled),
      "black_pawn_attackers_count":len(pawn_attackers_black),
      "black_legal_capture_reply_count":len(cap)}
def vector(board,pair):
    a,b=(features_at(board,m) for m in pair)
    return {"single":a,"double":b,"double_minus_single":{k:b[k]-a[k] for k in a}}
def same(a,b):return a["double_minus_single"]==b["double_minus_single"]
def contrast_diff(a,b):
    v,w=a["double_minus_single"],b["double_minus_single"]
    return {k:[v[k],w[k]] for k in v if v[k]!=w[k]}
def material(board):
    return tuple(sum(len(board.pieces(pt,c)) for pt in chess.PIECE_TYPES) for c in (chess.WHITE,chess.BLACK))

def make_world(pre,bl_move,orig_pair):
    b=pre.copy(stack=True);m=chess.Move.from_uci(bl_move)
    if m not in b.legal_moves or b.is_capture(m) or m.promotion or b.is_castling(m):return None
    b.push(m)
    if b.is_check() or not b.is_valid():return None
    if not all(chess.Move.from_uci(k) in b.legal_moves for k in orig_pair):return None
    return {"black18_uci":bl_move,"root_full_FEN":b.fen(en_passant="fen"),
            "black_piece_type":pre.piece_at(m.from_square).piece_type,
            "same_material_as_predecessor":material(pre)==material(b),
            "pawn_structure_concept":vector(b,orig_pair)}
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--pgn",required=True);a.add_argument("--cohort",required=True)
    a.add_argument("--out",required=True);x=a.parse_args()
    pgn=Path(x.pgn).read_bytes()
    assert blob_hash(pgn)==BLOB
    raw=Path(x.cohort).read_bytes()
    assert sha(raw)==COHORT_SHA
    cohort=json.loads(raw)
    assert cohort["schema"]=="c3x-014-p2-official-s29-score-blind-independent-16-source-groups-v1"
    assert not cohort["hidden_p1_holdout_game_details_read"]
    selected=cohort["selected_16_game_groups"]
    assert len(selected)==16
    source_ids={r["source_game_id"]:r for r in selected}
    recovered={}
    f=io.StringIO(pgn.decode("utf-8-sig"))
    scanned=0
    while True:
        g=chess.pgn.read_game(f)
        if g is None:break
        scanned+=1
        if g.errors:continue
        allmoves=list(g.mainline_moves())
        if len(allmoves)<18:continue
        first18=[m.uci() for m in allmoves[:18]]
        head={k:g.headers.get(k,"") for k in ("Event","Site","Date","Round","White","Black")}
        gid=jhash("source_game:"+json.dumps(head,sort_keys=True)+":"+(" ".join(first18)))
        if gid not in source_ids:continue
        src=source_ids[gid]
        assert gid not in recovered
        prefix=chess.Board()
        for move in allmoves[:17]:
            assert move in prefix.legal_moves
            prefix.push(move)
        assert prefix.turn==chess.BLACK and prefix.is_valid()
        original_black=allmoves[17]
        assert original_black in prefix.legal_moves
        orig_board=prefix.copy(stack=True);orig_board.push(original_black)
        assert orig_board.fen(en_passant="fen")==src["full_root_fen"],"SOURCE_ORIGINAL_FEN_MISMATCH"
        pair=src["candidate_pair_uci"]
        original=make_world(prefix,original_black.uci(),pair)
        admissible=[]
        for m in prefix.legal_moves:
            v=make_world(prefix,m.uci(),pair)
            if v is not None and m!=original_black:
                admissible.append(v)
        admissible.sort(key=lambda c:c["black18_uci"])
        if original is None:
            status="ORIGINAL_BLACK_MOVE_NOT_QUIET_OR_OTHER_GUARD"
            targeted=None;sham=None
        else:
            targeted=next((v for v in admissible if not same(original["pawn_structure_concept"],v["pawn_structure_concept"])),None)
            sham=next((v for v in admissible if same(original["pawn_structure_concept"],v["pawn_structure_concept"])),None)
            status="TARGETED_AND_SHAM" if targeted and sham else ("TARGETED_NO_SHAM" if targeted else
                      "NO_TARGETED_CONCEPT_CHANGE")
        case={"source_game_id":gid,"source_group":src["opening_group_hash"],
              "official_original_game_headers":head,
              "root_candidate_pair":pair,
              "original_black18":original_black.uci(),
              "first_17_ply_path_uci":[m.uci() for m in allmoves[:17]],
              "first_17_ply_fen":prefix.fen(en_passant="fen"),
              "original_legal_history_root_fen":src["full_root_fen"],
              "original_root_concept":original["pawn_structure_concept"] if original else vector(orig_board,pair),
              "original_quiet_eligibility":original is not None,
              "available_legal_quiet_black_alternatives":len(admissible),
              "available_legal_alternates_changing_candidate_concept_contrast":
                  sum(original is not None and not same(original["pawn_structure_concept"],v["pawn_structure_concept"]) for v in admissible),
              "status":status,"concept_changing_world":targeted,
              "concept_preserving_world":sham,
              "targeted_concept_delta":contrast_diff(original["pawn_structure_concept"],targeted["pawn_structure_concept"]) if targeted else None,
              "historical_original_world":original}
        recovered[gid]=case
        print("C3X014_LEGAL_HISTORY",head["Round"],"status",status,
              "quiet_alternatives",len(admissible),
              "targeted",targeted["black18_uci"] if targeted else None,
              "sham",sham["black18_uci"] if sham else None,flush=True)
    assert scanned==100,(scanned,"UNEXPECTED_PGN_SOURCE_GAME_COUNT")
    assert set(recovered)==set(source_ids),"MISSING_PRESELECTED_OFFICIAL_GAMES"
    cases=[recovered[r["source_game_id"]] for r in selected]
    targets=sum(c["concept_changing_world"] is not None for c in cases)
    shams=sum(c["concept_preserving_world"] is not None for c in cases)
    both=sum(c["concept_changing_world"] is not None and c["concept_preserving_world"] is not None for c in cases)
    out={"schema":"c3x-014-legal-black18-alternative-chess-pawn-feature-court-v1",
         "formal_stage":"C3X 0.14","internal_work":True,
         "source":"TCEC official S29-final Superfinal PGN","source_commit":OFFICIAL_COMMIT,
         "full_source_blob_sha1":BLOB,"original_source_sha256":sha(pgn),
         "P2_source_cohort_sha256":COHORT_SHA,
         "games_scanned":scanned,"source_group_count":16,
         "original_games_recovered_with_exact_17_ply_legal_history":len(cases),
         "source_groups_with_legally_branchable_concept_changing_black18_alternative":targets,
         "source_groups_with_legal_concept_preserving_sham_black18_alternative":shams,
         "groups_with_both_worlds":both,
         "engine_scores_seen_during_source_freeze":False,
         "selection_tiebreak":"lexicographically first UCI black18 among all legal quiet moves preserving same white pawn candidate pair",
         "features_are_descriptive":True,
         "source_game_units_not_alt_black_move_independent":True,
         "source_ceiling":"Different black moves change chess tactics, NNUE, TT key, move order and clock/repetition context. Concept contrast difference is not isolated mediator causation.",
         "P1_sealed_holdout_read":False,"cases":cases}
    f=Path(x.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(out,indent=2)+"\n")
    print("C3X014_PAWN_CONCEPT_SOURCE_FREEZE",json.dumps({"games":len(cases),
         "targets":targets,"semantic_shams":shams,"both":both,"source":sha(pgn)}),flush=True)
if __name__=="__main__":main()
