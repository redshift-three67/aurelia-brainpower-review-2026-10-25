import requests
import json

def test_endpoint(endpoint, payload):
    url = f"http://localhost:11434/api/{endpoint}"
    print(f"Testing {url} with model '{payload['model']}'...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success!")
            # Zeige verkürzte Antwort
            print(str(response.json())[:100] + "...")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

models_to_test = ["llama3.2:3b", "llama3.2", "tinyllama:latest"]

for model in models_to_test:
    print("\n" + "-"*50)
    
    # Test 1: Generate API
    payload_gen = {
        "model": model,
        "prompt": "Hi",
        "stream": False
    }
    if test_endpoint("generate", payload_gen):
        break # Wenn erfolgreich, hör auf
        
    # Test 2: Chat API (Alternative)
    payload_chat = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    }
    test_endpoint("chat", payload_chat)
