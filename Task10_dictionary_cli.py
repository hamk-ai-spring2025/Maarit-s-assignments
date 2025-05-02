#!/usr/bin/env python3
"""dictionary_cli.py – A tiny CLI tool that turns any word into a JSON‑formatted
Finnish dictionary entry using an OpenAI chat model.

Usage
-----
$ python Task10_dictionary_cli.py <word>
# or, interactively
$ python Task10_dictionary_cli.py
Word? ohjelmointi

The script prints **only** valid JSON to stdout – no preamble, no extra text.
Make sure your OPENAI_API_KEY environment variable is set before running.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

import openai  # pip install openai>=1.0.0

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

SYSTEM_PROMPT = (
    "You are a bilingual English–Finnish dictionary generator. "
    "Given an English word, you output a JSON object with the following keys: "
    "'word' (the Finnish translation), 'definition' (Finnish), "
    "'synonyms' (Finnish list), 'antonyms' (Finnish list), and "
    "'examples' (list of Finnish example sentences). "
    "Output **valid JSON only** – no markdown, no prose, no commentary. "
    "If a list is empty, output an empty list ([]) not null. "
    "Encoding must be UTF‑8 and JSON must be parseable."
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def query_llm(word: str) -> Dict[str, Any]:
    """Send ``word`` to the chat model and return the parsed JSON response."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Generate a dictionary entry for the word: '" + word + "'. "
                "Remember: JSON output only."
            ),
        },
    ]

    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=TEMPERATURE,
    )

    raw_json: str = response.choices[0].message.content.strip()
    # Validate JSON; if invalid, raise a clear error.
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Model returned invalid JSON:\n" + raw_json) from exc


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        sys.stderr.write("Error: OPENAI_API_KEY environment variable not set.\n")
        sys.exit(1)

    # Read word either from CLI arg or interactive prompt.
    word = (
        sys.argv[1]
        if len(sys.argv) > 1
        else input("Word?").strip()
    )

    if not word:
        sys.stderr.write("No word provided. Exiting.\n")
        sys.exit(1)

    result = query_llm(word)

    # Pretty‑print JSON with UTF‑8 characters unescaped.
    json.dump(result, sys.stdout, ensure_ascii=False, indent=4)
    sys.stdout.write("\n")  # newline at end of file


if __name__ == "__main__":
    main()
