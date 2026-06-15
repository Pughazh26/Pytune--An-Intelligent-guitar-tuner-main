# 🎸 PYTUNE: Intelligent Guitar Tuner & AI Music Generator

End-to-end AI system for real-time guitar tuning and generative music creation.

## 🌟 Features

- **Smart Tuner**: Real-time pitch detection using Machine Learning (not just DSP).
- **AI Music Generation**: Generates infinite music tracks (Audio + MIDI) based on Genre/Mood.
- **Modern Dashboard**: Analytics and usage stats.
- **Embedded Ready**: Designed with lightweight models suitable for edge deployment.
- **Full Stack**: FastAPI Backend + React/Vite Frontend.

## 📂 Project Structure

```
/pytune
 ├── backend/            # FastAPI Server
 │   └── app.py
 ├── ml/                 # Machine Learning Modules
 │   ├── data/           # Datasets
 │   ├── models/         # Trained .pkl models
 │   ├── dataset_generator.py # Synthetic data creator
 │   ├── feature_extraction.py
 │   ├── train_tuner.py  # Model trainer
 │   └── music_generator.py
 ├── frontend/           # React + TypeScript Web App
 ├── outputs/            # Generated Music Files
 └── docs/               # Documentation
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 16+

### 1. Backend Setup

```bash
cd pytune
pip install -r requirements.txt
```

### 2. Machine Learning Pipeline (Required First Time)

Generate the dataset and train the model:

```bash
cd ml
python dataset_generator.py
python train_tuner.py
```
*This will create `ml/models/pytune_tuner_model.pkl`.*

### 3. Run Backend

```bash
cd ../backend
python app.py
```
*Server will run at `http://localhost:8000`*

### 4. Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```
*App will run at `http://localhost:5173`*

## 🧠 Model Architecture

- **Tuning Model**: Random Forest Classifier trained on Spectral Centroid, ZFCR, MFCCs, and Pitch estimates.
- **Music Gen**: Symbolic Music Generation with specialized rule-based progressions and synthesis.

## 🎼 API Endpoints

- `POST /tune`: Upload `.wav` -> Get Tuning Status.
- `POST /generate-music`: Params -> Get Audio/MIDI URL.

---
*Built for Advanced Full-Stack AI Engineering Demo*
