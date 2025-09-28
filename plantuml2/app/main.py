# app/main.py
import os
import shutil
import json
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from app.services.csv_service import (
    construct_test_cases_from_csv,
    process_csv_and_generate,
    refine_plantuml_code,
    enrich_test_cases_with_ai,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

print(FRONTEND_DIST_DIR, "FRONTEND_DIST_DIR");

# Default port configuration
DEFAULT_PORT = 8000

app = FastAPI(title="Test Case → PlantUML Generator")

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


@app.get("/test-case-info")
async def get_test_case_info():
    """
    Provide information about the enhanced test case generation capabilities.
    """
    return {
        "enhanced_features": {
            "comprehensive_analysis": "AI analyzes uploaded data to identify missing test scenarios",
            "pattern_detection": "Automatically detects data patterns and relationships",
            "coverage_expansion": "Generates additional test cases for complete coverage",
            "edge_case_generation": "Includes boundary conditions and error scenarios",
            "actor_identification": "Identifies all possible actors and user roles",
            "integration_testing": "Creates test cases for integration points",
            "data_validation": "Generates validation and input testing scenarios"
        },
        "supported_scenarios": [
            "Happy path testing",
            "Error handling and exception scenarios", 
            "Edge cases and boundary conditions",
            "Data validation scenarios",
            "Integration testing",
            "User experience flows",
            "Performance considerations",
            "Security testing (when applicable)"
        ],
        "ai_capabilities": {
            "data_analysis": "Deep analysis of CSV/Excel data structure",
            "pattern_recognition": "Identifies relationships and dependencies",
            "test_case_synthesis": "Creates comprehensive test cases from minimal data",
            "coverage_optimization": "Ensures complete test coverage",
            "scenario_expansion": "Generates missing test scenarios"
        }
    }


@app.post("/upload-csv/")
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """
    Upload CSV/Excel → construct test cases (even if missing) → return JSON
    for frontend editing. No PlantUML is generated yet.
    """
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
        print(f"=== CSV UPLOAD PROCESSING START ===")
        print(f"Processing file: {file.filename}")
        print(f"File size: {dest.stat().st_size} bytes")
        
        # Get API key from request headers
        openai_key = request.headers.get("X-OpenAI-API-Key")
        if not openai_key:
            print("WARNING: No OpenAI API key provided in headers - AI enhancement will be skipped")
            print("For comprehensive test case generation, please provide OpenAI API key in X-OpenAI-API-Key header")
        else:
            print(f"✓ OpenAI API Key found (length: {len(openai_key)})")
        
        # Step 1: Construct initial test cases from CSV
        print("Step 1: Constructing initial test cases from CSV...")
        test_cases = construct_test_cases_from_csv(str(dest), openai_key)
        print(f"✓ Generated {len(test_cases)} initial test cases")
        
        # Step 2: Enhance with AI analysis (only if API key is available)
        if openai_key:
            print("Step 2: Enhancing test cases with AI analysis...")
            print("This may take a moment as AI analyzes the data and generates comprehensive test coverage...")
            enhanced_test_cases = enrich_test_cases_with_ai(test_cases, openai_key)
            print(f"✓ AI enhancement completed - {len(enhanced_test_cases)} comprehensive test cases generated")
        else:
            print("Step 2: Skipping AI enhancement (no API key provided)")
            enhanced_test_cases = test_cases
        
        # Log some statistics about the enhancement
        if len(enhanced_test_cases) > len(test_cases):
            print(f"✓ AI added {len(enhanced_test_cases) - len(test_cases)} additional test cases for comprehensive coverage")
        
        # Count actors and steps
        total_actors = set()
        total_steps = 0
        for tc in enhanced_test_cases:
            total_actors.update(tc.get("actors", []))
            total_steps += len(tc.get("steps", []))
        
        print(f"✓ Final test suite contains:")
        print(f"  - {len(enhanced_test_cases)} test cases")
        print(f"  - {len(total_actors)} unique actors")
        print(f"  - {total_steps} total test steps")
        
        # Serialize safely for frontend
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

        print("=== CSV UPLOAD PROCESSING SUCCESS ===")
        return {"success": True, "test_cases": _serialize(enhanced_test_cases)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse CSV and construct test cases: {e}"
        )


@app.post("/generate-diagram/")
async def generate_diagram(request: Request, body: dict = Body(...)):
    """
    Accept edited test_cases JSON from frontend and resume PlantUML pipeline.
    """
    try:
        print("=== GENERATE DIAGRAM START ===")
        print(f"Request received at: {__import__('datetime').datetime.now()}")
        
        test_cases = body.get("test_cases")
        print(f"Test cases count: {len(test_cases) if test_cases else 0}")
        
        if not test_cases or not isinstance(test_cases, list):
            print("ERROR: No test_cases provided or invalid format")
            raise HTTPException(status_code=400, detail="No test_cases provided")

        print(f"Processing {len(test_cases)} test cases...")
        print(f"Output directory: {STATIC_DIR}")
        
        # Get API key from request headers
        openai_key = request.headers.get("X-OpenAI-API-Key")
        if not openai_key:
            print("ERROR: No OpenAI API key provided in headers")
            raise HTTPException(status_code=400, detail="OpenAI API key is required. Please provide it in the X-OpenAI-API-Key header.")
        
        print(f"OpenAI API Key present: {bool(openai_key)}")
        print(f"OpenAI API Key length: {len(openai_key)}")
        
        # Set the API key as environment variable for the service
        import os
        os.environ["OPENAI_API_KEY"] = openai_key
        
        result = process_csv_and_generate(
            csv_path=None, output_dir=str(STATIC_DIR), test_cases=test_cases
        )

        print(f"Process result success: {result.get('success', False)}")
        if not result.get("success", False):
            error_msg = result.get("error", "Failed to process test cases")
            print(f"ERROR in process_csv_and_generate: {error_msg}")
            print("=== GENERATE DIAGRAM ERROR ===")
            raise HTTPException(
                status_code=500,
                detail=error_msg,
            )

        print("Diagram generated successfully")
        print("=== GENERATE DIAGRAM SUCCESS ===")
        return result
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"UNEXPECTED ERROR in generate_diagram: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("=== GENERATE DIAGRAM UNEXPECTED ERROR ===")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@app.post("/chat-plantuml/")
async def chat_plantuml(request: Request, body: dict = Body(...)):
    plantuml_code = body.get("plantuml_code")
    user_message = body.get("message")
    if not plantuml_code or not user_message:
        raise HTTPException(
            status_code=400, detail="plantuml_code and message are required"
        )

    # Get API key from request headers
    openai_key = request.headers.get("X-OpenAI-API-Key")
    if not openai_key:
        raise HTTPException(status_code=400, detail="OpenAI API key is required. Please provide it in the X-OpenAI-API-Key header.")
    
    # Set the API key as environment variable for the service
    import os
    os.environ["OPENAI_API_KEY"] = openai_key

    result = refine_plantuml_code(
        plantuml_code=plantuml_code, message=user_message, output_dir=str(STATIC_DIR)
    )

    if not result.get("success", False):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to refine PlantUML"),
        )

    return result


# Catch-all route for React Router (must be last)
@app.get("/{full_path:path}")
async def serve_frontend_catch_all(full_path: str):
    """Catch-all route to serve React app for client-side routing"""
    # Check if the path is an API route
    if full_path.startswith(("api/", "upload-csv/", "generate-diagram/", "chat-plantuml/", "health")):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # For all other routes, serve the React app
    return FileResponse(FRONTEND_DIST_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT, reload=True)
