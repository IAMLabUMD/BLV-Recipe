from __future__ import annotations

import re, json, sys, os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib import request as urllib_request, parse as urllib_parse
from urllib.error import URLError


@dataclass
class RawRecipe:
    title:               str
    servings:            str
    time_info:           str
    difficulty:          str
    ingredient_sections: dict[str, list[str]]
    steps:               list[str]
    notes:               list[str]
    source_file:         str
    prep_time:           str = ""
    bake_time:           str = ""


def _extract_clean_text(html: str) -> list[str]:
    """Strip HTML → clean lines, removing nav / footer / wiki noise."""
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
    SKIP_RE = re.compile(
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
    lines = []
    for line in text.split('\n'):
        l = line.strip()
        if not l or len(l) < 3:
            continue
        if SKIP_RE.match(l):
            continue
        lines.append(l)
    return lines


def _find_title(lines: list[str]) -> str:
    for line in lines[:20]:
        m = re.match(r'Cookbook:(.+)', line)
        if m:
            raw = m.group(1).strip()
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
    m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else ""


def _find_ingredients(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "Ingredients"
    in_ing  = False
    STOP_RE = re.compile(
        r'^(Procedure|Instructions?|Directions?|Steps?|Method|'
        r'Notes?|Tips?|Warnings?|See also|Variations?|References?)', re.I
    )
    HDR_RE  = re.compile(
        r'^(Ingredients?|Crust|Filling|Topping|Sauce|Dough|'
        r'Glaze|Marinade|Batter|For the|Meatballs?|To serve|'
        r'Tomato Sauce|Pomodoro|Garnish|Dressing|Spice Blend)', re.I
    )
    HDR_MAX_LEN = 30
    AMT_RE  = re.compile(
        r'^([\d¼½¾⅓⅔⅛⅜⅝⅞]|\d+/\d+|[\d]+\s*(g|oz|lb|kg|ml|cup|tbsp?|'
        r'tsp?|tablespoon|teaspoon|pinch|dash|clove|can|jar|'
        r'bunch|sprig|stalk|fillet|pound|head|handful|wedge|slice))', re.I
    )
    for line in lines:
        if STOP_RE.match(line):
            in_ing = False
            continue
        if HDR_RE.match(line) and len(line) <= HDR_MAX_LEN:
            in_ing  = True
            current = line.strip()
            if current not in sections:
                sections[current] = []
            continue
        if in_ing and AMT_RE.match(line):
            sections.setdefault(current, []).append(line)
        elif not in_ing and AMT_RE.match(line) and len(line.split()) <= 12:
            sections.setdefault("Ingredients", []).append(line)
    return sections if any(v for v in sections.values()) else {"Ingredients": []}


def _find_steps(lines: list[str]) -> list[str]:
    steps: list[str] = []
    in_proc = False
    buf     = ""
    PROC_RE = re.compile(
        r'^(Procedure|Instructions?|Directions?|Steps?|Method|Preparation)(\s+\[.*?\])?$', re.I
    )
    STOP_RE = re.compile(
        r'^(Notes?|Tips?|Variations?|Warnings?|See also|References?|'
        r'Rate This Recipe|Let others know|Submit)', re.I
    )
    SUBSECT_RE = re.compile(
        r'^(Crust|Filling|Topping|Sauce|Dough|Glaze|Marinade|Batter)$', re.I
    )
    NUM_RE  = re.compile(r'^(\d+)[\.\):\-]\s*(.+)')
    VERB_START = re.compile(
        r'^(Rub|Add|Roll|Make|Place|Peel|Mix|Transfer|Pour|Dot|Cover|Firm|Cut|'
        r'Brush|Bake|Take|Serve|Boil|Melt|Cook|Drain|Divide|Season|Stir|Let|'
        r'Do not|Remove|Sift|Fold|Combine|Whisk|Knead|Refrigerate|Shape|Press|'
        r'Crimp|Sprinkle|Bring|Set|Heat|Reduce|Grate|Zest|Squeeze|Preheat|'
        r'Prepare|Fill|Clip|Attach|Drop|Tip|Slide|Turn)', re.I
    )
    for line in lines:
        if STOP_RE.match(line):
            in_proc = False
            continue
        if SUBSECT_RE.match(line):
            continue
        if PROC_RE.match(line):
            in_proc = True
            continue
        m = NUM_RE.match(line)
        if m and len(m.group(2)) > 10:
            if buf:
                steps.append(buf.strip())
                buf = ""
            buf = m.group(2)
            in_proc = True
            continue
        if in_proc and VERB_START.match(line) and len(line) > 15:
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
        proc_m = re.search(
            r'Procedure\s*(.+?)(?:Notes?|Tips?|Warnings?|See also|$)',
            full, re.DOTALL | re.I
        )
        if proc_m:
            block = proc_m.group(1)
            sents = re.split(r'(?<=[.!])\s+(?=[A-Z])', block)
            steps = [s.strip() for s in sents if len(s.strip()) > 15]
    return [s for s in steps if len(s) > 10]


def _find_notes(lines: list[str]) -> list[str]:
    notes, in_n = [], False
    for line in lines:
        lo = line.lower()
        if re.match(r'^(notes?|tips?|variation)', lo):
            in_n = True
            continue
        if re.match(r'^(see also|reference|warning|categor)', lo):
            in_n = False
        if in_n and len(line) > 8:
            notes.append(re.sub(r'^[-•*]\s*', '', line).strip())
    return notes


def _find_steps_from_html(raw_html: str) -> list[str]:
    proc_m = re.search(r'id=["\']Procedure["\']', raw_html, re.IGNORECASE)
    if not proc_m:
        return []

    after = raw_html[proc_m.start():]

    stop_m = re.search(
        r'<h2[^>]*>|id=["\'](?:Notes?|Tips?|Nutritional|Variations?|See_also|References?)["\']',
        after[100:],
        re.IGNORECASE
    )
    end_idx = (stop_m.start() + 100) if stop_m else 10000
    section = after[:end_idx]

    ol_blocks = re.findall(r'<ol[^>]*>(.*?)</ol>', section, re.DOTALL | re.IGNORECASE)

    steps: list[str] = []
    for ol in ol_blocks:
        for item in re.findall(r'<li[^>]*>(.*?)</li>', ol, re.DOTALL | re.IGNORECASE):
            text = re.sub(r'<[^>]+>', ' ', item)
            for ent, rep in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                             ('&#160;', ' '), ('&nbsp;', ' ')]:
                text = text.replace(ent, rep)
            text = ' '.join(text.split())
            if len(text) > 10:
                steps.append(text)

    return steps


def _parse_iso8601_duration(duration: str) -> str:
    if not duration:
        return ""
    m = re.match(
        r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
        duration, re.I
    )
    if not m:
        return duration
    days    = int(m.group(1) or 0)
    hours   = int(m.group(2) or 0) + days * 24
    minutes = int(m.group(3) or 0)
    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    return " ".join(parts) if parts else ""


def _extract_jsonld_recipe(raw_html: str) -> Optional[dict]:
    """Extract the first schema.org Recipe object from JSON-LD script tags."""
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
    title = title.strip()

    servings = recipe.get('recipeYield', '')
    if isinstance(servings, list):
        servings = servings[0] if servings else ''
    servings = str(servings).strip()

    prep_time = _parse_iso8601_duration(recipe.get('prepTime', ''))
    cook_time = _parse_iso8601_duration(recipe.get('cookTime', '')
                                        or recipe.get('totalTime', ''))

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
        'title':       title,
        'servings':    servings,
        'prep_time':   prep_time,
        'cook_time':   cook_time,
        'ingredients': ingredients,
        'steps':       steps,
        'description': notes_raw.strip(),
    }


