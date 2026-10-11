#!/usr/bin/env python3
"""Fixed-seed exposed original July256 four-lane root flip coincidence descriptive null."""
import argparse,glob,hashlib,json,random,statistics
from pathlib import Path
from collections import Counter
SHAS=(
"76eb58229a97cb9b39fb9b007233b2c30042b509274b866f25bf05c5aae9336e",
"68dc175dffd09bf4772918fba76a1766c70c876c98459cf5233e39b4adc1b27d",
"f3fd2097fcbb30a444c752c64ea37138a9048b1e97959042005f749ec2b9a2dc",
"4807f4dc023153a9c45b9b2891f84968f3ae61328364704780c3e8319bd43792")
ROLES=(("O","STRICT"),("O","BROAD"),("F","STRICT"),("F","BROAD"))
SCHEMA="c3x025-P1-exposed-July256-four-lane-root-flip-coincidence-permutation-null-v1"
ITERATIONS=20000
SEED=20261011
def read_shards(folder):
    paths=sorted(glob.glob(str(Path(folder)/"C3X024_P4_TREATED_SHARD_*.json")))
    if len(paths)!=4:raise ValueError("P1_NEEDS_EXACT_FOUR_HISTORIC_SHARDS")
    rows=[]
    for i,p in enumerate(paths):
        raw=Path(p).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SHAS[i]:
            raise ValueError("P1_ORIGINAL_NATIVE_TREATED_SHA_CHANGED")
        s=json.loads(raw)
        if s["schema"]!="c3x024-P4-256game-human-Git-presealed-six-model-physical-TT-FIRST-shard-v1" or s["shard"]!=i or s["case_range"]!=[i*64+1,(i+1)*64] or len(s["all_cells"])!=64:
            raise ValueError("P1_SOURCE_SHARD_ORDER_INVALID")
        rows.extend(s["all_cells"])
    if len(rows)!=256 or [row["game_id"] for row in rows]!=list(range(1,257)):
        raise ValueError("P1_EXACT_GAME_256_IDS_WRONG")
    return rows
def role_lanes(rows):
    lanes={f"{o}/{r}":{"eligible":[],"flipped":[]} for o,r in ROLES}
    actual=Counter()
    holds=contacts=flips=0
    for i,row in enumerate(rows,1):
        if len(row["roles"])!=4:raise ValueError("P1_FOUR_ORIGINAL_ROLE_CELLS_MISSING")
        for idx,(order,role) in enumerate(ROLES):
            x=row["roles"][idx]
            if (x["root_order"],x["role"])!=(order,role):
                raise ValueError("P1_ORDER_OR_ROLE_DRIFT")
            key=f"{order}/{role}"
            if x["status"]=="PRESEALED_INELIGIBLE_NO_FIRST_READER":
                holds+=1
                if x["actual_root_flip"] is not None or x["treated_bestmove"] is not None:
                    raise ValueError("P1_ORIGINAL_HOLD_TREATED")
                continue
            if x["status"]!="REAL_NATIVE_PHYSICAL_TT_FIRST" or not x["source_TT_first_contact"]:
                raise ValueError("P1_NO_ACTUAL_NATIVE_SOURCE_FIRST_CONTACT")
            contacts+=1;lanes[key]["eligible"].append(i)
            flip=(x["actual_root_flip"] is True)
            if flip:lanes[key]["flipped"].append(i);actual[i]+=1;flips+=1
            elif x["actual_root_flip"] is not False:
                raise ValueError("P1_AMBIGUOUS_REAL_ROOT_FLIP")
    if (holds,contacts,flips)!=(12,1012,96):
        raise ValueError("P1_ORIGINAL_1024_SOURCE_ROLE_DENOMINATORS_CHANGED")
    hist=Counter(actual.get(i,0) for i in range(1,257))
    if dict(hist)!={0:208,1:15,2:25,3:1,4:7}:
        raise ValueError("P1_ORIGINAL_GAME_FLIP_HISTOGRAM_WRONG")
    return lanes,actual,hist
def metrics(flipbygame):
    counts=list(flipbygame.values())
    return {
        "games_all_four_roles_changed":sum(n==4 for n in counts),
        "games_two_or_more_roles_changed":sum(n>=2 for n in counts),
        "games_three_or_more_roles_changed":sum(n>=3 for n in counts),
        "highest_roles_changed_in_a_game":max(counts,default=0)
    }
