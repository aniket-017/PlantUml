# app/services/csv_service.py
import re
import pandas as pd
import tempfile
import os
import csv
import json
from pathlib import Path
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.csv_tools import CsvTools
from .plantuml_service import render_plantuml_from_text


def _extract_code_block(text: str, lang_hint: str = None) -> str:
    if lang_hint:
        pattern = rf"```{lang_hint}\s*([\s\S]*?)```"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    m = re.search(r"```(?:\w+)?\s*([\s\S]*?)```", text)
    return m.group(1).strip() if m else text.strip()


def _extract_json_from_response(content: str) -> str:
    """Extract JSON from various response formats."""
    content = content.strip()
    
    # Try to extract from code blocks first
    if content.startswith('```'):
        extracted = _extract_code_block(content, lang_hint="json")
        if extracted:
            return extracted
    
    # Look for JSON array pattern
    json_patterns = [
        r'\[[\s\S]*\]',  # Array pattern
        r'\{[\s\S]*\}',  # Object pattern
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(0).strip()
    
    # If no patterns found, return the original content
    return content

def enrich_test_cases_with_ai(test_cases: list, openai_api_key: str = None) -> list:
    """
    Send constructed test cases to GPT so it can analyze the data deeply,
    identify missing test scenarios, and generate comprehensive test cases.
    """
    # Set API key if provided
    if openai_api_key:
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    agent = Agent(
        name="Comprehensive Test Case Analyzer",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "You are a senior QA engineer and test automation expert.",
            "Analyze the provided test cases and the underlying data patterns to generate comprehensive test coverage.",
            "Your task is to:",
            "1. Review existing test cases for completeness and clarity",
            "2. Identify missing test scenarios based on the data patterns",
            "3. Generate additional test cases to ensure full coverage",
            "4. Consider edge cases, boundary conditions, and error scenarios",
            "5. Ensure proper test case structure with: id, title, description, steps, actors, expected",
            "6. Group related test cases logically",
            "7. Include positive, negative, and edge case scenarios",
            "8. Make test cases specific, measurable, and actionable",
            "Return ONLY valid JSON (list of test cases)."
        ],
        markdown=True,
    )

    try:
        # Create a comprehensive analysis prompt
        analysis_prompt = f"""
        Analyze the following test cases and generate a comprehensive test suite:

        EXISTING TEST CASES:
        {json.dumps(test_cases, indent=2)}

        ANALYSIS REQUIREMENTS:
        1. Identify what functionality/features are being tested
        2. Determine what test scenarios are missing
        3. Consider different user roles, system states, and data conditions
        4. Think about integration points, error handling, and edge cases
        5. Ensure test cases cover happy path, alternative paths, and error paths

        GENERATE ADDITIONAL TEST CASES FOR:
        - Boundary value testing
        - Error handling and exception scenarios
        - Different user roles/actors
        - Data validation scenarios
        - Integration points
        - Performance considerations
        - Security aspects (if applicable)
        - User experience flows

        IMPORTANT: Return ONLY a valid JSON array of test cases. Each test case must have:
        - id: string
        - title: string
        - description: string
        - steps: array of objects with step_number, actor, action, expected
        - actors: array of strings
        - expected: string

        Return a comprehensive list of test cases that includes both enhanced versions of existing ones and new test cases to ensure complete coverage.
        """

        resp = agent.run(analysis_prompt)
        print(f"AI Response received: {type(resp)}")
        print(f"Response content length: {len(resp.content) if hasattr(resp, 'content') else 'No content attr'}")
        print(f"Response content preview: {str(resp.content)[:200] if hasattr(resp, 'content') else 'No content'}...")
        
        # Extract content and clean it
        content = resp.content if hasattr(resp, 'content') else str(resp)
        
        # Extract JSON from the response
        content = _extract_json_from_response(content)
        
        # Clean the content
        content = content.strip()
        if not content:
            print("✗ Empty response from AI")
            return test_cases
        
        # Try to parse JSON
        try:
            result = json.loads(content)
            if isinstance(result, list):
                print(f"✓ Successfully parsed {len(result)} test cases from AI response")
                return result
            else:
                print(f"✗ AI response is not a list: {type(result)}")
                return test_cases
        except json.JSONDecodeError as json_err:
            print(f"✗ JSON parsing failed: {json_err}")
            print(f"Raw content: {content[:500]}...")
            # Try to create a simple fallback test case from the AI response
            fallback_tc = {
                "id": "AI_Generated_1",
                "title": "AI Generated Test Case",
                "description": "Test case generated from AI analysis",
                "steps": [{"step_number": 1, "actor": None, "action": content[:200], "expected": "Success"}],
                "actors": [],
                "expected": "Success"
            }
            print("✓ Created fallback test case from AI response")
            return test_cases + [fallback_tc]
            
    except Exception as e:
        print(f"✗ AI enrichment failed: {e}")
        import traceback
        traceback.print_exc()
        return test_cases  # fallback


