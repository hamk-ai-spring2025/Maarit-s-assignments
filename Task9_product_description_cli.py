#!/usr/bin/env python3
"""Generate product descriptions and marketing slogans from 1‒N images via **Google Gemini**.

Usage
~~~~~
    Task9_product_description_cli.py image1.jpg image2.png \
        --extra "Hand‑woven in Finland, 100 % organic cotton"
e.g. python Task9_product_description_cli.py kakkara.jpg --extra "white"
The script prints results and saves them to **output.json**.

Requirements
~~~~~~~~~~~~
    pip install google-generativeai Pillow rich

Environment
~~~~~~~~~~~
    export GEMINI_API_KEY="YOUR_API_KEY"

API quota: Free Google AI Studio keys are throttled—prefer paid keys for batch work.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image
from rich import print
from rich.console import Console
from rich.table import Table

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    sys.stderr.write("[ERROR] google-generativeai not installed. Run: pip install google-generativeai\n")
    sys.exit(1)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def load_image(path: Path) -> Image.Image:
    """Load an image and ensure it is RGB (Gemini Vision requirement)."""
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def build_prompt(extra: str | None = None) -> str:
    """Return the textual prompt given any extra user context."""
    base = (
        "You are a product copywriter. For the given product photo, "
        "write a vivid 2–3‑sentence product description (100 words max). "
        "Then craft a catchy 8‑word marketing slogan. Output exactly the JSON schema:\n"  # noqa: E501
        "{\n  \"description\": <string>,\n  \"slogan\": <string>\n}\n"
    )
    if extra:
        base += f"Additional context: {extra}"
    return base


def generate_for_image(model: genai.GenerativeModel, prompt: str, img: Image.Image) -> Dict[str, Any]:
    """Call Gemini Vision and return the parsed JSON dict."""
    response = model.generate_content([img, prompt])  # type: ignore[arg-type]
    # Gemini might wrap JSON in markdown fencing – find first brace
    txt = response.text.strip()
    json_start = txt.find("{")
    json_end = txt.rfind("}") + 1
    try:
        data = json.loads(txt[json_start:json_end])
    except json.JSONDecodeError:
        data = {
            "description": txt,
            "slogan": "(Could not parse slogan)",
        }
    return data

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Generate product copy from images via Gemini Vision")
    parser.add_argument("images", metavar="IMAGE", nargs="+", help="Path(s) to product photo(s)")
    parser.add_argument("--extra", "-e", help="Extra context to refine the description", default=None)
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini Vision model name")
    parser.add_argument("--outfile", default="output.json", help="File to dump JSON results")
    args = parser.parse_args(argv)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.stderr.write("[ERROR] GEMINI_API_KEY env var not set.\n")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    prompt = build_prompt(args.extra)
    results: Dict[str, Dict[str, str]] = {}

    console = Console()
    table = Table(title="Gemini Product Descriptions", show_lines=True)
    table.add_column("Image", style="cyan")
    table.add_column("Description")
    table.add_column("Slogan", style="magenta")

    for img_path in args.images:
        path = Path(img_path)
        if not path.exists():
            console.print(f"[red]Skipping missing file[/red] {path}")
            continue
        img = load_image(path)
        data = generate_for_image(model, prompt, img)
        results[path.name] = data
        table.add_row(path.name, data.get("description", "-"), data.get("slogan", "-"))

    console.print(table)

    with open(args.outfile, "w", encoding="utf-8") as fp:
        json.dump(results, fp, indent=2, ensure_ascii=False)
    console.print(f"\nResults saved to [bold]{args.outfile}[/bold]")


if __name__ == "__main__":  # pragma: no cover
    main()
