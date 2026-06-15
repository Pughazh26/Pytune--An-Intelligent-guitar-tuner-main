# API Documentation

## Base URL
`http://localhost:8000`

## Endpoints

### 1. Tune Guitar

Analyzes an audio file and returns tuning information.

- **URL**: `/tune`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `file`: Audio file (.wav, .mp3)

**Response**:
```json
{
  "detected_pitch": "A2",
  "frequency": 110.05,
  "tuning_offset_cents": 0.8,
  "tuning_status": "In-Tune",
  "confidence": 0.98
}
```

### 2. Generate Music

Generates a new music track.

- **URL**: `/generate-music`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**:
```json
{
    "genre": "Pop",
    "tempo": 120,
    "mood": "Happy",
    "duration": 15
}
```

**Response**:
```json
{
  "genre": "Pop",
  "audio_url": "http://localhost:8000/outputs/pop_happy_1234.wav",
  "midi_url": "http://localhost:8000/outputs/pop_happy_1234.mid"
}
```

### 3. Dashboard Metrics

Get system statistics.

- **URL**: `/dashboard-metrics`
- **Method**: `GET`
