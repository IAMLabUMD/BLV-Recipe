# BLV-Recipe

This project converts a recipe HTML file into an accessible, blind-friendly version.

## How the pipeline works

1. Parse the recipe HTML
2. Adapt it into blind-friendly Markdown
3. Add tool callouts
4. Detect visual cues
5. Replace visual cues with non-visual cues
6. Convert the result to accessible HTML
7. Add tool links

## How to run

1. Install dependencies:
	`pip install -r requirements.txt`
2. Run the pipeline with an input HTML file:
	`python main.py data/input/pasta-carbonara.html`

The outputs are saved in `data/output/<recipe-name>/`.