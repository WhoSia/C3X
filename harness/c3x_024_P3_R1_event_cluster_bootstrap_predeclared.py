#!/usr/bin/env python3
"""R1 fixed event/event-date bootstrap, using 128 precommitted source hashes.
Read original PGN PRIVATE, publish no source player/event names or ID mapping.
"""
import argparse,hashlib,io,json,random
from pathlib import Path
from collections import defaultdict
import chess.pgn,zstandard
from c3x_024_P0_aug2025_engineblind_source16 import game_digest

ORIGINAL_ARCHIVE_SHA256="da3a261e926a2c0f5e79c393818e643d76448edf94cfdaefa3892258a6f9e7ba"
ORIG_SOURCE_GAME_REGISTRY="c3x/forecasts/c3x-024-P3-Sept2025-128game-source-SHA-literal-preNative-Git-seal-20261011.json"
ORIGINAL_FORECAST_SHA256="c402a6808bcaa2d73ec58632f87aa4ba7e8be0577b051b85e0a5610750eb1887"
BS_REPS=10000
SEED=20261011
def events(path,wanted):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=ORIGINAL_ARCHIVE_SHA256:
        raise ValueError("P3_EVENT_BOOTSTRAP_ORIGINAL_PGN_ARCHIVE_CHANGED")
    found={}
    scanned=0
    with Path(path).open("rb") as f:
        with zstandard.ZstdDecompressor().stream_reader(f) as decompressed:
            with io.TextIOWrapper(decompressed,encoding="utf-8",errors="strict") as reader:
                while scanned<20000 and len(found)<128:
                    game=chess.pgn.read_game(reader)
                    if game is None:break
                    scanned+=1
                    if game.errors:continue
                    moves=list(game.mainline_moves())
                    if len(moves)<70:continue
                    sha=game_digest(game.headers,[m.uci() for m in moves])
                    if sha not in wanted:continue
                    if sha in found:raise ValueError("P3_EVENT_BOOTSTRAP_DUPLICATE_SELECTED_GAME")
                    found[sha]=(game.headers.get("Event","").strip(),game.headers.get("Date","").strip())
    if set(found)!=wanted:raise ValueError("P3_EVENT_BOOTSTRAP_NOT_ALL_SELECTED_GAMES_RECOVERED")
    return found
def eligible(field):
    return bool(field and field not in ("?","Unknown","unknown","-"))
def group_mapping(seal,metadata,mode):
    group={}
    for gid,sha in enumerate(seal["ordered_source_game_SHA256"],1):
        event,date=metadata[sha]
        if not eligible(event) or (mode=="event_date" and (not eligible(date) or "?" in date)):
            group[gid]=("MISSING_METADATA_SINGLETON",gid)
        elif mode=="event":
            group[gid]=("EVENT",event)
        else:
            group[gid]=("EVENT_AND_COMPLETE_DATE",event,date)
    return group
def bootstrap(vals,assignment,mode):
    groups=defaultdict(list)
    for gid,delta in vals.items():
        groups[assignment[gid]].append(delta)
    keys=list(groups)
    rng=random.Random(SEED+int(mode=="event_date"))
    samples=[]
    zero_denom=0
    for _ in range(BS_REPS):
        sampled=[groups[keys[rng.randrange(len(keys))]] for j in range(len(keys))]
        denom=sum(len(q) for q in sampled)
        if not denom:
            zero_denom+=1
            continue
        mean=sum(sum(q) for q in sampled)/denom
        samples.append(mean)
    if not samples:raise ValueError("P3_BOOTSTRAP_ZERO_OBSERVED_GROUPS")
    samples.sort()
    return {"metadata_grouping":mode,
      "observed_groups_including_missing_singletons":len(groups),
      "bootstrap_iterations_requested":BS_REPS,
      "bootstrap_iterations_valid":len(samples),
      "censored_zero_contact_samples":zero_denom,
      "seed":SEED+int(mode=="event_date"),
      "mean_game_effect_original":sum(vals.values())/len(vals),
      "percentile_95pct_CI":[samples[int(0.025*(len(samples)-1))],samples[int(0.975*(len(samples)-1))]],
      "method":"Resample observed anonymous groups with replacement, bring all contacted games in drawn event, equal game weights"}
def audit(zst,results):
    seal=json.loads(Path(ORIG_SOURCE_GAME_REGISTRY).read_text())
    if seal["source_game_count"]!=128 or len(seal["ordered_source_game_SHA256"])!=128:
        raise ValueError("P3_REGISTRY_NOT_128_FROZEN")
    if results["schema"]!="c3x024-P3-September2025-128-game-prospective-after-human-Git-presealed-five-models-v1" or results["original_literally_Git_sealed_predictions_SHA256"]!=ORIGINAL_FORECAST_SHA256 or results["independent_source_game_rows"]!=128:
        raise ValueError("P3_MODEL_SCORE_NOT_ORIGINAL_128_PRESEALED_RUN")
    rows=results["source_only_deidentified_game_results"]
    if len(rows)!=128 or [x["game_id"] for x in rows]!=list(range(1,129)):
        raise ValueError("P3_EVENT_GROUPING_GAME_ROW_OR_SELECTION_CHANGED")
    source=events(zst,set(seal["ordered_source_game_SHA256"]))
    diffs={}
    for g in rows:
        if not g["contact_role_cells"]:continue
        counts=g["correct_role_counts"]
        diffs[g["game_id"]]=(counts["M3_v2"]-counts["M0"])/g["contact_role_cells"]
    if len(diffs)!=results["contacted_games"]:
        raise ValueError("P3_CONTACT_DENOMINATOR_DRIFT")
    b1=bootstrap(diffs,group_mapping(seal,source,"event"),"event")
    b2=bootstrap(diffs,group_mapping(seal,source,"event_date"),"event_date")
    return {"schema":"c3x024-P3-R1-September128-anonymous-source-event-cluster-sensitivity-v1",
      "scientific_status":"POST_OUTCOME_BOOTSTRAP_BY_PRETREATMENT_LOCKED_METHOD",
      "source_games":128,"contacted_games":len(diffs),
      "untreated_source_file_SHA256":ORIGINAL_ARCHIVE_SHA256,
      "exact_five_model_forecast_pre_first_SHA256":ORIGINAL_FORECAST_SHA256,
      "mean_game_level_M3v2_minus_M0":sum(diffs.values())/len(diffs),
      "event_label_group_bootstrap":b1,
      "event_plus_date_group_bootstrap":b2,
      "natural_TT_SEE_mediation_proven":False,
      "cannot_retrofit_M3_v2_after_outcome":True,
      "no_source_event_or_player_metadata_published":True}
def main():
    p=argparse.ArgumentParser()
    for k in ("zst","model-score","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    full=Path(a.model_score).read_bytes()
    result=audit(a.zst,json.loads(full))
    o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X024_P3_R1_EVENT_CLUSTER_SENSITIVITY",{
       "mean":result["mean_game_level_M3v2_minus_M0"],
       "event_CI":result["event_label_group_bootstrap"]["percentile_95pct_CI"],
       "event_date_CI":result["event_plus_date_group_bootstrap"]["percentile_95pct_CI"],
       "contacted_games":result["contacted_games"]},
       hashlib.sha256(o.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
