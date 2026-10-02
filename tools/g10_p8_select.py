#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import harness.g95_p16_court as p16
from c3x_g10.acquisition_policy import select

def load(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--pair-freeze",action="append",required=True);ap.add_argument("--ecology",required=True);ap.add_argument("--out-freeze",required=True);ap.add_argument("--out-receipt",required=True)
 a=ap.parse_args();pfs=[p16.load_pair(x) for x in a.pair_freeze];eco=load(a.ecology)
 out,receipt=select(pfs,eco)
 p16.seal(out)
 Path(a.out_freeze).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 receipt["selected_pair_freeze_receipt_sha256"]=out["receipt_sha256"]
 Path(a.out_receipt).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 print("G10_P8_ACQUISITION_FREEZE","support",receipt["support_pass"],"target",receipt["target_count"],"control",receipt["control_count"])
if __name__=="__main__":main()
