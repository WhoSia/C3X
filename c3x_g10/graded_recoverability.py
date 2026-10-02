from __future__ import annotations
import itertools, json
from copy import deepcopy
from c3x_g10.acquisition_policy import (
    GRAMMAR, trigger_from_chain, trigger_from_cert, transform_trigger,
    nontrivial_orbit_prototypes, position_features, distance
)
from c3x_g10.morphism_grammar import development_adjudication

INF = 99

def _canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))

def cayley_distance(a, b):
    """Minimum word length under frozen C/S/E, or INF if unreachable."""
    target = _canon(b)
    for r in range(len(GRAMMAR) + 1):
        for subset in itertools.combinations(GRAMMAR, r):
            if _canon(transform_trigger(a, subset)) == target:
                return r
    return INF

def polarity_profile(t):
    return tuple(sorted(edge[1] for edge in t["delta_edges"]))

def development_geometry(ecology):
    d = development_adjudication(ecology)
    certs = {c["id"]: c for c in ecology["certificates"]}
    families = {}
    nonfamily = []
    for i, part in enumerate(d["orbit_partition"]):
        rows = [trigger_from_cert(certs[cid]) for cid in part]
        if len(part) >= 2:
            families[f"orbit-{i}"] = {"members": list(part), "triggers": rows}
        else:
            nonfamily.extend({"id": cid, "trigger": trigger_from_cert(certs[cid])} for cid in part)
    return families, nonfamily

def chain_score(ch, families, nonfamily):
    t = trigger_from_chain(ch)
    family_dist = {}
    for fid, fam in families.items():
        family_dist[fid] = min(cayley_distance(t, p) for p in fam["triggers"])
    ordered = sorted(family_dist.items(), key=lambda kv: (kv[1], kv[0]))
    best_family, best_d = ordered[0]
    second_d = ordered[1][1] if len(ordered) > 1 else INF
    same_pol_rivals = [
        cayley_distance(t, row["trigger"])
        for row in nonfamily
        if polarity_profile(row["trigger"]) == polarity_profile(t)
    ]
    rival_d = min(same_pol_rivals) if same_pol_rivals else INF
    margin = min(4, rival_d) - min(4, best_d)
    specificity = min(4, second_d) - min(4, best_d)
    return {
        "chain_id": ch["chain_id"],
        "best_family": best_family,
        "family_distance": best_d,
        "family_margin": margin,
        "family_specificity": specificity,
        "polarity_profile": list(polarity_profile(t)),
        "family_distances": family_dist,
        "rival_distance": rival_d,
    }

def _rank_tuple(score):
    return (
        int(score["family_margin"]),
        -int(score["family_distance"]),
        int(score["family_specificity"]),
        float(score["family_consensus"]),
    )

def position_score(pid, p, families, nonfamily):
    cs = [chain_score(ch, families, nonfamily) for ch in p.get("chain_candidates", [])]
    if not cs:
        raise ValueError(f"{pid}: no chain candidates")
    cs.sort(key=lambda s: (
        s["family_margin"], -s["family_distance"], s["family_specificity"],
        s["best_family"], s["chain_id"]
    ), reverse=True)
    best = cs[0]
    same = sum(1 for s in cs if s["best_family"] == best["best_family"])
    out = deepcopy(best)
    out.update({
        "position_id": pid,
        "chain_candidate_count": len(cs),
        "family_consensus": same / len(cs),
        "rank_tuple": None,
        "all_chain_scores": cs,
    })
    out["rank_tuple"] = list(_rank_tuple(out))
    return out

def _strictly_higher(a, b):
    return _rank_tuple(a) > _rank_tuple(b)

def census(pair_freezes, ecology, max_pairs_per_source=12, min_pairs_per_source=6):
    families, nonfamily = development_geometry(ecology)
    positions = {}
    for pf in pair_freezes:
        positions.update(pf["positions"])

    by_source = {}
    for pid, p in positions.items():
        if p.get("admitted") and p.get("chain_candidates"):
            by_source.setdefault(p["source_id"], []).append((pid, p))

    assignments = []
    source_stats = {}
    all_scores = {}

    for source, rows in sorted(by_source.items()):
        scored = []
        for pid, p in rows:
            s = position_score(pid, p, families, nonfamily)
            all_scores[pid] = s
            scored.append((pid, p, s))

        rank_values = sorted({_rank_tuple(s) for _, _, s in scored}, reverse=True)
        variation = len(rank_values) > 1

        by_pol = {}
        for row in scored:
            by_pol.setdefault(tuple(row[2]["polarity_profile"]), []).append(row)

        src_assign = []
        for pol, group in sorted(by_pol.items()):
            group.sort(key=lambda x: (_rank_tuple(x[2]), x[0]), reverse=True)
            n = len(group)
            if n < 2:
                continue
            hi = group[: n // 2]
            lo = group[(n + 1) // 2 :]
            used = set()
            for tpid, tp, ts in hi:
                avail = [
                    (cpid, cp, cs) for cpid, cp, cs in lo
                    if cpid not in used and _strictly_higher(ts, cs)
                ]
                if not avail:
                    continue
                cpid, cp, cs = min(
                    avail,
                    key=lambda x: (distance(tp, x[1]), x[0])
                )
                used.add(cpid)
                src_assign.append({
                    "source_id": source,
                    "polarity_profile": list(pol),
                    "target_position_id": tpid,
                    "control_position_id": cpid,
                    "target_score": ts["rank_tuple"],
                    "control_score": cs["rank_tuple"],
                    "target_family": ts["best_family"],
                    "control_family": cs["best_family"],
                    "match_distance": distance(tp, cp),
                    "target_features": position_features(tp),
                    "control_features": position_features(cp),
                })

        src_assign.sort(key=lambda a: (
            tuple(a["target_score"]), -a["match_distance"], a["target_position_id"]
        ), reverse=True)
        src_assign = src_assign[:max_pairs_per_source]
        assignments.extend(src_assign)

        source_stats[source] = {
            "chain_eligible_positions": len(scored),
            "distinct_rank_tuples": len(rank_values),
            "rank_variation": variation,
            "matched_rank_separated_pairs": len(src_assign),
            "polarity_counts": {
                "|".join(k): len(v) for k, v in sorted(by_pol.items())
            },
        }

    firewall = True
    if not source_stats:
        verdict = "HOLD_GRADED_SELECTOR_NONDISCRIMINATIVE"
    elif any(not s["rank_variation"] for s in source_stats.values()):
        verdict = "HOLD_GRADED_SELECTOR_NONDISCRIMINATIVE"
    elif any(s["matched_rank_separated_pairs"] < min_pairs_per_source for s in source_stats.values()):
        verdict = "HOLD_MATCHED_CONTROL_POSITIVITY_INSUFFICIENT"
    else:
        verdict = "PASS_PREOUTCOME_GRADED_SELECTOR_POSITIVITY"

    return {
        "schema": "c3x-g10-p9-preoutcome-census-v1",
        "verdict": verdict,
        "firewall_pass": firewall,
        "pair_freeze_run": 36980730341,
        "grammar": list(GRAMMAR),
        "families": {
            k: {"members": v["members"]} for k, v in families.items()
        },
        "nonfamily_prototypes": [x["id"] for x in nonfamily],
        "source_stats": source_stats,
        "assignments": assignments,
        "position_scores": all_scores,
        "forbidden_outcomes_consulted": [],
        "chain_qualification_opened": False,
        "factorial_outcomes_opened": False,
        "certificate_outcomes_opened": False,
        "family_admission_opened": False,
    }
