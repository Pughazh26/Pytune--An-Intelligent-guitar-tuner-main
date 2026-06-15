import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from feature_extraction import extract_features
import dataset_generator

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "guitar_tuning_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "pytune_tuner_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

def train_model():
    # 1. Check/Generate Data
    if not os.path.exists(CSV_PATH):
        print("Dataset not found. Generating...")
        dataset_generator.generate_dataset()
        
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded dataset with {len(df)} samples.")
    
    # 2. Extract Features
    print("Extracting features...")
    X = []
    y_string = []
    y_status = []
    
    # We need to process each file. encoding filepath is needed.
    for index, row in df.iterrows():
        fpath = row['filepath']
        if not os.path.exists(fpath):
            continue
            
        feats = extract_features(fpath)
        # Convert dict to list in consistent order (using keys from extract_features)
        # We rely on the dictionary insertion order (Python 3.7+) or explicit sorting
        feat_vals = [
            feats["zcr_mean"], feats["cent_mean"], feats["cent_std"], 
            feats["rms_mean"], feats["pitch_mean"]
        ]
        # Add MFCCs
        for i in range(13):
            feat_vals.append(feats[f"mfcc_mean_{i}"])
            feat_vals.append(feats[f"mfcc_std_{i}"])
        # Add Chroma
        for i in range(12):
            feat_vals.append(feats[f"chroma_{i}"])
            
        X.append(feat_vals)
        y_string.append(row['string'])
        y_status.append(row['status'])
        
    X = np.array(X)
    y_string = np.array(y_string)
    y_status = np.array(y_status)
    
    # 3. Train Test Split
    X_train, X_test, y_str_train, y_str_test, y_stat_train, y_stat_test = train_test_split(
        X, y_string, y_status, test_size=0.2, random_state=42
    )
    
    # 4. Train Models
    print("Training Random Forest Classifier for String Detection...")
    rf_string = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_string.fit(X_train, y_str_train)
    
    print("Training Random Forest Classifier for Tuning Status...")
    rf_status = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_status.fit(X_train, y_stat_train)
    
    # Evaluate
    str_acc = accuracy_score(y_str_test, rf_string.predict(X_test))
    stat_acc = accuracy_score(y_stat_test, rf_status.predict(X_test))
    
    print(f"String Detection Accuracy: {str_acc * 100:.2f}%")
    print(f"Tuning Status Accuracy: {stat_acc * 100:.2f}%")
    
    # Save Combined Model
    model_bundle = {
        "string_model": rf_string,
        "status_model": rf_status,
        "feature_order": [
            "zcr_mean", "cent_mean", "cent_std", "rms_mean", "pitch_mean",
            "mfcc_mean_0..12", "mfcc_std_0..12", "chroma_0..11"
        ]
    }
    
    joblib.dump(model_bundle, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
