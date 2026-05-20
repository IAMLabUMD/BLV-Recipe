from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = "llama-3.3-70b-versatile"
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "output" / "step3_tool_callouts.md"
TOOL_DICTIONARY_PATH = BASE_DIR / "data" / "tool_dictionary.txt"


def _build_groq_client() -> Groq:
    load_dotenv(dotenv_path=BASE_DIR / ".env")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env.")
    return Groq(api_key=api_key)


def run_step3(step2_output_path: str | Path, output_dir: str | Path | None = None) -> str:
    recipe_path = Path(step2_output_path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"Step 2 output file not found: {recipe_path}")

    markdown_content = recipe_path.read_text(encoding="utf-8")
    tool_dictionary_text = TOOL_DICTIONARY_PATH.read_text(encoding="utf-8")

    SYSTEM_PROMPT = r"""You are an expert assistant helping a blind chef add specialized tool recommendations to an already-adapted blind-friendly recipe.

        You will be given a blind-adapted recipe in Markdown format. Your only job is to identify steps where a TBK (The Blind Kitchen) tool would meaningfully improve safety or accessibility, and insert the appropriate tool callouts.

        Rules:
        - Use exact tool names from the tool dictionary. Do not paraphrase.
        - Place the TBK callout on its own line immediately after the step it relates to.
        - Only add a callout where a tool genuinely improves safety or accessibility for
          that specific step. A step qualifies if it involves: precision measurement,
          a heat or cut safety risk, or a technique that is meaningfully harder without
          specialist equipment.
        - Each tool should only appear ONCE in the entire recipe. Before inserting a callout,
          check whether that tool has already been used in an earlier step. If it has,
          do not add it again. If no new tool applies, leave the step without a callout.
        - It is acceptable and expected that some steps will have no TBK callout at all.
        - These tools are just suggestions — the cook may choose to use them or not based on their own preferences and experience. Do not write the callouts as if the tools are mandatory.
        - For any step where you add a TBK tool callout, you must also provide a tool-free alternative. Both paths must be fully usable on their own. The tool-free alternative should never suggest that someone should assist the cook.
        - Return the full recipe in Markdown with the tool callouts inserted. Do not summarize or rewrite any recipe content.

        Format each callout exactly like this:

        For a step with one tool:
          TBK Tool: Talking Thermometer — announces the internal temperature aloud so you don't need to read a display.
          Tool-free: Use a timer and the touch test instead — the meat should feel firm with no give when pressed.

        For a step with multiple tools:
          TBK Tool: Salt Cellar — lets you measure salt by pinching rather than pouring.
          TBK Tool: Long Wood Spoon — keeps hands away from heat while stirring.
          Tool-free: Pre-measure salt into a small bowl before starting, and use any long-handled spoon to stir.

        Never do this (missing Tool-free line):
          TBK Tool: Salt Cellar — lets you measure salt by pinching."""

    USER_PROMPT = f"""
        Below is the tool dictionary listing all available TBK tools, followed by a reference guide for which tools apply to which types of steps, followed by the recipe.

        ---TOOL DICTIONARY---
        {tool_dictionary_text}

        ---TBK TOOL REFERENCE---
        Select a tool based on the specific needs of the step:

          Measuring dry ingredients          → Dry Measure Cups, Dry Measure Spoons
          Measuring wet ingredients          → Wet Measure Cups, Wet Measure Spoons
          Oil by the tablespoon from bottle  → Auto-Measure Spout
          Butter pats or slices              → Butter Slicer
          Weighing ingredients               → Talking Scale
          Pasta portions                     → Pasta Portioner
          Consistent scooping (cookies etc.) → Portion Scoop

          Cutting / knife safety             → Cut Glove (non-dominant hand, always)
          Even slices                        → Slicing Guide, Finger Guard
          Peeling vegetables and fruit       → Palm Peeler
          Coring apples, tomatoes            → Food Corer, Shark
          Zesting, grating hard cheese       → Mini Box Grater
          Scraping bowls, transferring dough → Bench Scraper, Bowl Scraper
          Garlic peeling                     → Garlic Peeler
          Storing sharp tools safely         → Sharps Basket

          Detecting boiling water            → Boil Alert Disk
          Stirring in deep or hot pans       → Long Wood Spoon
          Lifting, flipping food in a pan    → Double Spatula, Long Wood Tongs
          Monitoring liquid temperature      → Talking Thermometer, Thermometer Clip
          Timing cooking stages              → Talking Countdown Timer
          Draining hot liquid one-handed     → Side Strainer
          Protecting hands from hot pans     → Heat Gloves, Pan Handle Cover
          Straining solids from liquid       → Straining System, Mesh Strainer
          Shaping eggs or pancakes in pan    → Egg Rings
          Tasting safely from a hot pan      → Tasting Spoon

          Rolling dough to even thickness    → Adjustable Rolling Pin
          Shaping and sizing pie dough       → Pie Dough Bag
          Pulling oven racks without burns   → Oven Push-Pull
          Guarding against rack burns        → Oven Rack Guards
          Cutting baked goods into portions  → Baking Grid Pan
          Protecting pie crust edges         → Pie Crust Protector

          Containing spills, organising prep → Work Trays
          Holding a bag open for filling     → Bag Holder
          Labelling containers, appliances   → Bump Dots, Tactile Paint, WayAround, Wikki Stix

        ---RECIPE---
        {markdown_content}
        """

    client = _build_groq_client()
    print("Step 3: Calling Groq API for tool callouts...")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )
    print("Step 3: Groq API call complete.")

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
    parser = argparse.ArgumentParser(description="Insert TBK tool callouts into adapted recipe.")
    parser.add_argument("input_path", help="Path to the Step 2 adapted recipe Markdown file")
    args = parser.parse_args()
    output_path = run_step3(args.input_path)
    print(output_path)


if __name__ == "__main__":
    main()