def simulate(lanes,repetitions=ITERATIONS,seed=SEED):
    if repetitions<=0:raise ValueError("P1_POSITIVE_REPLICATIONS_REQUIRED")
    rng=random.Random(seed)
    keys=[f"{o}/{r}" for o,r in ROLES]
    for key in keys:
        e=lanes[key]["eligible"];f=lanes[key]["flipped"]
        if len(set(e))!=len(e) or not set(f).issubset(set(e)):
            raise ValueError("P1_INVALID_FIXED_ELIGIBILITY_MASK")
    distribution={k:[] for k in (
        "games_all_four_roles_changed","games_two_or_more_roles_changed",
        "games_three_or_more_roles_changed","highest_roles_changed_in_a_game")}
    for _ in range(repetitions):
        cnt=Counter()
        for k in keys:
            e=lanes[k]["eligible"]
            n=len(lanes[k]["flipped"])
            for gid in rng.sample(e,n):cnt[gid]+=1
        stats=metrics(cnt)
        for k,x in stats.items():distribution[k].append(x)
    return distribution
def report(rows,repetitions=ITERATIONS,seed=SEED):
    lanes,observed,hist=role_lanes(rows)
    obs=metrics(observed);sim=simulate(lanes,repetitions,seed)
    summary={}
    for name,raw in sim.items():
        q=sorted(raw)
        hi=sum(v>=obs[name] for v in raw)
        summary[name]={
            "observed":obs[name],
            "artificial_role_independence_null_mean":sum(raw)/len(raw),
            "null_median":q[(len(q)-1)//2],
            "null_95pct_percentile_range":[q[int(.025*(len(q)-1))],q[int(.975*(len(q)-1))]],
            "descriptive_one_sided_monte_carlo_p":(hi+1)/(repetitions+1),
            "replicates_ge_observed":hi
        }
    return {
       "schema":SCHEMA,
       "science_status":"EXPOSED_DEVELOPMENT_DESCRIPTIVE_ARTIFICIAL_ROLE_EXCHANGEABILITY_NULL",
       "historical_original_shard_SHA256":list(SHAS),
       "source_game_rows":256,
       "nested_role_cells":1024,
       "actual_physically_contacted":1012,
       "original_prior_HOLD":12,
       "actual_root_flips":96,
       "original_games_with_any_flip":48,
       "observed_games_by_number_of_changed_roles":{str(k):hist[k] for k in range(5)},
       "four_source_role_lanes":{k:{"eligible_original_game_positions":len(v["eligible"]),
                                    "original_root_flips":len(v["flipped"])}
                                 for k,v in lanes.items()},
       "null_fixed_original_preHOLD_mask":True,
       "null_fixed_role_specific_marginal_flip_counts":True,
       "null_independent_original_game_reassignment_per_role":True,
       "monte_carlo_replicates":repetitions,"PRNG_seed":seed,
       "developmental_cooccurrence_tests":summary,
       "what_cannot_be_concluded":[
          "One-sided Monte Carlo p-values describe role-label exchangeability, not a real randomized TT mechanism or independent model validation.",
          "Original games share player/event and state features; each fixed source game contains nested O/F STRICT/BROAD roles.",
          "Correlated root flips do not isolate actual TT score use, natural SEE activation, branch pruning or full root ancestry.",
          "Original 2025July source is fully exposed and cannot be a new M5 heldout."],
       "legal_source":"Lichess official July2025 broadcast CC BY-SA4 and Stockfish16 research derivative; source full PGN/player names/FEN/native TT keys not uploaded"
    }
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--shards",required=True)
    a.add_argument("--out",required=True)
    x=a.parse_args()
    r=report(read_shards(x.shards))
    out=Path(x.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("C3X025_P1_JULY256_ROLE_FLIP_PERMUTATION_VERDICT",
          {"histogram":r["observed_games_by_number_of_changed_roles"],
           "role_lane_counts":r["four_source_role_lanes"],
           "descriptive_monte_carlo":r["developmental_cooccurrence_tests"]},
          flush=True)
    print("C3X025_P1_ORIGINAL_EXPOSED_GAME_CORRELATION_JSON_SHA256",
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
