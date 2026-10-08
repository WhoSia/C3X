from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from typing import Any
from .core import analyze_pgn
from .certificate_trust import admitted_certificates

def load_packets(paths:list[str])->list[dict[str,Any]]:
    out=[]
    for p in paths:
        x=json.load(open(p,encoding="utf-8"))
        if isinstance(x,list):out.extend(x)
        elif isinstance(x,dict) and isinstance(x.get("packets"),list):out.extend(x["packets"])
        else:out.append(x)
    return out

def markdown_report(out:dict[str,Any])->str:
    lines=[
      "# C3X Commentary",
      "",
      f"- Rating band: {out.get('rating_band')}",
      f"- Selected moments: {out.get('moment_count')}",
      f"- Susceptibility packets: {out.get('susceptibility_packet_count',0)}",
      "",
    ]
    for m in out.get("moments",[]):
        lines += [
          f"## Ply {m['ply']} — {m['played_san']}",
          "",
          m.get("commentary") or "_No bounded commentary surface._",
          "",
          "**Evidence / authority**",
        ]
        for a in m.get("atoms",[]):
            if not a.get("text"):continue
            lines.append(f"- `{a.get('type')}` · `{a.get('authority')}` · `{a.get('provenance')}` · atom `{a.get('atom_id')}`")
        abst=m.get("render_packet",{}).get("abstained_atoms",[])
        if abst:
            lines.append("")
            lines.append("**Abstentions**")
            for z in abst:lines.append(f"- {z.get('atom_id')}: {z.get('reason')}")
        lines.append("")
    lines += [
      "## Authority note",
      "",
      str(out.get("authority_note") or ""),
      "",
      "Transparent intervention-admissibility evidence predicts whether a counterfactual measurement is worth attempting; it does not establish mechanism authority or objective chess truth.",
      ""
    ]
    return "\n".join(lines)

def main()->None:
    ap=argparse.ArgumentParser(prog="python -m c3x_explain",description="Evidence-aware C3X chess commentator")
    ap.add_argument("--pgn",required=True,help="Input PGN path")
    ap.add_argument("--engine",help="Optional UCI engine executable")
    ap.add_argument("--rating-band",choices=["beginner","intermediate","advanced","expert"],default="advanced")
    ap.add_argument("--multipv",type=int,default=3)
    ap.add_argument("--nodes",type=int,default=20000)
    ap.add_argument("--certificate",action="append",default=[])
    ap.add_argument("--susceptibility",action="append",default=[],help="Transparent admissibility packet JSON")
    ap.add_argument("--ep8-observation",action="append",default=[],help="P8 EP8 descriptive engine panel; never a causal certificate")
    ap.add_argument("--ep10-observation",action="append",default=[],help="Exact byte-hash-frozen EP10 local search-path diagnostic; never strategic causal authority")
    ap.add_argument("--json-out",required=True)
    ap.add_argument("--markdown-out")
    a=ap.parse_args()
    pgn=Path(a.pgn).read_text(encoding="utf-8")
    # The public CLI never accepts unsigned/unreviewed causal certificate files.
    # Direct library calls retain historical fixture compatibility, not 0.12 authority.
    certs=admitted_certificates(a.certificate)
    packets=load_packets(a.susceptibility)
    ep8=load_packets(a.ep8_observation)
    from .p8_ep10 import ANCHOR_SHA
    ep10=[]
    for file in a.ep10_observation:
        b=Path(file).read_bytes()
        if hashlib.sha256(b).hexdigest()!=ANCHOR_SHA:
            raise ValueError('EP10 raw observation SHA-256 does not match the verified experiment artifact')
        ep10.append(json.loads(b))
    out=analyze_pgn(
      pgn,engine_path=a.engine,multipv=a.multipv,nodes=a.nodes,
      certificates=certs,rating_band=a.rating_band,susceptibility_packets=packets,ep8_observation_packets=ep8,ep10_observation_packets=ep10
    )
    Path(a.json_out).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if a.markdown_out:
        Path(a.markdown_out).write_text(markdown_report(out),encoding="utf-8")
    print("C3X_COMMENTARY_PASS",out["moment_count"],out["evaluation_packet"]["firewall_failed_moments"],
          out["susceptibility_packet_count"])

if __name__=="__main__":main()
