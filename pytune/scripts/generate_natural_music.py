
import os
import sys

# Add the ml/core directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../ml/core')))

from music_generator_v3 import ComprehensiveMusicGenerator
from instrument_dataset import INSTRUMENT_DATASET

def generate_natural_music():
    # Initialize generator
    # We use the absolute path to outputs to ensure we can find the files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_dir = os.path.join(base_dir, 'outputs')
    
    print(f"Initializing Music Generator...")
    print(f"Outputs directory: {outputs_dir}")
    
    gen = ComprehensiveMusicGenerator(outputs_dir=outputs_dir)
    
    # Define the natural acoustic ensemble
    # Piano, Acoustic Guitar, Violin, Cello, Flute, Light Percussion (Congas/Shaker implied)
    # Note: 'shaker' is not in dataset, using 'congas' or 'drums'
    
    acoustic_ensemble = ['piano', 'guitar', 'violin', 'cello', 'flute']
    jazz_ensemble = ['piano', 'upright_bass', 'guitar', 'flute', 'congas']
    
    print("\n" + "="*60)
    print("GENERATING NATURAL ACOUSTIC MUSIC")
    print("="*60)
    
    # 1. Cinematic / Organic (using Classical logic for flowing melodies)
    print("\n[TRACK 1] Style: Cinematic/Organic (Classical Logic)")
    print("Mood: Romantic | Tempo: 85 BPM")
    result1 = gen.generate_music(
        genre="Classical",
        tempo=85,
        duration=20,
        mood="Romantic",
        instruments=acoustic_ensemble
    )
    print(f"Generated: {result1['audio_url']}")
    
    # 2. Live Session / Lounge (using Jazz logic for swing/walking bass)
    print("\n[TRACK 2] Style: Live Session (Jazz Logic)")
    print("Mood: Calm | Tempo: 90 BPM")
    result2 = gen.generate_music(
        genre="Jazz",
        tempo=90,
        duration=20,
        mood="Calm",
        instruments=jazz_ensemble
    )
    print(f"Generated: {result2['audio_url']}")

    print("\n" + "="*60)
    print("Generation Complete! Files are ready in the 'outputs' folder.")
    print("="*60)

if __name__ == "__main__":
    generate_natural_music()
