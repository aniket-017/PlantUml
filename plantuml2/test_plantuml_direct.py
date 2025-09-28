import sys
import os
sys.path.append('app')

from services.plantuml_service import render_plantuml_from_text

# Test PlantUML generation directly
test_puml = """@startuml
actor User
User -> "System": Login
"System" --> User: Success
@enduml"""

print("Testing PlantUML generation directly...")
try:
    result = render_plantuml_from_text(test_puml, "static", "test_direct")
    print(f"✓ Success! Generated image at: {result}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
