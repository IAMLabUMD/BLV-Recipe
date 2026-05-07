from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "output" / "step1_recipe.txt"


@dataclass
class RawRecipe:
    title: str
    servings: str
    time_info: str
    difficulty: str
    ingredient_sections: dict[str, list[str]]
    steps: list[str]
    notes: list[str]
    source_file: str
    prep_time: str = ""
    bake_time: str = ""


def _extract_clean_text(html: str) -> list[str]:
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
    for tag in ['</p>', '</li>', '</h1>', '</h2>', '</h3>', '</h4>',
                '</dt>', '</dd>', '</tr>', '<br', '<br/>']:
        text = text.replace(tag, '\n')
    text = re.sub(r'<[^>]+>', ' ', text)
    for ent, rep in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                     ('&#160;', ' '), ('&nbsp;', ' ')]:
        text = text.replace(ent, rep)
    text = re.sub(r'\[\s*edit\s*\|\s*edit\s*source\s*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(
        r'Jump to content.*?(?=Apple|Cookbook|Garlic|Recipe|Ingredient)',
        '', text, flags=re.DOTALL
    )
    skip_re = re.compile(
        r'^(Main menu|Navigation|Main Page|Help|Browse|Recent changes|'
        r'Special pages|Random|Using Wikibooks|Community|Reading room|'
        r'Policies|Contact|Search|Appearance|Donations|Create account|'
        r'Log in|Personal|Add languages|Add links|Recipe Discussion|'
        r'Read|Edit source|View history|Tools|General|What links|'
        r'Related|Upload|Permanent|Page information|Cite|Download|'
        r'Print|Wikidata|Sister|Wikipedia|Wikiversity|Wiktionary|'
        r'Wikinews|Wikivoyage|Commons|MediaWiki|Meta|Categories|'
        r'Retrieved from|Text is available|Privacy|About Wikibooks|'
        r'Disclaimers|Code of Conduct|Developers|Statistics|Cookie|'
        r'Mobile view|This page was last edited|Hidden category)',
        re.I
    )
    lines: list[str] = []
    for line in text.split('\n'):
        cleaned = line.strip()
        if not cleaned or len(cleaned) < 3:
            continue
        if skip_re.match(cleaned):
            continue
        lines.append(cleaned)
    return lines


def _find_title(lines: list[str]) -> str:
    for line in lines[:20]:
        match = re.match(r'Cookbook:(.+)', line)
        if match:
            raw = match.group(1).strip()
            return raw.split(' - ')[0].strip()
        if '>' in line:
            continue
        if re.match(r'^(Cookbook:|Category|Servings|Time|Difficulty|Ingredients|'
                    r'Procedure|From Wikibooks|YIELDS?|PREP TIME|COOK TIME|TOTAL TIME)', line, re.I):
            continue
        if 5 < len(line) < 80 and not line[0].isdigit():
            return line.split(' - ')[0].strip()
    return "Untitled Recipe"


