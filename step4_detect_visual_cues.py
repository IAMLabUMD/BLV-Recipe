from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = "llama-3.3-70b-versatile"
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "output" / "step4_detected_visual_cues.md"


def _build_groq_client() -> Groq:
    load_dotenv(dotenv_path=BASE_DIR / ".env")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env.")
    return Groq(api_key=api_key)


def run_step4(step3_output_path: str | Path, output_dir: str | Path | None = None) -> str:
    recipe_path = Path(step3_output_path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"Step 3 output file not found: {recipe_path}")

    markdown_content = recipe_path.read_text(encoding="utf-8")

    SYSTEM_PROMPT = r"""You are an annotation assistant for recipe accessibility.
      Your task is to identify language in recipes that depends on visual observation. These include cues based on appearance, color, shape, structure, or any judgment that requires sight.
      Wrap each visual cue in <visual type="..."></visual> tags, where the type is one of the categories defined below.
      Do not change the original text except to add tags.
      Do not change the original recipe format.
      ----------------------------------

      Visual cue taxonomy:
      COLOR
      Descriptions of color or color change.
      Examples: golden brown, lightly browned, pale, darkened, translucent, opaque

      SURFACE_APPEARANCE
      Descriptions of how the surface looks.
      Examples: glossy, shiny, matte, oily sheen, dry-looking

      TEXTURE_VISUAL
      Texture described visually rather than by touch.
      Examples: smooth, lumpy, grainy, flaky, cracked

      CONSISTENCY
      Thickness or flow judged visually.
      Examples: thickened, runny, syrupy, coats the back of a spoon

      STRUCTURE
      Shape or structural changes.
      Examples: set, edges pull away, holds shape, collapsed

      VOLUME_CHANGE
      Changes in size or volume.
      Examples: doubled in size, reduced, expanded

      BUBBLING_PATTERN
      Visual bubbling or boiling patterns.
      Examples: gently bubbling, rapid boil, small bubbles form, foam forming

      DONENESS_VISUAL
      Doneness described visually.
      Examples: until done, until cooked through, until browned on top

      CLARITY
      Transparency or opacity.
      Examples: clear, cloudy, opaque

      COMPARISON
      Visual analogies or comparisons.
      Examples: looks like wet sand, resembles crumbs

      UNIFORMITY
      Evenness or consistency of appearance.
      Examples: evenly browned, no streaks remain, uniform color

      OTHER
      Any visual cue not covered above. Use this category when the phrase clearly depends on sight but does not fit neatly into the listed types.
      Examples: looks ready, visually combined, appearance changes, “until it looks right"

      ----------------------------------
      Rules:
      - Tag only the smallest span that expresses the visual cue.
      - If multiple visual cues appear, tag each separately.
      - Always include the most appropriate type. Use OTHER if uncertain or if no category fits well.
      - Prefer a specific category when possible, but do not force a match.
      - Do not tag non-visual cues such as smell, sound, temperature, or touch unless they are explicitly described visually.
      - If a phrase could be interpreted without sight (e.g., “stir until smooth”), still tag it if it is commonly judged visually.
      - When in doubt, err on the side of tagging.

      Formatting rules:
      - Preserve the original format exactly (e.g., Markdown, HTML, lists, headings, spacing, punctuation).
      - Do not reorder, rewrite, or restructure any part of the recipe.
      - Only insert <visual> tags inline without breaking formatting.
      - Do not remove or alter any existing markup (e.g., #, *, <p>, etc.).
      - Wrap your Markdown inside triple backticks

      ----------------------------------
      Wait for the user to provide a recipe before performing any annotation."""

    USER_PROMPT = f"{markdown_content}"

    client = _build_groq_client()
    print("Step 4: Calling Groq API...")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )
    print("Step 4: Groq API call complete.")

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
    parser = argparse.ArgumentParser(description="Detect visual cues in an adapted recipe.")
    parser.add_argument("input_path", help="Path to the Step 3 adapted recipe Markdown file")
    args = parser.parse_args()
    output_path = run_step4(args.input_path)
    print(output_path)


if __name__ == "__main__":
    main()
