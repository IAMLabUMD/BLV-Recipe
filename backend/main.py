import traceback
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from urllib import parse as urllib_parse
import re
import asyncio

from pipeline.run_pipeline import run_pipeline
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

app = FastAPI()

# Track the current active task and cancellation flag
current_generation_task = None
generation_cancelled = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecipeRequest(BaseModel):
    url: str

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
def index():
    return FileResponse("../frontend/index.html")

@app.get("/{page}.html")
def serve_page(page: str):
    return FileResponse(f"../frontend/{page}.html")

@app.post("/test")
async def test(request: RecipeRequest):
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

def _get_output_dir_name(input_url: str) -> str:
    input_str = str(input_url).strip()
    if input_str.startswith('http://') or input_str.startswith('https://'):
        parsed = urllib_parse.urlparse(input_str)
        segments = [s for s in parsed.path.split('/') if s]
        name = segments[-1] if segments else parsed.netloc
        name = re.sub(r'\.(html?|php|aspx?)$', '', name, flags=re.I)
        name = re.sub(r'[^a-zA-Z0-9]+', '-', name).strip('-')
        return name or 'recipe'
    else:
        return Path(input_url).stem

def sse_message(event: str, data: dict) -> str:
    """Format a server-sent event message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

@app.post("/generate")
async def generate(request: RecipeRequest):
    global current_generation_task, generation_cancelled
    generation_cancelled = False
    current_generation_task = asyncio.current_task()

    async def stream():
        global generation_cancelled
        try:
            base = Path(__file__).resolve().parent
            output_dir = base / "pipeline" / "data" / "output" / _get_output_dir_name(request.url)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            yield sse_message("progress", {"step": 1, "total": 7, "message": "Parsing recipe..."})
            step1_output = await asyncio.to_thread(run_step1, request.url, output_dir=output_dir)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            yield sse_message("progress", {"step": 2, "total": 7, "message": "Adapting recipe for accessibility..."})
            step2_output = await asyncio.to_thread(run_step2, step1_output, output_dir=output_dir)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            yield sse_message("progress", {"step": 3, "total": 7, "message": "Adding tool suggestions..."})
            step3_output = await asyncio.to_thread(run_step3, step2_output, output_dir=output_dir)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            yield sse_message("progress", {"step": 4, "total": 7, "message": "Detecting visual cues..."})
            step4_output = await asyncio.to_thread(run_step4, step3_output, output_dir=output_dir)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            yield sse_message("progress", {"step": 5, "total": 7, "message": "Replacing visual cues..."})
            step5_output = await asyncio.to_thread(run_step5, step4_output, output_dir=output_dir)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            yield sse_message("progress", {"step": 6, "total": 7, "message": "Converting to HTML..."})
            step6_output = await asyncio.to_thread(run_step6, step5_output, output_dir=output_dir)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            yield sse_message("progress", {"step": 7, "total": 7, "message": "Adding tool links..."})
            step7_output = await asyncio.to_thread(run_step7, step6_output, output_dir=output_dir)

            if generation_cancelled:
                yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
                return

            with open(step7_output, "r", encoding="utf-8") as f:
                html_content = f.read()

            yield sse_message("complete", {"html": html_content})

        except asyncio.CancelledError:
            yield sse_message("cancelled", {"message": "Recipe generation was cancelled."})
        except Exception as e:
            traceback.print_exc()
            yield sse_message("error", {"message": str(e)})
        finally:
            global current_generation_task
            current_generation_task = None

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.post("/cancel")
async def cancel():
    global current_generation_task, generation_cancelled
    generation_cancelled = True
    if current_generation_task and not current_generation_task.done():
        current_generation_task.cancel()
    return {"status": "cancelled"}

# @app.get("/")
# def index():
#     return FileResponse("../frontend/index.html")

# @app.get("/{page}.html")
# def serve_page(page: str):
#     return FileResponse(f"../frontend/{page}.html")

# @app.post("/test")
# async def test(request: RecipeRequest):
#     # Mock test endpoint for frontend development (returns sample HTML)
#     mock_html = """
#     <html>
#         <head><title>Test Recipe</title></head>
#         <body>
#             <h1>Chocolate Chip Cookies</h1>
#             <p>A simple test recipe for development.</p>
#             <ol>
#                 <li>Mix ingredients</li>
#                 <li>Bake at 350°F</li>
#                 <li>Cool and enjoy</li>
#             </ol>
#         </body>
#     </html>
#     """
#     return {"html": mock_html}

# @app.post("/generate")
# async def generate(request: RecipeRequest):
#     try:
#         html_content = run_pipeline(request.url)
#         return {"html": html_content}
#     except Exception as e:
#         # Print full traceback to uvicorn terminal
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

