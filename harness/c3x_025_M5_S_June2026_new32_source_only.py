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
    frozen.main()
