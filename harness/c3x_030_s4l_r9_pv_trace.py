"""Bind each post-PV substitution to the value consumed in its root call."""
import argparse
import json
from pathlib import Path

PV = "C3X_R9_PV "
ROOT = "C3X_S4L_ROOT_SCORE "


def fields(line):
    return dict(item.split("=", 1) for item in line.split()[1:])


def audit(directory):
    result = {}
    logs = sorted(directory.glob("*post-*/stderr.txt"))
    if len(logs) != 8:
        raise ValueError("Expected eight native experiment arms")
    for path in logs:
        lines = path.read_text().splitlines()
        index, = [i for i, line in enumerate(lines) if line.startswith(PV)]
        action = fields(lines[index])
        following = lines[index + 1:]
        if not following or not following[0].startswith(ROOT):
            raise ValueError(f"Missing immediate root receipt in {path}")
        root = fields(following[0])
        if (action["parent"], action["child"], action["after"]) != (
                root["root_id"], root["child_id"], root["value"]):
            raise ValueError(f"Unexpected root consumption in {path}")
        retry = next((row for row in map(fields, (line for line in following[1:]
                                                  if line.startswith(ROOT)))
                      if row["root_id"] != root["root_id"]), None)
        if retry is None or retry["epoch"] != root["epoch"] or retry["iteration"] != root["iteration"]:
            if int(root["value"]) >= int(root["beta"]):
                raise ValueError(f"Missing first aspiration retry in {path}")
            retry = None
        result[path.parent.name] = {"injected": action, "root_consumed": root,
                                    "next_root_call_first_receipt": retry}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
