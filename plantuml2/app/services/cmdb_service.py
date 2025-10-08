# app/services/cmdb_service.py
import re
import json
import tempfile
import os
import csv
from pathlib import Path
import pandas as pd

# Reuse the same agent/tooling if available in your project (phi.Agent + OpenAIChat)
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.csv_tools import CsvTools

from .plantuml_service import render_plantuml_from_text, PlantUMLSyntaxError

def _extract_code_block(text: str, lang_hint: str = None) -> str:
    if lang_hint:
        pattern = rf"```{lang_hint}\s*([\s\S]*?)```"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    m = re.search(r"```(?:\w+)?\s*([\s\S]*?)```", text)
    return m.group(1).strip() if m else text.strip()

def construct_cmdb_from_file(file_path: str) -> list:
    """
    Parse a CMDB file and return structured items.
    Accepts CSV, Excel, JSON, YAML, or single-cell free-text JSON/YAML.
    Output: list of dicts with keys like id/name, type, attributes, relations (if present).
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    try:
        if suffix in (".xlsx", ".xls"):
            df = pd.read_excel(path)
            tmp = path.with_suffix(".csv")
            df.to_csv(tmp, index=False)
            df = pd.read_csv(tmp)
        elif suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix in (".json", ".yaml", ".yml"):
            # Attempt to read JSON / YAML into list
            text = path.read_text(encoding="utf-8")
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    # attempt to find top-level components
                    items = data.get("components") or data.get("resources") or [data]
                elif isinstance(data, list):
                    items = data
                else:
                    items = [data]
                # Normalize into list of dicts
                return [_normalize_cmdb_item(it) for it in items]
            except Exception:
                # fallback to treating file as text
                df = pd.DataFrame({"text": [text]})
        else:
            # Unknown type -> try to load as single-cell text
            text = path.read_text(encoding="utf-8")
            # if looks like JSON, try parse
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return [_normalize_cmdb_item(it) for it in data]
                elif isinstance(data, dict):
                    items = data.get("components") or [data]
                    return [_normalize_cmdb_item(it) for it in items]
            except Exception:
                # fallback: create one item with raw text
                return [{
                    "id": "CMDB_TEXT_1",
                    "name": "Imported CMDB Text",
                    "type": "unstructured",
                    "attributes": {"raw": text},
                    "relations": []
                }]

        # If we have a DataFrame, try to infer columns
        if isinstance(df, pd.DataFrame):
            df = df.fillna("")
            # common columns
            lower_cols = {c.lower(): c for c in df.columns}
            id_col = lower_cols.get("id") or lower_cols.get("name") or lower_cols.get("component") or None
            type_col = lower_cols.get("type") or lower_cols.get("role")
            relation_col = lower_cols.get("depends_on") or lower_cols.get("depends") or lower_cols.get("relationship")
            items = []
            if id_col:
                for _, row in df.iterrows():
                    item = {
                        "id": str(row[id_col]),
                        "name": str(row[id_col]),
                        "type": str(row[type_col]) if type_col else "component",
                        "attributes": {},
                        "relations": []
                    }
                    # capture remaining columns as attributes
                    for c in df.columns:
                        if c not in (id_col, type_col, relation_col):
                            val = row[c]
                            if pd.notna(val) and str(val).strip():
                                item["attributes"][c] = val
                    if relation_col and pd.notna(row[relation_col]) and str(row[relation_col]).strip():
                        # allow comma-separated relations
                        relations = [r.strip() for r in str(row[relation_col]).split(",") if r.strip()]
                        for rel in relations:
                            item["relations"].append({"target": rel, "type": "depends_on"})
                    items.append(item)
            else:
                # no clear id column: create items per row with enumerated ids
                for idx, row in df.iterrows():
                    item = {
                        "id": f"CMDB_ROW_{idx+1}",
                        "name": f"Row {idx+1}",
                        "type": "component",
                        "attributes": {},
                        "relations": []
                    }
                    for c in df.columns:
                        val = row[c]
                        if pd.notna(val) and str(val).strip():
                            item["attributes"][c] = val
                    items.append(item)
            return items

    except Exception as e:
        # Fallback: return a single raw item
        return [{
            "id": "CMDB_PARSE_ERROR",
            "name": "ParseError",
            "type": "unstructured",
            "attributes": {"error": str(e)},
            "relations": []
        }]

def _normalize_cmdb_item(raw: dict) -> dict:
    """
    Normalize arbitrary dict into CMDB item shape.
    """
    item = {}
    item["id"] = raw.get("id") or raw.get("name") or raw.get("component") or raw.get("hostname") or raw.get("uid") or raw.get("key") or "UNKNOWN"
    item["name"] = raw.get("name") or item["id"]
    item["type"] = raw.get("type") or raw.get("role") or "component"
    # attributes: keep everything except relations
    attributes = {}
    relations = []
    for k, v in raw.items():
        if k.lower() in ("depends_on", "depends", "relations", "relation", "links", "connected_to"):
            if isinstance(v, list):
                for t in v:
                    relations.append({"target": t, "type": "depends_on"})
            elif isinstance(v, str):
                for t in v.split(","):
                    if t.strip():
                        relations.append({"target": t.strip(), "type": "depends_on"})
        elif k.lower() not in ("id", "name", "type", "role"):
            attributes[k] = v
    item["attributes"] = attributes
    item["relations"] = relations
    return item

def enrich_cmdb_with_ai(cmdb_items: list, openai_api_key: str = None) -> list:
    """
    Use AI to infer missing relations, group into layers (frontend/backend/db), detect SOG (single points of failure),
    and return augmented list of items. MUST keep all original items intact.
    """
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

    agent = Agent(
        name="CMDB Enhancer",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "You are a system architect and infrastructure engineer.",
            "Given CMDB items (components), infer missing relationships, group components into logical layers (edge, app, data, infra), detect potential single points of failure, and provide normalized CMDB JSON.",
            "CRITICAL: Keep ALL original items (do not remove or rename original ids). Add inferred relations or new auxiliary items if required, prefix new item ids with NEW_ if you generate them.",
            "Output: Return ONLY valid JSON array of items with keys: id, name, type, attributes, relations (relations: [{target, type, reason}])",
        ],
        markdown=True,
    )

    prompt = f"""
    You are given {len(cmdb_items)} CMDB item(s). Preserve all originals and add inferred items/relations.
    ORIGINAL ITEMS (JSON):
    {json.dumps(cmdb_items, indent=2)}
    Requirements:
    - Keep original ids unchanged.
    - Add inferred relations as relations entries with 'target' and optional 'reason'.
    - Group each item into a 'layer' attribute inside attributes (one of: edge, application, database, infrastructure, network, other).
    - Add notes about single points of failure as attributes.spoF (if found).
    Return ONLY valid JSON array.
    """

    try:
        resp = agent.run(prompt)
        content = resp.content if hasattr(resp, "content") else str(resp)
        # extract JSON if in codeblock
        parsed = _extract_code_block(content, lang_hint="json")
        try:
            data = json.loads(parsed)
            # Ensure originals are included; if not present, append them
            original_ids = {it.get("id") for it in cmdb_items}
            result_ids = {it.get("id") for it in data}
            missing = original_ids - result_ids
            if missing:
                for m in missing:
                    orig = next((it for it in cmdb_items if it.get("id") == m), None)
                    if orig:
                        data.append(orig)
            return data
        except Exception:
            # fallback: return original plus one item summarizing AI content
            return cmdb_items + [{
                "id": "AI_ENRICH_FALLBACK",
                "name": "AI Enrichment Fallback",
                "type": "note",
                "attributes": {"note": parsed[:1000]},
                "relations": []
            }]
    except Exception as e:
        # On any error, return original
        return cmdb_items

def _write_cmdb_to_temp_csv(cmdb_items: list) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8", newline="")
    fieldnames = ["id", "name", "type", "attributes", "relations"]
    writer = csv.DictWriter(tmp, fieldnames=fieldnames)
    writer.writeheader()
    for it in cmdb_items:
        writer.writerow({
            "id": it.get("id"),
            "name": it.get("name"),
            "type": it.get("type"),
            "attributes": json.dumps(it.get("attributes", {}), ensure_ascii=False),
            "relations": json.dumps(it.get("relations", []), ensure_ascii=False),
        })
    tmp.flush()
    tmp.close()
    return tmp.name

def process_cmdb_and_generate(cmdb_items: list = None, output_dir: str = ".") -> dict:
    """
    Accepts cmdb_items (list). Writes a temp CSV and runs an AI agent to generate PlantUML architecture diagram.
    Returns plantuml_code, image (URL), components, relationships.
    """
    tmp_csv_path = None
    try:
        if not cmdb_items or not isinstance(cmdb_items, list):
            raise Exception("cmdb_items list required")

        tmp_csv_path = _write_cmdb_to_temp_csv(cmdb_items)

        # Require OPENAI_API_KEY env var
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise Exception("OPENAI_API_KEY environment variable is not set")

        model = OpenAIChat(id="gpt-4o-mini")

        # Wrap CSV as tool for agent
        csv_tool = CsvTools(csvs=[tmp_csv_path], read_csvs=True, list_csvs=True, read_column_names=True)

        agent = Agent(
            name="CMDB to PlantUML Agent",
            model=model,
            tools=[csv_tool],
            instructions=[
                "You are an expert system architect. Using the CMDB data, create a PlantUML diagram that shows components and relations.",
                "Use ONLY standard PlantUML syntax: @startuml, component, node, database, package, rectangle, @enduml.",
                "Do NOT use !define statements or custom macros.",
                "Use proper PlantUML component diagram syntax with clear component names and relationships.",
                "Return ONLY a fenced ```plantuml``` block (no extra text)."
            ],
            markdown=True,
        )

        resp = agent.run("Analyze the CMDB CSV and create a PlantUML architecture diagram (component/deployment).")
        puml_text_raw = resp.content if hasattr(resp, "content") else str(resp)

        plantuml_code = _extract_code_block(puml_text_raw, lang_hint="plantuml")

        # attempt render with retries & auto-fix syntax
        max_retries = 2
        retry_count = 0
        img_path = None
        while retry_count <= max_retries:
            try:
                img_path = render_plantuml_from_text(plantuml_code, output_dir=output_dir, filename_base="cmdb_diagram")
                break
            except PlantUMLSyntaxError as syntax_error:
                if retry_count < max_retries:
                    # simple fix attempt: ask agent to repair the plantuml (reuse same agent style)
                    repair_agent = Agent(
                        name="PlantUML Fixer for CMDB",
                        model=model,
                        instructions=[
                            "You are an expert in PlantUML. Fix the provided PlantUML code to be valid while preserving intent.",
                            "Use ONLY standard PlantUML syntax: @startuml, component, node, database, package, rectangle, @enduml.",
                            "Do NOT use !define statements, custom macros, or complex syntax.",
                            "Keep component names simple and avoid special characters in names.",
                            "Use proper PlantUML component diagram syntax.",
                            "Return ONLY valid PlantUML code in ```plantuml``` fenced block."
                        ],
                        markdown=True,
                    )
                    fix_prompt = f"""
                    ERROR: {str(syntax_error)[:500]}
                    INVALID CODE:
                    ```plantuml
                    {plantuml_code}
                    ```
                    Please fix and return valid PlantUML.
                    """
                    resp_fix = repair_agent.run(fix_prompt)
                    plantuml_code = _extract_code_block(resp_fix.content if hasattr(resp_fix, "content") else str(resp_fix), lang_hint="plantuml")
                    retry_count += 1
                else:
                    # Final fallback: create a simple valid PlantUML
                    plantuml_code = _create_fallback_plantuml(cmdb_items)
                    try:
                        img_path = render_plantuml_from_text(plantuml_code, output_dir=output_dir, filename_base="cmdb_diagram")
                        break
                    except Exception:
                        raise syntax_error

        if not img_path:
            raise Exception("Failed to generate PlantUML image after retries")

        components = _extract_components_from_plantuml(plantuml_code)
        relations = _extract_relations_from_plantuml(plantuml_code)

        return {
            "success": True,
            "plantuml_code": plantuml_code,
            "plantuml_image": f"/static/{Path(img_path).name}",
            "components": components,
            "relations": relations,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "plantuml_code": None, "plantuml_image": None, "components": [], "relations": []}
    finally:
        if tmp_csv_path and os.path.exists(tmp_csv_path):
            os.unlink(tmp_csv_path)

def _create_fallback_plantuml(cmdb_items: list) -> str:
    """
    Create a simple, valid PlantUML diagram as fallback when AI generation fails.
    """
    lines = ["@startuml"]
    
    # Add components
    for item in cmdb_items[:10]:  # Limit to first 10 items
        name = item.get("name", item.get("id", "Component"))
        item_type = item.get("type", "component").lower()
        
        # Clean name for PlantUML
        clean_name = re.sub(r'[^\w\s-]', '', name).strip()
        if not clean_name:
            clean_name = f"Component_{item.get('id', '1')}"
        
        if item_type in ["database", "db"]:
            lines.append(f'database "{clean_name}" as {clean_name.replace(" ", "_")}')
        elif item_type in ["service", "api", "microservice"]:
            lines.append(f'component "{clean_name}" as {clean_name.replace(" ", "_")}')
        else:
            lines.append(f'component "{clean_name}" as {clean_name.replace(" ", "_")}')
    
    # Add simple relationships
    for i, item in enumerate(cmdb_items[:5]):  # Limit relationships
        relations = item.get("relations", [])
        if relations and i < len(relations):
            rel = relations[0]
            target = rel.get("target", "")
            if target:
                clean_target = re.sub(r'[^\w\s-]', '', target).strip().replace(" ", "_")
                clean_source = re.sub(r'[^\w\s-]', '', item.get("name", item.get("id", "Component"))).strip().replace(" ", "_")
                if clean_source and clean_target:
                    lines.append(f'{clean_source} --> {clean_target}')
    
    lines.append("@enduml")
    return "\n".join(lines)

def _extract_components_from_plantuml(plantuml_code: str) -> list:
    patterns = [
        r'component\s+"([^"]+)"', r'node\s+"([^"]+)"', r'database\s+"([^"]+)"', r'container\s+"([^"]+)"',
        r'component\s+(\w+)', r'node\s+(\w+)', r'database\s+(\w+)'
    ]
    comps = []
    for p in patterns:
        comps.extend(re.findall(p, plantuml_code, re.IGNORECASE))
    return sorted(set([c.strip() for c in comps]))

def _extract_relations_from_plantuml(plantuml_code: str) -> list:
    rels = []
    for line in plantuml_code.splitlines():
        if "->" in line or "-->" in line or "<--" in line:
            # naive parse
            parts = line.split()
            # try to find left and right and optional label after ':'
            if ":" in line:
                try:
                    left_right, label = line.split(":", 1)
                except ValueError:
                    left_right = line
                    label = ""
            else:
                left_right = line
                label = ""
            tokens = left_right.strip().split()
            if len(tokens) >= 3:
                src = tokens[0].strip().strip('"')
                dst = tokens[-1].strip().strip('"')
                rels.append({"source": src, "target": dst, "label": label.strip()})
    return rels

def refine_cmdb_plantuml_code(plantuml_code: str, message: str, output_dir: str):
    """
    Like refine_plantuml_code but tailored for CMDB diagrams: asks AI to update PlantUML and tries to render.
    """
    try:
        model = OpenAIChat(id="gpt-4o-mini")
        agent = Agent(
            name="CMDB PlantUML Refiner",
            model=model,
            instructions=[
                "Modify the provided PlantUML per user request. Output ONLY a fenced ```plantuml``` block.",
                "Use ONLY standard PlantUML syntax: @startuml, component, node, database, package, rectangle, @enduml.",
                "Do NOT use !define statements, custom macros, or complex syntax.",
                "Keep component names simple and avoid special characters in names.",
                "Use proper PlantUML component diagram syntax.",
            ],
            markdown=True,
        )
        resp = agent.run(f"```plantuml\n{plantuml_code}\n```\n\nUser request: {message}")
        updated_code = _extract_code_block(resp.content if hasattr(resp, "content") else str(resp), lang_hint="plantuml")

        # Render and retry with basic AI fix if necessary
        max_retries = 2
        retry_count = 0
        img_path = None
        while retry_count <= max_retries:
            try:
                img_path = render_plantuml_from_text(updated_code, output_dir=output_dir, filename_base="cmdb_diagram")
                break
            except PlantUMLSyntaxError as syntax_error:
                if retry_count < max_retries:
                    # attempt automated fix
                    fix_agent = Agent(
                        name="PlantUML Fixer",
                        model=model,
                        instructions=[
                            "Fix the PlantUML code so it is syntactically correct. Return ONLY ```plantuml``` code block.",
                            "Use ONLY standard PlantUML syntax: @startuml, component, node, database, package, rectangle, @enduml.",
                            "Do NOT use !define statements, custom macros, or complex syntax.",
                            "Keep component names simple and avoid special characters in names.",
                            "Use proper PlantUML component diagram syntax."
                        ],
                        markdown=True,
                    )
                    resp_fix = fix_agent.run(f"ERROR: {str(syntax_error)[:300]}\n\nCode:\n```plantuml\n{updated_code}\n```")
                    updated_code = _extract_code_block(resp_fix.content if hasattr(resp_fix, "content") else str(resp_fix), lang_hint="plantuml")
                    retry_count += 1
                else:
                    raise syntax_error

        return {
            "success": True,
            "plantuml_code": updated_code,
            "plantuml_image": f"/static/{Path(img_path).name}",
            "components": _extract_components_from_plantuml(updated_code),
            "relations": _extract_relations_from_plantuml(updated_code),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "plantuml_code": None, "plantuml_image": None, "components": [], "relations": []}
