from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = "llama-3.3-70b-versatile"
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "output" / "step7_linked_accessible_recipe.html"
TOOL_LINK_DICTIONARY_PATH = BASE_DIR / "data" / "tool_link_dictionary.txt"


def _build_groq_client() -> Groq:
    load_dotenv(dotenv_path=BASE_DIR / ".env")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env.")
    return Groq(api_key=api_key)


def run_step7(step6_output_path: str | Path, output_dir: str | Path | None = None) -> str:
    recipe_path = Path(step6_output_path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"Step 6 output file not found: {recipe_path}")

    html_content = recipe_path.read_text(encoding="utf-8")
    tool_link_dictionary_text = TOOL_LINK_DICTIONARY_PATH.read_text(encoding="utf-8")

    SYSTEM_PROMPT = r"""You are an HTML-preserving linker.

      You will receive:
      1. An HTML recipe
      2. A TXT file of TBK tools and URLs

      TASK:
      Find the "TBK Tools:" label in the HTML, and within its associated ordered list (<ol>), wrap each TBK tool name in an anchor tag using the TXT file.

      ----------------------------------
      STRICT RULES

      - Do NOT change, rewrite, reorder, or remove any content.
      - Do NOT change punctuation, spacing, or formatting.
      - ONLY add <a href="URL">Tool Name</a> around matched tool names.

      ----------------------------------
      SCOPE (CRITICAL)

      - Only link tool names that appear inside the <ol> list that follows:
        <p>TBK Tools:</p>

      - Do NOT link tool names anywhere else in the document.

      ----------------------------------
      TXT FORMAT

      Each line:
      Tool Name: URL

      - The first ":" separates the tool name from the URL.

      ----------------------------------
      MATCHING

      - Prefer exact matches.
      - Allow small differences (capitalization, spacing, hyphens, singular/plural).
      - If unsure, do NOT link.

      ----------------------------------
      LINKING

      - Wrap ONLY the tool name text.
      - Keep punctuation (like ":" or commas) outside the link.
      - Do NOT modify any surrounding text.
      - If already linked, leave unchanged.

      ----------------------------------
      HTML SAFETY

      - Do NOT break HTML structure.
      - Do NOT move or restructure elements.
      - Only insert <a> tags inline.

      ----------------------------------
      OUTPUT

      - Return the full HTML document only.
      - No explanations.
      - Wrap your HTML inside triple backticks

      ----------------------------------
      Wait for the user to provide a HTML recipe."""

    USER_PROMPT = f"""
      HTML RECIPE: {html_content}
      TBK TOOL LINK DICTIONARY: {tool_link_dictionary_text}
    """

    client = _build_groq_client()
    print("Step 7: Calling Groq API...")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )
    print("Step 7: Groq API call complete.")

    if output_dir:
        outdir = Path(output_dir)
    else:
        outdir = DEFAULT_OUTPUT_PATH.parent
    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / DEFAULT_OUTPUT_PATH.name
    output_text = response.choices[0].message.content if response.choices else ""
    output_path.write_text(output_text or "", encoding="utf-8")
    return str(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Add tool links to an accessible HTML recipe.")
    parser.add_argument("input_path", help="Path to the Step 6 HTML file")
    args = parser.parse_args()
    output_path = run_step7(args.input_path)
    print(output_path)


if __name__ == "__main__":
    main()
