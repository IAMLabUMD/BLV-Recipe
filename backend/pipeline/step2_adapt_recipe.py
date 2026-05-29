from __future__ import annotations

import argparse
from pathlib import Path

from pipeline.llm_client import LLMClient

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "output" / "step2_adapted_recipe.md"
FEW_SHOT_DIR = BASE_DIR / "data" / "few_shot_pairs"
TOOL_DICTIONARY_PATH = BASE_DIR / "data" / "tool_dictionary.txt"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_step2(step1_output_path: str | Path, output_dir: str | Path | None = None) -> str:
    recipe_path = Path(step1_output_path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"Step 1 output file not found: {recipe_path}")

    tool_dictionary_text = _read_text(TOOL_DICTIONARY_PATH)

    sightedExample1 = _read_text(FEW_SHOT_DIR / "sighted/hoppin-john.txt")
    blindExample1 = _read_text(FEW_SHOT_DIR / "blind/hoppin-john.txt")
    sightedExample2 = _read_text(FEW_SHOT_DIR / "sighted/english-breakfast.txt")
    blindExample2 = _read_text(FEW_SHOT_DIR / "blind/english-breakfast.txt")
    sightedExample3 = _read_text(FEW_SHOT_DIR / "sighted/green-bean-casserole.txt")
    blindExample3 = _read_text(FEW_SHOT_DIR / "blind/green-bean-casserole.txt")
    sightedExample4 = _read_text(FEW_SHOT_DIR / "sighted/key-lime-pie.txt")
    blindExample4 = _read_text(FEW_SHOT_DIR / "blind/key-lime-pie.txt")
    newRecipe = _read_text(recipe_path)

    SYSTEM_PROMPT = r"""You are an expert assistant helping a blind chef adapt standard recipes
        to be accessible for blind and visually impaired cooks. When adapting recipes you:
        - Replace all visual cues (color, appearance) with tactile, auditory, or smell-based cues
        - Never use visual language (like refrencing how something 'looks' or being able to 'see' something)
        - Suggest specialized tools where helpful
        - Break steps down more granularly so nothing is assumed to be visually obvious
        - When a recipe tip is included, it must appear immediately after the step it relates to — never grouped at the end. Tips are optional and should only be added when they offer genuinely useful guidance for that specific step, such as an easier technique, a safety note, or a relevant substitution.
        - Never include a long list of tools with no explanations at the beginning or end.
        - Convert all fractions into spoken form:
        ½ → a half
        ⅓ → a third
        ¼ → a quarter
        ¾ → three quarters
        Mixed numbers:
        1 ½ → one and a half
        2 ⅓ → two and one third
        - Use full names for measurements (e.g. "tablespoons" instead of "tbsp")
        - The first time an ingredient is used in a step, state its full amount inline in spoken form (CORRECT: "Add the one thinly sliced onion and the three cloves of thinly sliced garlic to the pan." INCORRECT: "Add the thinly sliced onion and garlic to the pan"). For all subsequent steps that reference the same ingredient, omit the amount and refer to it naturally (e.g. "stir the pasta to prevent sticking"). Do not repeat amounts after the first use.
            The final output must be a markdown file.
        - Never directly reference that this recipe is adapted for blind cooks. The recipe should feel natural and not call attention to the fact that it is adapted. Do not use phrases like "for blind cooks" or "visually impaired cooks" in the recipe steps."""

    USER_PROMPT = rf"""
        You will be shown examples of recipe pairs. In each pair, the sighted version and the blind-adapted version are for the same dish but are NOT exact matches — they may differ in ingredient amounts, number of steps, or specific ingredients used. This is intentional.

        Your job is NOT to spot the differences between them. Instead, focus on understanding
        the TECHNIQUES used to make the blind-adapted version more accessible. Specifically, look for:

        - How visual cues (color, appearance, visual doneness checks) are replaced with tactile, auditory, or smell-based cues — but only where genuinely necessary. Do not add sensory cues to every step, or in cases where the cue could be dangerous (such as touching hot food). Use them only when a sighted recipe would otherwise rely on visual information to judge doneness, safety, or technique.
        - How steps are broken down more granularly so nothing assumes visual awareness
        - How spatial and physical guidance is made more explicit (e.g. hand placement, container positioning, how to tell when something has changed texture or temperature)
        - How a brief introduction and numbered section overview is provided before the steps, so cooks can mentally prepare for the full process.
        - How the recipe overview contains the number of servings the recipe makes (only if the original recipe provides it), and an estimated time commitment. For blind cooks, the estimated time is usually double the time listed in a sighted recipe.
        - How the adapted recipe may ADD steps or techniques not present in the sighted version if they meaningfully improve accessibility or safety
        - How some steps have a recipe tip immediately after the step to help the cook find easier ways to complete it, but these tips are optional and not necessary to complete the recipe
        - How plating instructions include tactile spatial guidance

        The audience is blind and visually impaired adults who are competent home cooks. Do not over-explain basic cooking tasks unless there is a specific accessibility reason to do so.
        Do not simplify by removing useful detail, but avoid unnecessary jargon, chef-specific terminology, or status-signaling language.

        ---EXAMPLE 1---
        SIGHTED VERSION:
        ${sightedExample1}

        BLIND-ADAPTED VERSION:
        ${blindExample1}

        ---EXAMPLE 2---
        SIGHTED VERSION:
        ${sightedExample2}

        BLIND-ADAPTED VERSION:
        ${blindExample2}

        ---EXAMPLE 3---
        SIGHTED VERSION:
        ${sightedExample3}

        BLIND-ADAPTED VERSION:
        ${blindExample3}

        ---EXAMPLE 4---
        SIGHTED VERSION:
        ${sightedExample4}

        BLIND-ADAPTED VERSION:
        ${blindExample4}

        ---NOW ADAPT THIS RECIPE---
        SIGHTED VERSION:
        ${newRecipe}

        BLIND-ADAPTED VERSION:"""

    print("Step 2: Calling API...")
    client = LLMClient.from_step_name("step2_adapt_recipe")
    response_text = client.chat(
        system=SYSTEM_PROMPT,
        user_message=USER_PROMPT,
    )
    print("Step 2: API call complete.")

    if output_dir:
      outdir = Path(output_dir)
    else:
      outdir = DEFAULT_OUTPUT_PATH.parent
    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / DEFAULT_OUTPUT_PATH.name
    output_path.write_text(response_text or "", encoding="utf-8")
    return str(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Adapt a recipe into blind-friendly Markdown.")
    parser.add_argument("input_path", help="Path to the Step 1 recipe text file")
    args = parser.parse_args()
    output_path = run_step2(args.input_path)


if __name__ == "__main__":
  main()