def _fetch_html(url: str) -> str:
    req = urllib_request.Request(
        url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    )
    with urllib_request.urlopen(req, timeout=15) as resp:
        charset = 'utf-8'
        ct = resp.headers.get_content_charset()
        if ct:
            charset = ct
        return resp.read().decode(charset, errors='replace')


def _stem_from_url(url: str) -> str:
    parsed = urllib_parse.urlparse(url)
    segments = [s for s in parsed.path.split('/') if s]
    stem = segments[-1] if segments else parsed.netloc
    stem = re.sub(r'\.(html?|php|aspx?)$', '', stem, flags=re.I)
    stem = re.sub(r'[^a-zA-Z0-9]+', '_', stem).strip('_')
    return stem or 'recipe'


def _write_parse_summary(recipe: RawRecipe, method: str, url: str, out_dir: str) -> None:
    SEP = "─" * 60
    total_ings = sum(len(v) for v in recipe.ingredient_sections.values())

    lines: list[str] = []
    lines.append(f"\n{SEP}")
    lines.append(f"  PARSED RECIPE  [{method}]")
    lines.append(SEP)

    lines.append(f"  Title      : {recipe.title}")
    lines.append(f"  Source URL : {url}")
    lines.append(f"  Servings   : {recipe.servings    or '(not found)'}")
    lines.append(f"  Prep Time  : {recipe.prep_time   or '(not found)'}")
    lines.append(f"  Cook Time  : {recipe.bake_time   or '(not found)'}")
    if recipe.difficulty:
        lines.append(f"  Difficulty : {recipe.difficulty}")

    lines.append(f"\n  INGREDIENTS  ({total_ings} items)")
    for sect, items in recipe.ingredient_sections.items():
        lines.append(f"    [{sect}]")
        for item in items:
            lines.append(f"      - {item}")

    lines.append(f"\n  STEPS  ({len(recipe.steps)})")
    for i, step in enumerate(recipe.steps, 1):
        lines.append(f"    {i:>2}. {step.replace(chr(10), ' ')}")

    if recipe.notes:
        lines.append(f"\n  NOTES  ({len(recipe.notes)})")
        for note in recipe.notes:
            lines.append(f"      - {note}")

    lines.append(SEP + "\n")

    parse_out_dir = os.path.join(out_dir, "parse_output")
    os.makedirs(parse_out_dir, exist_ok=True)

    stem     = _stem_from_url(url)
    out_path = os.path.join(parse_out_dir, f"{stem}.txt")

    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))

    print(f"Saved parse summary → parse_output/{stem}.txt")


