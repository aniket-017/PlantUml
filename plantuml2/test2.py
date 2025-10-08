#!/usr/bin/env python3
"""
test.py

Usage:
    python test.py /path/to/cmdb.csv

Behavior:
 - Try to import app.services.cmdb_service and run process_cmdb_and_generate() locally.
 - If local import fails, it will attempt to POST the CSV to a running FastAPI server
   at http://localhost:8000/upload-cmdb/ and then call /generate-cmdb-diagram/.
 - Writes resulting PlantUML image into ./static/ and attempts to open it.

Notes:
 - For AI/enrichment features, set OPENAI_API_KEY in the environment.
 - Requires 'requests' for server-mode fallback: pip install requests
"""
from pathlib import Path
import sys
import os
import json
import logging
import webbrowser

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("test.py")

def open_image(path: Path):
    try:
        logger.info(f"Opening image: {path}")
        webbrowser.open(path.as_uri())
    except Exception as e:
        logger.warning(f"Could not open image automatically: {e}. Image saved at: {path}")

def run_local_mode(csv_path: Path, output_dir: Path):
    """
    Attempt to import local cmdb_service and run process_cmdb_and_generate.
    """
    logger.info("Attempting local mode (importing app.services.cmdb_service)...")

    here = Path(__file__).resolve().parent
    candidates = [here, here.parent, here.parent.parent]
    for c in candidates:
        if str(c) not in sys.path:
            sys.path.insert(0, str(c))

    try:
        from app.services.cmdb_service import construct_cmdb_from_file, process_cmdb_and_generate
    except Exception as e:
        logger.info(f"Local import failed: {e}")
        raise

    logger.info(f"Parsing CMDB file: {csv_path}")
    cmdb_items = construct_cmdb_from_file(str(csv_path))
    logger.info(f"Parsed {len(cmdb_items)} items. Running process_cmdb_and_generate...")

    output_dir.mkdir(parents=True, exist_ok=True)

    # >>> Correct place to set the key
    OPENAI_API_KEY = "add your key here"
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  # ensures subprocesses and imported modules can access it
    logger.info("✅ OpenAI API key set in environment for this process.")

    result = process_cmdb_and_generate(cmdb_items=cmdb_items, output_dir=str(output_dir))
    if not result.get("success"):
        raise RuntimeError(f"process_cmdb_and_generate failed: {result.get('error')}")

    img_rel = result.get("plantuml_image")
    if not img_rel:
        raise RuntimeError("No plantuml_image returned from local processing")

    img_name = Path(img_rel).name
    img_path = output_dir / img_name
    if not img_path.exists():
        raise FileNotFoundError(f"Expected image at {img_path} but it does not exist")

    logger.info(f"Diagram generated: {img_path}")
    open_image(img_path)
    return img_path


def run_server_mode(csv_path: Path, output_dir: Path, server_url="http://localhost:8000"):
    """
    Upload CSV to running FastAPI server and request diagram generation.
    """
    logger.info("Attempting server mode (uploading to FastAPI)...")
    try:
        import requests
    except Exception:
        raise RuntimeError("requests library required for server mode. Install it with: pip install requests")

    upload_url = f"{server_url.rstrip('/')}/upload-cmdb/"
    generate_url = f"{server_url.rstrip('/')}/generate-cmdb-diagram/"

    headers = {}
    # Pass OPENAI_API_KEY if present
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        headers["X-OpenAI-API-Key"] = api_key
    else:
        logger.warning("OPENAI_API_KEY not set. Server-side AI features may be skipped or fail.")

    logger.info(f"Uploading CMDB file to {upload_url} ...")
    with open(csv_path, "rb") as f:
        files = {"file": (csv_path.name, f, "text/csv")}
        resp = requests.post(upload_url, headers=headers, files=files, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"Upload failed ({resp.status_code}): {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Upload endpoint returned error: {data}")

    cmdb_items = data.get("cmdb_items") or []
    logger.info(f"Server parsed {len(cmdb_items)} items. Requesting diagram generation...")

    # Call generate endpoint with the parsed/edited cmdb_items
    payload = {"cmdb_items": cmdb_items}
    resp2 = requests.post(generate_url, headers={**headers, "Content-Type": "application/json"}, json=payload, timeout=180)
    if resp2.status_code != 200:
        raise RuntimeError(f"Generate failed ({resp2.status_code}): {resp2.text}")
    gdata = resp2.json()
    if not gdata.get("success"):
        raise RuntimeError(f"Generate returned error: {gdata}")

    img_rel = gdata.get("plantuml_image")
    if not img_rel:
        raise RuntimeError("No plantuml_image returned from server")

    # Download the image to output_dir
    img_url = server_url.rstrip("/") + img_rel if img_rel.startswith("/") else img_rel
    logger.info(f"Downloading generated image from {img_url} ...")
    rimg = requests.get(img_url, timeout=60)
    output_dir.mkdir(parents=True, exist_ok=True)
    img_name = Path(img_rel).name
    img_path = output_dir / img_name
    with open(img_path, "wb") as fh:
        fh.write(rimg.content)

    logger.info(f"Downloaded image to {img_path}")
    open_image(img_path)
    return img_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python test.py /path/to/cmdb.csv")
        sys.exit(1)

    csv_file = Path(sys.argv[1]).expanduser().resolve()
    if not csv_file.exists():
        print(f"File not found: {csv_file}")
        sys.exit(1)

    static_dir = Path("./static").resolve()
    # Try local mode first
    try:
        img_path = run_local_mode(csv_file, static_dir)
        logger.info(f"Local mode succeeded. Image at: {img_path}")
        return
    except Exception as e:
        logger.info(f"Local mode unavailable or failed: {e}")

    # Fallback to server mode
    try:
        img_path = run_server_mode(csv_file, static_dir)
        logger.info(f"Server mode succeeded. Image at: {img_path}")
        return
    except Exception as e:
        logger.error(f"Server mode failed: {e}")
        logger.error("Make sure your FastAPI server is running (uvicorn app.main:app --reload) and OPENAI_API_KEY is set if needed.")
        sys.exit(2)

if __name__ == "__main__":
    main()
