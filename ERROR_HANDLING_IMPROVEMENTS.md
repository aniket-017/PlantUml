# Error Handling Improvements for PlantUML Generation

## Problem

The application was encountering `exit status 200` errors from PlantUML when the AI generated invalid PlantUML syntax. This caused diagram generation to fail without any recovery mechanism.

## Solutions Implemented

### 1. **Enhanced Error Detection** (`plantuml_service.py`)

#### Added Custom Exception

- Created `PlantUMLSyntaxError` exception class for specific syntax error handling
- Distinguishes PlantUML syntax errors (exit code 200) from other errors

#### Improved Error Handling in `render_plantuml_from_text()`

```python
# Before: Used check=True, which raised generic CalledProcessError
result = subprocess.run(cmd, check=True, ...)

# After: Capture error details and raise specific exceptions
result = subprocess.run(cmd, capture_output=True, ...)
if result.returncode != 0:
    if result.returncode == 200:
        raise PlantUMLSyntaxError(f"Invalid PlantUML syntax. {error_details}")
    else:
        raise Exception(error_details)
```

**Benefits:**

- Captures PlantUML's actual error messages (stdout/stderr)
- Differentiates syntax errors from other failures
- Enables targeted error recovery

---

### 2. **AI-Powered Syntax Fixing** (`csv_service.py`)

#### New Function: `_fix_invalid_plantuml_code()`

Automatically fixes invalid PlantUML syntax using AI:

**Features:**

- Sends invalid code and error message to GPT-4o-mini
- AI analyzes the syntax error and fixes it
- Preserves the original diagram's semantic meaning
- Has fallback to minimal valid diagram if fixing fails

**Common Issues Fixed:**

- Missing `@startuml` or `@enduml` tags
- Invalid participant/actor declarations
- Incorrect arrow syntax
- Missing quotes around names with spaces
- Unclosed alt/loop/opt blocks
- Invalid note syntax

---

### 3. **Automatic Retry Logic** (`csv_service.py`)

#### Enhanced `process_csv_and_generate()`

Implements intelligent retry mechanism:

```python
max_retries = 2
while retry_count <= max_retries:
    try:
        img_path = render_plantuml_from_text(plantuml_code, ...)
        break  # Success
    except PlantUMLSyntaxError as syntax_error:
        if retry_count < max_retries:
            # Use AI to fix the code
            plantuml_code = _fix_invalid_plantuml_code(plantuml_code, str(syntax_error))
            retry_count += 1
        else:
            raise  # Max retries reached
```

**Retry Flow:**

1. **Attempt 1:** Try to render original AI-generated code
2. **If fails:** AI analyzes error and generates fixed code
3. **Attempt 2:** Try to render fixed code
4. **If fails again:** AI tries one more fix
5. **Attempt 3:** Final retry with second fix
6. **If still fails:** Return error to user with detailed information

#### Enhanced `refine_plantuml_code()`

Same retry logic applied when users request diagram refinements

---

### 4. **Improved Test Case Enrichment** (`enrich_test_cases_with_ai()`)

#### Guarantees All Original Test Cases Are Preserved

**Updated Instructions:**

- AI **MUST** include ALL original user-provided test cases
- AI should understand the logical flow from existing test cases
- AI can reorder test cases for better execution sequence
- AI can add NEW test cases to fill gaps

**Validation Logic:**

```python
# Validate that all original test cases are included
original_ids = {tc.get('id') for tc in test_cases}
result_ids = {tc.get('id') for tc in result}
missing_ids = original_ids - result_ids

if missing_ids:
    # Add missing test cases back
    missing_cases = [tc for tc in test_cases if tc.get('id') in missing_ids]
    result.extend(missing_cases)
```

**Flow Understanding:**

- AI analyzes test cases to understand application workflow
- Reorders test cases logically: Setup → Happy Path → Alternative Flows → Error Cases → Cleanup
- Identifies dependencies between test cases
- Adds missing scenarios while preserving all original ones

