#!/usr/bin/env python3
"""Zeus Assist — terminal chat against the OpenAI API.

Path 2 of the two deployment options (see ../README.md). Use this only if you need
the assistant somewhere a Custom GPT cannot go — embedded in the ICT dashboard, or
behind a Teams bot. For the four technicians using it directly, the Custom GPT is
the better tool and needs none of this.

    export OPENAI_API_KEY=sk-...
    pip install -r requirements.txt
    python chat.py

The system prompt is ../instructions.md and the grounding is ../knowledge/*.md, so
both deployment paths stay in sync from the same files in git.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from openai import OpenAI

# The knowledge base is small enough (a few thousand tokens) to send in full on every
# turn. That is deliberate: no retrieval step means nothing can silently fail to
# retrieve, which is the most common way a grounded assistant starts making things up.
# Revisit only if the knowledge base grows past ~50k tokens.
ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS = ROOT / "instructions.md"
KNOWLEDGE_DIR = ROOT / "knowledge"

# Check platform.openai.com/docs/models for the current list before pinning.
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.1")


def build_system_prompt() -> str:
    parts = [INSTRUCTIONS.read_text(encoding="utf-8")]
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        parts.append(f"\n\n# Knowledge base file: {path.name}\n\n{path.read_text(encoding='utf-8')}")
    return "".join(parts)


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    client = OpenAI()
    messages = [{"role": "system", "content": build_system_prompt()}]

    print(f"Zeus Assist ({MODEL}). Ctrl-C or an empty line to quit.\n")

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not user:
            return 0

        messages.append({"role": "user", "content": user})

        print("\nzeus> ", end="", flush=True)
        reply = []
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            piece = chunk.choices[0].delta.content
            if piece:
                reply.append(piece)
                print(piece, end="", flush=True)
        print("\n")

        messages.append({"role": "assistant", "content": "".join(reply)})


if __name__ == "__main__":
    raise SystemExit(main())