def parse_url_recipe(url: str) -> RawRecipe:
    print(f"Fetching: {url}")
    raw = _fetch_html(url)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    jsonld = _extract_jsonld_recipe(raw)
    if jsonld and jsonld['steps']:
        ing_sects: dict[str, list[str]] = {'Ingredients': jsonld['ingredients']}

        recipe = RawRecipe(
            title               = jsonld['title'] or 'Untitled Recipe',
            servings            = jsonld['servings'],
            time_info           = '',
            difficulty          = '',
            ingredient_sections = ing_sects,
            steps               = jsonld['steps'],
            notes               = [jsonld['description']] if jsonld['description'] else [],
            source_file         = url,
            prep_time           = jsonld['prep_time'],
            bake_time           = jsonld['cook_time'],
        )
        _write_parse_summary(recipe, method="JSON-LD", url=url, out_dir=script_dir)
        return recipe

    lines     = _extract_clean_text(raw)
    full_text = '\n'.join(lines)
    title     = _find_title(lines)
    servings  = _find_pattern(full_text, r'Servings?\s+([\d\-–]+[^\n]*)')
    servings  = servings.split('\n')[0].strip() if servings else servings
    time_info = _find_pattern(full_text, r'Time\s+([^\n]{5,60}?)(?:\n|Difficulty|Category)')
    difficulty= _find_pattern(full_text, r'Difficulty\s+([^\n]{2,25}?)(?:\n|Cookbook|Ingredient)')

    prep_time = _find_pattern(full_text, r'prep(?:aration)?[:\s]+([^\n,;]{3,40})')
    bake_time = _find_pattern(
        full_text,
        r'(?:bak(?:ing|e)|cook(?:ing)?|total)[:\s]+([^\n,;]{3,40})'
    )
    prep_time = re.sub(r'^[~>]', '', prep_time).strip()
    bake_time = re.sub(r'^[~>]', '', bake_time).strip()
    ing_sects = _find_ingredients(lines)
    html_steps = _find_steps_from_html(raw)
    steps      = html_steps if html_steps else _find_steps(lines)
    method     = "HTML <ol> extraction" if html_steps else "plain-text scraping"
    notes      = _find_notes(lines)

    recipe = RawRecipe(
        title=title, servings=servings, time_info=time_info,
        difficulty=difficulty, ingredient_sections=ing_sects,
        steps=steps, notes=notes, source_file=url,
        prep_time=prep_time, bake_time=bake_time,
    )
    _write_parse_summary(recipe, method=method, url=url, out_dir=script_dir)
    return recipe


