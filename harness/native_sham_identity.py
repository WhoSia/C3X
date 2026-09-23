#!/usr/bin/env python3
import argparse
import re
import subprocess

FEN = "r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PPQN1PPP/R1B2RK1 w - - 4 9"

def run(binary, mode=None, telemetry=False, nodes=30000):
    p = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    cmds = ["uci"]
    if mode is not None:
        cmds += [f"setoption name C3X_TTReadMode value {mode}",
                 f"setoption name C3X_Telemetry value {'true' if telemetry else 'false'}"]
    cmds += [
        "setoption name Threads value 1",
        "setoption name Hash value 64",
        "setoption name SyzygyProbeLimit value 0",
        "setoption name UCI_ShowWDL value true",
        "setoption name Clear Hash",
        "isready",
        f"position fen {FEN}",
        f"go nodes {nodes}",
    ]
    for c in cmds:
        p.stdin.write(c + "\n")
    p.stdin.flush()

    lines=[]
    for line in p.stdout:
        line=line.strip()
        lines.append(line)
        if line.startswith("bestmove "):
            break
    premature = p.poll()
    if premature is not None:
        rest = p.stdout.read()
        if rest:
            lines.extend(rest.splitlines())
        raise RuntimeError(
            f"engine exited before quit rc={premature}\\n" + "\\n".join(lines[-80:])
        )

    try:
        p.stdin.write("quit\\n")
        p.stdin.flush()
    except BrokenPipeError:
        p.wait(timeout=20)
        rest = p.stdout.read()
        if rest:
            lines.extend(rest.splitlines())
        raise RuntimeError(
            f"broken pipe before orderly quit rc={p.returncode}\\n" + "\\n".join(lines[-80:])
        )
    p.wait(timeout=20)

    best = next((x for x in reversed(lines) if x.startswith("bestmove ")), None)
    infos = [x for x in lines if x.startswith("info depth ") and " score " in x and " pv " in x]
    if not best or not infos:
        raise RuntimeError("missing bestmove/final info\n" + "\n".join(lines[-50:]))
    final=infos[-1]

    def grab(pattern, default=""):
        m=re.search(pattern, final)
        return m.group(1) if m else default

    semantic = {
        "bestmove": best,
        "depth": grab(r"\bdepth (\d+)"),
        "seldepth": grab(r"\bseldepth (\d+)"),
        "score": grab(r"\bscore ((?:cp|mate) -?\d+)"),
        "wdl": grab(r"\bwdl (\d+ \d+ \d+)"),
        "nodes": grab(r"\bnodes (\d+)"),
        "pv": grab(r"\bpv (.+)$"),
    }
    telemetry_line = next((x for x in lines if x.startswith("info string c3x_ttread_v1 ")), None)
    return semantic, telemetry_line, lines

def parse_telemetry(line):
    if not line:
        return {}
    out={}
    for token in line.split()[3:]:
        if "=" in token:
            k,v=token.split("=",1)
            out[k]=v
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--patched", required=True)
    ap.add_argument("--nodes", type=int, default=30000)
    args=ap.parse_args()

    base, _, _ = run(args.baseline, None, False, args.nodes)
    native, native_t, _ = run(args.patched, "NATIVE", True, args.nodes)
    sham, sham_t, _ = run(args.patched, "SHAM", True, args.nodes)

    if base != native:
        raise SystemExit(f"BASELINE_NATIVE_MISMATCH\nbase={base}\nnative={native}")
    if native != sham:
        raise SystemExit(f"NATIVE_SHAM_MISMATCH\nnative={native}\nsham={sham}")

    nt=parse_telemetry(native_t)
    st=parse_telemetry(sham_t)
    if nt.get("mode") != "NATIVE" or st.get("mode") != "SHAM":
        raise SystemExit(f"TELEMETRY_MODE_FAIL native={native_t} sham={sham_t}")
    if int(st.get("probes_main","0")) <= 0 or int(st.get("raw_hits_main","0")) <= 0:
        raise SystemExit(f"SHAM_ENGAGEMENT_ZERO {sham_t}")

    print("NATIVE_SHAM_IDENTITY_PASS")
    print("semantic", sham)
    print("native_telemetry", native_t)
    print("sham_telemetry", sham_t)

if __name__ == "__main__":
    main()
