#!/usr/bin/env python3
"""C3X 0.14 source-only, chess-law pin mechanism subtype census.

Exact TCEC official S29 Superfinal PGN 100 games. NO engine evaluation may
be loaded, used or consulted to select positions or legal pin features.
Pins are absolute king-geometry pins only; relative queen pins later.
"""
import argparse,collections,hashlib,io,json
from pathlib import Path
import chess,chess.pgn

PGN_GIT_BLOB="68141d7a9afad301c237106c3b2a3324cb35b130"
SOURCE_COMMIT="3dd69a40b3cf6ccc74144df7411ef4e8e2140286"
MAX_PLIES=120
SAMPLE_LIMIT=40
PIECE={chess.PAWN:"PAWN",chess.KNIGHT:"KNIGHT",chess.BISHOP:"BISHOP",
       chess.ROOK:"ROOK",chess.QUEEN:"QUEEN",chess.KING:"KING"}

def git_blob(x):return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\0"+x).hexdigest()
def sgn(a):return int(a>0)-int(a<0)
def pin_ray_witness(board,side,from_sq):
    king=board.king(side)
    if king is None or from_sq==king:return None
    kf,kr=chess.square_file(king),chess.square_rank(king)
    pf,pr=chess.square_file(from_sq),chess.square_rank(from_sq)
    dx,dy=pf-kf,pr-kr
    if not(dx==0 or dy==0 or abs(dx)==abs(dy)):return None
    stepf,stepr=sgn(dx),sgn(dy)
    if not(stepf or stepr):return None
    f,r=kf+stepf,kr+stepr
    while (f,r)!=(pf,pr):
        if board.piece_at(chess.square(f,r)) is not None:return None
        f+=stepf;r+=stepr
    f+=stepf;r+=stepr
    while 0<=f<8 and 0<=r<8:
        pin_sq=chess.square(f,r)
        pc=board.piece_at(pin_sq)
        if pc is not None:
            aligned_axis="FILE" if dx==0 else ("RANK" if dy==0 else "DIAGONAL")
            qualified=pc.color!=side and (
                pc.piece_type==chess.QUEEN or
                (aligned_axis=="DIAGONAL" and pc.piece_type==chess.BISHOP) or
                (aligned_axis in ("FILE","RANK") and pc.piece_type==chess.ROOK))
            if qualified:return {"pinning_square":chess.square_name(pin_sq),
                  "pinning_piece":PIECE[pc.piece_type],"axis":aligned_axis,
                  "king_square":chess.square_name(king),
                  "ray_king_to_pinned":max(abs(dx),abs(dy)),
                  "ray_pinned_to_attacker":max(abs(f-pf),abs(r-pr))}
            break
        f+=stepf;r+=stepr
    return None

def witnesses(board,game_number,ply,history,head):
    side=board.turn
    result=[]
    for piece_sq,pc in sorted(board.piece_map().items()):
        if pc.color!=side or pc.piece_type==chess.KING or not board.is_pinned(side,piece_sq):continue
        ray=pin_ray_witness(board,side,piece_sq)
        if ray is None:raise RuntimeError("CHESS_IS_PINNED_HAS_NO_VALID_GEOMETRIC_SLIDER")
        board_mask=chess.BB_SQUARES[piece_sq]
        legal=list(board.generate_legal_moves(from_mask=board_mask))
        pseudo=list(board.generate_pseudo_legal_moves(from_mask=board_mask))
        # Full source/board game history maintained; legality considered ONLY
        # for side to move, never hypothetical arbitrary color turn.
        cap=[m.uci() for m in legal if m.to_square==chess.parse_square(ray["pinning_square"])
             and board.is_capture(m)]
        legal_moves=[m.uci() for m in legal]
        sample={"game_index":game_number,"source_round":head["Round"],
                "source_game_head":head,"ply":ply,"source_game_history_uci":list(history),
                "board_six_field_FEN":board.fen(en_passant="fen"),
                "side_to_move":"WHITE" if side==chess.WHITE else "BLACK",
                "pinned_square":chess.square_name(piece_sq),
                "pinned_piece":PIECE[pc.piece_type],**ray,
                "opponent_king_in_check":board.is_check(),
                "pinned_piece_legal_moves_count":len(legal),
                "pinned_piece_pseudolegal_moves_count":len(pseudo),
                "pinned_piece_has_legal_move":bool(legal),
                "pinned_piece_can_legally_capture_pinner":bool(cap),
                "pinning_piece_capture_moves":cap,
                "legal_moves_of_pinned_piece":legal_moves,
                "lost_moves_due_to_king_absolute_pin":
                  len([m for m in pseudo if m not in legal]),
                "side_to_move_full_legal_moves_count":board.legal_moves.count()}
        # This feature grammar is by chess law, not NNUE latent labels.
        sample["source_chess_law_subtype"]={
            "pinned_piece":sample["pinned_piece"],
            "pinning_piece":sample["pinning_piece"],
            "axis":sample["axis"],
            "legal_pinned_piece_mobility":"ZERO" if not legal else "NONZERO",
            "can_legally_capture_pinner":bool(cap)}
        result.append(sample)
    return result
