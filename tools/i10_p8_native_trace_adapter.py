#!/usr/bin/env python3
"""C3X 0.25 I10-P8: byte-attested UCI log -> P7 raw-input envelope.

The receipt attests input bytes only, not engine identity or semantic validity.
This adapter does not edit any original log or interpret causality.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = 'c3x-p7-raw-uci-v1'
ADAPTER_SCHEMA = 'c3x-i10-p8-ingest-receipt-v1'
MAX_BYTES = 64 * 1024 * 1024
MAX_LINES = 500_000
PREFIXES = ('c3x025_p8', 'c3x025_p11', 'c3x025_p12', 'c3x025_p13', 'c3x025_p14', 'c3x_p6', 'c3x_i10p6')

class Hold(Exception):
    pass

def transform(raw: bytes, run_id: str, source_receipt: str | None):
    if not run_id.strip() or not raw or len(raw) > MAX_BYTES:
        raise Hold('RUN_ID_OR_INPUT_SIZE_INVALID')
    try:
        decoded = raw.decode('utf-8', 'strict')
    except UnicodeDecodeError as e:
        raise Hold('RAW_LOG_NOT_UTF8') from e
    lines = decoded.splitlines()
    if len(lines) > MAX_LINES:
        raise Hold('RAW_LOG_TOO_MANY_LINES')
    markers = []
    for i, line in enumerate(lines, 1):
        if not line.startswith('info string '):
            continue
        body = line[len('info string '):].split(maxsplit=1)
        if body and body[0] in PREFIXES:
            markers.append({'line_number': i, 'family': body[0]})
    # Deliberately preserve ALL text lines, including other UCI info and bestmove.
    # Rust's parser decides relevance, so no line number or ordering is fabricated.
    envelope = {
        'schema': SCHEMA,
        'run_id': run_id,
        'source_receipt': source_receipt,
        'lines': lines,
    }
    receipt = {
        'schema': ADAPTER_SCHEMA,
        'run_id': run_id,
        'raw_sha256': hashlib.sha256(raw).hexdigest(),
        'raw_size_bytes': len(raw),
        'raw_line_count': len(lines),
        'recognized_family_line_count': len(markers),
        'recognized_families': sorted({m['family'] for m in markers}),
        'source_receipt': source_receipt,
        'source_authentication': 'EXTERNAL_SOURCE_AND_ENGINE_ATTESTATION_REQUIRED',
        'evidence_scope': 'BYTE_CUSTODY_ONLY_NOT_SOURCE_CAUSALITY',
        'known_limitation': 'Rust P7 currently tests structural tuple joins; native event fields and censorship coverage require a real-source audit',
    }
    return envelope, receipt

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw', required=True, type=Path, help='Existing raw UCI log; never modified')
    p.add_argument('--run-id', required=True)
    p.add_argument('--source-receipt', default=None, help='Existing external receipt identifier; no authenticity implied')
    p.add_argument('--output-json', required=True, type=Path)
    p.add_argument('--output-receipt', required=True, type=Path)
    args = p.parse_args(argv)
    try:
        if args.output_json == args.output_receipt or args.raw in (args.output_json, args.output_receipt):
            raise Hold('INPUT_OUTPUT_PATH_COLLISION')
        if args.output_json.exists() or args.output_receipt.exists():
            raise Hold('OUTPUT_EXISTS_NO_OVERWRITE')
        raw = args.raw.read_bytes()
        envelope, receipt = transform(raw, args.run_id, args.source_receipt)
        # Ensure two outputs go to an existing caller-owned directory; never mkdir.
        if not args.output_json.parent.is_dir() or not args.output_receipt.parent.is_dir():
            raise Hold('OUTPUT_DIRECTORY_MISSING')
        args.output_json.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        args.output_receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(f"INGEST_OK raw_sha256={receipt['raw_sha256']} recognized={receipt['recognized_family_line_count']} custody_only=true")
    except (OSError, Hold) as e:
        print(f'I10_P8_INGEST_HOLD: {e}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
