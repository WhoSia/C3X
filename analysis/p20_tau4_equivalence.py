#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"compiler"/"exact_world"))
import chess
import p19_compile as old
from p20_tau4_fast import tau4_fast

MAX=50000
rows=[]
for material,(_,_,pieces) in old.VERTICES.items():
    found=0
    for i in range(24):
        for side in (chess.WHITE,chess.BLACK):
            b=old.candidate(material,pieces,side,i)
            if b is None:
                continue
            a=old.tau4(b,max_paths=MAX)
            z=tau4_fast(b,max_paths=MAX)
            if a!=z:
                print(json.dumps({
                    "material":material,
                    "i":i,
                    "side":"WHITE" if side else "BLACK",
                    "fen":b.fen(),
                    "old":a,
                    "fast":z,
                },indent=2,sort_keys=True))
                raise SystemExit("P20_TAU4_EQUIVALENCE_FAIL")
            rows.append({
                "material":material,
                "i":i,
                "side":"WHITE" if side else "BLACK",
                "overflow":a["overflow"],
                "paths":a["enumerated_depth4_paths"],
                "tau4":a["tau4"],
            })
            found+=1
            if found>=2:
                break
        if found>=2:
            break
    if found<2:
        raise SystemExit("P20_TAU4_TEST_INPUT_SHORTFALL "+material)
print(json.dumps({
    "schema":"c3x-p20-tau4-fast-equivalence-v1",
    "python_chess":chess.__version__,
    "max_paths":MAX,
    "cases":len(rows),
    "verdict":"PASS",
    "rows":rows,
},indent=2,sort_keys=True))
