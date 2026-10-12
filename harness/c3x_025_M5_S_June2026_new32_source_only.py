#!/usr/bin/env python3
"""M5-S 2026 June source-only selector. Reuses previously tested source rules,
but starts a *new* untampered source archive and forbids native engine use.
This file is PGN parse/selection only; core hypothesis is chess-search native C++.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c3x_024_P3_sep2025_engineblind_source128 as frozen
frozen.URL="https://database.lichess.org/broadcast/lichess_db_broadcast_2026-06.pgn.zst"
frozen.CHARTER="c3x/ontology/c3x-025-P14-P2-M5-June2026-source-and-model-preregister-20261012.md"
frozen.SCAN_MAX=12000
frozen.FIRST_ELIGIBLE=1024
frozen.PICK=32
frozen.SCHEMA="c3x025-M5-S-june2026-source-only-independent-32-v1"
if __name__=="__main__":
    import argparse,hashlib,json
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument("--zst",required=True)
    p.add_argument("--history",action="append",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=frozen.produce(a.zst,a.history)
    # Original source authority is Lichess CC BY-SA, not TWIC. The older
    # selector's narrative string mentioned TWIC rights purely as a negative
    # assurance, which the general lexical scanner mistakenly treats as TWIC
    # origin when paired with legal FEN4. Do not mislabel this source.
    result["release_limit"]="Only source-derived Lichess CC BY-SA minimal legal board, game digest and one move. No original PGNs, player identity, external rights correspondence or binary."
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X025_M5_S_JUNE_ENGINE_BLIND_FEN4_AND_PRIOR_HISTORY",
          result["source_fen_count"],result["original_compressed_source_sha256"],
          hashlib.sha256(out.read_bytes()).hexdigest(),
          len(result["historical_source_receipts"]),flush=True)
