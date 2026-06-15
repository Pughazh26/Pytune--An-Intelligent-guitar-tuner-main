
import os
import sys
import numpy as np
import librosa
import joblib
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add the ml/core directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../ml/core')))

from music_generator_v3 import ComprehensiveMusicGenerator

def analyze_audio_file(file_path):
    """
    Analyze an audio file to extract musical parameters for generation.
    """
    print(f"Analyzing input: {os.path.basename(file_path)}...")
    
    try:
        y, sr = librosa.load(file_path, duration=30)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    # 1. Extract Tempo (BPM)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
    tempo = int(round(tempo))
    print(f"  -> Detected Tempo: {tempo} BPM")

    # 2. Extract Energy (RMS) -> Mood
    rms = librosa.feature.rms(y=y)
    avg_rms = np.mean(rms)
    print(f"  -> Average Energy (RMS): {avg_rms:.4f}")
    
    # Simple Mood Logic
    if avg_rms > 0.1:
        mood = "Energetic"
    elif avg_rms < 0.02:
        mood = "Sad"
    else:
        # Check spectral centroid for brightness
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        avg_cent = np.mean(cent)
        if avg_cent > 3000:
            mood = "Happy"
        elif avg_cent > 1500:
            mood = "Calm"
        else:
            mood = "Dark"
    print(f"  -> Inferred Mood: {mood}")

    # 3. Extract Key / Root Note
    # Simple heuristic: stronger pitch class is root
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    root_idx = np.argmax(chroma_mean)
    
    # Map index 0-11 to MIDI note (60 is Middle C)
    # 0=C, 1=C#, ..., 9=A
    # We'll map to octave 4 (60-71)
    root_note = 60 + root_idx
    
    # Detect Major/Minor based on simple triad correlation
    # This is a very basic approximation
    major_profile = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
    minor_profile = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
    
    # Rotate chroma to root
    chroma_rotated = np.roll(chroma_mean, -root_idx)
    
    maj_corr = np.corrcoef(major_profile, chroma_rotated)[0, 1]
    min_corr = np.corrcoef(minor_profile, chroma_rotated)[0, 1]
    
    scale_type = "major" if maj_corr >= min_corr else "minor"
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    print(f"  -> Detected Key: {note_names[root_idx]} {scale_type}")

    # 4. Infer Genre based on Features
    # This is speculative, but we can try
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    avg_cent = np.mean(cent)
    
    if avg_cent > 3000 and tempo > 120:
        genre = "Pop" # Bright and fast
    elif avg_cent > 3000:
        genre = "Jazz" # Bright but maybe slower
    elif tempo > 100:
        genre = "Rock"
    elif "violin" in file_path.lower() or "classical" in file_path.lower():
        genre = "Classical"
    else:
        genre = "Classical" # Default to organic/acoustic if low centroid
        
    print(f"  -> Inferred Genre: {genre}")

    return {
        "tempo": tempo,
        "mood": mood,
        "root_note": root_note,
        "genre": genre,
        "scale": scale_type
    }

def generate_responsive_music(input_file):
    # 1. Analyze
    params = analyze_audio_file(input_file)
    if not params:
        print("Analysis failed.")
        return

    # 2. Initialize Generator
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_dir = os.path.join(base_dir, 'outputs')
    gen = ComprehensiveMusicGenerator(outputs_dir=outputs_dir)

    print("\n" + "="*60)
    print("GENERATING RESPECTIVE OUTPUT")
    print("="*60)
    print(f"Using parameters from analysis:")
    print(f"Genre: {params['genre']}")
    print(f"Mood: {params['mood']}")
    print(f"Tempo: {params['tempo']} BPM")
    print(f"Root Note: {params['root_note']}")
    
    # 3. Generate
    # We try to keep the instrumentation "Natural" if the input seemed acoustic, or standard based on genre
    # For this demo, let's stick to the genre defaults but maybe override if Classical
    
    instruments = None
    if params['genre'] == 'Classical':
        instruments = ['piano', 'violin', 'cello', 'flute']
    elif params['genre'] == 'Jazz':
        instruments = ['piano', 'upright_bass', 'drums', 'saxophone']
        
    result = gen.generate_music(
        genre=params['genre'],
        tempo=params['tempo'],
        duration=20,
        mood=params['mood'],
        root_note=params['root_note'],
        instruments=instruments
    )
    
    print(f"\nSuccessfully generated response track: {result['audio_url']}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate music based on input audio analysis")
    parser.add_argument("input_file", nargs='?', help="Path to input audio file")
    
    args = parser.parse_args()
    
    target_file = args.input_file
    
    # If no file provided, find the most recent WAV in outputs
    if not target_file:
        outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../outputs'))
        wav_files = [f for f in os.listdir(outputs_dir) if f.endswith('.wav')]
        if wav_files:
            # Sort by time, newest first
            wav_files.sort(key=lambda x: os.path.getmtime(os.path.join(outputs_dir, x)), reverse=True)
            target_file = os.path.join(outputs_dir, wav_files[0])
            print(f"No input file specified. Using most recent output: {target_file}")
        else:
            print("No generated files found to test with. Please provide an input file path.")
            sys.exit(1)
            
    if os.path.exists(target_file):
        generate_responsive_music(target_file)
    else:
        print(f"Input file not found: {target_file}")
