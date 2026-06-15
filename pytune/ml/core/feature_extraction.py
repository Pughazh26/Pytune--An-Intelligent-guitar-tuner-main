import librosa
import numpy as np
import os

def extract_features_from_buffer(y, sr):
    """
    Extracts a comprehensive set of features from an audio buffer.
    Returns a dictionary of features.
    """
    try:
        # Pre-process
        if len(y) == 0:
            return None
            
        # 1. Basic Spectral Features
        zcr = librosa.feature.zero_crossing_rate(y)
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        rms = librosa.feature.rms(y=y)
        
        # 2. Pitch Detection (using YIN)
        # We'll use a median of the detected pitches as the 'pitch_mean'
        f0 = librosa.yin(y, fmin=50, fmax=2000, sr=sr)
        f0 = f0[~np.isnan(f0)]
        pitch_mean = np.median(f0) if len(f0) > 0 else 0.0
        
        # 3. MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # 4. Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # Build Results
        features = {
            "zcr_mean": float(np.mean(zcr)),
            "cent_mean": float(np.mean(cent)),
            "cent_std": float(np.std(cent)),
            "rms_mean": float(np.mean(rms)),
            "pitch_mean": float(pitch_mean)
        }
        
        # Add MFCC means and stds
        for i in range(13):
            features[f"mfcc_mean_{i}"] = float(np.mean(mfccs[i]))
            features[f"mfcc_std_{i}"] = float(np.std(mfccs[i]))
            
        # Add Chroma means
        chroma_mean = np.mean(chroma, axis=1)
        for i in range(12):
            features[f"chroma_{i}"] = float(chroma_mean[i])
            
        return features
    except Exception as e:
        print(f"Feature extraction error: {e}")
        return None

def extract_features(file_path):
    """
    Load audio file and extract features.
    """
    if not os.path.exists(file_path):
        return None
        
    try:
        y, sr = librosa.load(file_path, sr=None)
        return extract_features_from_buffer(y, sr)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

if __name__ == "__main__":
    # Test with a dummy signal
    sr = 44100
    t = np.linspace(0, 1, sr)
    y = np.sin(2 * np.pi * 440 * t) # A4 note
    feats = extract_features_from_buffer(y, sr)
    if feats:
        print("Successfully extracted features:")
        print(f"Pitch Mean: {feats['pitch_mean']:.2f} Hz")
        print(f"MFCCs extracted: {len([k for k in feats if 'mfcc' in k])}")
