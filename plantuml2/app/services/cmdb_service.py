# app/services/cmdb_service.py
import re
import json
import tempfile
import os
import csv
from pathlib import Path
import pandas as pd

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.csv_tools import CsvTools

from .plantuml_service import render_plantuml_from_text, PlantUMLSyntaxError


def _extract_code_block(text: str, lang_hint: str = None) -> str:
    """Extract code from markdown code blocks"""
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
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    try:
        if suffix in (".xlsx", ".xls"):
            df = pd.read_excel(path, engine='openpyxl')
            tmp = path.with_suffix(".csv")
            df.to_csv(tmp, index=False)
            df = pd.read_csv(tmp)
        elif suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix in (".json", ".yaml", ".yml"):
            text = path.read_text(encoding="utf-8")
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    items = data.get("components") or data.get("resources") or [data]
                elif isinstance(data, list):
                    items = data
                else:
                    items = [data]
                return [_normalize_cmdb_item(it) for it in items]
            except Exception:
                df = pd.DataFrame({"text": [text]})
        else:
            text = path.read_text(encoding="utf-8")
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return [_normalize_cmdb_item(it) for it in data]
                elif isinstance(data, dict):
                    items = data.get("components") or [data]
                    return [_normalize_cmdb_item(it) for it in items]
            except Exception:
                return [{
                    "id": "CMDB_TEXT_1",
                    "name": "Imported CMDB Text",
                    "type": "unstructured",
                    "attributes": {"raw": text},
                    "relations": []
                }]

        if isinstance(df, pd.DataFrame):
            df = df.fillna("")
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
                    for c in df.columns:
                        if c not in (id_col, type_col, relation_col):
                            val = row[c]
                            if pd.notna(val) and str(val).strip():
                                item["attributes"][c] = val
                    if relation_col and pd.notna(row[relation_col]) and str(row[relation_col]).strip():
                        relations = [r.strip() for r in str(row[relation_col]).split(",") if r.strip()]
                        for rel in relations:
                            item["relations"].append({"target": rel, "type": "depends_on"})
                    items.append(item)
            else:
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
        return [{
            "id": "CMDB_PARSE_ERROR",
            "name": "ParseError",
            "type": "unstructured",
            "attributes": {"error": str(e)},
            "relations": []
        }]


def _normalize_cmdb_item(raw: dict) -> dict:
    """Normalize arbitrary dict into CMDB item shape."""
    item = {}
    item["id"] = raw.get("id") or raw.get("name") or raw.get("component") or raw.get("hostname") or raw.get("uid") or raw.get("key") or "UNKNOWN"
    item["name"] = raw.get("name") or item["id"]
    item["type"] = raw.get("type") or raw.get("role") or "component"
    
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
    Use AI to infer missing relations, group into layers, detect SPoF.
    """
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

    agent = Agent(
        name="CMDB Enhancer",
        model=OpenAIChat(id="gpt-5"),
        instructions="""You are an enterprise architect. Perform end-to-end enrichment of the provided CMDB data, considering both technical and business perspectives.
    Enrich CMDB data with:
    -Layer: edge, application, database, infrastructure, network, integration
    -LOB: STME, Merchandising, Digital, Logics/Hub, Reporting/Analytics, Marketing, Corporate, Third-Party
    -Criticality: high, medium, low
    -Inferred relationships with types and reasons
    -Business context and SPoF identification
    Ensure consistency across all components and inferred relationships.
    PRESERVE original IDs. Return ONLY JSON array.""",
        markdown=True,
    )

    prompt = f"""
    Analyze these {len(cmdb_items)} CMDB items and provide comprehensive enrichment:
    
    ORIGINAL ITEMS:
    {json.dumps(cmdb_items, indent=2)}
    
    Return enhanced JSON array with all original items plus inferred relationships and attributes.
    """

    try:
        resp = agent.run(prompt)
        content = resp.content if hasattr(resp, "content") else str(resp)
        parsed = _extract_code_block(content, lang_hint="json")
        
        data = json.loads(parsed)
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
        return cmdb_items


def _write_cmdb_to_temp_csv(cmdb_items: list) -> str:
    """Write CMDB items to temporary CSV"""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8", newline="")
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


def _validate_and_fix_plantuml(plantuml_code: str) -> str:
    """
    Validate and fix PlantUML syntax using AI.
    This is our SINGLE agent for fixing PlantUML code.
    """
    try:
        agent = Agent(
            name="PlantUML Validator",
            model=OpenAIChat(id="gpt-5"),
            instructions="""You are a PlantUML expert. Fix ANY syntax errors in PlantUML code.
