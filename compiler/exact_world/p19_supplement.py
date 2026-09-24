#!/usr/bin/env python3
"""Outcome-blind supplemental P19 Stage-A constitution.

Uses the already frozen P19 compiler semantics but moves the deterministic
candidate seed offset to 70000 so every vertex receives a disjoint 36-world
supplement. No engine outcome is consulted.
"""
import p19_compile as base

base.OFFSET=70000

if __name__=="__main__":
    base.main()
