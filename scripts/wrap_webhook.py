#!/usr/bin/env python3
"""Wrap a raw Feishu Card JSON 2.0 object for a custom-bot webhook.

The script writes JSON only. It never sends the webhook request.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


def generate_sign(timestamp: str, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    digest = hmac.new(string_to_sign, digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def load_card(path: Path) -> dict[str, Any]:
    if str(path) == "-":
        value = json.load(sys.stdin)
    else:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("card root must be a JSON object")
    if value.get("schema") != "2.0":
        raise ValueError('card must explicitly set "schema": "2.0"')
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wrap raw Feishu Card JSON 2.0 for a custom-bot webhook."
    )
    parser.add_argument("card", type=Path, help="raw card JSON path, or - for stdin")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="write to this path instead of stdout",
    )
    parser.add_argument(
        "--secret-env",
        metavar="ENV_NAME",
        help="read a signing secret from this environment variable",
    )
    parser.add_argument(
        "--timestamp",
        help="override Unix timestamp for deterministic testing",
    )
    args = parser.parse_args()

    try:
        card = load_card(args.card)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload: dict[str, Any] = {
        "msg_type": "interactive",
        "card": card,
    }

    if args.secret_env:
        secret = os.environ.get(args.secret_env)
        if not secret:
            print(
                f"ERROR: environment variable {args.secret_env!r} is unset or empty",
                file=sys.stderr,
            )
            return 2
        timestamp = args.timestamp or str(int(time.time()))
        payload["timestamp"] = timestamp
        payload["sign"] = generate_sign(timestamp, secret)

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