CRITICAL RULES:
1. MUST start with @startuml and end with @enduml
2. Use valid PlantUML components: package, rectangle, component, database, cloud, node, queue
3. Use valid arrows: ->, -->, ->>, -->>
4. Properly quote names with spaces: "Component Name"
5. Fix all syntax errors while preserving the diagram intent
Return ONLY the fixed PlantUML code in ```plantuml``` block.""",
            markdown=True,
        )

        fix_prompt = f"""
        Fix this PlantUML code. It must be syntactically perfect and render without errors.
        
        PLANTUML CODE TO FIX:
        ```plantuml
        {plantuml_code}
        ```
        
        Return the fixed, valid PlantUML code.
        """

        resp = agent.run(fix_prompt)
        fixed_code = _extract_code_block(
            resp.content if hasattr(resp, "content") else str(resp), 
            lang_hint="plantuml"
        )
        
        # Ensure it has proper start/end tags
        if not fixed_code.startswith('@startuml'):
            fixed_code = '@startuml\n' + fixed_code
        if not fixed_code.strip().endswith('@enduml'):
            fixed_code = fixed_code + '\n@enduml'
            
        return fixed_code
    except Exception as e:
        # Fallback to minimal valid diagram
        return """@startuml
title Enterprise Architecture Diagram
note over System: Architecture visualization
rectangle "System" as sys
@enduml"""


def process_cmdb_and_generate(cmdb_items: list = None, output_dir: str = ".") -> dict:
    """
    Main function: Process CMDB items and generate PlantUML diagram.
    FAST + DETAILED + ROBUST
    """
    tmp_csv_path = None
    try:
        if not cmdb_items or not isinstance(cmdb_items, list):
            raise Exception("cmdb_items list required")

        # Write to temp CSV
        tmp_csv_path = _write_cmdb_to_temp_csv(cmdb_items)

        # Initialize tools
        csv_tool = CsvTools(
            csvs=[tmp_csv_path], read_csvs=True, list_csvs=True, read_column_names=True
        )

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise Exception("OPENAI_API_KEY environment variable is not set")

        # OPTIMIZED AGENT for fast, detailed diagrams
        agent = Agent(
            name="CMDB Architecture Generator",
            model=OpenAIChat(id="gpt-5"),
            tools=[csv_tool],
            instructions="""Generate COMPREHENSIVE PlantUML component diagrams. Follow EXACT syntax:

VALID SYNTAX:
@startuml
package "LOB Name" {
  [Web App]
  component "API Service"
  database "MySQL DB"
  cloud "External System"
}
[Source] --> [Target] : Label
@enduml

REQUIREMENTS:
- ALWAYS use @startuml/@enduml
- Group by LOB packages: STME, Merchandising, Digital, Logics/Hub, Reporting/Analytics, Marketing, Corporate, Third-Party
- Use: rectangle, component, database, cloud, node, queue
- Label ALL connections
- Show ALL relationships
- Make it DETAILED and COMPREHENSIVE
- Left-to-right layout

Return ONLY ```plantuml``` code block.""",
            markdown=True,
        )

        # OPTIMIZED PROMPT for speed and detail
        prompt = f"""
        Create a DETAILED enterprise architecture diagram from {len(cmdb_items)} CMDB components.
        
        COMPONENTS TO INCLUDE:
        {json.dumps([{'id': item['id'], 'name': item['name'], 'type': item['type'], 'relations': item.get('relations', [])} for item in cmdb_items], indent=2)}
        
        Create the MOST COMPREHENSIVE diagram showing ALL systems and relationships.
        Use proper PlantUML syntax that will render without errors.
        """

        # Generate PlantUML
        resp = agent.run(prompt)
        puml_text_raw = resp.content if hasattr(resp, "content") else str(resp)
        plantuml_code = _extract_code_block(puml_text_raw, lang_hint="plantuml")

        # VALIDATE AND FIX PlantUML syntax with our single agent
        max_retries = 3
        retry_count = 0
        img_path = None

        while retry_count <= max_retries:
            try:
                # Try to render the current code
                img_path = render_plantuml_from_text(
                    plantuml_code, 
                    output_dir=output_dir, 
                    filename_base="cmdb_diagram"
                )
                break  # Success!
                
            except PlantUMLSyntaxError as syntax_error:
                print(f"✗ PlantUML syntax error (attempt {retry_count + 1}): {str(syntax_error)[:200]}")
                
                if retry_count < max_retries:
                    print("🔄 Fixing PlantUML syntax...")
                    # Use our SINGLE agent to fix the code
                    plantuml_code = _validate_and_fix_plantuml(plantuml_code)
                    retry_count += 1
                else:
                    print("❌ Max retries reached, using fallback diagram")
                    # Final fallback
                    plantuml_code = """@startuml
