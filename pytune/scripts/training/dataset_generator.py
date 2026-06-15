import numpy as np
import pandas as pd
import soundfile as sf
import os
import random

# Constants
SAMPLE_RATE = 44100
DURATION = 2.0  # seconds
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
WAV_DIR = os.path.join(DATA_DIR, "wav")

os.makedirs(WAV_DIR, exist_ok=True)

# Guitar Standard Tuning Frequencies (Hz)
GUITAR_STRINGS = {
    'E2': 82.41,
    'A2': 110.00,
    'D3': 146.83,
    'G3': 196.00,
    'B3': 246.94,
    'e4': 329.63
}

def karplus_strong(frequency, duration, sample_rate=44100, drift=0.0):
    """
    Generates a guitar-like sound using the Karplus-Strong algorithm.
    frequency: Fundamental frequency.
    duration: Duration in seconds.
    drift: Random detuning drift (not used in basic KS but kept for interface).
    """
    N = int(sample_rate * duration)
    period = int(sample_rate / frequency)
    
    # Excitation: White noise burst
    burst_len = period
    noise_burst = np.random.uniform(-1, 1, burst_len)
    
    # Initialize ring buffer
    buffer = np.zeros(period)
    buffer[:burst_len] = noise_burst
    
    # Output signal
    output = np.zeros(N)
    
    # Feedback loop decay factor (controls sustain)
    decay = 0.99 - (frequency / 5000) # Higher freqs decay faster
    
    current_idx = 0
    for i in range(N):
        output[i] = buffer[current_idx]
        
        # Karplus-Strong update using the average of two adjacent samples
        prev_val = output[i]
        next_val = buffer[(current_idx + 1) % period]
        
        # Low-pass filter (simple averaging)
        new_val = decay * 0.5 * (prev_val + next_val)
        
        buffer[current_idx] = new_val
        current_idx = (current_idx + 1) % period
        
    return output

def add_noise(signal, noise_level=0.01):
    noise = np.random.normal(0, noise_level, len(signal))
    return signal + noise

def cents_to_hz_ratio(cents):
    return 2 ** (cents / 1200)

def generate_dataset(num_samples_per_string=20):
    data = []
    
    print("Generating synthetic guitar dataset...")
    
    file_count = 0
    
    for string_name, fundamental_freq in GUITAR_STRINGS.items():
        for i in range(num_samples_per_string):
            # 1. Decide tuning status
            # 33% In-tune, 33% Sharp, 33% Flat
            status_roll = random.random()
            
            if status_roll < 0.33:
                status = "In-Tune"
                # Allow tiny deviation even for in-tune (human error simulation)
                cents_offset = random.uniform(-5, 5) 
            elif status_roll < 0.66:
                status = "Sharp"
                cents_offset = random.uniform(10, 50)
            else:
                status = "Flat"
                cents_offset = random.uniform(-50, -10)
            
            # Calculate actual frequency
            freq_offset_factor = cents_to_hz_ratio(cents_offset)
            actual_freq = fundamental_freq * freq_offset_factor
            
            # Generate Audio
            audio = karplus_strong(actual_freq, DURATION, SAMPLE_RATE)
            
            # Add Noise/distortion
            if random.random() > 0.5:
                audio = add_noise(audio, noise_level=random.uniform(0.001, 0.005))
            
            # Normalize
            audio = audio / np.max(np.abs(audio))
            
            filename = f"{string_name}_{i}_{status}.wav"
            filepath = os.path.join(WAV_DIR, filename)
            
            sf.write(filepath, audio, SAMPLE_RATE)
            
            data.append({
                "filename": filename,
                "filepath": filepath,
                "string": string_name,
                "fundamental_freq": fundamental_freq,
                "actual_freq": actual_freq,
                "offset_cents": cents_offset,
                "status": status
            })
            file_count += 1
            
    df = pd.DataFrame(data)
    csv_path = os.path.join(DATA_DIR, "guitar_tuning_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset generated with {file_count} samples at {csv_path}")

if __name__ == "__main__":
    generate_dataset(num_samples_per_string=30) # Generates 6 strings * 30 samples = 180 samples
