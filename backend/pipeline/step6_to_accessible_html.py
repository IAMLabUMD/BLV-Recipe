from __future__ import annotations

import argparse
from pathlib import Path

from pipeline.llm_client import LLMClient

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "output" / "step6_accessible_recipe.html"


def run_step6(step5_output_path: str | Path, output_dir: str | Path | None = None) -> str:
    recipe_path = Path(step5_output_path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"Step 5 output file not found: {recipe_path}")

    markdown_content = recipe_path.read_text(encoding="utf-8")

    SYSTEM_PROMPT = r"""Convert the following Markdown recipe into a complete, accessible HTML document.

      GOAL:
      Produce a clean, semantic, screen-reader-friendly recipe page that is easy to navigate and consistent in structure.

      ----------------------------------
      STRICT CONTENT PRESERVATION (CRITICAL):

      1. Preserve ALL original recipe content exactly as written.
        - Do NOT rewrite, paraphrase, simplify, or summarize any text.
        - Do NOT change wording, punctuation, or formatting of the original text.

      2. Preserve the EXACT order of all content.
        - Do NOT reorder sections, paragraphs, or list items.

      3. Perform a STRUCTURAL TRANSFORMATION ONLY:
        - Convert Markdown into HTML.
        - Wrap content in HTML tags without modifying the original text.

      4. You MAY add ONLY the following structural elements:
        - HTML document tags (<html>, <head>, <body>, etc.)
        - Section wrappers (<main>, <article>, <section>, etc.)
        - Step headings (e.g., "Step 1", "Step 2", etc.)

      5. Do NOT add any new content beyond required structural elements.

      ----------------------------------
      TAG HANDLING (CRITICAL):

      Visual and non-visual cues may appear as:
      - <visual>text</visual>
      - <visual ...>text</visual>
      - <non-visual>text</non-visual>
      - <non-visual ...>text</non-visual>

      Rules:
      - Convert ALL of the above to: <strong>text</strong>
      - Remove the original tags entirely
      - Do NOT modify the text inside the tags

      ----------------------------------
      HTML DOCUMENT STRUCTURE:

      1. Output a complete HTML document:
        - <!DOCTYPE html>
        - <html lang="en">
        - <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recipe Title</title>
          </head>
        - <body>

      2. Wrap the recipe content in:
        - <main>
        - <article aria-labelledby="recipe-title">

      3. Add a <header> section containing:
        - <h1 id="recipe-title">Recipe title</h1>
        - If the Markdown includes an introductory paragraph directly after the title, preserve it and place it under the <h1> inside a <p> tag.
        - If no introduction exists in the Markdown, include only the <h1> without a paragraph.
        - Do NOT generate or invent an introduction.

      4. Use semantic sections:
        - Wrap each major section in:
            <section aria-labelledby="...">
        - Use heading hierarchy consistently:
            - <h2> for main sections (e.g., Overview, Ingredients, Instructions)
            - <h3> for subsections
            - <h4> for individual instruction steps

      5. Ingredients:
        - Create a section with <h2>Ingredients</h2>
        - ALWAYS use an ordered list (<ol>) for ingredients
        - Each ingredient must be its own <li>

        - If ingredients are grouped under subheadings:
          - Preserve them as <h3> subsections
          - Each group must have its own <ol>

      6. Instructions:
        - Create a section with <h2>Instructions</h2>

        - If there are subsections:
            - Use <h3> headings
            - Always label them sequentially as:
              <h3>Part 1: [Original Title]</h3>, <h3>Part 2: [Original Title]</h3>, etc.
            - Preserve the original subsection title after the Part number
            - If no subsection title exists, use only:
              <h3>Part 1</h3>, <h3>Part 2</h3>, etc.

        - Each step must:
          - Add a step heading: <h4>Step 1</h4>, <h4>Step 2</h4>, etc.
          - Place the instruction text in a <p> immediately after the heading

        - Number steps continuously across all sections (do not reset numbering)

        - Do NOT use <li> for steps

      7. Inside each step:
        - The main instruction must be in a <p>

        - If additional content exists (TBK tools, tips, safety notes):
          - Place them AFTER the main instruction <p>

        - TBK Tools:
          - Add:
            <p>TBK Tools:</p>
          - Follow with an ordered list (<ol>)
          - Each tool must be its own <li>

        - Recipe tips and safety notes:
          - Keep as separate <p> elements:
            <p>Recipe Tip: ...</p>
            <p>Safety Note: ...</p>

      ----------------------------------
      ACCESSIBILITY REQUIREMENTS:

      8. Use semantic HTML for all content:
        - <main>, <article>, <header>, <section>, <footer>
        - <h1>–<h4>, <p>, <ol>, <ul>, <li>

      9. Ensure valid HTML:
        - Do NOT place block elements (like <ol>) inside <p>
        - Maintain clean, readable structure

      ----------------------------------
      OUTPUT RULES:

      - Output ONLY the final HTML
      - Do NOT include explanations or markdown formatting
      - Ensure the HTML is properly indented and easy to copy
      - The output must be directly usable as a .html file
      - Wrap your HTML inside triple backticks

      ----------------------------------
      Wait for the user to provide a Markdown recipe."""

    USER_PROMPT = f"{markdown_content}"

    client = LLMClient.from_step_name("step6_to_accessible_html")
    print("Step 6: Calling API for accessible HTML conversion...")
    response_text = client.chat(
        system=SYSTEM_PROMPT,
        user_message=USER_PROMPT,
    )
    print("Step 6: API call complete.")

    if output_dir:
        outdir = Path(output_dir)
    else:
        outdir = DEFAULT_OUTPUT_PATH.parent
    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / DEFAULT_OUTPUT_PATH.name
    output_path.write_text(response_text or "", encoding="utf-8")
    return str(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a Markdown recipe into accessible HTML.")
    parser.add_argument("input_path", help="Path to the Step 5 Markdown file")
    args = parser.parse_args()
    output_path = run_step6(args.input_path)


if __name__ == "__main__":
    main()