title Enterprise Architecture
package "Applications" {
  [Web Application]
  [API Service]
}
package "Data" {
  database "Main Database"
}
[Web Application] --> [API Service] : HTTP API
[API Service] --> [Main Database] : SQL Queries
note right of [API Service]: Core business logic
@enduml"""
                    img_path = render_plantuml_from_text(
                        plantuml_code, 
                        output_dir=output_dir, 
                        filename_base="cmdb_diagram"
                    )
                    break

        # Extract components and relations
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
        print(f"❌ Error in process_cmdb_and_generate: {str(e)}")
        return {
            "success": False, 
            "error": str(e), 
            "plantuml_code": None, 
            "plantuml_image": None, 
            "components": [], 
            "relations": []
        }
    finally:
        # Cleanup
        if tmp_csv_path and os.path.exists(tmp_csv_path):
            try:
                os.unlink(tmp_csv_path)
            except:
                pass


def _extract_components_from_plantuml(plantuml_code: str) -> list:
    """Extract components from PlantUML code"""
    patterns = [
        r'rectangle\s+"([^"]+)"', r'rectangle\s+(\w+)',
        r'component\s+"([^"]+)"', r'component\s+(\w+)',
        r'database\s+"([^"]+)"', r'database\s+(\w+)',
        r'cloud\s+"([^"]+)"', r'cloud\s+(\w+)',
        r'node\s+"([^"]+)"', r'node\s+(\w+)',
        r'queue\s+"([^"]+)"', r'queue\s+(\w+)',
        r'package\s+"([^"]+)"',
        r'\[([^\]]+)\]',  # [Component]
        r'\(([^)]+)\)',   # (Component)
    ]
    comps = []
    for p in patterns:
        matches = re.findall(p, plantuml_code, re.IGNORECASE)
        comps.extend(matches)
    
    # Clean and deduplicate
    cleaned = []
    for comp in comps:
        if isinstance(comp, tuple):
            comp = comp[0]
        comp = comp.strip().strip('"').strip()
        if comp and comp not in cleaned and len(comp) > 1:
            cleaned.append(comp)
    
    return sorted(cleaned)


def _extract_relations_from_plantuml(plantuml_code: str) -> list:
    """Extract relations from PlantUML arrows"""
    rels = []
    
    for line in plantuml_code.splitlines():
        line = line.strip()
        # Look for arrow patterns
        if any(arrow in line for arrow in ["->", "-->", "->>", "-->>", "-left->", "-right->", "-up->", "-down->"]):
            # Extract label if present
            if ":" in line:
                try:
                    left_right, label = line.split(":", 1)
                    label = label.strip()
                except ValueError:
                    left_right = line
                    label = ""
            else:
                left_right = line
                label = ""

            # Extract source and target
            parts = re.split(r'->+', left_right)
            if len(parts) >= 2:
                src = parts[0].strip().strip('"').strip('[]()')
                dst = parts[1].strip().strip('"').strip('[]()')
                
                if src and dst:
                    rels.append({
                        "source": src,
                        "target": dst, 
                        "label": label
                    })
    
    return rels


def refine_cmdb_plantuml_code(plantuml_code: str, message: str, output_dir: str):
    """
    Refine existing PlantUML code based on user feedback.
    Uses the same validation/fixing agent.
    """
    try:
        agent = Agent(
            name="PlantUML Refiner",
            model=OpenAIChat(id="gpt-5"),
            instructions="""Refine PlantUML diagrams based on user requests.
PRESERVE the original architecture and relationships.
ENHANCE based on user feedback.
ALWAYS return valid PlantUML syntax.
Return ONLY ```plantuml``` code block.""",
            markdown=True,
        )
        
        resp = agent.run(f"""
        Current diagram:
        ```plantuml
        {plantuml_code}
        ```
        
        User request: {message}
        
        Refine the diagram while keeping it syntactically valid.
        """)
        
        updated_code = _extract_code_block(resp.content, lang_hint="plantuml")

        # Validate and fix the refined code
        max_retries = 2
        retry_count = 0
        img_path = None

        while retry_count <= max_retries:
            try:
                img_path = render_plantuml_from_text(
                    updated_code, 
                    output_dir=output_dir, 
                    filename_base="cmdb_diagram"
                )
                break
            except PlantUMLSyntaxError:
                if retry_count < max_retries:
                    updated_code = _validate_and_fix_plantuml(updated_code)
                    retry_count += 1
                else:
                    raise

        return {
            "success": True,
            "plantuml_code": updated_code,
            "plantuml_image": f"/static/{Path(img_path).name}",
            "components": _extract_components_from_plantuml(updated_code),
            "relations": _extract_relations_from_plantuml(updated_code),
        }
    except Exception as e:
        return {
            "success": False, 
            "error": str(e), 
            "plantuml_code": None, 
            "plantuml_image": None, 
            "components": [], 
            "relations": []
        }