---

## Error Handling Flow Diagram

```
User uploads CSV
       ↓
Extract test cases
       ↓
AI generates PlantUML
       ↓
┌──────────────────────┐
│ Try to render (1st)  │
└──────────────────────┘
       ↓
  Syntax error?
       ├─ No → ✓ Success! Return diagram
       └─ Yes → AI analyzes error and fixes code
                      ↓
              ┌──────────────────────┐
              │ Try to render (2nd)  │
              └──────────────────────┘
                      ↓
                 Syntax error?
                      ├─ No → ✓ Success! Return diagram
                      └─ Yes → AI fixes again
                                  ↓
                          ┌──────────────────────┐
                          │ Try to render (3rd)  │
                          └──────────────────────┘
                                  ↓
                             Syntax error?
                                  ├─ No → ✓ Success! Return diagram
                                  └─ Yes → ✗ Return error with details
```

---

## Benefits

### For Users

✅ **Automatic Recovery:** Most PlantUML syntax errors are fixed automatically  
✅ **Transparent:** Detailed logging shows what's happening  
✅ **Reliable:** Fallback mechanisms ensure something is always returned  
✅ **Test Case Preservation:** All user test cases are guaranteed to be included  
✅ **Better Flow:** Test cases are logically sequenced for better understanding

### For Developers

✅ **Specific Exceptions:** `PlantUMLSyntaxError` vs generic exceptions  
✅ **Detailed Logging:** Every step is logged for debugging  
✅ **Maintainable:** Clear separation of concerns  
✅ **Extensible:** Easy to add more retry strategies or validators

---

## Example Output

### Before (Error)

```
ERROR: Command '['java', '-jar', '...plantuml.jar', ...]'
returned non-zero exit status 200.
```

### After (Auto-fixed)

```
✗ PlantUML syntax error on attempt 1: Invalid PlantUML syntax...
⚠ Attempting to fix invalid PlantUML syntax (attempt 1/2)...
=== FIXING INVALID PLANTUML CODE ===
✓ Fixed PlantUML code generated (length: 450)
Retry attempt 1/2...
✓ Image generated successfully at: .../e2e_test_diagram.png
✓ AI added 3 new test case(s) for better coverage
```

---

## Testing Recommendations

1. **Test with intentionally broken PlantUML:**

   - Missing `@startuml`/`@enduml`
   - Invalid syntax in arrows
   - Unclosed blocks

2. **Test retry limits:**

   - Verify system gives up after 2 retries
   - Check fallback diagram is generated

3. **Test test case preservation:**

   - Upload CSV with specific test cases
   - Verify all original IDs are in output
   - Verify new test cases have unique IDs

4. **Test error messages:**
   - Verify detailed error logs are produced
   - Check that PlantUML errors are captured

---

## Configuration

### Retry Settings

Currently hardcoded in `csv_service.py`:

```python
max_retries = 2  # Total of 3 attempts (initial + 2 retries)
```

### AI Model

Uses `gpt-4o-mini` for:

- Test case generation
- Test case enrichment
- PlantUML code generation
- PlantUML syntax fixing

Can be changed by modifying:

```python
model=OpenAIChat(id="gpt-4o-mini")  # Change to gpt-4, etc.
```

---

## Future Enhancements

### Potential Improvements

1. **Pre-validation:** Validate PlantUML syntax before calling Java
2. **Caching:** Cache successful PlantUML patterns to avoid regeneration
3. **User Feedback:** Let users choose to retry or accept fallback
4. **Configurable Retries:** Make retry count configurable via API
5. **Syntax Hints:** Provide AI with PlantUML documentation context
6. **Pattern Learning:** Learn from successful fixes to improve future generations

### Monitoring Recommendations

- Track syntax error rate
- Monitor retry success rate
- Log which types of errors are most common
- Measure AI fix success rate
