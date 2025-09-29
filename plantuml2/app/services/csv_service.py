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
from .plantuml_service import render_plantuml_from_text, PlantUMLSyntaxError


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
    Analyze user-provided test cases, understand the flow, and return a comprehensive test suite.
    
    The function will:
    1. Keep ALL original user-provided test cases (mandatory)
    2. Understand the logical flow and sequence of operations
    3. Reorder test cases to follow a logical execution flow
    4. Add new test cases to fill gaps in coverage
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
            "CRITICAL REQUIREMENTS:",
            "1. MUST include ALL original user-provided test cases in your output (do not remove or skip any)",
            "2. Analyze and understand the logical flow from the provided test cases",
            "3. Reorder the test cases to follow a logical execution sequence (setup → happy path → alternatives → error cases → teardown)",
            "4. Add NEW test cases to fill gaps in coverage, but keep ALL original ones",
            "5. Ensure proper test case structure with: id, title, description, steps, actors, expected",
            "6. Make test cases specific, measurable, and actionable",
            "7. Include positive, negative, and edge case scenarios",
            "Return ONLY valid JSON (list of test cases) that includes ALL original test cases plus any new ones you generate."
        ],
        markdown=True,
    )

    try:
        # Create a comprehensive analysis prompt
        analysis_prompt = f"""
        You are given {len(test_cases)} test case(s) from the user's CSV file.
        
        YOUR TASK:
        1. **UNDERSTAND THE FLOW**: Analyze these test cases to understand the application/system flow and behavior
        2. **KEEP ALL ORIGINAL TEST CASES**: You MUST include ALL {len(test_cases)} original test cases in your response
        3. **LOGICAL SEQUENCING**: Reorder the test cases in a logical flow that makes sense for execution:
           - Setup/Prerequisites first
           - Happy path scenarios
           - Alternative flows
           - Error/Exception scenarios
           - Cleanup/Teardown
        4. **ADD MISSING TEST CASES**: Identify gaps in coverage and add NEW test cases to ensure comprehensive testing

        ORIGINAL TEST CASES PROVIDED BY USER:
        {json.dumps(test_cases, indent=2)}

        FLOW ANALYSIS GUIDELINES:
        - Identify the main user journey or system workflow
        - Understand dependencies between test cases
        - Identify which tests should run first (prerequisites)
        - Group related test cases together
        - Consider the logical order of operations in the system

        ADDITIONAL TEST CASES TO CONSIDER:
        - Setup and initialization scenarios
        - Boundary value testing
        - Error handling and exception scenarios
        - Different user roles/actors
        - Data validation scenarios
        - Integration points between components
        - Edge cases and corner cases
        - Negative testing scenarios
        - Cleanup and teardown scenarios

        OUTPUT REQUIREMENTS:
        Return ONLY a valid JSON array with:
        - ALL {len(test_cases)} original test cases (with their original IDs preserved)
        - Any NEW test cases you generate (give them unique IDs like "NEW_TC_001", "NEW_TC_002", etc.)
        - Test cases ordered in logical execution sequence
        
        Each test case must have:
        - id: string (keep original IDs for user test cases, create new IDs for generated ones)
        - title: string
        - description: string
        - steps: array of objects with step_number, actor, action, expected
        - actors: array of strings
        - expected: string

        CRITICAL: Do NOT skip or remove any of the original {len(test_cases)} test case(s). All must be present in your output.
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
                
                # Validate that all original test cases are included
                original_ids = {tc.get('id') for tc in test_cases}
                result_ids = {tc.get('id') for tc in result}
                missing_ids = original_ids - result_ids
                
                if missing_ids:
                    print(f"⚠ WARNING: {len(missing_ids)} original test case(s) missing from AI response: {missing_ids}")
                    print(f"⚠ Adding missing test cases back to the result")
                    # Add missing test cases back
                    missing_cases = [tc for tc in test_cases if tc.get('id') in missing_ids]
                    result.extend(missing_cases)
                    print(f"✓ Total test cases after adding missing ones: {len(result)}")
                else:
                    print(f"✓ All {len(original_ids)} original test cases are present in AI response")
                
                # Count new test cases added
                new_test_cases = len(result) - len(test_cases)
                if new_test_cases > 0:
                    print(f"✓ AI added {new_test_cases} new test case(s) for better coverage")
                
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


def _fix_invalid_plantuml_code(invalid_code: str, error_message: str) -> str:
    """
    Use AI to fix invalid PlantUML syntax.
    """
    try:
        print("=== FIXING INVALID PLANTUML CODE ===")
        print(f"Error message: {error_message[:200]}...")
        
        agent = Agent(
            name="PlantUML Syntax Fixer",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "You are an expert in PlantUML syntax.",
                "Fix the provided invalid PlantUML code to make it syntactically correct.",
                "Common issues to fix:",
                "- Missing @startuml or @enduml tags",
                "- Invalid participant/actor declarations",
                "- Incorrect arrow syntax (should be -> or --> or ->>)",
                "- Missing quotes around names with spaces",
                "- Invalid color or style syntax",
                "- Unclosed alt/loop/opt blocks",
                "- Invalid note syntax",
                "Preserve the semantic meaning and flow of the diagram.",
                "Return ONLY valid PlantUML code in ```plantuml fenced block```."
            ],
            markdown=True,
        )
        
        fix_prompt = f"""
        The following PlantUML code has a syntax error and failed to render:
        
        ERROR MESSAGE:
        {error_message}
        
        INVALID PLANTUML CODE:
        ```plantuml
        {invalid_code}
        ```
        
        Please fix the syntax errors and return valid PlantUML code that will render successfully.
        Make minimal changes to preserve the original intent.
        Ensure all PlantUML syntax rules are followed.
        """
        
        resp = agent.run(fix_prompt)
        fixed_code = _extract_code_block(resp.content if hasattr(resp, "content") else str(resp), lang_hint="plantuml")
        
        print(f"✓ Fixed PlantUML code generated (length: {len(fixed_code)})")
        print(f"Fixed code preview: {fixed_code[:200]}...")
        
        return fixed_code
        
    except Exception as e:
        print(f"✗ Failed to fix PlantUML code: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a minimal valid PlantUML diagram as fallback
        return """@startuml