def _generate_test_cases_from_text(raw_text: str, openai_api_key: str = None) -> list:
    """Use AI to generate comprehensive structured test cases from free-text project description."""
    # Set API key if provided
    if openai_api_key:
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    agent = Agent(
        name="Comprehensive Test Case Synthesizer",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "You are a senior QA engineer and test automation expert.",
            "Given a project design/requirements text, generate comprehensive structured test cases.",
            "Your task is to:",
            "1. Analyze the project description to identify all features and functionalities",
            "2. Identify all possible user roles, actors, and system components",
            "3. Generate test cases covering:",
            "   - Happy path scenarios",
            "   - Alternative path scenarios", 
            "   - Error handling scenarios",
            "   - Edge cases and boundary conditions",
            "   - Integration points",
            "   - Data validation scenarios",
            "   - User experience flows",
            "4. Each test case must have: id, title, description, steps (step_number, actor, action, expected), actors, expected",
            "5. Ensure test cases are specific, measurable, and actionable",
            "6. Group related test cases logically",
            "7. Include both positive and negative test scenarios",
            "Return comprehensive JSON only."
        ],
        markdown=True,
    )

    comprehensive_prompt = f"""
    Generate comprehensive test cases from the following project description:

    PROJECT DESCRIPTION:
    {raw_text}

    REQUIREMENTS:
    1. Identify all features, functionalities, and user flows mentioned
    2. Determine all possible actors (users, systems, external services)
    3. Generate test cases for each identified feature/flow
    4. Include test cases for:
       - Normal operations (happy path)
       - Error conditions and exception handling
       - Edge cases and boundary values
       - Data validation and input validation
       - Integration scenarios
       - User experience and usability
       - Performance considerations
       - Security aspects (if applicable)
    5. Ensure each test case has clear steps with specific actors and expected outcomes
    6. Make test cases detailed enough to be executable

    Return a comprehensive JSON array of test cases.
    """

    try:
        resp = agent.run(comprehensive_prompt)
        print(f"AI Response received: {type(resp)}")
        print(f"Response content length: {len(resp.content) if hasattr(resp, 'content') else 'No content attr'}")
        print(f"Response content preview: {str(resp.content)[:200] if hasattr(resp, 'content') else 'No content'}...")
        
        # Extract content and clean it
        content = resp.content if hasattr(resp, 'content') else str(resp)
        
        # Extract JSON from the response
        content = _extract_json_from_response(content)
        
        # Clean the content
        content = content.strip()
        if not content:
            print("✗ Empty response from AI")
            raise Exception("Empty response from AI")
        
        # Try to parse JSON
        try:
            result = json.loads(content)
            if isinstance(result, list):
                print(f"✓ Successfully parsed {len(result)} test cases from AI response")
                return result
            else:
                print(f"✗ AI response is not a list: {type(result)}")
                raise Exception(f"AI response is not a list: {type(result)}")
        except json.JSONDecodeError as json_err:
            print(f"✗ JSON parsing failed: {json_err}")
            print(f"Raw content: {content[:500]}...")
            # Create a fallback test case from the AI response
            fallback_tc = {
                "id": "AI_Generated_1",
                "title": "AI Generated Test Case",
                "description": "Test case generated from AI analysis",
                "steps": [{"step_number": 1, "actor": None, "action": content[:200], "expected": "Success"}],
                "actors": [],
                "expected": "Success"
            }
            print("✓ Created fallback test case from AI response")
            return [fallback_tc]
            
    except Exception as e:
        print(f"✗ AI test case generation failed: {e}")
        import traceback
        traceback.print_exc()
        # fallback minimal case
        return [{
            "id": "TC_1",
            "title": "Generated test case",
            "description": raw_text,
            "steps": [{"step_number": 1, "actor": None, "action": raw_text, "expected": ""}],
            "actors": [],
            "expected": ""
        }]


