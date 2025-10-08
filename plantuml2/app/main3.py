# app/main.py
import os
import shutil
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from app.services.csv_service import (
    construct_test_cases_from_csv,
    process_csv_and_generate,
    refine_plantuml_code,
    enrich_test_cases_with_ai,
)

# New CMDB service imports
from app.services.cmdb_service import (
    construct_cmdb_from_file,
    process_cmdb_and_generate,
    refine_cmdb_plantuml_code,
    enrich_cmdb_with_ai as enrich_cmdb_with_ai_service,
)

load_dotenv()

# Hardcode API key for testing (remove this in production!)
HARDCODED_API_KEY = "your key here"

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

logger.info(f"Frontend dist directory: {FRONTEND_DIST_DIR}")

# Default port configuration
DEFAULT_PORT = 8000

app = FastAPI(title="Test Case → PlantUML & CMDB → PlantUML Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve React frontend static files
app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="frontend_assets")


@app.get("/")
async def serve_frontend():
    """Serve the React frontend index.html"""
    return FileResponse(FRONTEND_DIST_DIR / "index.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ------------------------
# Existing test-case endpoints remain unchanged
# ------------------------

@app.post("/upload-csv/")
async def upload_csv(request: Request, file: UploadFile = File(...)):
    filename = file.filename.lower()
    dest = UPLOAD_DIR / file.filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Convert Excel → CSV
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(dest)
        csv_path = dest.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        dest = csv_path
    elif not filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files allowed")

    try:
        logger.info(f"=== CSV UPLOAD PROCESSING START ===")
        logger.info(f"Processing file: {file.filename}")
        logger.info(f"File size: {dest.stat().st_size} bytes")
        
        # Get API key from request headers or use hardcoded for testing
        openai_key = request.headers.get("X-OpenAI-API-Key") or HARDCODED_API_KEY
        if openai_key == HARDCODED_API_KEY:
            logger.info("Using hardcoded API key for testing")
        else:
            logger.info(f"✓ OpenAI API Key found in headers (length: {len(openai_key)})")
        
        # Step 1: Construct initial test cases from CSV
        logger.info("Step 1: Constructing initial test cases from CSV...")
        test_cases = construct_test_cases_from_csv(str(dest), openai_key)
        logger.info(f"✓ Generated {len(test_cases)} initial test cases")
        
        # Step 2: Enhance with AI analysis (only if API key is available)
        if openai_key:
            logger.info("Step 2: Enhancing test cases with AI analysis...")
            enhanced_test_cases = enrich_test_cases_with_ai(test_cases, openai_key)
            logger.info(f"✓ AI enhancement completed - {len(enhanced_test_cases)} comprehensive test cases generated")
        else:
            logger.info("Step 2: Skipping AI enhancement (no API key provided)")
            enhanced_test_cases = test_cases
        
        # Safe-serialize for frontend
        def _serialize(tc_list):
            out = []
            for tc in tc_list:
                tc_copy = dict(tc)
                steps = []
                for s in tc_copy.get("steps", []):
                    s_copy = dict(s)
                    if isinstance(s_copy.get("action"), (dict, list)):
                        s_copy["action"] = json.dumps(s_copy["action"], default=str)
                    steps.append(s_copy)
                tc_copy["steps"] = steps
                out.append(tc_copy)
            return out

        logger.info("=== CSV UPLOAD PROCESSING SUCCESS ===")
        return {"success": True, "test_cases": _serialize(enhanced_test_cases)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse CSV and construct test cases: {e}"
        )


@app.post("/generate-diagram/")
async def generate_diagram(request: Request, body: dict = Body(...)):
    try:
        logger.info("=== GENERATE DIAGRAM START ===")
        test_cases = body.get("test_cases")
        if not test_cases or not isinstance(test_cases, list):
            raise HTTPException(status_code=400, detail="No test_cases provided")
        openai_key = request.headers.get("X-OpenAI-API-Key") or HARDCODED_API_KEY
        if openai_key == HARDCODED_API_KEY:
            logger.info("Using hardcoded API key for testing")
        os.environ["OPENAI_API_KEY"] = openai_key

        result = process_csv_and_generate(csv_path=None, output_dir=str(STATIC_DIR), test_cases=test_cases)
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to process test cases"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in generate-diagram")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat-plantuml/")
async def chat_plantuml(request: Request, body: dict = Body(...)):
    plantuml_code = body.get("plantuml_code")
    user_message = body.get("message")
    if not plantuml_code or not user_message:
        raise HTTPException(status_code=400, detail="plantuml_code and message are required")
    openai_key = request.headers.get("X-OpenAI-API-Key") or HARDCODED_API_KEY
    if openai_key == HARDCODED_API_KEY:
        logger.info("Using hardcoded API key for testing")
    os.environ["OPENAI_API_KEY"] = openai_key

    result = refine_plantuml_code(plantuml_code=plantuml_code, message=user_message, output_dir=str(STATIC_DIR))
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to refine PlantUML"))
    return result


