#!/usr/bin/env python3
"""R46, outcome-blind publisher source audit only.
Never runs an engine. Raw PGNs stay in job temp; aggregate excludes moves/FEN.
A provisional sample is NOT an independently admitted cohort.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import unicodedata
import zipfile
import chess
import chess.pgn
from c3x_031_p2_source_intake import tournament_series,check_blocklist

PRIOR=(1663,1664,1669,1670,1671)
NEW=1672
CHECKPOINTS=(40,41,50,51,60,61,70,71,80,81)
SEED="C3X-R46-TWIC1672-PREFREEZE-v1"\n
CAP=64

def sha(b):return hashlib.sha256(b).hexdigest()
def order(s):return sha((SEED+"/"+s).encode())
def name(s):return unicodedata.normalize("NFC",s).casefold().strip()
def group(s):
    n=name(s)
    # R46b: pre-outcome title audit; deliberately conservative macro grouping.
    if "total chess pilot" in n:return "total-chess-pilot-series"
    if n.startswith("na youth"):return "north-american-youth-series"
    if "charlotte fall" in n:return "charlotte-fall-series"
    if "tch-cro" in n:return "croatian-team-series"
    if "bundesliga" in n:return "bundesliga-series"
    if "world cadet" in n:return "world-cadet-series"
    if "turkic nations" in n:return "turkic-nations-series"
    if "jerusalem" in n:return "jerusalem-series"
    if "danzhou" in n:return "danzhou-series"
    if ("u20" in n or "world junior" in n) and ("world" in n or "fide" in n):return "world-junior-series"
    if "asean plus" in n:return "asean-plus-series"
    if "tal memorial" in n:return "tal-memorial-series"
    if "future stars" in n:return "future-stars-series"
    # Merge explicit section suffixes; no inferred date/identity equivalence.
    n=re.sub(r"\s+(?:women|woman|girls|open|rapid|blitz|classical|main|group [a-z]|gp[a-z])(?=\s|$)","",n)
    return tournament_series(n)

def board_key(b):return " ".join(b.fen(en_passant="legal").split()[:4])
def read_archive(folder,issue):
    raw=(folder/f"twic{issue}g.zip").read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        files=z.namelist()
        assert len(files)==1 and files[0].lower().endswith(".pgn") and str(issue) in files[0]
        pgn=z.read(files[0])
    receipt={"issue":issue,"zip_sha256":sha(raw),"pgn_sha256":sha(pgn),"zip_bytes":len(raw),
             "pgn_bytes":len(pgn),"event_header_records":pgn.count(b'[Event "')}
    # Preserve parsing-count discrepancies, don't silently accept listed count as actual.
    return io.StringIO(pgn.decode("latin-1")),receipt

def scan(folder,blocklist,admission,out):
    previous=set(check_blocklist(blocklist))
    previous.update(json.loads(admission.read_text())["admitted_family_counts"])
    prior_groups={group(x) for x in previous}
    prior_titles={name(x) for x in previous}
    old_hashes=set()
    old_board_keys=set()
    receipts=[]
    for issue in PRIOR:
        stream,receipt=read_archive(folder,issue)
        count=Counter();families=Counter()
        while (g:=chess.pgn.read_game(stream)) is not None:
            count["parsed"]+=1
            event=g.headers.get("Event","?")
            families[name(event)]+=1
            prior_titles.add(name(event));prior_groups.add(group(event))
            if g.errors or g.board().fen()!=chess.STARTING_FEN or g.board().chess960:
                count["invalid"]+=1;continue
            moves=list(g.mainline_moves())
            if not moves:count["empty"]+=1;continue
            old_hashes.add(sha(" ".join(m.uci() for m in moves).encode()))
            b=g.board()
            # Cover all previous and current checkpoint plies from documented R26/R28/P2.
            for ply,m in enumerate(moves,1):
                b.push(m)
                if ply in {30,41,50,61,70,81,96,*CHECKPOINTS}:old_board_keys.add(board_key(b))
                if ply>=96:break
            count["legal_nonempty"]+=1
        receipt.update(counts=dict(count),raw_family_count=len(families))
        receipts.append(receipt)
    stream,receipt=read_archive(folder,NEW)
    families=Counter();counts=Counter();pools=defaultdict(list);status=defaultdict(Counter);seen=set()
    while (g:=chess.pgn.read_game(stream)) is not None:
        counts["parsed"]+=1
        event=g.headers.get("Event","?")
        title=name(event);key=group(event);families[title]+=1
        status[title]["all"]+=1
        def reject(reason):
            counts[reason]+=1;status[title][reason]+=1
        if g.errors or event=="?" or g.board().fen()!=chess.STARTING_FEN or g.board().chess960:
            reject("invalid");continue
        moves=list(g.mainline_moves())
        if not moves:reject("empty");continue
        digest=sha(" ".join(m.uci() for m in moves).encode())
        if digest in seen:reject("duplicate_new_history");continue
        seen.add(digest)
        if digest in old_hashes:reject("prior_history_overlap");continue
        if title in prior_titles:reject("prior_exact_title");continue
        if key in prior_groups:reject("prior_macro_family");continue
        b=g.board();candidate=None
        for ply,m in enumerate(moves,1):
            b.push(m)
            if ply in CHECKPOINTS and b.legal_moves.count()>=2 and not b.is_game_over():
                candidate=(ply,board_key(b));break
            if ply>=CHECKPOINTS[-1]:break
        if candidate is None:reject("no_checkpoint");continue
        ply,bk=candidate
        if bk in old_board_keys:reject("prior_board_overlap");continue
        pools[key].append((digest,sha(bk.encode()),ply,counts["parsed"],title))
        counts["provisional_eligible"]+=1;status[title]["provisional_eligible"]+=1
    groups=sorted(pools,key=order)
    for key in groups:pools[key].sort(key=lambda x:order(x[0]))
    sample=[];boards=set()
    for offset in range(max((len(x) for x in pools.values()),default=0)):
        for key in groups:
            if offset>=len(pools[key]):continue
            game,bk,ply,ordinal,title=pools[key][offset]
            if bk in boards:continue
            boards.add(bk)
            sample.append({"game_sha256":game,"board_sha256":bk,"ply":ply,"ordinal":ordinal,"event":title,"macro_family":key})
            if len(sample)>=CAP:break
        if len(sample)>=CAP:break
    assert receipt["zip_sha256"]=="d1c90cb7fe483e428446fc699c9f67daad742234c5badfe0df393d341ac11862", "new archive drift"
    assert receipt["pgn_sha256"]=="613d2d90c008f015529e19432b32142eb643f4113c4cf285dd631f3b0b35a8d7", "new PGN drift"
    assert counts["parsed"]==8117, "publisher census drift"
    receipt.update(counts=dict(counts),raw_family_count=len(families),publisher_listed_games=8117)
    result={"gate":"PROVISIONAL_SOURCE_AUDIT_NOT_ADMISSION","old_issues":receipts,"new_issue":receipt,
        "old_distinct_complete_histories":len(old_hashes),"old_checkpoint_board_keys":len(old_board_keys),
        "prior_title_count":len(prior_titles),"prior_macro_family_count":len(prior_groups),
        "per_title":{k:{"macro_family":group(k),**dict(v)} for k,v in sorted(status.items())},
        "provisional_sample":sample,"provisional_family_count":len({x["macro_family"] for x in sample}),
        "engine_searches":0,"treatment_outcomes":0,
        "limitations":["All five prior issue archives plus frozen 94 and P2 family lists, not exhaustive historical sources.",
            "Board overlap checked only at documented checkpoints; title/series alias review needed.",
            "Provisional sample, no raw PGN or FEN in output, no native study until exact admission sealed."]}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("R46_CENSUS",json.dumps({k:v for k,v in result.items() if k not in ("per_title","provisional_sample")},sort_keys=True),flush=True)
    for k,v in result["per_title"].items(): print("R46_TITLE",json.dumps({"title":k,**v},sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("folder","blocklist","admission","out"):p.add_argument(k,type=Path)
    a=p.parse_args();scan(a.folder,a.blocklist,a.admission,a.out)
