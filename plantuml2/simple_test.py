import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_generate_diagram():
    # Sample test cases
    test_cases = [
        {
            "id": "TC001",
            "title": "User Login Test",
            "steps": [
                {"action": "Open browser", "expected": "Browser opens successfully"},
                {"action": "Navigate to login page", "expected": "Login page loads"},
                {"action": "Enter credentials", "expected": "Credentials accepted"},
                {"action": "Click login", "expected": "User logged in successfully"}
            ]
        },
        {
            "id": "TC002", 
            "title": "Form Submission Test",
            "steps": [
                {"action": "Fill form fields", "expected": "Fields populated"},
                {"action": "Click submit", "expected": "Form submitted successfully"}
            ]
        }
    ]
    
    url = f"{BASE_URL}/generate-diagram/"
    payload = {"test_cases": test_cases}
    headers = {"X-OpenAI-API-Key": "test-key"}  # Dummy key for testing
    
    print("Testing diagram generation...")
    print(f"URL: {url}")
    print(f"Test cases count: {len(test_cases)}")
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                print("✓ Diagram generation successful!")
                print(f"PlantUML code length: {len(data.get('plantuml_code', ''))}")
                print(f"Image URL: {data.get('plantuml_image', 'N/A')}")
            else:
                print("✗ Diagram generation failed:")
                print(data)
        else:
            print(f"✗ HTTP Error {resp.status_code}:")
            print(resp.text)
            
    except Exception as e:
        print(f"✗ Exception: {e}")

if __name__ == "__main__":
    test_generate_diagram()
