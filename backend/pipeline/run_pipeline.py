from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib import parse as urllib_parse


from pipeline.step1_parse_recipe import run_step1
from pipeline.step2_adapt_recipe import run_step2
from pipeline.step3_handle_tools import run_step3
from pipeline.step4_detect_visual_cues import run_step4
from pipeline.step5_replace_visual_cues import run_step5
from pipeline.step6_to_accessible_html import run_step6
from pipeline.step7_add_tool_links import run_step7

from pipeline.config import LLMConfig, LLMProvider, MODELS

LLMConfig.set_all_steps(
    provider=LLMProvider.ANTHROPIC,
    model=MODELS["claude-sonnet-4.6"],
)


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


def run_pipeline(input_url: str | Path) -> tuple[str, str, str, str, str, str, str]:
    base = Path(__file__).resolve().parent
    output_dir_name = _get_output_dir_name(input_url)
    output_dir = base / "data" / "output" / output_dir_name
    step1_output = run_step1(input_url, output_dir=output_dir)
    step2_output = run_step2(step1_output, output_dir=output_dir)
    step3_output = run_step3(step2_output, output_dir=output_dir)
    step4_output = run_step4(step3_output, output_dir=output_dir)
    step5_output = run_step5(step4_output, output_dir=output_dir)
    step6_output = run_step6(step5_output, output_dir=output_dir)
    step7_output = run_step7(step6_output, output_dir=output_dir)

    with open(step7_output, "r", encoding="utf-8") as f:
        html_content = f.read()

    return html_content


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full recipe adaptation pipeline.")
    parser.add_argument("input_url", help="Path to the input HTML recipe file")
    args = parser.parse_args()

    run_pipeline(args.input_url)


if __name__ == "__main__":
    main()
