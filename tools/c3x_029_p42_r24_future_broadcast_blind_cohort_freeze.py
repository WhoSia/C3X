#!/usr/bin/env python3
"""C3X P42/R24-C: blind future-source official broadcast cohort selector.

Source event URL and game/position selection rules were committed BEFORE
the Nov 9 Swedish broadcast Round 3 start. This tool will NOT download,
simulate, predict or judge future games: it accepts provided RAW official
PGN bytes and freezes all valid 30-ply positions before any engine labels.
Source raw PGN stays private; public record contains hashes/counts only.
"""
import argparse,hashlib,io,json
from pathlib import Path
import chess,chess.pgn

FROZEN_ROUND="https://lichess.org/broadcast/lag-dm-2026/round-3/sbfCtgNj"
FROZEN_ROUND_ID="sbfCtgNj"
SOURCE_EVENT_DATE="2026-11-09"
TARGET_GAMES=8
FIXED_PLY=30
MIN_FULL_GAME_PLY=60
VALID_RESULTS={"1-0","0-1","1/2-1/2"}

def sha(data):return hashlib.sha256(data).hexdigest()

def harvest(raw:bytes,minimum=MIN_FULL_GAME_PLY,target=TARGET_GAMES):
    if len(raw)<64 or raw[:2]==b"PK" or raw[:4]==b"\x28\xb5\x2f\xfd":
        raise ValueError("R24_C_HOLD_RAW_PGN_REQUIRED_NOT_COMPRESSED_OR_PLACEHOLDER")
    try:body=raw.decode("utf-8-sig",errors="strict")
    except UnicodeDecodeError as e:
        raise ValueError("R24_C_HOLD_INVALID_UTF8_SOURCE") from e
    text=io.StringIO(body)
    eligible=[]
    census={"parsed_games":0,"syntax_illegal":0,"incomplete_result":0,
            "source_round_mismatch":0,
            "nonstandard_start_or_variant":0,"short_game":0,"duplicate_full_uci":0}
    seen=set()
    while True:
        game=chess.pgn.read_game(text)
        if game is None:break
        census["parsed_games"]+=1
        # Source URL in each official PGN record is a REQUIRED content gate.
        # Metadata alone does not authenticate bytes; HTTPS origin + SHA custody
        # are separate requirements for the actual future-source runner.
        round_header=game.headers.get("BroadcastURL","")
        game_header=game.headers.get("GameURL","")
        if (round_header!=FROZEN_ROUND and
            not (game_header.startswith(FROZEN_ROUND+"/")
                 and game_header[len(FROZEN_ROUND)+1:].count("/")==0)):
            census["source_round_mismatch"]+=1;continue
        if game.errors:
            census["syntax_illegal"]+=1;continue
        if game.headers.get("Result") not in VALID_RESULTS:
            census["incomplete_result"]+=1;continue
        if game.headers.get("Variant","Standard") not in ("Standard","Chess"):
            census["nonstandard_start_or_variant"]+=1;continue
        if game.board().fen()!=chess.STARTING_FEN:
            census["nonstandard_start_or_variant"]+=1;continue
        b=game.board()
        moves=[]
        legal=True
        for move in game.mainline_moves():
            if move not in b.legal_moves:
                legal=False;break
            moves.append(move.uci());b.push(move)
        if not legal:
            census["syntax_illegal"]+=1;continue
        if len(moves)<minimum or len(moves)<FIXED_PLY:
            census["short_game"]+=1;continue
        canonical=" ".join(moves).encode("ascii")
        uid=sha(canonical)
        if uid in seen:
            census["duplicate_full_uci"]+=1;continue
        seen.add(uid)
        b=game.board()
        for move in moves[:FIXED_PLY]:b.push_uci(move)
        eligible.append({
            "game_uci_sha256":uid,
            "original_full_game_ply":len(moves),
            "frozen_source_ply":FIXED_PLY,
            "prefix_uci":moves[:FIXED_PLY],
            "frozen_fen4":" ".join(b.fen(en_passant="fen").split()[:4]),
            "fixed_legal_root_moves":sorted(x.uci() for x in b.legal_moves)
        })
    ordered=sorted(eligible,key=lambda z:z["game_uci_sha256"])
    selected=ordered[:target]
    public={
      "schema":"c3x042-r24-C-nov9-source-before-model-cohort-v1",
      "status":"FROZEN_POST_OFFICIAL_SOURCE_ACQUISITION_PRE_ANY_ENGINE" if len(selected)==target
               else "HOLD_TOO_FEW_COMPLETE_STANDARD_LICENSED_GAMES",
      "prospective_round_precommitted_before_start":True,
      "fixed_official_source_url":FROZEN_ROUND,
      "source_round_id":FROZEN_ROUND_ID,
      "original_byte_sha256":sha(raw),
      "source_bytes":len(raw),
      "census":census,
      "eligible_full_games":len(eligible),
      "selected_game_count":len(selected),
      "fixed_ply":FIXED_PLY,
      "minimum_full_game_ply":minimum,
      "selection":"lexicographically smallest 8 SHA256 of complete canonical UCI mainline; fixed before exposure, no engine scores",
      "selected_full_game_uci_hashes":[x["game_uci_sha256"] for x in selected],
      "excluded_prior_source_archive_complete_audit":False,
      "model_scores_known_at_source_freeze":False,
      "source_engine_candidates_selected":False,
      "reference_judge_seen":False,
      "not_a_prospective_validation_result":True,
    }
    private={**public,"selected_source_positions":selected}
    return private,public

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-pgn",required=True)
    p.add_argument("--private-out",required=True)
    p.add_argument("--public-out",required=True)
    a=p.parse_args()
    private,public=harvest(Path(a.raw_pgn).read_bytes())
    for filename,obj in ((a.private_out,private),(a.public_out,public)):
        out=Path(filename);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    print("R24_C_ORIGINAL_FUTURE_BROADCAST_SOURCE_FREEZE",public["status"],
          public["eligible_full_games"],public["selected_game_count"])
    if not public["status"].startswith("FROZEN_"):raise SystemExit(2)
if __name__=="__main__":main()
