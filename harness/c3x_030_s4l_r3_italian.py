"""Run Italian root-value restoration and between-go reset controls."""
import argparse
import json
from pathlib import Path
import re
import subprocess

FEN = "r1bqk2r/ppp2ppp/2np1n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQK2R w KQkq - 0 6"
TARGET = 1341504945262310742
ARMS = {"sham": (2**64-1, 10000, 0), "one": (TARGET, 1, 0),
        "two": (TARGET, 2, 0), "second": (TARGET, 1, 1)}

def run(binary, work, arm, reset, replacement):
    work.mkdir(parents=True)
    (work / "c3x_s4l_r2_control.txt").write_text(f"{TARGET} %d %d %d\n" % ARMS[arm])
    (work / "c3x_s4l_r3_value.txt").write_text(str(replacement))
    with (work / "stderr.txt").open("w") as err, subprocess.Popen(
        [str(binary.resolve())], cwd=work, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=err, text=True,
    ) as proc:
        def send(command):
            print(command, file=proc.stdin, flush=True)

        def read(prefix):
            lines = []
            for line in proc.stdout:
                lines.append(line.rstrip())
                if line.startswith(prefix):
                    return lines
            raise RuntimeError(f"Missing {prefix}")

        send("uci")
        read("uciok")
        for option in ("Threads value 1", "Hash value 16", "Use NNUE value false"):
            send("setoption name " + option)
        send("ucinewgame")
        send("isready")
        read("readyok")
        results = []
        with (work / "uci.txt").open("w") as log:
            for epoch in (1, 2):
                if epoch == 2 and reset != "none":
                    send("c3xreset " + reset)
                    print(*read("c3xresetok " + reset), sep="\n", file=log)
                send("position fen " + FEN)
                send("go nodes 12000")
                lines = read("bestmove ")
                print(*lines, sep="\n", file=log)
                info = next(line for line in reversed(lines) if " score " in line and " pv " in line)
                fields = info.split()
                results.append({"move": lines[-1].split()[1], "nodes": int(fields[fields.index("nodes")+1]),
                                "info": " ".join(fields[:fields.index("nps")] + fields[fields.index("pv"):])})
        send("quit")
    if proc.returncode:
        raise RuntimeError(f"Engine exited: {proc.returncode}")
    stderr = (work / "stderr.txt").read_text()
    return {"searches": results,
            "masks": re.findall(r"^C3X_S4G_MASK (.+)$", stderr, re.M),
            "overrides": re.findall(r"^C3X_R3_VALUE (.+)$", stderr, re.M)}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("original", "instrumented", "output", "r2_json"):
        p.add_argument(name, type=Path)
    a = p.parse_args()
    result = {"original": run(a.original, a.output / "original", "sham", "none", 0)}
    archived = json.loads(a.r2_json.read_text())["trials"]
    for arm in ("sham", "one", "two", "second"):
        for reset in ("none", "tt", "threads", "both", "history", "prior", "tt_history", "tt_prior"):
            label = f"{arm}_{reset}"
            row = run(a.instrumented, a.output / label, arm, reset, 0)
            expected = archived["second_only" if arm == "second" else arm]
            assert row["searches"][0]["info"] == expected[0]["info"]
            if reset == "none":
                assert row["searches"][1]["info"] == expected[1]["info"]
            result[label] = row
    assert result["original"]["searches"] == result["sham_none"]["searches"]
    for label, count in (("sham", 0), ("one", 1), ("two", 2), ("second", 1)):
        for name, row in result.items():
            if name.startswith(label + "_"):
                assert len(row["masks"]) == count
                assert all("epoch=1" in mask for mask in row["masks"])
    for arm, value in (("one", 134), ("two", 134), ("sham", 149), ("two", 149)):
        label = f"{arm}_value{value}"
        row = run(a.instrumented, a.output / label, arm, "none", value)
        assert len(row["overrides"]) == 1 and "parent=43 child=44" in row["overrides"][0]
        result[label] = row
    assert result["two_value149"]["searches"] == result["two_none"]["searches"]
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
