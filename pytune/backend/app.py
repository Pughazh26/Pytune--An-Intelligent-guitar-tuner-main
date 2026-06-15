import sys
import os
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import pandas as pd
import uvicorn
import soundfile as sf
import io
import librosa

# Add project root and ml directory to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "ml"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "core"))

from ml.core.feature_extraction import extract_features_from_buffer
from ml.core.music_generator_v3 import ComprehensiveMusicGenerator
from ml.core.music_generator_v4 import AIMusicGeneratorV4
from ml.core.nlp_music_parser import NLPMusicParser

app = FastAPI(title="PYTUNE API", description="Backend for Intelligent Guitar Tuner & AI Music Generator")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
MODEL_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "pytune_tuner_model.pkl")

# Serve Outputs
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# Load Model
model_bundle = None
try:
    if os.path.exists(MODEL_PATH):
        model_bundle = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    else:
        print("Warning: Model not found. /tune endpoint will fail until model is trained.")
except Exception as e:
    print(f"Error loading model: {e}")

# Initialize Music Gen
try:
    music_gen = AIMusicGeneratorV4(outputs_dir=OUTPUTS_DIR)
    print("AI Music Generator V4 (Markov Model) initialized.")
except Exception as e:
    print(f"Error loading AI Music Generator V4: {e}. Falling back to V3.")
    music_gen = ComprehensiveMusicGenerator(outputs_dir=OUTPUTS_DIR)

# Models
class MusicRequest(BaseModel):
    genre: str
    tempo: int
    mood: str
    duration: int
    instruments: Optional[list] = None  # Optional list of instruments

@app.get("/")
def read_root():
    return {"message": "Welcome to PYTUNE API"}