def _find_pattern(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def _find_ingredients(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "Ingredients"
    in_ing = False
    stop_re = re.compile(
        r'^(Procedure|Instructions?|Directions?|Steps?|Method|'
        r'Notes?|Tips?|Warnings?|See also|Variations?|References?)', re.I
    )
    hdr_re = re.compile(
        r'^(Ingredients?|Crust|Filling|Topping|Sauce|Dough|'
        r'Glaze|Marinade|Batter|For the|Meatballs?|To serve|'
        r'Tomato Sauce|Pomodoro|Garnish|Dressing|Spice Blend)', re.I
    )
    hdr_max_len = 30
    amt_re = re.compile(
        r'^([\d¼½¾⅓⅔⅛⅜⅝⅞]|\d+/\d+|[\d]+\s*(g|oz|lb|kg|ml|cup|tbsp?|'
        r'tsp?|tablespoon|teaspoon|pinch|dash|clove|can|jar|'
        r'bunch|sprig|stalk|fillet|pound|head|handful|wedge|slice))', re.I
    )
    for line in lines:
        if stop_re.match(line):
            in_ing = False
            continue
        if hdr_re.match(line) and len(line) <= hdr_max_len:
            in_ing = True
            current = line.strip()
            if current not in sections:
                sections[current] = []
            continue
        if in_ing and amt_re.match(line):
            sections.setdefault(current, []).append(line)
        elif not in_ing and amt_re.match(line) and len(line.split()) <= 12:
            sections.setdefault("Ingredients", []).append(line)
    return sections if any(v for v in sections.values()) else {"Ingredients": []}


def _find_steps(lines: list[str]) -> list[str]:
    steps: list[str] = []
    in_proc = False
    buf = ""
    proc_re = re.compile(
        r'^(Procedure|Instructions?|Directions?|Steps?|Method|Preparation)(\s+\[.*?\])?$', re.I
    )
    stop_re = re.compile(
        r'^(Notes?|Tips?|Variations?|Warnings?|See also|References?|'
        r'Rate This Recipe|Let others know|Submit)', re.I
    )
    subsect_re = re.compile(r'^(Crust|Filling|Topping|Sauce|Dough|Glaze|Marinade|Batter)$', re.I)
    num_re = re.compile(r'^(\d+)[\.\):\-]\s*(.+)')
    verb_start = re.compile(
        r'^(Rub|Add|Roll|Make|Place|Peel|Mix|Transfer|Pour|Dot|Cover|Firm|Cut|'
        r'Brush|Bake|Take|Serve|Boil|Melt|Cook|Drain|Divide|Season|Stir|Let|'
        r'Do not|Remove|Sift|Fold|Combine|Whisk|Knead|Refrigerate|Shape|Press|'
        r'Crimp|Sprinkle|Bring|Set|Heat|Reduce|Grate|Zest|Squeeze|Preheat|'
        r'Prepare|Fill|Clip|Attach|Drop|Tip|Slide|Turn)', re.I
    )
    for line in lines:
        if stop_re.match(line):
            in_proc = False
            continue
        if subsect_re.match(line):
            continue
        if proc_re.match(line):
            in_proc = True
            continue
        match = num_re.match(line)
        if match and len(match.group(2)) > 10:
            if buf:
                steps.append(buf.strip())
                buf = ""
            buf = match.group(2)
            in_proc = True
            continue
        if in_proc and verb_start.match(line) and len(line) > 15:
            if buf and not buf.endswith(line):
                steps.append(buf.strip())
                buf = line
            elif not buf:
                buf = line
            continue
        if in_proc and buf and len(line) > 5:
            buf += " " + line
    if buf:
        steps.append(buf.strip())
    if not steps:
        full = " ".join(lines)
        proc_m = re.search(r'Procedure\s*(.+?)(?:Notes?|Tips?|Warnings?|See also|$)', full, re.DOTALL | re.I)
        if proc_m:
            block = proc_m.group(1)
            sents = re.split(r'(?<=[.!])\s+(?=[A-Z])', block)
            steps = [s.strip() for s in sents if len(s.strip()) > 15]
    return [s for s in steps if len(s) > 10]


def _find_notes(lines: list[str]) -> list[str]:
    notes, in_notes = [], False
    for line in lines:
        lower = line.lower()
        if re.match(r'^(notes?|tips?|variation)', lower):
            in_notes = True
            continue
        if re.match(r'^(see also|reference|warning|categor)', lower):
            in_notes = False
        if in_notes and len(line) > 8:
            notes.append(re.sub(r'^[-•*]\s*', '', line).strip())
    return notes


def _parse_iso8601_duration(duration: str) -> str:
    if not duration:
        return ""
    match = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration, re.I)
    if not match:
        return duration
    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0) + days * 24
    minutes = int(match.group(3) or 0)
    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    return " ".join(parts) if parts else ""


