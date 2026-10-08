#!/usr/bin/env bash
while IFS= read -r cmd; do
 case "$cmd" in
 uci) printf 'id name SyntheticFixture\nuciok\n';;
 isready) printf 'readyok\n';;
 'go depth 8 searchmoves '*) printf 'info depth 8 multipv 1 score cp 12 pv e2e4\ninfo depth 8 multipv 2 score cp 7 pv d2d4\nbestmove e2e4\n';;
 quit) exit 0;;
 esac
done
