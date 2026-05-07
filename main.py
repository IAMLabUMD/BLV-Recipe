from __future__ import annotations

import argparse
from pathlib import Path

from step1_parse_recipe import run_step1
from step2_adapt_recipe import run_step2
from step3_handle_tools import run_step3
from step4_detect_visual_cues import run_step4
from step5_replace_visual_cues import run_step5
from step6_to_accessible_html import run_step6
from step7_add_tool_links import run_step7


def run_pipeline(input_html_path: str | Path) -> tuple[str, str, str, str, str, str, str]:
    base = Path(__file__).resolve().parent
    input_path = Path(input_html_path)
    output_dir = base / "data" / "output" / input_path.stem
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