title Error: Could not generate diagram
note over System: The AI generated invalid PlantUML syntax\\nand automatic fixing failed.\\nPlease try regenerating the diagram.
@enduml"""


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
        max_retries = 2
        retry_count = 0
        img_path = None
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    print(f"Retry attempt {retry_count}/{max_retries}...")
                
                img_path = render_plantuml_from_text(plantuml_code, output_dir=output_dir, filename_base="e2e_test_diagram")
                print(f"✓ Image generated successfully at: {img_path}")
                break  # Success, exit retry loop
                
            except PlantUMLSyntaxError as syntax_error:
                print(f"✗ PlantUML syntax error on attempt {retry_count + 1}: {str(syntax_error)[:200]}")
                
                if retry_count < max_retries:
                    print(f"⚠ Attempting to fix invalid PlantUML syntax (attempt {retry_count + 1}/{max_retries})...")
                    try:
                        # Use AI to fix the invalid code
                        plantuml_code = _fix_invalid_plantuml_code(plantuml_code, str(syntax_error))
                        print(f"✓ Generated fixed PlantUML code, retrying render...")
                        retry_count += 1
                    except Exception as fix_error:
                        print(f"✗ Failed to fix PlantUML code: {str(fix_error)}")
                        raise syntax_error
                else:
                    print(f"✗ Max retries ({max_retries}) reached, giving up")
                    raise syntax_error
                    
            except Exception as e:
                print(f"✗ ERROR rendering PlantUML: {str(e)}")
                raise
        
        if not img_path:
            raise Exception("Failed to generate PlantUML image after all retries")

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
    """
    Refine PlantUML code based on user message with automatic error handling.
    """
    try:
        agent = Agent(
            name="PlantUML Refiner",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Modify the provided PlantUML code according to user request.",
                "Ensure the output is valid PlantUML syntax.",
                "Return ONLY fenced ```plantuml code```.",
            ],
            markdown=True,
        )
        resp = agent.run(f"```plantuml\n{plantuml_code}\n```\n\nUser request: {message}")
        updated_code = _extract_code_block(resp.content, lang_hint="plantuml")
        
        # Render with retry logic for syntax errors
        max_retries = 2
        retry_count = 0
        img_path = None
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    print(f"Retry attempt {retry_count}/{max_retries}...")
                
                img_path = render_plantuml_from_text(updated_code, output_dir=output_dir, filename_base="e2e_test_diagram")
                print(f"✓ Refined diagram generated successfully")
                break  # Success
                
            except PlantUMLSyntaxError as syntax_error:
                print(f"✗ PlantUML syntax error in refined code: {str(syntax_error)[:200]}")
                
                if retry_count < max_retries:
                    print(f"⚠ Attempting to fix invalid PlantUML syntax...")
                    updated_code = _fix_invalid_plantuml_code(updated_code, str(syntax_error))
                    retry_count += 1
                else:
                    raise syntax_error
                    
            except Exception as e:
                print(f"✗ ERROR rendering refined PlantUML: {str(e)}")
                raise

        return {
            "success": True,
            "plantuml_code": updated_code,
            "plantuml_image": f"/static/{Path(img_path).name}",
            "actors": _extract_actors_from_plantuml(updated_code),
            "activities": _extract_activities_from_plantuml(updated_code),
        }
    except Exception as e:
        print(f"✗ Failed to refine PlantUML: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "plantuml_code": None, "plantuml_image": None, "actors": [], "activities": []}