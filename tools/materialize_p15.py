#!/usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
P12 = ROOT / "tools" / "materialize_p12.py"

MODES = {
    "NATIVE": "NONE",
    "SHAM": "NONE",
    "MASK_MAIN": "MAIN",
    "MASK_SUCCESSOR": "SUCCESSOR",
    "MASK_QSEARCH": "QSEARCH",
    "MASK_MAIN_SUCCESSOR": "MAIN|SUCCESSOR",
    "MASK_MAIN_QSEARCH": "MAIN|QSEARCH",
    "MASK_SUCCESSOR_QSEARCH": "SUCCESSOR|QSEARCH",
    "MASK_ALL": "MAIN|SUCCESSOR|QSEARCH",
    "MASKED": "MAIN|SUCCESSOR|QSEARCH"
}

def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 exact anchor, found {n}")
    return text.replace(old, new, 1)

def run_p12(sf, target):
    subprocess.check_call([sys.executable, str(P12), "--stockfish", str(sf), "--target", target])

def patch_header(sf):
    p = sf / "src/c3x_ttread.h"
    t = p.read_text()
    t = replace_once(
        t,
        "enum class C3XTTReadMode { NATIVE, SHAM, MASKED };",
        "enum class C3XTTReadMode { NATIVE, SHAM, MASK_MAIN, MASK_SUCCESSOR, MASK_QSEARCH, MASK_MAIN_SUCCESSOR, MASK_MAIN_QSEARCH, MASK_SUCCESSOR_QSEARCH, MASK_ALL, MASKED };",
        "mode enum"
    )
    t = replace_once(
        t,
        "    bool masked() const { return mode == C3XTTReadMode::MASKED; }",
        """    bool masked(C3XTTReadSite site) const {
        if (mode == C3XTTReadMode::MASKED || mode == C3XTTReadMode::MASK_ALL)
            return true;
        if (site == C3XTTReadSite::MAIN)
            return mode == C3XTTReadMode::MASK_MAIN
                || mode == C3XTTReadMode::MASK_MAIN_SUCCESSOR
                || mode == C3XTTReadMode::MASK_MAIN_QSEARCH;
        if (site == C3XTTReadSite::SUCCESSOR_VERIFY)
            return mode == C3XTTReadMode::MASK_SUCCESSOR
                || mode == C3XTTReadMode::MASK_MAIN_SUCCESSOR
                || mode == C3XTTReadMode::MASK_SUCCESSOR_QSEARCH;
        return mode == C3XTTReadMode::MASK_QSEARCH
            || mode == C3XTTReadMode::MASK_MAIN_QSEARCH
            || mode == C3XTTReadMode::MASK_SUCCESSOR_QSEARCH;
    }""",
        "masked(site)"
    )
    t = replace_once(
        t,
        """    case C3XTTReadMode::NATIVE: return "NATIVE";
    case C3XTTReadMode::SHAM: return "SHAM";
    case C3XTTReadMode::MASKED: return "MASKED";""",
        """    case C3XTTReadMode::NATIVE: return "NATIVE";
    case C3XTTReadMode::SHAM: return "SHAM";
    case C3XTTReadMode::MASK_MAIN: return "MASK_MAIN";
    case C3XTTReadMode::MASK_SUCCESSOR: return "MASK_SUCCESSOR";
    case C3XTTReadMode::MASK_QSEARCH: return "MASK_QSEARCH";
    case C3XTTReadMode::MASK_MAIN_SUCCESSOR: return "MASK_MAIN_SUCCESSOR";
    case C3XTTReadMode::MASK_MAIN_QSEARCH: return "MASK_MAIN_QSEARCH";
    case C3XTTReadMode::MASK_SUCCESSOR_QSEARCH: return "MASK_SUCCESSOR_QSEARCH";
    case C3XTTReadMode::MASK_ALL: return "MASK_ALL";
    case C3XTTReadMode::MASKED: return "MASKED";""",
        "mode names"
    )
    p.write_text(t)

def patch_search(sf):
    p = sf / "src/search.cpp"
    t = p.read_text()
    old = """    const std::string c3xModeOption = std::string(options["C3X_TTReadMode"]);
    const C3XTTReadMode c3xMode = c3xModeOption == "MASKED"
                                      ? C3XTTReadMode::MASKED
                                  : c3xModeOption == "SHAM"
                                      ? C3XTTReadMode::SHAM
                                      : C3XTTReadMode::NATIVE;"""
    new = """    const std::string c3xModeOption = std::string(options["C3X_TTReadMode"]);
    C3XTTReadMode c3xMode = C3XTTReadMode::NATIVE;
    if (c3xModeOption == "SHAM") c3xMode = C3XTTReadMode::SHAM;
    else if (c3xModeOption == "MASK_MAIN") c3xMode = C3XTTReadMode::MASK_MAIN;
    else if (c3xModeOption == "MASK_SUCCESSOR") c3xMode = C3XTTReadMode::MASK_SUCCESSOR;
    else if (c3xModeOption == "MASK_QSEARCH") c3xMode = C3XTTReadMode::MASK_QSEARCH;
    else if (c3xModeOption == "MASK_MAIN_SUCCESSOR") c3xMode = C3XTTReadMode::MASK_MAIN_SUCCESSOR;
    else if (c3xModeOption == "MASK_MAIN_QSEARCH") c3xMode = C3XTTReadMode::MASK_MAIN_QSEARCH;
    else if (c3xModeOption == "MASK_SUCCESSOR_QSEARCH") c3xMode = C3XTTReadMode::MASK_SUCCESSOR_QSEARCH;
    else if (c3xModeOption == "MASK_ALL") c3xMode = C3XTTReadMode::MASK_ALL;
    else if (c3xModeOption == "MASKED") c3xMode = C3XTTReadMode::MASKED;"""
    t = replace_once(t, old, new, "mode parser")
    mask_anchor = "if (c3xTt.masked() && ttHit)"
    if t.count(mask_anchor) != 2:
        raise RuntimeError(f"main/qsearch masks: expected 2 anchors, found {t.count(mask_anchor)}")
    t = t.replace(mask_anchor, "if (c3xTt.masked(C3XTTReadSite::MAIN) && ttHit)", 1)
    t = t.replace(mask_anchor, "if (c3xTt.masked(C3XTTReadSite::QSEARCH) && ttHit)", 1)
    t = replace_once(t, "if (c3xTt.masked() && ttHitNext)", "if (c3xTt.masked(C3XTTReadSite::SUCCESSOR_VERIFY) && ttHitNext)", "successor mask")
    p.write_text(t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stockfish", required=True)
    ap.add_argument("--target", required=True, choices=["frozen_20260810", "stockfish_18", "stockfish_19"])
    args = ap.parse_args()
    sf = pathlib.Path(args.stockfish).resolve()
    run_p12(sf, args.target)
    patch_header(sf)
    patch_search(sf)
    print(f"materialized P15 selective-mask target={args.target}")
    subprocess.check_call(["git", "diff", "--check"], cwd=sf)

if __name__ == "__main__":
    main()
