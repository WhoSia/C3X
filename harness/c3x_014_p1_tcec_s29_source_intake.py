#!/usr/bin/env python3
"""C3X 0.14 P1 source-disjoint TCEC game cohort gate.

No engine scores or strategy labels are computed. Holdout game and move data are
procedurally sealed into a separate artifact; GitHub repo administrators can
read the artifact, so this is NOT cryptographic access control.
"""
import argparse,hashlib,io,json
from pathlib import Path
import chess
import chess.pgn

EXPECTED_BLOB="68141d7a9afad301c237106c3b2a3324cb35b130"
SALT="C3X_014_P1_TCEC_S29_SOURCE_FREEZE_V1"
REQUIRED=8
TARGET_PLY=18
SOURCE_COMMIT="3dd69a40b3cf6ccc74144df7411ef4e8e2140286"
SOURCE_REPO="TCEC-Chess/tcecgames"
SOURCE_PATH="master-archive/TCEC_Season_29_-_Superfinal.pgn"

def git_blob_sha1(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def digest(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def eligible(raw):
    game_total=0;valid_games=0;eligible_games=0
    by_opening={}
    input_stream=io.StringIO(raw.decode("utf-8-sig",errors="strict"))
    while True:
        game=chess.pgn.read_game(input_stream)
        if game is None:break
        game_total+=1
        if game.errors:continue
        board=game.board()
        if board.chess960 or not board.is_valid():continue
        fen_at_12=None;at_root=None;first_moves=[]
        for k,move in enumerate(game.mainline_moves(),start=1):
            if k<=TARGET_PLY:first_moves.append(move.uci())
            if move not in board.legal_moves:break
            board.push(move)
            if k==12:fen_at_12=board.fen(en_passant="fen")
            if k==TARGET_PLY:
                at_root=board.copy(stack=True)
                break
        if at_root is None or fen_at_12 is None:continue
        valid_games+=1
        if at_root.turn!=chess.WHITE or not at_root.is_valid():continue
        candidates=[]
        legal=set(at_root.legal_moves)
        for sq in at_root.pieces(chess.PAWN,chess.WHITE):
            if chess.square_rank(sq)!=1:continue
            single=chess.Move(sq,sq+8)
            double=chess.Move(sq,sq+16)
            if single in legal and double in legal:
                candidates.append((single.uci(),double.uci()))
        if not candidates:continue
        eligible_games+=1
        move_pair=min(candidates)
        hdr=game.headers
        meta={k:hdr.get(k,"") for k in ("Event","Site","Date","Round","White","Black")}
        group=digest("opening_prefix12:"+fen_at_12)
        game_id=digest("source_game:"+json.dumps(meta,sort_keys=True)+":"+(" ".join(first_moves)))
        rec={"source_game_id":game_id,"opening_group_hash":group,
             "source_headers":meta,"full_root_fen":at_root.fen(en_passant="fen"),
             "ply":TARGET_PLY,"candidate_pair_uci":list(move_pair),
             "candidate_pair_san":[at_root.san(chess.Move.from_uci(x)) for x in move_pair],
             "first_18_plies_sha256":digest(" ".join(first_moves)),
             "source_file_path":SOURCE_PATH}
        if group not in by_opening or game_id<by_opening[group]["source_game_id"]:
            by_opening[group]=rec
    return by_opening,{"total_games_read":game_total,
                       "valid_games_with_target_ply":valid_games,
                       "legal_same_pawn_single_double_eligible_games":eligible_games,
                       "distinct_eligible_opening_prefix_groups":len(by_opening)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pgn",required=True);p.add_argument("--out-public",required=True)
    p.add_argument("--out-sealed",required=True)
    a=p.parse_args()
    raw=Path(a.pgn).read_bytes()
    blob=git_blob_sha1(raw)
    if blob!=EXPECTED_BLOB:
        raise SystemExit(f"P1_SOURCE_BLOB_MISMATCH expected={EXPECTED_BLOB} actual={blob}")
    groups,counts=eligible(raw)
    keys=sorted(groups,key=lambda g:digest(SALT+":"+g))
    samples=[groups[g] for g in keys[:REQUIRED]]
    size_ok=len(samples)==REQUIRED
    development=samples[:4]
    heldout=samples[4:]
    public={
      "schema":"c3x-014-p1-tcec-s29-source-disjoint-intake-v1",
      "status":"FROZEN_SOURCE_COHORT_ONLY__NO_ENGINE_EVALUATION",
      "origin":{"repo":SOURCE_REPO,"git_commit":SOURCE_COMMIT,
                "path":SOURCE_PATH,"git_blob_sha1":blob,
                "sha256":hashlib.sha256(raw).hexdigest(),
                "source_byte_length":len(raw)},
      "eligibility":{"fixed_ply":TARGET_PLY,"same_original_rank_white_pawn_single_double_moves":True,
                     "deduplicate_by":"exact board FEN after 12 plies, one game per opening group",
                     "selection_salt":SALT,"required_groups":REQUIRED},
      "audit":counts,"all_game_groups_are_source_disjoint":len({x["opening_group_hash"] for x in samples})==len(samples),
      "eligibility_pass":size_ok,
      "development_games":development,
      "procedurally_sealed_holdout_group_hashes":[x["opening_group_hash"] for x in heldout],
      "holdout_game_count":len(heldout),
      "holdout_data_is_not_cryptographically_inaccessible":True,
      "engine_scores_observed":False,
      "search_path_interventions_run":False,
      "concept_mediation_proven":False,
      "C3X_014":"P1_SOURCE_INTAKE_ONLY"
    }
    sealed={
      "schema":"c3x-014-p1-procedural-sealed-holdout-manifest-v1",
      "warning":"Accessible to authorized GitHub artifact readers. Must not be loaded by development-stage outcome analysis.",
      "release_gate":"Separate later validation stage after P1 development analysis freeze",
      "source_sha256":public["origin"]["sha256"],
      "holdout_games":heldout
    }
    for k,v in ((a.out_public,public),(a.out_sealed,sealed)):
        dest=Path(k);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n")
    print("C3X_014_P1_SOURCE_AUDIT",json.dumps(counts),flush=True)
    print("C3X_014_P1_ELIGIBILITY",size_ok,
          "development",len(development),"holdout",len(heldout),flush=True)
    if not size_ok:raise SystemExit("P1_INSUFFICIENT_DISTINCT_LEGAL_OPENING_GROUPS_HOLD")
    if any(g["full_root_fen"]==h["full_root_fen"] for g in development for h in heldout):
        raise SystemExit("P1_DEVELOPMENT_HOLDOUT_ROOT_LEAKAGE")
    assert not any(k in public for k in ("holdout_games","holdout_root_fens","holdout_pair_uci"))
    assert all(tuple(g["candidate_pair_uci"])==tuple(sorted(g["candidate_pair_uci"])) for g in development)
    print("C3X_014_P1_SEALED_SOURCE_SELECTION_PASS")
if __name__=="__main__":main()
