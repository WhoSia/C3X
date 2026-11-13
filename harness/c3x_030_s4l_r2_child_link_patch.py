"""Trace the consuming root call and TT mask epoch in the pinned S4-L build."""
import argparse
import hashlib
from pathlib import Path
import re

from c3x_030_s4l_root_score_patch import patch as s4l_patch

PINNED = "d10ff8f1285c3845ebda08753d3bf58df29d538451bdb6c9fd1edc79d25383a9"

def patch(source):
    patched = s4l_patch(source)
    if hashlib.sha256(patched.encode()).hexdigest() != PINNED:
        raise ValueError("Unexpected S4-L intermediate source")
    start = patched.index("      // Step 17.")
    end = patched.index("      // Step 19.", start)
    block = patched[start:end]
    pattern = r"(?m)^( +)value = -search<(NonPV|PV)>\(([^\n]+)\);$"
    phases = iter(("reduced", "research", "nonpv", "pv"))

    def log(match):
        space, _, _ = match.groups()
        phase = next(phases)
        return (f'{space}{{\n{space}{match[0].lstrip()}\n'
                f'{space}  if (rootNode)\n'
                f'{space}    std::cerr << "C3X_R2_EDGE phase={phase}"\n'
                f'{space}      << " epoch=" << c3x_k_go_epoch.load(std::memory_order_relaxed)\n'
                f'{space}      << " parent=" << c3x_e_scope.id << " child=" << c3x_e_last_child[1]\n'
                f'{space}      << " move=" << static_cast<int>(move) << " value=" << value\n'
                f'{space}      << " iteration=" << thisThread->rootDepth << " depth=" << depth\n'
                f'{space}      << " alpha=" << alpha << " beta=" << beta\n'
                f'{space}      << " stopped=" << int(Threads.stop.load(std::memory_order_relaxed)) << std::endl;\n'
                f'{space}}}')

    block, count = re.subn(pattern, log, block)
    if count != 4:
        raise ValueError("Root child call sites changed")
    patched = patched[:start] + block + patched[end:]
    for old, new in (
        ('<< " hit_before=1 hit_after=0" << std::endl;',
         '<< " hit_before=1 hit_after=0 epoch=" << c3x_k_go_epoch.load(std::memory_order_relaxed) << std::endl;'),
        ('<< " root_move_raw=" << static_cast<int>(move)\n                        << " value=" << value',
         '<< " root_move_raw=" << static_cast<int>(move)\n'
         '                        << " root_id=" << c3x_e_scope.id << " child_id=" << c3x_e_last_child[1]\n'
         '                        << " iteration=" << thisThread->rootDepth\n                        << " value=" << value'),
        ('if (c3x_l_rank < 512)', 'if (c3x_l_rank < 4096)'),
    ):
        if patched.count(old) != (2 if "root_move_raw" in old else 1):
            raise ValueError(f"Unexpected anchor {old!r}")
        patched = patched.replace(old, new, 1)
    # Some managed launchers strip custom process environment variables.
    # Each arm reads the same three-value file format in its own working directory.
    patched = "#include <fstream>\n" + patched
    for index, name in enumerate(("C3X_S4E_KEY", "C3X_S4G_MASK_KEY", "C3X_S4G_MASK_LIMIT")):
        line = f'        const char* s = std::getenv("{name}");'
        start = patched.index(line)
        end = patched.index("\n", start + len(line) + 1)
        field = ("trace_key", "mask_key", "limit")[index]
        patched = patched[:start] + (
            '        std::ifstream config("c3x_s4l_r2_control.txt");\n'
            '        unsigned long long trace_key = 0, mask_key = 0, limit = 0;\n'
            '        config >> trace_key >> mask_key >> limit;\n'
            + f'        return {field};') + patched[end:]
    # The default start is zero, reproducing the original prefix-dose arms.
    old = "        if (ordinal < c3x_g_mask_limit)"
    new = """        static const unsigned start = []() {
            std::ifstream config("c3x_s4l_r2_control.txt");
            unsigned long long trace_key = 0, mask_key = 0, limit = 0;
            unsigned offset = 0;
            config >> trace_key >> mask_key >> limit >> offset;
            return offset;
        }();
        if (ordinal >= start && ordinal - start < c3x_g_mask_limit)"""
    if patched.count(old) != 1:
        raise ValueError("Mask ordinal anchor changed")
    patched = patched.replace(old, new, 1)
    original_return = "    if (depth <= 0)\n        return qsearch<PV>(pos, ss, alpha, beta);"
    replacement = """    if (depth <= 0)
    {
        const Value result = qsearch<PV>(pos, ss, alpha, beta);
        if (c3x_e_scope.interested)
            std::cerr << "C3X_R2_QRETURN id=" << c3x_e_scope.id
                      << " parent=" << c3x_e_scope.parent_id
                      << " value=" << result << " depth=" << depth
                      << " ttHit=" << ss->ttHit << " ttMove=" << static_cast<int>(ttMove)
                      << std::endl;
        return result;
    }"""
    if patched.count(original_return) != 1:
        raise ValueError("Expected one post-reduction qsearch delegation")
    return patched.replace(original_return, replacement, 1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(patch(args.source.read_text()))