def _extract_jsonld_recipe(raw_html: str) -> Optional[dict]:
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        raw_html, re.DOTALL | re.IGNORECASE
    )
    recipe = None
    for block in blocks:
        try:
            data = json.loads(block.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        candidates = []
        if isinstance(data, list):
            candidates = data
        elif isinstance(data, dict):
            candidates = data.get('@graph', [data])
        for obj in candidates:
            if isinstance(obj, dict) and obj.get('@type') in ('Recipe', ['Recipe']):
                recipe = obj
                break
        if recipe:
            break

    if not recipe:
        return None

    title = recipe.get('name', '')
    if isinstance(title, list):
        title = title[0] if title else ''
    title = str(title).strip()

    servings = recipe.get('recipeYield', '')
    if isinstance(servings, list):
        servings = servings[0] if servings else ''
    servings = str(servings).strip()

    prep_time = _parse_iso8601_duration(recipe.get('prepTime', ''))
    cook_time = _parse_iso8601_duration(recipe.get('cookTime', '') or recipe.get('totalTime', ''))

    raw_ings = recipe.get('recipeIngredient', [])
    ingredients = [str(i).strip() for i in raw_ings if str(i).strip()]

    raw_steps = recipe.get('recipeInstructions', [])
    steps: list[str] = []
    for s in raw_steps:
        if isinstance(s, str):
            text = s.strip()
        elif isinstance(s, dict):
            text = (s.get('text') or s.get('name') or '').strip()
            if not text and s.get('@type') == 'HowToSection':
                for sub in s.get('itemListElement', []):
                    sub_text = (sub.get('text') or sub.get('name') or '').strip()
                    if sub_text:
                        steps.append(sub_text)
                continue
        else:
            continue
        if text:
            steps.append(text)

    notes_raw = recipe.get('description', '')
    if isinstance(notes_raw, list):
        notes_raw = ' '.join(notes_raw)

    return {
        'title': title,
        'servings': servings,
        'prep_time': prep_time,
        'cook_time': cook_time,
        'ingredients': ingredients,
        'steps': steps,
        'description': str(notes_raw).strip(),
    }


def _format_parse_summary(recipe: RawRecipe, method: str) -> str:
    sep = "─" * 60
    total_ings = sum(len(v) for v in recipe.ingredient_sections.values())

    lines: list[str] = []
    lines.append(f"\n{sep}")
    lines.append(f"  PARSED RECIPE  [{method}]")
    lines.append(sep)
    lines.append(f"  Title      : {recipe.title}")
    lines.append(f"  Servings   : {recipe.servings or '(not found)'}")
    lines.append(f"  Prep Time  : {recipe.prep_time or '(not found)'}")
    lines.append(f"  Cook Time  : {recipe.bake_time or '(not found)'}")
    if recipe.difficulty:
        lines.append(f"  Difficulty : {recipe.difficulty}")
    lines.append(f"\n  INGREDIENTS  ({total_ings} items)")
    for section, items in recipe.ingredient_sections.items():
        lines.append(f"    [{section}]")
        for item in items:
            lines.append(f"      - {item}")
    lines.append(f"\n  STEPS  ({len(recipe.steps)})")
    for index, step in enumerate(recipe.steps, 1):
        lines.append(f"    {index:>2}. {step.replace(chr(10), ' ')}")
    if recipe.notes:
        lines.append(f"\n  NOTES  ({len(recipe.notes)})")
        for note in recipe.notes:
            lines.append(f"      - {note}")
    lines.append(sep + "\n")
    return "\n".join(lines)


def _parse_html_recipe(input_path: Path) -> tuple[RawRecipe, str]:
    raw_html = input_path.read_text(encoding="utf-8", errors="ignore")

    jsonld = _extract_jsonld_recipe(raw_html)
    if jsonld and jsonld["steps"]:
        ingredient_sections: dict[str, list[str]] = {"Ingredients": jsonld["ingredients"]}
        recipe = RawRecipe(
            title=jsonld["title"] or "Untitled Recipe",
            servings=jsonld["servings"],
            time_info="",
            difficulty="",
            ingredient_sections=ingredient_sections,
            steps=jsonld["steps"],
            notes=[jsonld["description"]] if jsonld["description"] else [],
            source_file=str(input_path),
            prep_time=jsonld["prep_time"],
            bake_time=jsonld["cook_time"],
        )
        return recipe, "JSON-LD"

    lines = _extract_clean_text(raw_html)
    full_text = "\n".join(lines)
    recipe = RawRecipe(
        title=_find_title(lines),
        servings=_find_pattern(full_text, r'Servings?\s+([\d\-–]+[^\n]*)').split('\n')[0].strip(),
        time_info=_find_pattern(full_text, r'Time\s+([^\n]{5,60}?)(?:\n|Difficulty|Category)'),
        difficulty=_find_pattern(full_text, r'Difficulty\s+([^\n]{2,25}?)(?:\n|Cookbook|Ingredient)'),
        ingredient_sections=_find_ingredients(lines),
        steps=_find_steps(lines),
        notes=_find_notes(lines),
        source_file=str(input_path),
        prep_time=re.sub(r'^[~>]', '', _find_pattern(full_text, r'prep(?:aration)?[:\s]+([^\n,;]{3,40})')).strip(),
        bake_time=re.sub(r'^[~>]', '', _find_pattern(full_text, r'(?:bak(?:ing|e)|cook(?:ing)?|total)[:\s]+([^\n,;]{3,40})')).strip(),
    )
    return recipe, "plain-text scraping"


def _extract_recipe_text(input_path: Path) -> str:
    recipe, method = _parse_html_recipe(input_path)
    return _format_parse_summary(recipe, method)


def run_step1(input_path: str | Path, output_dir: str | Path | None = None) -> str:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input HTML file not found: {input_file}")

    output_text = _extract_recipe_text(input_file)

    if output_dir:
        outdir = Path(output_dir)
    else:
        outdir = DEFAULT_OUTPUT_PATH.parent
    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / DEFAULT_OUTPUT_PATH.name
    output_path.write_text(output_text, encoding="utf-8")
    return str(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse an HTML recipe page with Groq.")
    parser.add_argument("input_path", help="Path to a local HTML recipe file")
    args = parser.parse_args()
    output_path = run_step1(args.input_path)
    print(output_path)


if __name__ == "__main__":
    main()
