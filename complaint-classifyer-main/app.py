"""Minimal CLI for running the support agent on a customer tweet."""
from __future__ import annotations

import json
import sys

from src.pipeline import run


def main():
    sample = "@VerizonSupport My 5G is painfully slow this morning. Please help."
    text = sys.argv[1] if len(sys.argv) > 1 else sample
    result = run(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
