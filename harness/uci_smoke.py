#!/usr/bin/env python3
import argparse
import subprocess
import sys

def transact(binary, commands):
    p = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    out = []
    for cmd, stop_token in commands:
        p.stdin.write(cmd + "\n")
        p.stdin.flush()
        for line in p.stdout:
            line = line.rstrip("\n")
            out.append(line)
            if stop_token in line:
                break
    p.stdin.write("quit\n")
    p.stdin.flush()
    p.wait(timeout=10)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binary")
    args = ap.parse_args()
    out = transact(args.binary, [("uci", "uciok"), ("isready", "readyok")])
    text = "\n".join(out)
    required = [
        "option name C3X_TTReadMode type combo default NATIVE var SHAM var MASKED",
        "option name C3X_Telemetry type check default false",
        "uciok",
        "readyok",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        print(text)
        raise SystemExit("missing UCI surface: " + repr(missing))
    print("UCI_SMOKE_PASS")

if __name__ == "__main__":
    main()
