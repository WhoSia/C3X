#!/usr/bin/env python3
"""P35/R5: fail-closed read-only route log insertion into pinned SF16 evaluate.cpp.
Build the modified engine independently, and compare against the untouched engine
under node-limited, single-threaded search before interpreting any route events.
"""
from __future__ import annotations
import argparse
import hashlib
import re
from pathlib import Path

SOURCE_BLOB_SHA1 = "35d054270ee7120e1f0438f58867248146053edc"
FUNCTION_START = "Value Eval::evaluate(const Position& pos) {"
FUNCTION_END = "\n/// trace() is like evaluate()"
ROUTE_ANCHOR = "  bool useClassical = !useNNUE || abs(psq) > 2048;"
RETURN_ANCHOR = "  return v;\n}"
LOG_PREFIX = "C3X_P35_ROUTE"

def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def apply_patch(original: bytes) -> bytes:
    if git_blob_sha1(original) != SOURCE_BLOB_SHA1:
        raise ValueError("HOLD_SOURCE_BLOB_SHA_MISMATCH")
    source = original.decode("utf-8")
    if source.count(FUNCTION_START) != 1 or source.count(FUNCTION_END) != 1:
        raise ValueError("HOLD_EVALUATOR_ANCHOR_CARDINALITY")
    beginning, rest = source.split(FUNCTION_START, 1)
    fn, ending = rest.split(FUNCTION_END, 1)
    if fn.count(ROUTE_ANCHOR) != 1 or fn.count(RETURN_ANCHOR) != 1:
        raise ValueError("HOLD_EVALUATOR_DISPATCH_CARDINALITY")
    if LOG_PREFIX in source:
        raise ValueError("HOLD_ALREADY_INSTRUMENTED")
    new_fn = fn.replace(RETURN_ANCHOR, (
        "  // C3X diagnostic: invoked only on actual Eval::evaluate() execution.\n"
        "  if (std::getenv(\"C3X_P35_ROUTE_AUDIT\"))\n"
        "      std::fprintf(stderr, \"C3X_P35_ROUTE key=%llu arm=%s psq=%d value=%d\\n\",\n"
        "                   static_cast<unsigned long long>(pos.key()),\n"
        "                   useClassical ? \"HCE\" : \"NNUE\",\n"
        "                   static_cast<int>(psq), static_cast<int>(v));\n"
        "  return v;\n}"
    ), 1)
    if "#include <cstdio>\n" in beginning:
        raise ValueError("HOLD_ALREADY_HAS_CSTDIO")
    if "#include <cstdlib>\n" not in beginning:
        raise ValueError("HOLD_CSTDLIB_INCLUDE_MISSING")
    beginning = beginning.replace("#include <cstdlib>\n", "#include <cstdlib>\n#include <cstdio>\n", 1)
    patched = beginning + FUNCTION_START + new_fn + FUNCTION_END + ending
    if patched.count("C3X_P35_ROUTE key=") != 1 or patched.count("C3X_P35_ROUTE_AUDIT") != 1:
        raise ValueError("HOLD_PATCH_INTERNAL_CARDINALITY")
    return patched.encode("utf-8")

def parse_route_log(raw: str) -> list[dict]:
    pattern = re.compile(r"^C3X_P35_ROUTE key=(\d+) arm=(NNUE|HCE) psq=(-?\d+) value=(-?\d+)$")
    rows = []
    for line in raw.splitlines():
        if not line.startswith(LOG_PREFIX):
            continue
        m = pattern.fullmatch(line)
        if not m:
            raise ValueError("HOLD_MALFORMED_ROUTE_LOG")
        key, arm, psq, value = m.groups()
        psq = int(psq)
        if arm != ("HCE" if abs(psq) > 2048 else "NNUE"):
            raise ValueError("HOLD_ROUTE_BRANCH_CONTRADICTS_SOURCE")
        rows.append({"key": int(key), "arm": arm, "psq": psq, "value": int(value)})
    return rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = apply_patch(a.source.read_bytes())
    a.out.write_bytes(result)
    print("P35_SOURCE_DISPATCH_PATCH_CREATED", hashlib.sha256(result).hexdigest())

if __name__ == "__main__":
    main()
