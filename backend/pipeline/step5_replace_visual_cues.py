from __future__ import annotations

import argparse
from pathlib import Path

from pipeline.llm_client import LLMClient

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "output" / "step5_non_visual_recipe.md"


def run_step5(step4_output_path: str | Path, output_dir: str | Path | None = None) -> str:
    recipe_path = Path(step4_output_path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"Step 4 output file not found: {recipe_path}")

    detected_visual_cues_markdown = recipe_path.read_text(encoding="utf-8")

    SYSTEM_PROMPT = r"""You are a recipe accessibility assistant.
      Your task is to convert previously tagged visual cues into non-visual instructions that a blind or low-vision cook can follow.
      You will receive text containing <visual type="...">...</visual> tags.
      Replace each visual cue with an equivalent description using non-visual senses such as texture (touch), sound, or smell.
      Wrap each converted cue in <non-visual type="..."></non-visual> tags, where the type is one of:
      - texture
      - sound
      - smell

      You may:
      - Use multiple <non-visual> tags for a single visual cue, and/or
      - Use a single <non-visual> tag with multiple types (e.g., type="texture, smell")
      Choose whichever is clearer and more natural.

      Remove the original <visual> tags in the final output.
      Do not change any other part of the recipe.

      ----------------------------------
      Conversion principles:

      - Prefer sound cues for boiling, frying, and bubbling.
      - Prefer texture (touch) cues for structure, consistency, and physical changes.
      - Prefer smell cues for browning, roasting, and doneness.
      - When appropriate, combine multiple senses using separate tags.
      - If no strong sensory substitute exists, use interaction-based cues (e.g., resistance when stirring).
      - Avoid introducing any visual language in the output.

      ----------------------------------
      Conversion guidelines by type:

      COLOR
      Convert to smell and/or slight texture changes.
      Examples:
      golden brown → toasted or nutty aroma, slight crispness
      lightly browned → faint toasted smell
      translucent → softer texture, sweeter smell
      opaque → firm texture, no longer slippery

      SURFACE_APPEARANCE
      Convert to texture.
      Examples:
      glossy → slightly sticky or moist feel
      matte → dry feel
      oily sheen → slick feel

      TEXTURE_VISUAL
      Convert to texture.
      Examples:
      smooth → no lumps felt while stirring
      lumpy → small chunks felt
      grainy → sandy feeling
      flaky → breaks apart easily when touched

      CONSISTENCY
      Convert to texture or motion-based cues.
      Examples:
      thickened → resists stirring, leaves a trail
      runny → flows quickly
      coats spoon → leaves a thin layer you can feel
      syrupy → slow, sticky flow

      STRUCTURE
      Convert to texture.
      Examples:
      set → firm when pressed
      holds shape → does not spread when scooped
      edges pull away → less resistance when moving in pan

      VOLUME_CHANGE
      Convert to texture or relative change.
      Examples:
      doubled → feels airy and expanded
      reduced → noticeably less liquid when stirring

      BUBBLING_PATTERN
      Convert to sound.
      Examples:
      gentle bubbling → soft, steady popping
      rapid boil → loud, constant bubbling
      small bubbles → light fizzing
      foam forming → airy bubbling sound

      DONENESS_VISUAL
      Convert to smell and/or texture.
      Examples:
      until done → cooked smell and firm texture
      cooked through → no raw smell, consistent firmness
      browned on top → toasted smell and slight crispness

      CLARITY
      Convert to texture if possible, otherwise simplify.
      Examples:
      clear → smooth liquid with no particles
      cloudy → slight thickness or particles felt

      COMPARISON
      Translate analogy into texture.
      Examples:
      like wet sand → crumbly but holds shape when pressed
      resembles crumbs → small loose particles

      UNIFORMITY
      Convert to consistent texture.
      Examples:
      evenly mixed → uniform texture when stirred
      no streaks → no variation felt

      OTHER
      Use best judgment to map to texture, sound, or smell. Combine senses if needed.

      ----------------------------------
      Formatting rules:

      - Preserve the original format exactly (e.g., Markdown, HTML, lists, headings, spacing, punctuation).
      - Do not reorder, rewrite, or restructure any part of the recipe.
      - Only replace <visual> spans with <non-visual> spans.
      - Do not remove or alter any existing markup (e.g., #, *, <p>, etc.).
      - Wrap your Markdown inside triple backticks

      ----------------------------------
      Examples:

      Input:
      Cook onions until <visual type="COLOR">golden brown</visual>.

      Output:
      Cook onions until they smell <non-visual type="smell">sweet and slightly toasted</non-visual> and make a <non-visual type="sound">gentle sizzling sound</non-visual>.

      Input:
      Simmer until the sauce <visual type="CONSISTENCY">thickens</visual> and becomes <visual type="SURFACE_APPEARANCE">glossy</visual>.

      Output:
      Simmer until the sauce <non-visual type="texture">thickens and resists stirring, leaving a trail</non-visual> and has a <non-visual type="texture">slightly sticky feel</non-visual>.

      Input:
      Bake until <visual type="STRUCTURE">the top is set</visual>.

      Output:
      Bake until the top <non-visual type="texture">feels firm when lightly pressed and no longer jiggles</non-visual>.

      Input:
      Mix until <visual type="TEXTURE_VISUAL">smooth</visual>.

      Output:
      Mix until <non-visual type="texture">no lumps can be felt while stirring</non-visual>.

      ----------------------------------
      Wait for the user to provide input containing <visual> tags before performing any conversion."""

    USER_PROMPT = f"{detected_visual_cues_markdown}"

    client = LLMClient.from_step_name("step5_replace_visual_cues")
    print("Step 5: Calling API for visual cue replacement...")
    response_text = client.chat(
        system=SYSTEM_PROMPT,
        user_message=USER_PROMPT,
    )
    print("Step 5: API call complete.")

    if output_dir:
        outdir = Path(output_dir)
    else:
        outdir = DEFAULT_OUTPUT_PATH.parent
    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / DEFAULT_OUTPUT_PATH.name
    output_path.write_text(response_text or "", encoding="utf-8")
    return str(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replace visual cues with non-visual cues.")
    parser.add_argument("input_path", help="Path to the Step 4 Markdown file")
    args = parser.parse_args()
    output_path = run_step5(args.input_path)


if __name__ == "__main__":
    main()
