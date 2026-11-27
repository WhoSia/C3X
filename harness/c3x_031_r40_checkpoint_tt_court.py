#!/usr/bin/env python3
"""P3-B0 partial native court: full physical TT log and checkpoint lookup contact.
The log establishes field continuity and lookup contact, NOT actual downstream
field consumption, mediator sufficiency, or strategic value.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from c3x_030_r23_native_replay import run
from c3x_030_r33_gate_panel import events

ZERO = (0,-7,0,0,0,0,0,0)
FIELDS = {"move": (5,), "score": (0,1,2,3,6,7), "generation": (4,)}
HIST = "2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4"
NET = "5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"
R33 = "ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1"

def require(ok, why):
    if not ok:
        raise ValueError(why)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fields(line):
    out={}
    for token in line.split()[1:]:
        key,value=token.split("=",1)
        require(key not in out,"duplicate token")
        out[key]=value
    return out

def entry(s):
    t=tuple(map(int,s.split(",")))
    require(len(t)==8,"raw tuple arity")
    return t

def changed(a,b,indices):
    return any(a[i]!=b[i] for i in indices)

def replay(lines):
    state={}
    writers={}
    counts=Counter()
    cluster_count=0
    checkpoint=None
    checkpoint_writers=None
    cp=None
    end16=None
    start16=None
    lookups={}
    written=set()
    y1=None
    for serial,line in enumerate(lines,1):
        if line.startswith("C3X_R23_START "):
            x=fields(line)
            if x["attempt"]=="16": start16=x
        elif line.startswith("C3X_R23_END "):
            x=fields(line)
            if x["attempt"]=="16": end16=x
        elif line.startswith("C3X_R23_CANDIDATE "):
            x=fields(line)
            if x["attempt"]=="17" and x["move"]=="f4e5":
                require(y1 is None,"multiple Y1 candidates")
                y1=x
        elif line.startswith("C3X_R40_RESET "):
            require(checkpoint is None or y1 is not None,"reset inside checkpoint-to-Y1 interval")
            cluster_count=int(fields(line)["clusters"])
            require(cluster_count==524288,"unexpected 16MiB TT geometry")
            state.clear()
            writers.clear()
            counts["reset"]+=1
        elif line.startswith("C3X_R40_CHECKPOINT "):
            require(checkpoint is None and cluster_count and end16 and start16,"invalid checkpoint order")
            cp=fields(line)
            require(cp["attempt"]=="17" and cp["root_depth"]=="14" and cp["completed"]=="13"
                    and cp["stopped"]=="0" and cp["pv_idx"]=="0","wrong physical checkpoint")
            require(end16["stopped"]=="0" and int(start16["alpha"])<int(end16["value"])<int(start16["beta"])
                    and cp["nodes"]==end16["nodes"],"END16 did not finish accepted aspiration")
            checkpoint=state.copy()
            checkpoint_writers=writers.copy()
        elif line.startswith(("C3X_R40_SAVE ","C3X_R40_PROBE ")):
            require(cluster_count>0,"event before table reset")
            x=fields(line)
            key=int(x["key"])
            slot=(int(x["cluster"]),int(x["slot"]))
            require(0<=key<2**64 and 0<=slot[0]<cluster_count and 0<=slot[1]<3
                    and slot[0]==(key*cluster_count)>>64,"invalid physical cluster/slot")
            before,after=entry(x["before"]),entry(x["after"])
            require(state.get(slot,ZERO)==before,"unlogged native state mutation")
            active=checkpoint is not None and y1 is None
            if line.startswith("C3X_R40_SAVE "):
                require(x["valid"]=="1","save pointer outside requested cluster")
                mw,sw=int(x["move_write"]),int(x["score_write"])
                require(mw in (0,1) and sw in (0,1),"invalid write flags")
                require(mw or before[5]==after[5],"unlogged move write")
                require(sw or not changed(before,after,FIELDS["score"]+FIELDS["generation"]),"unlogged score/gen write")
                require(not sw or after[0]==(key&65535),"score writer tag mismatch")
                writes=({"move"} if mw else set()) | ({"score","generation"} if sw else set())
                counts["save"]+=1
            else:
                refresh,hit=int(x["refresh"]),int(x["hit"])
                require(refresh in (0,1) and hit in (0,1),"invalid lookup flags")
                require(not changed(before,after,FIELDS["move"]+FIELDS["score"]),"probe modified non-age fields")
                require((refresh and after[4]==int(x["generation"])) or
                        (not refresh and not hit and after==before),"invalid generation mutation")
                require(not refresh or (hit==(before[1]!=-7) and (not hit or before[0]==(key&65535))),"hit/tag mismatch")
                if active:
                    for field in FIELDS:
                        token=(slot,field)
                        if token not in written and token not in lookups and (hit or field=="generation"):
                            writer=writers.get(token)
                            lookups[token]={"query":key,"writer_exact":bool(writer and writer[0]==key),"hit":bool(hit)}
                writes={"generation"} if refresh else set()
                counts["probe"]+=1
            for field in writes:
                writers[(slot,field)]=(key,serial)
                if active: written.add((slot,field))
            state[slot]=after
    require(checkpoint is not None and checkpoint_writers is not None and y1 is not None and counts["save"] and counts["probe"],"incomplete R40 event window")
    return {"state":checkpoint,"writers":checkpoint_writers,"cp":cp,"y1":y1,"lookups":lookups,"counts":dict(counts)}

def compare(a,b):
    slots=set(a["state"])|set(b["state"])
    diff=Counter()
    contact={"sham":Counter(),"both":Counter()}
    exact={"sham":Counter(),"both":Counter()}
    for slot in slots:
        left=a["state"].get(slot,ZERO)
        right=b["state"].get(slot,ZERO)
        for field,indices in FIELDS.items():
            if not changed(left,right,indices): continue
            diff[field]+=1
            for name,arm in (("sham",a),("both",b)):
                match=arm["lookups"].get((slot,field))
                if match:
                    contact[name][field]+=1
                    exact[name][field]+=int(match["writer_exact"])
    return {"differing_checkpoint_slots_by_field":dict(diff),
            "before_next_field_write_lookup_contact":{k:dict(v) for k,v in contact.items()},
            "contact_with_matching_full_writer_key":{k:dict(v) for k,v in exact.items()},
            "scope":"lookup contact, not actual field consumption"}

def main():
    p=argparse.ArgumentParser()
    for name in ("history","net","baseline","observer","output"):
        p.add_argument(name,type=Path)
    a=p.parse_args()
    require(digest(a.history)==HIST and digest(a.net)==NET and digest(a.baseline)==R33,"input identity")
    case=next(r for r in json.loads(a.history.read_text())["sample"] if r["id"]=="P2-028")
    out=a.output
    out.mkdir(parents=True,exist_ok=True)
    results={}
    for depth in (15,16):
        for arm,skip in (("sham",0),("both",1)):
            variants=[]
            logs=[]
            for label,binary,observe in (("baseline",a.baseline,0),("off",a.observer,0),("on0",a.observer,1),("on1",a.observer,1)):
                directory=out/f"d{depth}-{arm}-{label}"
                env={"C3X_R33_OBSERVE":"1","C3X_R33_TARGET":"19",
                     "C3X_R33_SKIP_FUTILITY":str(skip),"C3X_R33_SKIP_NULL":str(skip),
                     "C3X_R29_PROBES":"0","C3X_R31_OBSERVE":"0","C3X_NO_TT_PICKER":"0","C3X_NO_TT_VALUE":"0",
                     "C3X_R29_MASK_MOVE":"0","C3X_R29_MASK_VALUE":"0","C3X_R40_TT_EVENTS":str(observe)}
                uci,proof=run(binary,{"history":case["moves"]},a.net,directory,
                              logging=True,paired=False,nnue=True,depth=depth,environment=env)
                lines=(directory/"stderr.txt").read_text().splitlines()
                match=[x for x in events(lines) if x["open"]["event"]=="19"]
                require(len(match)==1 and match[0]["open"]["key"]=="18244396700095567446"
                        and match[0]["open"]["nodes"]=="7477"
                        and match[0]["close"]["value"]==("-2500" if skip else "-2429"),"wrong source event")
                require(proof["best"]["completed"]==str(depth),"depth not completed")
                variants.append((uci,proof,match))
                if observe: logs.append(replay(lines))
                else: require(not any(l.startswith("C3X_R40_") for l in lines),"off observer leaked")
            require(all(v==variants[0] for v in variants[1:]),"physical noninterference failure")
            require(logs[0]==logs[1],"observer cold repeat mismatch")
            require(logs[0]["y1"]["value"]==("2280" if skip else "2265"),"Y1 drift")
            results[(depth,arm)]=logs[0]
            print("R40_PARITY",depth,arm,logs[0]["counts"],flush=True)
    receipt={"stage":"P3_B0_PARTIAL_PASSIVE_LOOKUP_CONTACT","native_searches":16,
             "source_inputs":{"history_sha256":HIST,"net_sha256":NET,"baseline_sha256":R33,
                              "observer_sha256":digest(a.observer)},
             "cases":{str(d):{"sham_checkpoint":results[(d,"sham")]["cp"],
                               "both_checkpoint":results[(d,"both")]["cp"],
                               **compare(results[(d,"sham")],results[(d,"both")])} for d in (15,16)},
             "physical_transplant_executed":False,"mediator_sufficiency":"HOLD"}
    (out/"R40_AGGREGATE_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
