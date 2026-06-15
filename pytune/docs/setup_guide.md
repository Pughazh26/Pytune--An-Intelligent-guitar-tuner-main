# Setup Guide

## System Requirements
- OS: Windows, macOS, or Linux
- Python: Version 3.8 or higher
- Node.js: Version 16 or higher (for frontend)

## Installation Steps

1. **Clone/Unzip**: Extract the project to your desired location.
2. **Backend Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **ML Training**:
   Before running the app, you must train the models.
   ```bash
   cd ml
   python dataset_generator.py
   python train_tuner.py
   ```
4. **Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   ```
   *Note: If `npm` is not found, please install Node.js from nodejs.org*

## Running the Application

You need two terminals.

**Terminal 1 (Backend)**:
```bash
cd backend
python app.py
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

Open your browser to the URL shown in the frontend terminal (usually `http://localhost:5173`).
