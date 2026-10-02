from __future__ import annotations
import argparse
from c3x_g10.invariant_lattice import main
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--metrology",required=True)
    ap.add_argument("--p12",required=True)
    ap.add_argument("--p16",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    main(a.metrology,a.p12,a.p16,a.out)
