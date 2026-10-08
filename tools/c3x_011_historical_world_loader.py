#!/usr/bin/env python3
"""C3X 0.11 historical world loader: explicit JSON/JSONL/EPD boundary.

All historical sources must be inventoried and provenance-qualified separately.
Parses FEN-only from EPD: bm, comments, ids and themes never enter outputs.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from g10_p19_source_census import walk_history, canonicalize_fen_text

def sha(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()

def load(root: Path):
    root=Path(root)
    if not root.is_dir(): raise ValueError("HISTORY_ROOT_NOT_FOUND")
    fingerprints=set()
    manifest=[]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".json",".jsonl",".epd"):
            continue
        raw=path.read_bytes()
        try:
            source=raw.decode("utf-8-sig")
        except UnicodeDecodeError as e:
            raise ValueError(f"HISTORY_DECODE_FAILURE:{path}") from e
        seen=set()
        if path.suffix.lower()==".json":
            try: walk_history(json.loads(source),seen)
            except Exception as e: raise ValueError(f"HISTORY_BAD_JSON:{path}") from e
        elif path.suffix.lower()==".jsonl":
            for n,line in enumerate(source.splitlines(),1):
                if not line.strip():continue
                try: obj=json.loads(line)
                except Exception as e: raise ValueError(f"HISTORY_BAD_JSONL:{path}:{n}") from e
                walk_history(obj,seen)
        else:
            for n,line in enumerate(source.splitlines(),1):
                if not line.strip() or line.lstrip().startswith("#"):continue
                epd=line.split(";",1)[0].strip().split()
                if len(epd)<4:
                    raise ValueError(f"HISTORY_BAD_EPD:{path}:{n}")
                normalized=canonicalize_fen_text(" ".join(epd[:4])+" 0 1")
                if not normalized:
                    raise ValueError(f"HISTORY_ILLEGAL_EPD_FEN:{path}:{n}")
                seen.add(sha(normalized))
        fingerprints.update(seen)
        manifest.append({"relative_path":str(path.relative_to(root)),
                         "raw_sha256":hashlib.sha256(raw).hexdigest(),
                         "unique_fen_hashes":len(seen),"kind":path.suffix.lower()})
    if not manifest:raise ValueError("HISTORY_EMPTY_INVENTORY")
    return fingerprints,manifest
