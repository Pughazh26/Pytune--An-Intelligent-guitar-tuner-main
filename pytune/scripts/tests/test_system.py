import requests
import json
import os
import time

API_URL = "http://localhost:8081"
DATA_DIR = os.path.join("ml", "data", "wav")

def test_backend():
    print(f"Testing Backend at {API_URL}...")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{API_URL}/")
        print(f"GET / -> Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return

    # 2. Test Music Generation
    print("\n[Testing Music Generation]")
    payload = {
        "genre": "Lo-fi",
        "tempo": 90,
        "mood": "Chill",
        "duration": 5
    }
    try:
        resp = requests.post(f"{API_URL}/generate-music", json=payload)
        print(f"POST /generate-music -> Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Response:", json.dumps(resp.json(), indent=2))
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Error generating music: {e}")

    # 3. Test Tuning (using a sample file)
    print("\n[Testing Guitar Tuner]")
    # Find a sample file
    sample_file = None
    if os.path.exists(DATA_DIR):
        files = os.listdir(DATA_DIR)
        if files:
            sample_file = os.path.join(DATA_DIR, files[0])
            print(f"Using sample file: {sample_file}")

    if sample_file:
        try:
            with open(sample_file, 'rb') as f:
                files = {'file': (os.path.basename(sample_file), f, 'audio/wav')}
                resp = requests.post(f"{API_URL}/tune", files=files)
                print(f"POST /tune -> Status: {resp.status_code}")
                if resp.status_code == 200:
                    print("Response:", json.dumps(resp.json(), indent=2))
                else:
                    print("Error:", resp.text)
        except Exception as e:
            print(f"Error tuning: {e}")
    else:
        print("No sample file found to test tuner. (Did dataset_generator run?)")

if __name__ == "__main__":
    test_backend()
