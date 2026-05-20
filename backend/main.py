from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib import parse as urllib_parse

from backend.pipeline.step1_parse_recipe import run_step1
from backend.pipeline.step2_adapt_recipe import run_step2
from backend.pipeline.step3_handle_tools import run_step3
from backend.pipeline.step4_detect_visual_cues import run_step4
from backend.pipeline.step5_replace_visual_cues import run_step5
from backend.pipeline.step6_to_accessible_html import run_step6
from backend.pipeline.step7_add_tool_links import run_step7


def _get_output_dir_name(input_path: str | Path) -> str:
    """
    Extract a directory name from either a URL or a file path.
    """
    input_str = str(input_path).strip()

    if input_str.startswith('http://') or input_str.startswith('https://'):
        # Extract meaningful name from URL
        parsed = urllib_parse.urlparse(input_str)
        segments = [s for s in parsed.path.split('/') if s]
        name = segments[-1] if segments else parsed.netloc
        # Remove file extensions
        name = re.sub(r'\.(html?|php|aspx?)$', '', name, flags=re.I)
        # Replace non-alphanumeric with underscore
        name = re.sub(r'[^a-zA-Z0-9]+', '-', name).strip('-')
        return name or 'recipe'
    else:
        # Use file stem for local files
        return Path(input_path).stem


def run_pipeline(input_html_path: str | Path) -> tuple[str, str, str, str, str, str, str]:
    base = Path(__file__).resolve().parent
    output_dir_name = _get_output_dir_name(input_html_path)
    output_dir = base / "data" / "output" / output_dir_name
    print("=" * 80)
    print("STEP 1 — Parse recipe HTML")
    step1_output = run_step1(input_html_path, output_dir=output_dir)

    print("=" * 80)
    print("STEP 2 — Adapt recipe to blind-friendly Markdown")
    step2_output = run_step2(step1_output, output_dir=output_dir)

    print("=" * 80)
    print("STEP 3 — Insert TBK tool callouts")
    step3_output = run_step3(step2_output, output_dir=output_dir)

    print("=" * 80)
    print("STEP 4 — Detect visual cues")
    step4_output = run_step4(step3_output, output_dir=output_dir)

    print("=" * 80)
    print("STEP 5 — Replace visual cues with non-visual cues")
    step5_output = run_step5(step4_output, output_dir=output_dir)

    print("=" * 80)
    print("STEP 6 — Convert markdown to accessible HTML")
    step6_output = run_step6(step5_output, output_dir=output_dir)

    print("=" * 80)
    print("STEP 7 — Add tool links")
    step7_output = run_step7(step6_output, output_dir=output_dir)

    return step1_output, step2_output, step3_output, step4_output, step5_output, step6_output, step7_output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full recipe adaptation pipeline.")
    parser.add_argument("input_html_path", help="Path to the input HTML recipe file")
    args = parser.parse_args()

    step1_output, step2_output, step3_output, step4_output, step5_output, step6_output, step7_output = run_pipeline(args.input_html_path)

    print("=" * 80)
    print("Pipeline complete. Output files:")
    print(f"1. {step1_output}")
    print(f"2. {step2_output}")
    print(f"3. {step3_output}")
    print(f"4. {step4_output}")
    print(f"5. {step5_output}")
    print(f"6. {step6_output}")
    print(f"7. {step7_output}")


if __name__ == "__main__":
    main()