# ------------------------
# New: CMDB endpoints (modeled after CSV/test-case flow)
# ------------------------

@app.post("/upload-cmdb/")
async def upload_cmdb(request: Request, file: UploadFile = File(...)):
    """
    Upload a CMDB file (CSV / Excel / JSON / YAML / single-cell JSON text).
    Returns structured CMDB items for frontend editing (components, attributes, relationships).
    """
    filename = file.filename.lower()
    dest = UPLOAD_DIR / file.filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        logger.info(f"=== CMDB UPLOAD START ===")
        logger.info(f"Processing CMDB file: {file.filename} (size: {dest.stat().st_size} bytes)")

        # Attempt to convert Excel -> CSV for convenience (construct_cmdb_from_file handles CSV/Excel)
        cmdb_items = construct_cmdb_from_file(str(dest))
        logger.info(f"✓ Parsed {len(cmdb_items)} CMDB items")

        # AI enhancement with hardcoded key for testing
        openai_key = request.headers.get("X-OpenAI-API-Key") or HARDCODED_API_KEY
        if openai_key == HARDCODED_API_KEY:
            logger.info("Using hardcoded API key for testing")
        logger.info("Enhancing CMDB with AI to infer relationships and topology...")
        enhanced = enrich_cmdb_with_ai_service(cmdb_items, openai_api_key=openai_key)
        logger.info(f"✓ AI enriched CMDB items (count now: {len(enhanced)})")

        return {"success": True, "cmdb_items": enhanced}
    except Exception as e:
        logger.exception("Failed to process CMDB upload")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-cmdb-diagram/")
async def generate_cmdb_diagram(request: Request, body: dict = Body(...)):
    """
    Accept edited CMDB JSON and generate PlantUML architecture diagram + image + extracted components/relationships.
    """
    try:
        cmdb_items = body.get("cmdb_items")
        if not cmdb_items or not isinstance(cmdb_items, list):
            raise HTTPException(status_code=400, detail="cmdb_items (list) is required")

        openai_key = request.headers.get("X-OpenAI-API-Key") or HARDCODED_API_KEY
        if openai_key == HARDCODED_API_KEY:
            logger.info("Using hardcoded API key for testing")
        os.environ["OPENAI_API_KEY"] = openai_key

        result = process_cmdb_and_generate(cmdb_items=cmdb_items, output_dir=str(STATIC_DIR))
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate CMDB diagram"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in generate-cmdb-diagram")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat-cmdb-plantuml/")
async def chat_cmdb_plantuml(request: Request, body: dict = Body(...)):
    plantuml_code = body.get("plantuml_code")
    user_message = body.get("message")
    if not plantuml_code or not user_message:
        raise HTTPException(status_code=400, detail="plantuml_code and message are required")
    openai_key = request.headers.get("X-OpenAI-API-Key") or HARDCODED_API_KEY
    if openai_key == HARDCODED_API_KEY:
        logger.info("Using hardcoded API key for testing")
    os.environ["OPENAI_API_KEY"] = openai_key

    result = refine_cmdb_plantuml_code(plantuml_code=plantuml_code, message=user_message, output_dir=str(STATIC_DIR))
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to refine CMDB PlantUML"))
    return result


# Catch-all route for React Router (must be last)
@app.get("/{full_path:path}")
async def serve_frontend_catch_all(full_path: str):
    """Catch-all route to serve React app for client-side routing"""
    if full_path.startswith(("api/", "upload-csv/", "generate-diagram/", "chat-plantuml/", "health", "upload-cmdb/", "generate-cmdb-diagram/", "chat-cmdb-plantuml/")):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    return FileResponse(FRONTEND_DIST_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
