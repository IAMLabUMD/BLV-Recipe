import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pipeline.run_pipeline import run_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecipeRequest(BaseModel):
    url: str

# Serve frontend static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
def index():
    return FileResponse("../frontend/index.html")

@app.get("/{page}.html")
def serve_page(page: str):
    return FileResponse(f"../frontend/{page}.html")

@app.post("/test")
async def test(request: RecipeRequest):
    # Mock test endpoint for frontend development (returns sample HTML)
    mock_html = """
    <html>
        <head><title>Test Recipe</title></head>
        <body>
            <h1>Chocolate Chip Cookies</h1>
            <p>A simple test recipe for development.</p>
            <ol>
                <li>Mix ingredients</li>
                <li>Bake at 350°F</li>
                <li>Cool and enjoy</li>
            </ol>
        </body>
    </html>
    """
    return {"html": mock_html}

@app.post("/generate")
async def generate(request: RecipeRequest):
    try:
        html_content = run_pipeline(request.url)
        return {"html": html_content}
    except Exception as e:
        # Print full traceback to uvicorn terminal
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))