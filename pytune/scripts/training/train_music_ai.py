
import os
import joblib
import numpy as np
from collections import defaultdict
import random

def train_music_model():
    print("Training AI Music Generation Model...")
    
    # Store transitions: model[genre][mood][instrument][current_state] -> {next_state: count}
    model = {
        g: {m: defaultdict(lambda: defaultdict(lambda: defaultdict(int))) 
            for m in ['Happy', 'Sad', 'Energetic', 'Calm']}
        for g in ['Pop', 'Jazz', 'Rock', 'EDM', 'Classical']
    }

    # Helper to add a pattern to the model
    def add_pattern(genre, mood, instrument, pattern):
        for i in range(len(pattern) - 1):
            curr_state = pattern[i]
            next_state = pattern[i+1]
            model[genre][mood][instrument][curr_state][next_state] += 1

    # --- HAPPY PATTERNS (Major, upbeat) ---
    happy_pattern = [(0, 0.5), (4, 0.5), (7, 0.5), (9, 0.5), (7, 1.0)]
    for g in model: add_pattern(g, 'Happy', 'melodic', happy_pattern)

    # --- SAD PATTERNS (Minor, slow, lower) ---
    sad_pattern = [(0, 1.0), (3, 1.0), (2, 1.0), (0, 2.0), (-2, 1.0)]
    for g in model: add_pattern(g, 'Sad', 'melodic', sad_pattern)
    
    # --- ENERGETIC PATTERNS (Fast, wide jumps) ---
    energetic_pattern = [(0, 0.25), (7, 0.25), (12, 0.25), (7, 0.25), (0, 0.5)]
    for g in model: add_pattern(g, 'Energetic', 'melodic', energetic_pattern)

    # --- CALM PATTERNS (Minimal movement, slow) ---
    calm_pattern = [(0, 2.0), (2, 2.0), (4, 4.0)]
    for g in model: add_pattern(g, 'Calm', 'melodic', calm_pattern)

    # Convert counts to probabilities
    final_model = {}
    for genre in model:
        final_model[genre] = {}
        for mood in model[genre]:
            final_model[genre][mood] = {}
            for inst in model[genre][mood]:
                final_model[genre][mood][inst] = {}
                for state in model[genre][mood][inst]:
                    transitions = model[genre][mood][inst][state]
                    total = sum(transitions.values())
                    probs = {next_s: count/total for next_s, count in transitions.items()}
                    final_model[genre][mood][inst][state] = probs

    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), "models", "music_ai_model.pkl")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(final_model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_music_model()
