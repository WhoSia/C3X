#!/usr/bin/env python3
"""P42/R9: original Stockfish16 value_draw use and node-mod4 causal test.

Instrument the *actual* source value_draw() boundary (all callers), rather
than assuming the Game14 trace passed a draw. Counterfactual neutrality is an
experimental perturbation and therefore not a chess-truth or natural mediation
claim. Apply on top of the existing immutable R8 native recipe before make.
"""
import argparse
import hashlib
import json
from pathlib import Path

ANCHOR = "    return VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2);"
FUNCTION = "  Value value_draw(const Thread* thisThread) {"
REPLACEMENT = r'''
    // R9: actual source call, never fabricate a draw just to register contact.
    const Value c3x042_r9_native = VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2);
    const bool c3x042_r9_neutral = std::getenv("C3X042_R9_DRAW_PARITY_NEUTRAL") != nullptr;
    if (const char* c3x042_r9_path = std::getenv("C3X042_R9_DRAW_TRACE")) {
        if (*c3x042_r9_path) {
            if (auto* f = std::fopen(c3x042_r9_path, "a")) {
                std::fprintf(f,
                  "c3x042_r9_draw call=1 node_mod4=%d original=%d neutral=%d return=%d\n",
                  int(thisThread->nodes & 3), int(c3x042_r9_native),
                  int(c3x042_r9_neutral),
                  int(c3x042_r9_neutral ? VALUE_DRAW : c3x042_r9_native));
                std::fclose(f);
            }
        }
    }
    return c3x042_r9_neutral ? VALUE_DRAW : c3x042_r9_native;'''

def patch(source: str) -> str:
    if "c3x042_r9_native" in source:
        raise ValueError("R9_ALREADY_INSTRUMENTED")
    if source.count(FUNCTION) != 1 or source.count(ANCHOR) != 1:
        raise ValueError("R9_SOURCE_ANCHOR_NOT_UNIQUE")
    a=source.index(FUNCTION)
    b=source.index(ANCHOR)
    if not a < b < a+300:
        raise ValueError("R9_FUNCTION_AND_RETURN_NOT_ADJACENT")
    return source.replace(ANCHOR, REPLACEMENT,1)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True)
    a.add_argument("--out-manifest",required=True)
    args=a.parse_args()
    f=Path(args.source)/"src/search.cpp"
    before=f.read_bytes()
    after=patch(before.decode("utf-8")).encode("utf-8")
    f.write_bytes(after)
    out=Path(args.out_manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
        "schema":"c3x042-r9-native-draw-perturbation-v1",
        "before_sha256":hashlib.sha256(before).hexdigest(),
        "after_sha256":hashlib.sha256(after).hexdigest(),
        "native_observation":"C3X042_R9_DRAW_TRACE",
        "neutralization":"C3X042_R9_DRAW_PARITY_NEUTRAL",
        "source_original_value":"VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2)",
        "scope":"ALL actual value_draw calls, not a discovered Game14 specific path",
        "scientific_outcome":"HOLD_UNTIL_ACTUAL_NATIVE_ABCD_REPLAY"
    },sort_keys=True,indent=2)+"\n")
    print("R9_SOURCE_PATCH_CREATED_NO_NATIVE_VALUE_CLAIM")

if __name__=="__main__":
    main()
