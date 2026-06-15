import requests
import numpy as np
import io
import soundfile as sf

def test_tuner():
    # Generate a 1-second 440Hz sine wave (A4)
    sr = 44100
    t = np.linspace(0, 1, sr)
    y = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    # Save to buffer as WAV
    buf = io.BytesIO()
    sf.write(buf, y, sr, format='WAV')
    buf.seek(0)
    
    # Send to backend
    url = "http://localhost:8000/tune"
    files = {'file': ('test.wav', buf, 'audio/wav')}
    
    try:
        response = requests.post(url, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tuner()