def construct_test_cases_from_csv(csv_path: str, openai_api_key: str = None) -> list:
    """
    Build test cases from CSV whether or not it explicitly contains them.
    Handles structured CSVs and free-text single-cell files with comprehensive analysis.
    """
    df = pd.read_csv(csv_path)
    print(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")

    # If the CSV is basically just one big text block, handle with AI
    if df.shape[0] <= 1 and df.shape[1] <= 1:
        raw_text = str(df.iloc[0, 0]) if not df.empty else ""
        if raw_text.strip():
            print("Detected single-cell text content, using AI generation")
            return _generate_test_cases_from_text(raw_text, openai_api_key)

    # Analyze the data structure to understand what we're working with
    print("Analyzing CSV structure...")
    cols_lower_to_actual = {c.lower(): c for c in df.columns}
    
    # Detect potential data patterns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    unique_values_per_col = {col: df[col].nunique() for col in df.columns}
    
    print(f"Numeric columns: {numeric_cols}")
    print(f"Text columns: {text_cols}")
    print(f"Unique values per column: {unique_values_per_col}")

    # Detect grouping column
    candidate_group_cols = ["test_case_id", "test_case", "scenario", "title", "id", "name", "feature"]
    group_col = None
    for cand in candidate_group_cols:
        if cand in cols_lower_to_actual:
            group_col = cols_lower_to_actual[cand]
            break

    # If no explicit grouping column, try to detect patterns
    if not group_col:
        # Look for columns that might group related rows
        for col in df.columns:
            if df[col].nunique() < len(df) * 0.8:  # Column has repeated values
                group_col = col
                print(f"Auto-detected grouping column: {col}")
                break

    test_cases = []
    if group_col:
        print(f"Grouping by column: {group_col}")
        grouped = df.groupby(group_col, sort=False)
        for name, group in grouped:
            steps = []
            actor_col = next(
                (cols_lower_to_actual[c] for c in ["actor", "actors", "user", "role"] if c in cols_lower_to_actual), None
            )
            action_col = next(
                (cols_lower_to_actual[c] for c in ["action", "description", "step_action", "step", "operation"] if c in cols_lower_to_actual), None
            )
            expected_col = next(
                (cols_lower_to_actual[c] for c in ["expected", "expected_result", "result", "outcome"] if c in cols_lower_to_actual), None
            )

            for idx, row in group.iterrows():
                step_data = {
                    "step_number": len(steps) + 1,
                    "actor": row[actor_col] if actor_col else None,
                    "action": row[action_col] if action_col else row.to_dict(),
                    "expected": row[expected_col] if expected_col else "",
                }
                steps.append(step_data)

            actors = sorted({s["actor"] for s in steps if s.get("actor")})
            test_cases.append(
                {
                    "id": str(name),
                    "title": str(name),
                    "description": f"Test case for {name}",
                    "steps": steps,
                    "actors": actors,
                    "expected": "",
                }
            )
    else:
        print("No grouping detected, treating each row as a test case")
        # No grouping — each row = one test case
        for idx, row in df.iterrows():
            # Try to create meaningful test case from row data
            title = str(row[df.columns[0]]) if len(df.columns) > 0 else f"Test Case {idx+1}"
            description = f"Test case based on row {idx+1} data"
            
            # Create steps from all non-null values in the row
            steps = []
            step_num = 1
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    steps.append({
                        "step_number": step_num,
                        "actor": None,
                        "action": f"{col}: {row[col]}",
                        "expected": ""
                    })
                    step_num += 1
            
            if not steps:  # Fallback if no meaningful data
                steps = [{
                    "step_number": 1,
                    "actor": None,
                    "action": row.to_dict(),
                    "expected": ""
                }]

            test_cases.append(
                {
                    "id": f"TC_{idx+1}",
                    "title": title,
                    "description": description,
                    "steps": steps,
                    "actors": [],
                    "expected": "",
                }
            )

    print(f"Generated {len(test_cases)} initial test cases from CSV")
    return test_cases


def _write_test_cases_to_temp_csv(test_cases: list) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8", newline="")
    fieldnames = ["test_case_id", "title", "step_number", "actor", "action", "expected"]
    writer = csv.DictWriter(tmp, fieldnames=fieldnames)
    writer.writeheader()

    for i, tc in enumerate(test_cases, start=1):
        tc_id = tc.get("id", f"TC_{i}")
        title = tc.get("title", "")
        for j, step in enumerate(tc.get("steps", []), start=1):
            action = step.get("action")
            if isinstance(action, (dict, list)):
                action = json.dumps(action, default=str)
            writer.writerow(
                {
                    "test_case_id": tc_id,
                    "title": title,
                    "step_number": j,
                    "actor": step.get("actor", ""),
                    "action": action,
                    "expected": step.get("expected", ""),
                }
            )

    tmp.flush()
    tmp.close()
    return tmp.name


def process_csv_and_generate(csv_path: str = None, output_dir: str = ".", test_cases: list = None) -> dict:
    """
    Accepts either csv_path or test_cases list. Writes a temp CSV, then runs AI → PlantUML.
    """
    import os  # Move import to function level
    tmp_csv_path = None
    try:
        print("=== PROCESS_CSV_AND_GENERATE START ===")
        print(f"Timestamp: {__import__('datetime').datetime.now()}")
        print(f"Output directory: {output_dir}")
        
        if test_cases:
            print(f"Writing {len(test_cases)} test cases to temp CSV...")
            tmp_csv_path = _write_test_cases_to_temp_csv(test_cases)
            print(f"✓ Temp CSV created successfully at: {tmp_csv_path}")
        else:
            print(f"Reading CSV from {csv_path}...")
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as tmp_file:
                df = pd.read_csv(csv_path)
                df.to_csv(tmp_file.name, index=False)
                tmp_csv_path = tmp_file.name
            print(f"✓ CSV processed and temp file created: {tmp_csv_path}")

        print("Initializing CsvTools...")
        try:
            csv_tool = CsvTools(csvs=[tmp_csv_path], read_csvs=True, list_csvs=True, read_column_names=True)
            print("✓ CsvTools initialized successfully")
        except Exception as e:
            print(f"✗ ERROR initializing CsvTools: {str(e)}")
            raise

        print("Checking OpenAI API key...")
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("✗ ERROR: OPENAI_API_KEY environment variable is not set")
            raise Exception("OPENAI_API_KEY environment variable is not set")
        else:
            print(f"✓ OpenAI API key found (length: {len(openai_key)})")
        
        print("Initializing OpenAI model...")
        try:
            model = OpenAIChat(id="gpt-4o-mini")
            print("✓ OpenAI model initialized successfully")
        except Exception as e:
            print(f"✗ ERROR initializing OpenAI model: {str(e)}")
            raise

        print("Creating Agent with tools...")
        try:
            agent = Agent(
                name="Test Case to PlantUML Agent",
                model=model,
                tools=[csv_tool],
                instructions=[
                    "You are an expert at analyzing test cases and creating PlantUML sequence diagrams.",
                    "Examine test case data → identify actors, steps, interactions.",
                    "Return only ```plantuml fenced code```.",
                ],
                markdown=True,
            )
            print("✓ Agent created successfully")
        except Exception as e:
            print(f"✗ ERROR creating Agent: {str(e)}")
            raise

        print("Running AI agent to generate PlantUML...")
        try:
            resp = agent.run("Analyze the test cases and create a PlantUML sequence diagram.")
            print("✓ AI agent response received")
            print(f"Response type: {type(resp)}")
            print(f"Response has content attr: {hasattr(resp, 'content')}")
            
            puml_text_raw = resp.content if hasattr(resp, "content") else str(resp)
            print(f"Raw PlantUML text length: {len(puml_text_raw)}")
            print(f"Raw PlantUML text preview: {puml_text_raw[:200]}...")
        except Exception as e:
            print(f"✗ ERROR during AI agent execution: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

        print("Extracting PlantUML code from response...")
        try:
            plantuml_code = _extract_code_block(puml_text_raw, lang_hint="plantuml")
            print(f"✓ PlantUML code extracted (length: {len(plantuml_code)})")
            print(f"PlantUML code preview: {plantuml_code[:200]}...")
        except Exception as e:
            print(f"✗ ERROR extracting PlantUML code: {str(e)}")
            raise

        print("Rendering PlantUML to image...")
        try:
            img_path = render_plantuml_from_text(plantuml_code, output_dir=output_dir, filename_base="e2e_test_diagram")
            print(f"✓ Image generated successfully at: {img_path}")
        except Exception as e:
            print(f"✗ ERROR rendering PlantUML: {str(e)}")
            raise

        print("Extracting actors and activities...")
        try:
            actors = _extract_actors_from_plantuml(plantuml_code)
            activities = _extract_activities_from_plantuml(plantuml_code)
            print(f"✓ Extracted {len(actors)} actors and {len(activities)} activities")
        except Exception as e:
            print(f"✗ ERROR extracting actors/activities: {str(e)}")
            # Don't fail the whole process for this
            actors = []
            activities = []

        print("=== PROCESS_CSV_AND_GENERATE SUCCESS ===")
        return {
            "success": True,
            "plantuml_code": plantuml_code,
            "plantuml_image": f"/static/{Path(img_path).name}",
            "actors": actors,
            "activities": activities,
        }
    except Exception as e:
        print(f"=== PROCESS_CSV_AND_GENERATE ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("=== PROCESS_CSV_AND_GENERATE ERROR END ===")
        return {"success": False, "error": str(e), "plantuml_code": None, "plantuml_image": None, "actors": [], "activities": []}
    finally:
        if tmp_csv_path and os.path.exists(tmp_csv_path):
            print(f"Cleaning up temp file: {tmp_csv_path}")
            os.unlink(tmp_csv_path)


def _extract_actors_from_plantuml(plantuml_code: str) -> list:
    patterns = [
        r'participant\s+"([^"]+)"', r"participant\s+(\w+)",
        r'actor\s+"([^"]+)"', r"actor\s+(\w+)",
        r'entity\s+"([^"]+)"', r"entity\s+(\w+)",
    ]
    actors = []
    for p in patterns:
        actors.extend(re.findall(p, plantuml_code, re.IGNORECASE))
    return sorted(set(actors))


def _extract_activities_from_plantuml(plantuml_code: str) -> list:
    return [line.strip() for line in plantuml_code.splitlines() if "->" in line and ":" in line]


def refine_plantuml_code(plantuml_code: str, message: str, output_dir: str):
    try:
        agent = Agent(
            name="PlantUML Refiner",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Modify the provided PlantUML code according to user request.",
                "Return ONLY fenced ```plantuml code```.",
            ],
            markdown=True,
        )
        resp = agent.run(f"```plantuml\n{plantuml_code}\n```\n\nUser request: {message}")
        updated_code = _extract_code_block(resp.content, lang_hint="plantuml")
        img_path = render_plantuml_from_text(updated_code, output_dir=output_dir, filename_base="e2e_test_diagram")

        return {
            "success": True,
            "plantuml_code": updated_code,
            "plantuml_image": f"/static/{Path(img_path).name}",
            "actors": _extract_actors_from_plantuml(updated_code),
            "activities": _extract_activities_from_plantuml(updated_code),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "plantuml_code": None, "plantuml_image": None, "actors": [], "activities": []}