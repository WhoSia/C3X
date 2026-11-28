#!/usr/bin/env python3
"""R56 frozen two-case history-only reciprocal intervention; exposed development."""
import argparse,json
from pathlib import Path
from c3x_031_r53_history_checkpoint_court import CASES,inspect
from c3x_031_r41_history_contact_court import compare
from c3x_031_r42_history_rescue_court import expected_image
from c3x_031_r47_frozen_discovery import load_frozen,sha,require,NET,BIN
from c3x_031_r48_new_cohort_intervention import DISCOVERY
from c3x_031_r51_root_guard_contrast import R48
from c3x_030_r23_native_replay import run,records
from c3x_030_r33_gate_panel import events
from c3x_031_p2_treatment import matched
from c3x_031_r40_checkpoint_tt_court import fields
CONTACT="0b7c4d7c3b97e93a8467f3b8064ccc8bdda284d1e61af37aaff06891093633b3"
def root_trace(lines):
    return [l for l in lines if l.startswith(("C3X_R23_","C3X_R33_"))]
def alignment(a,b):
    return all(a["cp"][k]==b["cp"][k] for k in ("attempt","root_depth","completed","alpha","beta")) and all(a["root"][k]==b["root"][k] for k in ("move","count","alpha","beta","depth"))
def signature(a):
    return {k:a["root"][k] for k in ("value","update")}
def main():
    p=argparse.ArgumentParser()
    for k in ("census","discovery","prior","contact","folder","base","observer","net","out","receipt"):p.add_argument(k,type=Path)
    a=p.parse_args()
    for f,h in ((a.discovery,DISCOVERY),(a.prior,R48),(a.contact,CONTACT),(a.base,BIN),(a.net,NET)):
        require(sha(f.read_bytes())==h,"identity drift "+f.name)
    cases={r["id"]:r for r in load_frozen(a.census,a.folder)}
    prior={r["id"]:r for r in json.loads(a.prior.read_text())["cases"]}
    frozen={r["id"]:r for r in json.loads(a.discovery.read_text())["cases"]}
    reference={r["id"]:r for r in json.loads(a.contact.read_text())["cases"]}
    rows=[]; count=0
    def search(ident,g,name,mode,receiver=None,image=None):
        nonlocal count
        target=frozen[ident]["targets"][g]["target"]
        skip=int(name=="both");folder=a.out/ident/name/mode
        env={"C3X_R33_OBSERVE":"1","C3X_R33_TARGET":target["event"],"C3X_R33_SKIP_FUTILITY":str(skip),"C3X_R33_SKIP_NULL":str(skip),
             "C3X_R29_PROBES":"0","C3X_R31_OBSERVE":"0","C3X_NO_TT_PICKER":"0","C3X_NO_TT_VALUE":"0","C3X_R29_MASK_MOVE":"0","C3X_R29_MASK_VALUE":"0","C3X_R41_HISTORY":"1"}
        if receiver is not None:env.update(C3X_R56_RECEIVER=str(receiver.resolve()),C3X_R56_IMAGE=str(image.resolve()))
        uci,proof=run(a.observer,{"history":cases[ident]["moves"]},a.net,folder,logging=True,paired=False,nnue=True,nodes=32000,environment=env)
        count+=1
        lines=(folder/"stderr.txt").read_text().splitlines()
        old=prior[ident]["targets"][g]["arms"][name]
        e=matched(events(lines),target)
        require(e["close"]["value"]==old["child_return"],"source target drift")
        obs=inspect(folder,lines)
        obs.update(folder=folder,best=proof["best"],trace=root_trace(lines),trace_hash=sha(("\n".join(root_trace(lines))+"\n").encode()))
        require(obs["cp"]==reference[ident]["checkpoints"][name],"receiver checkpoint drift")
        if receiver is None:
            original="\n".join(l for l in lines if not l.startswith(("C3X_R41_CP ","C3X_R41_END ")))+"\n"
            require(sha(original.encode())==old["trace_sha256"][0]==old["trace_sha256"][1] and proof["best"]==old["best"],"R48 parity")
            require(obs["root"]==reference[ident]["first_roots"][name],"R53 Y1 parity")
        else:
            require((folder/"r41_snapshot.bin").read_bytes()==image.read_bytes(),"post-splice image drift")
            markers=[fields(l) for l in lines if l.startswith("C3X_R56_SPLICE ")]
            require(len(markers)==1,"splice marker")
            obs["changed"]=int(markers[0]["changed"])
        return obs
    for ident,g in CASES:
        natural={n:search(ident,g,n,"natural") for n in ("sham","both")}
        x,y=(natural[n] for n in ("sham","both"))
        require(json.loads(json.dumps(compare(x,y)))==reference[ident]["contact"],"R53 contact replay drift")
        D={(n,i) for n in x["initial"] for i,(v,w) in enumerate(zip(x["initial"][n],y["initial"][n])) if v!=w}
        C=D & {(n,i) for arm in natural.values() for (n,i,op) in arm["first"] if op=="R"}
        U=D & {(n,i) for arm in natural.values() for (n,i,op) in arm["first"] if op=="U"}
        P=D-C
        freeze={"D":sorted(D),"C":sorted(C),"P":sorted(P),"U":sorted(U)}
        (a.out/ident/"FROZEN_CELLS.json").write_text(json.dumps(freeze,sort_keys=True)+"\n")
        print("R56_FROZEN",ident,json.dumps({k:len(v) for k,v in freeze.items()}),flush=True)
        for n,other in (("sham","both"),("both","sham")):
            own,donor=natural[n],natural[other]
            receiver=own["folder"]/"r41_snapshot.bin";donorfile=donor["folder"]/"r41_snapshot.bin"
            for mode,keys in (("self",set()),("full",D),("contact",C),("complement",P)):
                image=a.out/ident/n/(mode+".image")
                image.write_bytes(expected_image(receiver.read_bytes(),donorfile.read_bytes(),sorted(keys)))
                o=search(ident,g,n,mode,receiver,image)
                require(o["changed"]==len(keys),"changed-cell count")
                if mode=="self":require(o["trace"]==own["trace"] and o["best"]==own["best"],"self parity")
                row={"id":ident,"receiver":n,"mode":mode,"changed":len(keys),"aligned_own":alignment(o,own),"aligned_donor":alignment(o,donor),"checkpoint":o["cp"],"first_root":o["root"],"own_first_root":own["root"],"donor_first_root":donor["root"],"first_signature_matches_own":alignment(o,own) and signature(o)==signature(own),"first_signature_matches_donor":alignment(o,donor) and signature(o)==signature(donor),"best":o["best"],"own_best":own["best"],"donor_best":donor["best"],"draw_calls_before_y1":len(o["draws"]),"image_sha256":sha(image.read_bytes()),"trace_sha256":o["trace_hash"],"cells":{"D":len(D),"C":len(C),"P":len(P),"U":len(U)}}
                rows.append(row);print("R56_RESULT",json.dumps(row,sort_keys=True),flush=True)
    require(count==20 and len(rows)==16,"denominator")
    result={"scope":"two exposed R53 cases, conditional transfer not prospective confirmation","native_searches":count,"rows":rows,"observer_sha256":sha(a.observer.read_bytes()),"contact_sha256":CONTACT}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
