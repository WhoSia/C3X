#!/usr/bin/env python3
"""Anonymous descriptive event/player game clustering for sealed 128 Sept games.
Never output original metadata labels or hashed IDs; no chess engine imported.
"""
import argparse,hashlib,io,json,collections
from pathlib import Path
import chess.pgn,zstandard
from c3x_024_P0_aug2025_engineblind_source16 import game_digest
SOURCE_SHA="da3a261e926a2c0f5e79c393818e643d76448edf94cfdaefa3892258a6f9e7ba"
LITERAL_REG="c3x/forecasts/c3x-024-P3-Sept2025-128game-source-SHA-literal-preNative-Git-seal-20261011.json"
def analyse(file):
    raw=Path(file).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise ValueError("SEP2025_ORIGINAL_PGN_ARCHIVE_SHA_DRIFT")
    registry=json.loads(Path(LITERAL_REG).read_text())
    wanted=set(registry["ordered_source_game_SHA256"])
    if len(wanted)!=128 or registry["source_game_count"]!=128:
        raise ValueError("P3_SOURCE_GAME_HASH_FREEZE_INVALID")
    event=collections.Counter();eventdate=collections.Counter()
    players=collections.Counter()
    missing_event=missing_date=missing_player=0
    scanned=0;found=set()
    with Path(file).open("rb") as f:
        with zstandard.ZstdDecompressor().stream_reader(f) as stream:
            with io.TextIOWrapper(stream,encoding="utf-8",errors="strict") as reader:
                while scanned<20000 and len(found)<128:
                    game=chess.pgn.read_game(reader)
                    if game is None:break
                    scanned+=1
                    if game.errors:continue
                    moves=list(game.mainline_moves())
                    if len(moves)<70:continue
                    fingerprint=game_digest(game.headers,[m.uci() for m in moves])
                    if fingerprint not in wanted:continue
                    if fingerprint in found:raise ValueError("DUPLICATE_SOURCE_GAME_HASH")
                    found.add(fingerprint)
                    name=game.headers.get("Event","").strip()
                    date=game.headers.get("Date","").strip()
                    if name and name not in ("?","Unknown"):event[name]+=1
                    else:missing_event+=1
                    if name and name not in ("?","Unknown") and date and "?" not in date:
                        eventdate[(name,date)]+=1
                    else:missing_date+=1
                    for field in ("White","Black"):
                        player=game.headers.get(field,"").strip()
                        if player and player not in ("?","Unknown"):
                            players[player]+=1
                        else:missing_player+=1
    if found!=wanted:raise ValueError("SELECTED_128_GAMES_NOT_ALL_FOUND_"+str(len(found)))
    return {"schema":"c3x024-P3-source-only-anonymous-event-player-clustering-v1",
      "orig_archive_SHA256":SOURCE_SHA,
      "sealed_source_games":128,
      "source_only_no_engine":True,
      "TT_FIRST_SEE_interventions":0,
      "matched_source_games":len(found),"original_scanned_game_records":scanned,
      "event_label_groups_observed":len(event),
      "event_groups_at_least_two_games":sum(n>=2 for n in event.values()),
      "max_selected_games_same_event_label":max(event.values(),default=0),
      "event_plus_complete_date_groups_observed":len(eventdate),
      "event_date_groups_at_least_two_games":sum(n>=2 for n in eventdate.values()),
      "max_selected_games_same_event_and_date":max(eventdate.values(),default=0),
      "unique_player_labels_observed":len(players),
      "player_labels_appearing_in_multiple_games":sum(n>=2 for n in players.values()),
      "max_selected_games_for_a_player":max(players.values(),default=0),
      "missing_or_unknown_event_fields":missing_event,
      "missing_or_unknown_full_dates":missing_date,
      "missing_or_unknown_player_appearances":missing_player,
      "independence_warning":"Game selection units 128, possible correlated event/player clusters. Do not treat 512 role cells as independent games.",
      "no_original_headers_labels_or_player_hashes_released":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zst",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    d=analyse(a.zst)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("C3X024_P3_S2_ANONYMOUS_EVENT_PLAYER_CLUSTER_VERDICT",
          {k:v for k,v in d.items() if k in (
            "matched_source_games","event_label_groups_observed",
            "event_plus_complete_date_groups_observed",
            "max_selected_games_same_event_label",
            "max_selected_games_same_event_and_date",
            "unique_player_labels_observed",
            "max_selected_games_for_a_player")},flush=True)
if __name__=="__main__":main()
