#!/usr/bin/env python3
# ============================================================
# Owner: Faraz Ali ID
# Author: Faraz Ali ID
# Copyright (c) Faraz Ali ID
# ============================================================

"""
Decode Utility Script

Owner: Faraz Ali ID
Author: Faraz Ali ID

Usage:
    python3 decode.py <target_file.py>

Ye script kisi Python file ke andar base64/zlib (ya marshal/bz2/lzma) se
encode kiye hue payload ko DHOOND kar decode karta hai, bina usse EXECUTE
kiye. Sirf decoded source print/save karta hai taaki tum dekh sako file
andar se kya karti hai.
"""

import sys
import re
import base64
import zlib
import bz2
import lzma

def try_decompress(data: bytes):
    """Try various decompression methods, return (name, decompressed) or (None, None)."""
    for name, func in [("zlib", zlib.decompress), ("bz2", bz2.decompress), ("lzma", lzma.decompress)]:
        try:
            return name, func(data)
        except Exception:
            continue
    return None, data  # maybe it wasn't compressed at all

def find_b64_blobs(text: str):
    """Find long base64-looking string literals in the source."""
    pattern = r'''(['"])([A-Za-z0-9+/=\n]{40,})\1'''
    return [m.group(2).replace("\n", "") for m in re.finditer(pattern, text)]

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 decode.py <target_file.py>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", errors="ignore") as f:
        content = f.read()

    blobs = find_b64_blobs(content)
    if not blobs:
        print("Koi base64-jaisi string nahi mili is file me.")
        sys.exit(1)

    print(f"{len(blobs)} candidate blob(s) mile. Decode kar raha hoon...\n")

    for i, blob in enumerate(blobs, 1):
        print(f"--- Blob #{i} (length {len(blob)}) ---")
        try:
            raw = base64.b64decode(blob)
        except Exception as e:
            print(f"  base64 decode fail: {e}")
            continue

        method, decompressed = try_decompress(raw)
        if method:
            print(f"  Decompressed using: {method}")
        else:
            print("  Koi decompression nahi lagi, raw bytes hi dikha raha hoon.")

        try:
            text = decompressed.decode("utf-8")
        except Exception:
            text = decompressed.decode("latin-1", errors="replace")

        out_file = f"decoded_{i}.py"
        with open(out_file, "w") as out:
            out.write(text)

        print(f"  Saved to: {out_file}")
        print("  Preview (first 300 chars):")
        print("  " + text[:300].replace("\n", "\n  "))
        print()

if __name__ == "__main__":
    main()