def freeze_sample(occurrences):
    # First sample any new subtype based purely on chess law. Then fill by
    # source game ID, at most one per game, to limit repeated opening motifs.
    selected=[];used_ids=set();used_types=set()
    for r in occurrences:
        subtype=tuple(r["source_chess_law_subtype"].values())
        if subtype not in used_types and r["game_index"] not in used_ids:
            selected.append(r);used_types.add(subtype);used_ids.add(r["game_index"])
        if len(selected)==SAMPLE_LIMIT:return selected
    for r in occurrences:
        if r["game_index"] not in used_ids:
            selected.append(r);used_ids.add(r["game_index"])
        if len(selected)==SAMPLE_LIMIT:return selected
    return selected
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pgn",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    source=Path(a.pgn).read_bytes()
    if git_blob(source)!=PGN_GIT_BLOB:raise SystemExit("SOURCE_PGN_BLOB_NOT_PINNED_OFFICIAL")
    gamefile=io.StringIO(source.decode("utf-8-sig"))
    games=0;occurrences=[];fullpositions=0
    while True:
        game=chess.pgn.read_game(gamefile)
        if game is None:break
        games+=1
        if game.errors:raise RuntimeError("INVALID_OFFICIAL_PGN_"+str(games))
        board=game.board()
        head={k:game.headers.get(k,"") for k in ("Event","Site","Date","Round","White","Black")}
        history=[]
        for ply,m in enumerate(game.mainline_moves(),1):
            if ply>MAX_PLIES:break
            if m not in board.legal_moves:raise RuntimeError("ILLEGAL_OFFICIAL_MOVE")
            board.push(m);history.append(m.uci())
            if ply<18:continue
            fullpositions+=1
            occurrences.extend(witnesses(board,games,ply,history,head))
    if games!=100:raise RuntimeError("OFFICIAL_SOURCE_GAME_COUNT_NOT100_"+str(games))
    # A repeated pin at a later ply is a different native position, but can
    # dominate a naive count: unique source game+FEN+piece.
    unique={}
    for r in occurrences:
        k=(r["game_index"],r["board_six_field_FEN"],r["pinned_square"])
        unique.setdefault(k,r)
    distinct=list(unique.values())
    selected=freeze_sample(distinct)
    counts=collections.Counter(json.dumps(r["source_chess_law_subtype"],sort_keys=True) for r in distinct)
    per_piece=collections.Counter(r["pinned_piece"] for r in distinct)
    per_pinner=collections.Counter(r["pinning_piece"] for r in distinct)
    out={"schema":"c3x-014-official-TCEC-S29-chess-law-absolute-pin-subtype-census-before-engine-scores-v1",
         "formal_research_unit":"C3X 0.14","internal_discovery_not_formal_substage":True,
         "actual_source":"TCEC official Season 29 Superfinal source PGN",
         "original_TCEC_git_commit":SOURCE_COMMIT,
         "source_git_blob_sha1":PGN_GIT_BLOB,
         "actual_source_sha256":hashlib.sha256(source).hexdigest(),
         "games_read":games,"max_plies_per_game":MAX_PLIES,
         "legal_positions_scanned":fullpositions,
         "absolute_pins_with_side_to_move_census_all_occurrences":len(occurrences),
         "absolute_pins_unique_game_FEN_piece":len(distinct),
         "unique_game_groups_with_at_least_one_pin":len({r["game_index"] for r in distinct}),
         "pinned_piece_classes":dict(per_piece),
         "pinning_slider_classes":dict(per_pinner),
         "source_subtype_count":len(counts),
         "all_chess_law_subtype_frequency":dict(counts),
         "source_only_selected_sample_size":len(selected),
         "source_only_selection_rule":"First original PGN chronology by new (pinned piece,pinner,axis,legal mobility,pinner capture) subtype and unique source game; fill first each remaining game; cap40; no engine outcomes.",
         "source_only_selected_witnesses":selected,
         "all_legal_pin_witnesses_source_only":distinct,
         "engine_outputs_used_for_selection":False,
         "relative_queen_pins_studied":False,
         "stockfish_has_explicit_internal_pin_strategy_subtypes_proven":False,
         "stockfish_neural_latent_subtypes_proven":False,
         "scientific_limits":[
             "Only king-absolute pins where pinned side is to move; avoids misleading legal move counts for nonturn color.",
             "Chess law subtype is a hypothesized explanatory descriptor, not an observed internal Stockfish latent semantic label.",
             "Observed PGN variation does not isolate an individual pin's influence on search or evaluation.",
             "Source game is the unit; many pins per game are dependent longitudinal positions.",
             "If any subtype is absent from official corpus it stays absent; do not invent positive examples."
         ]}
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("C3X014_SOURCE_ONLY_PIN_GEOMETRY_SUBTYPE_VERDICT",json.dumps({
      "source_games":games,"positions":fullpositions,"distinct_pin_witnesses":len(distinct),
      "groups":out["unique_game_groups_with_at_least_one_pin"],
      "selected":len(selected),"subtypes":len(counts),"piece_types":dict(per_piece),
      "pinner_types":dict(per_pinner)}),flush=True)
if __name__=="__main__":main()
