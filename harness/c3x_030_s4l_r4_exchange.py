"""Run full TT × move-history exchange across the frozen development positions."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess

DONORS = {"sham": (2**64 - 1, 10000, 0), "two": (None, 2, 0), "second": (None, 1, 1)}

def run(binary, work, fen, target, arm, exports=(), imports=(), second_move=None, second_depth=None):
    work.mkdir(parents=True)
    key, limit, offset = DONORS[arm]
    (work / "c3x_s4l_r2_control.txt").write_text(f"{target} {key or target} {limit} {offset}\n")
    with (work / "stderr.txt").open("w") as err, subprocess.Popen(
        [str(binary)], cwd=work, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, text=True,
    ) as proc:
        def send(command):
            print(command, file=proc.stdin, flush=True)

        def read(prefix):
            lines = []
            for line in proc.stdout:
                lines.append(line.rstrip())
                if line.startswith(prefix):
                    return lines
            raise RuntimeError(f"Missing {prefix} at {work}")

        def exchange(mode, block, path):
            send(f"c3xexchange {mode} {block} {path}")
            if read("c3xexchange ")[-1] != "c3xexchange ok":
                raise RuntimeError(f"{mode} failed for {block}")

        def search(move=None, depth=None):
            send("position fen " + fen)
            limit = f"depth {depth}" if depth else "nodes 12000"
            send(f"go {limit} searchmoves {move}" if move else f"go {limit}")
            lines = read("bestmove ")
            raw.write("\n".join(lines) + "\n")
            info = next(x.split() for x in reversed(lines) if " score " in x and " pv " in x)
            return {"move": lines[-1].split()[1],
                    "info": " ".join(info[:info.index("nps")] + info[info.index("pv"):]),
                    "nodes": int(info[info.index("nodes")+1])}

        send("uci")
        read("uciok")
        for option in ("Threads value 1", "Hash value 16", "Use NNUE value false"):
            send("setoption name " + option)
        send("ucinewgame")
        send("isready")
        read("readyok")
        with (work / "uci.txt").open("w") as raw:
            first = search()
            for block, path in exports:
                exchange("save", block, path)
            for block, path in imports:
                exchange("load", block, path)
            second = search(second_move, second_depth)
        send("quit")
    if proc.returncode:
        raise RuntimeError(f"Engine exited: {proc.returncode}")
    masks = re.findall(r"^C3X_S4G_MASK (.+)$", (work/"stderr.txt").read_text(), re.M)
    return {"go1": first, "go2": second, "masks": masks}

def study(binary, output, spec, archived):
    ident, fen = spec["case_id"], spec["fen"]
    work = output / ident
    target = int(archived["frozen_key"])
    snapshots = {arm: {block: work / f"{arm}-{block}.bin" for block in ("tt", "history")}
                 for arm in DONORS}
    natural = {arm: run(binary, work / arm, fen, target, arm, exports=snapshots[arm].items())
               for arm in DONORS}
    for arm in ("sham", "two"):
        for ix, go in enumerate(("go1", "go2")):
            prior = archived["native_trials"][arm][ix]
            now = natural[arm][go]
            info = now["info"].split()
            assert (now["move"], now["nodes"], int(info[2]), int(info[info.index("score")+2]),
                    info[info.index("pv")+1:]) == (
                        prior["bestmove"], prior["nodes"], prior["depth"], prior["score"][1], prior["pv"])
    matrix = {}
    for t, h in itertools.product(DONORS, repeat=2):
        name = f"{t}-{h}"
        row = run(binary, work/name, fen, target, "sham",
                  imports=(("tt", snapshots[t]["tt"]), ("history", snapshots[h]["history"])))
        assert row["go1"] == natural["sham"]["go1"]
        assert not row["masks"]
        matrix[name] = row["go2"]
    assert matrix["sham-sham"] == natural["sham"]["go2"]
    digests = {}
    for arm, paths in snapshots.items():
        digests[arm] = {block: hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
                        for block, path in paths.items()}
        for path in paths.values():
            path.unlink()
    return ident, {"target": target, "game": spec["game_id"], "natural": natural,
                   "matrix": matrix, "snapshot_sha256": digests}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("binary", "protocol", "archive", "output"):
        p.add_argument(name, type=Path)
    a = p.parse_args()
    archive = a.archive.read_bytes()
    if hashlib.sha256(archive).hexdigest() != "a27b961985d2ba4475f51916c41be3426d8a32d3130bce0fab04497ca2eac5c9":
        raise ValueError("Expected immutable S4-L archive")
    prior = json.loads(archive)["cases"]
    specs = [x for x in json.loads(a.protocol.read_text())["cases"] if x["split"] == "development"]
    assert {x["case_id"] for x in specs} == set(prior)
    with ThreadPoolExecutor(max_workers=4) as pool:
        tasks = [pool.submit(study, a.binary.resolve(), a.output.resolve(), x, prior[x["case_id"]]) for x in specs]
        result = dict(t.result() for t in tasks)
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