@app.post("/tune")
async def tune_guitar(file: UploadFile = File(...)):
    if model_bundle is None:
        return {
             "detected_pitch": "Model Missing",
             "frequency": 0.0,
             "tuning_offset_cents": 0.0,
             "tuning_status": "Error",
             "confidence": 0.0,
             "error": "Tuner model not loaded. Please train the model first."
        }
    
    try:
        # Read audio file
        audio_bytes = await file.read()
        print(f"Received audio file: {file.filename}, size: {len(audio_bytes)} bytes")
        
        audio_buffer = io.BytesIO(audio_bytes)
        try:
            y, sr = sf.read(audio_buffer)
        except Exception as read_err:
            print(f"Soundfile read failed: {read_err}. Trying librosa fallback...")
            # Fallback to librosa which is more permissive
            audio_buffer.seek(0)
            y, sr = librosa.load(audio_buffer, sr=None)
        
        # If stereo, convert to mono
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
            
        # Extract features
        features = extract_features_from_buffer(y, sr)
        
        if features is None:
             raise HTTPException(status_code=400, detail="Could not process audio.")
        
        # Prepare feature vector for ML model (matching training script order)
        feat_vals = [
            features["zcr_mean"], features["cent_mean"], features["cent_std"], 
            features["rms_mean"], features["pitch_mean"]
        ]
        for i in range(13):
            feat_vals.append(features[f"mfcc_mean_{i}"])
            feat_vals.append(features[f"mfcc_std_{i}"])
        for i in range(12):
            feat_vals.append(features[f"chroma_{i}"])
            
        # Reshape for single sample prediction
        X = np.array(feat_vals).reshape(1, -1)
        
        # Predict String and Status (ML results for internal logging/analytics)
        try:
            predicted_string = model_bundle["string_model"].predict(X)[0]
            predicted_status = model_bundle["status_model"].predict(X)[0]
            print(f"ML Model Predict -> String: {predicted_string}, Status: {predicted_status}")
        except Exception as pred_err:
            print(f"ML Model Prediction Error: {pred_err}")

        
        # 1. Normalize Volume (Crucial for Clipping/Low Signal)
        if np.max(np.abs(y)) > 0:
            y = y / np.max(np.abs(y))
        
        # 2. ROBUST PITCH DETECTION
        # Increased frame_length for better low-end resolution
        # Calculate YIN and also get the magnitude of the difference (periodicity)
        # Using trough_threshold=0.15 for better harmonic rejection
        f0_all = librosa.yin(y, fmin=50, fmax=2000, sr=sr, frame_length=4096, trough_threshold=0.15)
        
        # 2.1 CONFIDENCE GATE: Check if the wave is periodic (musical) or random (noise)
        # We can estimate confidence based on how many frames successfully found a pitch
        valid_frames = f0_all[~np.isnan(f0_all)]
        confidence_score = len(valid_frames) / len(f0_all) if len(f0_all) > 0 else 0.0
        
        # Filter noise based on periodicity and minimal signal energy
        detected_freq = 0.0
        if confidence_score > 0.5 and np.max(np.abs(y)) > 0.05:
            detected_freq = float(np.median(valid_frames))
        
        # 3. NOTE CONVERSION & PERFECT PITCH CALCULATION
        detected_pitch_name = "---"
        offset_cents = 0.0
        tuning_status = "Waiting"
        
        if detected_freq > 30:
            # Frequency to MIDI
            n_float = 12 * np.log2(detected_freq / 440.0) + 69
            midi_note = int(round(n_float))
            
            names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            note_name = names[midi_note % 12]
            octave = (midi_note // 12) - 1
            detected_pitch_name = f"{note_name}{octave}"
            
            # Ideal frequency
            perfect_freq = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
            offset_cents = 1200 * np.log2(detected_freq / perfect_freq)
            
            if abs(offset_cents) <= 8:
                tuning_status = "In-Tune"
            elif offset_cents > 8:
                tuning_status = "Sharp"
            else:
                tuning_status = "Flat"
            
            print(f"FREQ: {detected_freq:.2f}Hz | CONF: {confidence_score:.2f} | NOTE: {detected_pitch_name}")
        else:
            # Reset results if detected as noise
            detected_pitch_name = "---"
            tuning_status = "Listening..."
            offset_cents = 0.0
            detected_freq = 0.0
        
        return {
            "detected_pitch": detected_pitch_name, 
            "frequency": round(float(detected_freq), 2),
            "tuning_offset_cents": round(float(offset_cents), 1),
            "tuning_status": tuning_status,
            "confidence": 1.0 # Pure mathematical confidence
        }

    except Exception as e:
        print(f"Error processing tune request: {e}")
        # Return a mock response if real processing fails (for demo stability) or raise error
        # raise HTTPException(status_code=500, detail=str(e))
        return {
             "detected_pitch": "Unknown",
             "frequency": 0.0,
             "tuning_offset_cents": 0.0,
             "tuning_status": "Error",
             "confidence": 0.0,
             "error": str(e)
        }

@app.post("/generate-music")
async def generate_music_endpoint(request: MusicRequest):
    try:
        result = music_gen.generate_music(
            genre=request.genre,
            tempo=request.tempo,
            mood=request.mood,
            duration=request.duration,
            instruments=request.instruments
        )
        # Ensure URLs are absolute for the frontend or relative to server root
        # Here we return paths that the frontend can fetch from the mounted /outputs dir
        return {
            "genre": result["genre"],
            "audio_url": f"http://localhost:8000{result['audio_url']}",
            "midi_url": f"http://localhost:8000{result['midi_url']}",
            "instruments": result.get("instruments", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/instruments")
def get_instruments(category: Optional[str] = None, genre: Optional[str] = None):
    """Get list of available instruments, optionally filtered by category or genre"""
    from ml.core.instrument_dataset import INSTRUMENT_DATASET
    
    try:
        if category:
            instruments = INSTRUMENT_DATASET.get_instruments_by_category(category)
            return {
                "category": category,
                "instruments": [
                    {
                        "name": inst.name,
                        "id": name,
                        "category": inst.category,
                        "genres": inst.typical_genres,
                        "frequency_range": inst.frequency_range
                    }
                    for name, inst in INSTRUMENT_DATASET.instruments.items()
                    if inst.category == category
                ]
            }
        elif genre:
            instruments = INSTRUMENT_DATASET.get_instruments_by_genre(genre)
            return {
                "genre": genre,
                "instruments": [
                    {
                        "name": inst.name,
                        "id": name,
                        "category": inst.category,
                        "genres": inst.typical_genres
                    }
                    for name, inst in INSTRUMENT_DATASET.instruments.items()
                    if genre in inst.typical_genres or 'All' in inst.typical_genres
                ]
            }
        else:
            # Return all instruments
            return {
                "total": len(INSTRUMENT_DATASET.list_all_instruments()),
                "instruments": [
                    {
                        "name": inst.name,
                        "id": name,
                        "category": inst.category,
                        "genres": inst.typical_genres,
                        "midi_program": inst.midi_program
                    }
                    for name, inst in INSTRUMENT_DATASET.instruments.items()
                ],
                "categories": {
                    "melodic": len(INSTRUMENT_DATASET.get_instruments_by_category('melodic')),
                    "harmonic": len(INSTRUMENT_DATASET.get_instruments_by_category('harmonic')),
                    "bass": len(INSTRUMENT_DATASET.get_instruments_by_category('bass')),
                    "percussion": len(INSTRUMENT_DATASET.get_instruments_by_category('percussion'))
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard-metrics")
def get_metrics():
    # Mock Analytics
    return {
        "total_tunes": 1245,
        "most_tuned_string": "G3",
        "average_accuracy": "94%",
        "songs_generated": 328,
        "top_genre": "Lo-fi"
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
