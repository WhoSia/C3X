#!/usr/bin/env python3
"""C3X 0.14 reproduce SF16 classical WeakQueen geometrical trigger subclasses.

Exact 100 official TCEC S29 PGN games. Classify the single ray blocker
relative to queen side vs attacking rook/bishop side, per source SF16
Position::slider_blockers; no engine search outcomes permitted.
"""
import argparse,collections,hashlib,io,json
from pathlib import Path
import chess,chess.pgn

BLOB="68141d7a9afad301c237106c3b2a3324cb35b130"
CAP=120
def gitblob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def role(c,qside):return "OWN_QUEEN_SIDE_BLOCKER_RELATIVE_PIN" if c==qside else "ENEMY_ATTACKER_SIDE_BLOCKER_DISCOVERY"
def classify(board,color):
    queens=board.pieces(chess.QUEEN,color)
    attackers=list(board.pieces(chess.BISHOP,not color)|board.pieces(chess.ROOK,not color))
    results=[]
    for qsq in queens:
        # Actual SF16 Position::slider_blockers considers all attacking rook
        # and bishop snipers on EMPTY board ray and temporarily XORs these
        # sniper bits out of occupancy before checking intermediate blockers.
        eligible=[]
        for sq in attackers:
            pc=board.piece_at(sq)
            dx,dy=abs(chess.square_file(sq)-chess.square_file(qsq)),abs(chess.square_rank(sq)-chess.square_rank(qsq))
            rook_aligned=dx==0 or dy==0
            bishop_aligned=dx==dy
            if (pc.piece_type==chess.ROOK and rook_aligned) or (pc.piece_type==chess.BISHOP and bishop_aligned):
                eligible.append(sq)
        mask=0
        for s in eligible:mask|=chess.BB_SQUARES[s]
        occupied_without_snipers=board.occupied^mask
        for sq in eligible:
            between=chess.between(qsq,sq)
            blockers=between&occupied_without_snipers
            if blockers.bit_count()!=1:continue
            block_sq=(blockers&-blockers).bit_length()-1
            pc=board.piece_at(block_sq)
            assert pc is not None
            pinner=board.piece_at(sq)
            dx=abs(chess.square_file(sq)-chess.square_file(qsq))
            dy=abs(chess.square_rank(sq)-chess.square_rank(qsq))
            results.append({"queen_square":chess.square_name(qsq),
                "queen_side":"WHITE" if color==chess.WHITE else "BLACK",
                "pinner_square":chess.square_name(sq),
                "attacking_slider":"ROOK" if pinner.piece_type==chess.ROOK else "BISHOP",
                "blocker_square":chess.square_name(block_sq),
                "blocker_piece":chess.piece_name(pc.piece_type).upper(),
                "blocker_side":"WHITE" if pc.color==chess.WHITE else "BLACK",
                "blocker_relation":role(pc.color,color),
                "axis":"DIAGONAL" if dx==dy else ("RANK" if dy==0 else "FILE")})
    return results

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--pgn",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    raw=Path(a.pgn).read_bytes()
    if gitblob(raw)!=BLOB:raise SystemExit("PINNED_OFFICIAL_SOURCE_BLOB_MISMATCH")
    inp=io.StringIO(raw.decode("utf-8-sig"))
    games=0;positions=0;all_witness=[];source_example=[]
    while True:
        g=chess.pgn.read_game(inp)
        if g is None:break
        games+=1
        if g.errors:raise RuntimeError("INVALID_SOURCE_GAME_"+str(games))
        b=g.board();hist=[]
        for ply,m in enumerate(g.mainline_moves(),1):
            if ply>CAP:break
            if m not in b.legal_moves:raise RuntimeError("ILLEGAL_GAME_MOVE")
            b.push(m);hist.append(m.uci())
            if ply<18:continue
            positions+=1
            for side in chess.COLORS:
                out=classify(b,side)
                for item in out:
                    rec={"source_game_id":games,"source_round":g.headers.get("Round",""),
                         "ply":ply,"history_uci":list(hist),
                         "FEN":b.fen(en_passant="fen"),**item}
                    all_witness.append(rec)
    if games!=100:raise RuntimeError("EXPECTED_100_GAMES_GOT_"+str(games))
    # Limit repeated identical game+FEN+queen line; no scored selection.
    unique={}
    for w in all_witness:
        k=(w["source_game_id"],w["FEN"],w["queen_square"],w["pinner_square"],w["blocker_square"])
        unique.setdefault(k,w)
    cases=list(unique.values())
    byrole=collections.Counter(x["blocker_relation"] for x in cases)
    byslider=collections.Counter(x["attacking_slider"] for x in cases)
    samples={}
    for x in cases:
        key=x["blocker_relation"]
        arr=samples.setdefault(key,[])
        if len(arr)<12 and x["source_game_id"] not in {q["source_game_id"] for q in arr}:
            arr.append(x)
    result={"schema":"c3x-014-source-equivalent-SF16-WeakQueen-one-blocker-relational-pin-discovered-attack-census-v1",
        "formal_research_unit":"C3X 0.14","internal_ontology_section_not_new_formal_stage":True,
        "original_sf16_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "source_algorithms":["src/position.cpp::Position::slider_blockers",
                             "src/evaluate.cpp::Evaluation::pieces<QUEEN> relative queen pin or discovered attack penalty"],
        "source_PGN_git_blob":BLOB,"source_PGN_sha256":hashlib.sha256(raw).hexdigest(),
        "actual_source_games":games,"actual_game_positions_after_plies18_to120":positions,
        "all_raw_source_branch_witnesses":len(all_witness),
        "unique_source_game_FEN_ray_witnesses":len(cases),
        "unique_source_games_with_WeakQueen_ray_trigger":len({q["source_game_id"] for q in cases}),
        "queen_side_blocker_vs_attacker_side_blocker_counts":dict(byrole),
        "relative_pin_vs_discovered_attack_representative_examples_first12_different_games_each":samples,
        "all_unique_ray_witnesses":cases,
        "engine_score_outcomes_consulted":False,
        "Stockfish_classical_WeakQueen_relative_pin_branch_operationally_testable":True,
        "NNUE_internal_semantic_category_claimed":False,
        "human_strategy_causality_claimed":False,
        "scientific_limits":[
            "The same classical weak queen penalty triggers for a source-equivalent kingless queen line blocker (own vs opponent) not discrete learned NNUE categories.",
            "This reproduces positional geometry predicate by examining all opponent bishop/rook rays, ignoring sniper occupancy consistent with Stockfish slider_blockers.",
            "No evaluation value was read: a trigger may be offset by other positional terms, and the native evaluator may be disabled when Use NNUE true.",
            "Some boards can contain multiple ray triggers; witnesses within the same source chess game are correlated."
        ]}
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_CLASSICAL_WEAK_QUEEN_RELATIONAL_GEOMETRY_VERDICT",json.dumps({
       "games":games,"positions":positions,"ray_witnesses":len(cases),
       "groups":result["unique_source_games_with_WeakQueen_ray_trigger"],
       "roles":dict(byrole),"slider":dict(byslider)}),flush=True)
if __name__=="__main__":main()
