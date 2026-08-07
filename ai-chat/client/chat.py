#!/usr/bin/env python3
"""Zeus Assist — terminal chat against the Claude API.

Path 2 of the two deployment options (see ../README.md). Use this only when the
assistant needs to live somewhere a Claude Project cannot go — embedded in the ICT
dashboard, or behind a Teams bot. For the four technicians using it directly, the
Project is the better tool and needs none of this.

    export ANTHROPIC_API_KEY=sk-ant-...
    pip install -r requirements.txt
    python chat.py

The system prompt is ../instructions.md and the grounding is ../knowledge/*.md, so
both deployment paths stay in sync from the same files in git.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS = ROOT / "instructions.md"
KNOWLEDGE_DIR = ROOT / "knowledge"

MODEL = "claude-opus-5"

# max_tokens caps thinking *and* response text together. Thinking is on by default
# on Opus 5, so this is deliberately generous — a tight cap truncates mid-answer.
MAX_TOKENS = 16000

# Depth of reasoning. "medium" is the right trade for helpdesk Q&A: the knowledge
# base does the heavy lifting, and lower effort keeps replies fast. Raise to "high"
# if answers come back shallow on genuinely hard diagnostics.
EFFORT = "medium"

# Claude Opus 5 runs safety classifiers that can decline a request outright. That is
# a live concern here, not a hypothetical: this assistant is asked about phishing,
# credential compromise and account lockouts every week, and benign security work
# occasionally trips the cyber classifier. With this on, a declined request is
# re-run server-side on a fallback model in the same call instead of coming back
# empty. Set False if the beta is not enabled on the account.
USE_REFUSAL_FALLBACK = True


def build_system_blocks() -> list[dict]:
    """Assemble the system prompt as one cacheable block.

    The knowledge base is small enough (~5k tokens) to send in full on every turn.
    That is deliberate: no retrieval step means nothing can silently fail to
    retrieve, which is the most common way a grounded assistant starts making
    things up. Revisit only past ~50k tokens.

    One `cache_control` breakpoint on the whole thing. Caching is a prefix match,
    so the content above it must be byte-identical every turn — never interpolate
    a timestamp, ticket number or user name into these files at runtime.
    """
    parts = [INSTRUCTIONS.read_text(encoding="utf-8")]
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        parts.append(f"\n\n# Knowledge base file: {path.name}\n\n{path.read_text(encoding='utf-8')}")
    return [{
        "type": "text",
        "text": "".join(parts),
        "cache_control": {"type": "ephemeral"},
    }]


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()
    system_blocks = build_system_blocks()
    messages: list[dict] = []

    print(f"Zeus Assist ({MODEL}, effort={EFFORT}). Ctrl-C or an empty line to quit.\n")

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not user:
            return 0

        messages.append({"role": "user", "content": user})

        kwargs = dict(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_blocks,
            messages=messages,
            output_config={"effort": EFFORT},
        )
        if USE_REFUSAL_FALLBACK:
            kwargs["betas"] = ["server-side-fallback-2026-07-01"]
            kwargs["fallbacks"] = "default"
            stream_ctx = client.beta.messages.stream(**kwargs)
        else:
            stream_ctx = client.messages.stream(**kwargs)

        print("\nzeus> ", end="", flush=True)
        with stream_ctx as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
            final = stream.get_final_message()
        print("\n")

        if final.stop_reason == "refusal":
            # Not an HTTP error — a 200 with empty or partial content. Reading
            # content[0] here without checking would raise IndexError.
            print("[declined by safety classifiers — rephrase, or handle by hand]\n")
            messages.pop()
            continue

        # Append the full content list, not just the text. On Opus 5 this carries
        # thinking blocks that must be passed back unchanged on the next turn.
        messages.append({"role": "assistant", "content": final.content})

        usage = final.usage
        if usage.cache_read_input_tokens:
            print(f"[cache read {usage.cache_read_input_tokens} tok, "
                  f"new input {usage.input_tokens}, out {usage.output_tokens}]\n")


if __name__ == "__main__":
    raise SystemExit(main())
