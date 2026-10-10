#!/usr/bin/env python3
"""P4 July256 exact original source-only StageA four 64-game shards and merge.
No native FIRST treatment. Four partitions are original game SHA-order indices.
"""
import argparse,json,hashlib
from pathlib import Path
from c3x_024_P4_July256_untreated_native_stageA import (
    immutable,stageA,populate_original_source_summary,SOURCE_SHA,REGISTRY,SCHEMA)
ECOLOGY="july2025_broadcast"
def source_shard(raw,shard):
    if shard not in range(4):raise ValueError("P4_EXPECTED_4_EXACT_SHARDS")
    if raw["source_fen_count"]!=256 or len(raw["selected"])!=256:
        raise ValueError("P4_ORIGINAL_SOURCE_MUST_BE_256")
    st=shard*64
    part=dict(raw);part["selected"]=raw["selected"][st:st+64]
    ids=[row["id"] for row in part["selected"]]
    if ids!=list(range(st+1,st+65)):
        raise ValueError("P4_SHARD_ORIGINAL_SHA_ORDER_WRONG")
    return part
def combine(raws):
    if len(raws)!=4:raise ValueError("P4_NEED_4_SHARDS")
    out=None
    original_sha=None
    for shard,j in enumerate(raws):
        if j["schema"]!=SCHEMA or j["source_sha256"]!=SOURCE_SHA or j["TT_or_SEE_treatment_executed"] is not False:
            raise ValueError("P4_WRONG_UNTREATED_ORIGINAL_SOURCE_PACKET")
        rows=j["ecologies"][ECOLOGY]["cases"]
        if len(rows)!=64 or [r["id"] for r in rows]!=list(range(shard*64+1,shard*64+65)):
            raise ValueError("P4_SOURCE_SHARD_MISSING_OR_REORDERED_ORIGINAL_GAME")
        if j["summary"]["distinct_source_boards"]!=64 or j["summary"]["potential_role_cells"]!=256:
            raise ValueError("P4_SHARD_SUMMARY_ORIGINAL_DENOMINATOR_DRIFT")
        if out is None:
            out={k:v for k,v in j.items() if k not in ("ecologies","summary")}
            out["ecologies"]={ECOLOGY:{"license":j["ecologies"][ECOLOGY]["license"],"cases":[]}}
        for k,v in out.items():
            if k not in ("ecologies","summary") and j[k]!=v:
                raise ValueError("P4_SHARD_SEMANTIC_NATIVE_MODEL_METADATA_DRIFT_"+k)
        out["ecologies"][ECOLOGY]["cases"].extend(rows)
    if len(out["ecologies"][ECOLOGY]["cases"])!=256 or        [x["id"] for x in out["ecologies"][ECOLOGY]["cases"]]!=list(range(1,257)):
        raise ValueError("P4_256_GAME_ORIGINAL_SHA_INPUT_IDENTITY_MERGE_INCOMPLETE")
    populate_original_source_summary(out)
    sm=out["summary"]
    if sm["distinct_source_boards"]!=256 or sm["world_count"]!=512 or sm["potential_role_cells"]!=1024 or        sm["actual_TT_FIRST_interventions"]!=0 or sm["actual_SEE_Boolean_interventions"]!=0 or sm["treatment_outcomes_seen"]:
        raise ValueError("P4_SOURCE_ONLY_MERGED_STAGEA_NOT_UNTREATED_256")
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--engine")
    p.add_argument("--shard",type=int)
    p.add_argument("--parts",nargs=4)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    original=immutable(a.source,SOURCE_SHA)
    if a.shard is not None and a.engine and not a.parts:
        part=source_shard(original,a.shard)
        j=stageA(part,a.engine,expected_ids=range(a.shard*64+1,a.shard*64+65))
        if len(j["ecologies"][ECOLOGY]["cases"])!=64 or j["summary"]["potential_role_cells"]!=256:
            raise ValueError("P4_SOURCE_SHARD_STAGEA_NOT_COMPLETE")
        print("C3X024_P4_S2_O2_64_ORIGINAL_UNTREATED_NATIVE_SHARD",a.shard,
              j["summary"],flush=True)
    elif a.parts and a.shard is None and not a.engine:
        parts=[json.loads(Path(x).read_bytes()) for x in a.parts]
        j=combine(parts)
        print("C3X024_P4_S2_O2_COMPLETE_256_ORIGINAL_UNTREATED_NATIVE_MERGE",
              j["summary"],flush=True)
    else:raise ValueError("P4_EXACTLY_SHARD_OR_MERGE_INPUT")
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(j,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X024_P4_S2_O2_ORIGINAL_SOURCE_RECONSTRUCTED_NATIVE_STAGEA_SHA256",
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