def parse_html_file(file_path: str | Path) -> RawRecipe:
    """Parse a local HTML file into a RawRecipe."""
    file_path = Path(file_path)
    print(f"Parsing HTML file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    source_url = str(file_path)

    jsonld = _extract_jsonld_recipe(raw)
    if jsonld and jsonld['steps']:
        ing_sects: dict[str, list[str]] = {'Ingredients': jsonld['ingredients']}

        recipe = RawRecipe(
            title               = jsonld['title'] or 'Untitled Recipe',
            servings            = jsonld['servings'],
            time_info           = '',
            difficulty          = '',
            ingredient_sections = ing_sects,
            steps               = jsonld['steps'],
            notes               = [jsonld['description']] if jsonld['description'] else [],
            source_file         = source_url,
            prep_time           = jsonld['prep_time'],
            bake_time           = jsonld['cook_time'],
        )
        return recipe

    lines     = _extract_clean_text(raw)
    full_text = '\n'.join(lines)
    title     = _find_title(lines)
    servings  = _find_pattern(full_text, r'Servings?\s+([\d\-–]+[^\n]*)')
    servings  = servings.split('\n')[0].strip() if servings else servings
    time_info = _find_pattern(full_text, r'Time\s+([^\n]{5,60}?)(?:\n|Difficulty|Category)')
    difficulty= _find_pattern(full_text, r'Difficulty\s+([^\n]{2,25}?)(?:\n|Cookbook|Ingredient)')

    prep_time = _find_pattern(full_text, r'prep(?:aration)?[:\s]+([^\n,;]{3,40})')
    bake_time = _find_pattern(
        full_text,
        r'(?:bak(?:ing|e)|cook(?:ing)?|total)[:\s]+([^\n,;]{3,40})'
    )
    prep_time = re.sub(r'^[~>]', '', prep_time).strip()
    bake_time = re.sub(r'^[~>]', '', bake_time).strip()
    ing_sects = _find_ingredients(lines)
    html_steps = _find_steps_from_html(raw)
    steps      = html_steps if html_steps else _find_steps(lines)
    method     = "HTML <ol> extraction" if html_steps else "plain-text scraping"
    notes      = _find_notes(lines)

    recipe = RawRecipe(
        title=title, servings=servings, time_info=time_info,
        difficulty=difficulty, ingredient_sections=ing_sects,
        steps=steps, notes=notes, source_file=source_url,
        prep_time=prep_time, bake_time=bake_time,
    )
    return recipe


def run_step1(input_path: str | Path, output_dir: str | Path | None = None) -> str:
    """
    Parse a recipe from either a URL or a local HTML file.

    Args:
        input_path: A URL (starting with http:/https://) or path to a local HTML file
        output_dir: Directory to save the output. If None, uses current directory.

    Returns:
        Path to the saved recipe file (step1_recipe.txt)
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Detect if input is a URL or file path
    input_str = str(input_path).strip()
    is_url = input_str.startswith('http://') or input_str.startswith('https://')

    if is_url:
        recipe = parse_url_recipe(input_str)
        source_identifier = input_str
    else:
        recipe = parse_html_file(input_path)
        source_identifier = str(Path(input_path).name)

    # Save the recipe summary to step1_recipe.txt
    output_file = output_dir / "step1_recipe.txt"

    SEP = "─" * 60
    total_ings = sum(len(v) for v in recipe.ingredient_sections.values())

    lines: list[str] = []
    lines.append(f"\n{SEP}")
    lines.append(f"  PARSED RECIPE  [Step 1]")
    lines.append(SEP)

    lines.append(f"  Title      : {recipe.title}")
    lines.append(f"  Source     : {source_identifier}")
    lines.append(f"  Servings   : {recipe.servings    or '(not found)'}")
    lines.append(f"  Prep Time  : {recipe.prep_time   or '(not found)'}")
    lines.append(f"  Cook Time  : {recipe.bake_time   or '(not found)'}")
    if recipe.difficulty:
        lines.append(f"  Difficulty : {recipe.difficulty}")

    lines.append(f"\n  INGREDIENTS  ({total_ings} items)")
    for sect, items in recipe.ingredient_sections.items():
        lines.append(f"    [{sect}]")
        for item in items:
            lines.append(f"      - {item}")

    lines.append(f"\n  STEPS  ({len(recipe.steps)})")
    for i, step in enumerate(recipe.steps, 1):
        lines.append(f"    {i:>2}. {step.replace(chr(10), ' ')}")

    if recipe.notes:
        lines.append(f"\n  NOTES  ({len(recipe.notes)})")
        for note in recipe.notes:
            lines.append(f"      - {note}")

    lines.append(SEP + "\n")

    with open(output_file, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))

    print(f"Saved parsed recipe → {output_file}")
    return str(output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 step1_parse_recipe.py <recipe-url>")
        print("Example: python3 step1_parse_recipe.py https://www.allrecipes.com/recipe/12682/apple-pie-i/")
        sys.exit(1)

    try:
        r = parse_url_recipe(sys.argv[1])
    except URLError as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)