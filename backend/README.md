# BLV-Recipe

This project converts a recipe URL into an accessible, blind-friendly version.

## How the pipeline works

1. Parse the recipe HTML
2. Adapt it into blind-friendly Markdown
3. Add tool callouts
4. Detect visual cues
5. Replace visual cues with non-visual cues
6. Convert the result to accessible HTML
7. Add tool links

## Running the App

1. Navigate to the backend folder and activate the virtual environment:
```bash
   cd backend
   source .venv/bin/activate
```

2. Start the server:
```bash
   python3 -m uvicorn main:app --reload
```

3. Open your browser and go to `http://127.0.0.1:8000`

To stop the server, press `Ctrl+C` in the terminal.