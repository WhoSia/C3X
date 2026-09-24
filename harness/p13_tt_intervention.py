#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

C2_KEYS = [
    "use_main_eval",
    "use_main_value",
    "use_main_cutoff_gate",
    "use_successor_value",
    "use_qsearch_eval",
    "use_qsearch_value",
    "use_qsearch_cutoff",
]

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_obj(obj):
    return hashlib.sha256(canonical_json(obj)).hexdigest()

def run_search(binary, fen, mode, nodes):
    p = subprocess.Popen(
        [binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    commands = [
        "uci",
        f"setoption name C3X_TTReadMode value {mode}",
        "setoption name C3X_Telemetry value true",
        "setoption name Threads value 1",
        "setoption name Hash value 64",
        "setoption name SyzygyProbeLimit value 0",
        "setoption name UCI_ShowWDL value true",
        "setoption name Clear Hash",
        "isready",
        f"position fen {fen}",
        f"go nodes {nodes}",
    ]
    for cmd in commands:
        p.stdin.write(cmd + "\n")
    p.stdin.flush()

    lines = []
    for line in p.stdout:
        line = line.rstrip("\n")
        lines.append(line)
        if line.startswith("bestmove "):
            break

    p.terminate()
    try:
        rest, _ = p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
        rest, _ = p.communicate(timeout=5)
    if rest:
        lines.extend(rest.splitlines())

    best = next((x for x in reversed(lines) if x.startswith("bestmove ")), None)
    infos = [x for x in lines if x.startswith("info depth ") and " score " in x and " pv " in x]
    telemetry_line = next((x for x in lines if x.startswith("info string c3x_ttread_v1 ")), None)
    if not best or not infos or not telemetry_line:
        raise RuntimeError("incomplete search receipt\n" + "\n".join(lines[-80:]))

    final = infos[-1]
    best_tokens = best.split()
    bestmove = best_tokens[1]
    ponder = best_tokens[3] if len(best_tokens) >= 4 and best_tokens[2] == "ponder" else None

    def grab(pattern):
        m = re.search(pattern, final)
        return m.group(1) if m else None

    telemetry = {}
    for tok in telemetry_line.split()[3:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            try:
                telemetry[k] = int(v)
            except ValueError:
                telemetry[k] = v

    semantic = {
        "bestmove": bestmove,
        "ponder": ponder,
        "depth": int(grab(r"\bdepth (\d+)") or 0),
        "seldepth": int(grab(r"\bseldepth (\d+)") or 0),
        "score": grab(r"\bscore ((?:cp|mate) -?\d+)"),
        "wdl": grab(r"\bwdl (\d+ \d+ \d+)"),
        "nodes": int(grab(r"\bnodes (\d+)") or 0),
        "pv": grab(r"\bpv (.+)$"),
    }
    return {"semantic": semantic, "telemetry": telemetry, "telemetry_line": telemetry_line}

def engagement(receipt):
    t = receipt["telemetry"]
    H = sum(int(t.get(k, 0)) for k in ("raw_hits_main", "raw_hits_successor", "raw_hits_qsearch"))
    U = int(t.get("semantic_uses", 0))
    B = int(t.get("breadth", 0))
    c2 = {k: int(t.get(k, 0)) for k in C2_KEYS}
    non_move_order = any(v > 0 for v in c2.values())
    passed = H >= 64 and U >= 16 and B >= 2 and non_move_order
    return {"H": H, "U": U, "B": B, "c2": c2, "non_move_order": non_move_order, "passed": passed}

def choose_tranche(rows, target=12):
    strata = defaultdict(list)
    for row in rows:
        c = row["candidate"]
        e = row["engagement"]
        key = (c["material_signature"], c["side_to_move"])
        strata[key].append(row)

    for key in strata:
        strata[key].sort(key=lambda r: (
            -int(r["candidate"]["tau4"]["tau4"]),
            -int(r["engagement"]["B"]),
            -int(r["engagement"]["U"]),
            -int(r["engagement"]["H"]),
            r["candidate"]["candidate_sha256"],
        ))

    ordered_keys = sorted(strata)
    chosen = []
    i = 0
    while len(chosen) < target and ordered_keys:
        progressed = False
        for key in ordered_keys:
            if i < len(strata[key]) and len(chosen) < target:
                chosen.append(strata[key][i])
                progressed = True
        if not progressed:
            break
        i += 1
    return chosen[:target]

def mover_world_class(candidate, uci):
    move_map = {m["uci"]: int(m["mover_wdl"]) for m in candidate["world"]["moves"]}
    return move_map.get(uci)

def sham_commit(args):
    stage = json.loads(Path(args.stage_a).read_text())
    rows = []
    for idx, candidate in enumerate(stage["candidates"], 1):
        receipt = run_search(args.binary, candidate["fen"], "SHAM", args.nodes)
        eg = engagement(receipt)
        rows.append({"candidate": candidate, "sham": receipt, "engagement": eg})
        print(
            f"SHAM {idx:02d}/{len(stage['candidates'])} "
            f"id={candidate['candidate_sha256'][:12]} "
            f"H={eg['H']} U={eg['U']} B={eg['B']} pass={eg['passed']}",
            flush=True,
        )

    engaged = [r for r in rows if r["engagement"]["passed"]]
    chosen = choose_tranche(engaged, target=12)

    materials = sorted({r["candidate"]["material_signature"] for r in chosen})
    turns = sorted({r["candidate"]["side_to_move"] for r in chosen})
    ready = len(chosen) >= 8 and len(materials) >= 3 and set(turns) == {"BLACK", "WHITE"}

    payload = {
        "schema": "c3x-p13-sham-precommit-v1",
        "scientific_stage": "C3X 0.7.0-G9.4-P13",
        "stage_a_pool_sha256": stage["pool_sha256"],
        "masked_outcomes_consulted": False,
        "binary": {
            "path_basename": os.path.basename(args.binary),
            "sha256": sha256_file(args.binary),
        },
        "runtime": {
            "threads": 1,
            "hash_mib": 64,
            "nodes": args.nodes,
            "clear_hash_each_arm": True,
            "syzygy_probe_limit": 0,
        },
        "gate": {
            "H_min": 64, "U_min": 16, "B_min": 2,
            "require_non_move_order": True,
        },
        "counts": {
            "stage_a": len(rows),
            "engaged": len(engaged),
            "committed": len(chosen),
            "material_signatures": len(materials),
            "sides_to_move": turns,
        },
        "authorization": "TARGET-INTERVENTION-READY" if ready else "TT-PATH-ENGAGEMENT-SCARCITY / RETURN-TO-COMPILER",
        "committed_cells": chosen,
    }
    payload["precommit_sha256"] = sha256_obj(payload)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        f"SHAM_PRECOMMIT authorization={payload['authorization']} "
        f"sha256={payload['precommit_sha256']} counts={payload['counts']}"
    )
    if not ready:
        raise SystemExit(2)

def masked_run(args):
    pre = json.loads(Path(args.precommit).read_text())
    if pre.get("authorization") != "TARGET-INTERVENTION-READY":
        raise SystemExit("MASKED-HOLD precommit not authorized")
    actual = sha256_file(args.binary)
    expected = pre["binary"]["sha256"]
    if actual != expected:
        raise SystemExit(f"BINARY-IDENTITY-FAIL {actual} != {expected}")

    pairs = []
    for idx, row in enumerate(pre["committed_cells"], 1):
        candidate = row["candidate"]
        sham = run_search(args.binary, candidate["fen"], "SHAM", args.nodes)
        masked = run_search(args.binary, candidate["fen"], "MASKED", args.nodes)

        sham_class = mover_world_class(candidate, sham["semantic"]["bestmove"])
        masked_class = mover_world_class(candidate, masked["semantic"]["bestmove"])
        if sham_class is None or masked_class is None:
            raise SystemExit(
                f"WORLD-MOVE-JOIN-FAIL id={candidate['candidate_sha256']} "
                f"sham={sham['semantic']['bestmove']} masked={masked['semantic']['bestmove']}"
            )
        pairs.append({
            "candidate_sha256": candidate["candidate_sha256"],
            "material_signature": candidate["material_signature"],
            "side_to_move": candidate["side_to_move"],
            "fen": candidate["fen"],
            "tau4": candidate["tau4"]["tau4"],
            "sham": sham,
            "masked": masked,
            "sham_world_class": sham_class,
            "masked_world_class": masked_class,
            "action_changed": sham["semantic"]["bestmove"] != masked["semantic"]["bestmove"],
            "quotient_changed": sham_class != masked_class,
            "world_delta": masked_class - sham_class,
        })
        print(
            f"MASKED_PAIR {idx:02d}/{len(pre['committed_cells'])} "
            f"id={candidate['candidate_sha256'][:12]} "
            f"sham={sham['semantic']['bestmove']}:{sham_class} "
            f"masked={masked['semantic']['bestmove']}:{masked_class}",
            flush=True,
        )

    q_changed = sum(p["quotient_changed"] for p in pairs)
    a_changed = sum(p["action_changed"] for p in pairs)
    degraded = sum(p["world_delta"] < 0 for p in pairs)
    improved = sum(p["world_delta"] > 0 for p in pairs)
    score_changed = sum(p["sham"]["semantic"]["score"] != p["masked"]["semantic"]["score"] for p in pairs)

    if q_changed:
        verdict = "TT-READ-PATH-DEPENDENT-QUOTIENT@ENGAGED-EXACT-WORLD-SCOPE"
    elif a_changed:
        verdict = "TT-READ-PATH-DEPENDENT-ACTION / QUOTIENT-STABLE@ENGAGED-EXACT-WORLD-SCOPE"
    elif score_changed:
        verdict = "TT-READ-PATH-DEPENDENT-SEARCH-OUTPUT / ACTION-QUOTIENT-STABLE@ENGAGED-EXACT-WORLD-SCOPE"
    else:
        verdict = "NO-DETECTED-MASKED-EFFECT@COMMITTED-TRANCHE"

    payload = {
        "schema": "c3x-p13-masked-result-v1",
        "scientific_stage": "C3X 0.7.0-G9.4-P13",
        "precommit_sha256": pre["precommit_sha256"],
        "binary_sha256": actual,
        "runtime": pre["runtime"],
        "counts": {
            "cells": len(pairs),
            "action_changed": a_changed,
            "quotient_changed": q_changed,
            "world_degraded": degraded,
            "world_improved": improved,
            "score_changed": score_changed,
        },
        "verdict": verdict,
        "authority_ceiling": "engaged exact-world committed tranche under frozen engine/fixed-node regime; no representation, knowledge, cognition, or general-chess inference",
        "pairs": pairs,
    }
    payload["result_sha256"] = sha256_obj(payload)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"P13_RESULT verdict={verdict} counts={payload['counts']} sha256={payload['result_sha256']}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sham-commit")
    s.add_argument("--stage-a", required=True)
    s.add_argument("--binary", required=True)
    s.add_argument("--nodes", type=int, default=300000)
    s.add_argument("--out", required=True)

    m = sub.add_parser("masked-run")
    m.add_argument("--precommit", required=True)
    m.add_argument("--binary", required=True)
    m.add_argument("--nodes", type=int, default=300000)
    m.add_argument("--out", required=True)

    args = ap.parse_args()
    if args.cmd == "sham-commit":
        sham_commit(args)
    else:
        masked_run(args)

if __name__ == "__main__":
    main()
