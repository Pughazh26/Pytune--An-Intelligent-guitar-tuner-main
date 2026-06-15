# Enhanced Multi-Instrument Music Generator

## Overview

The PYTUNE music generator has been upgraded with **advanced multi-instrument synthesis** capabilities! You can now create rich, layered music with realistic instrument sounds including:

- 🎹 **Piano** - Rich harmonics with realistic ADSR envelope
- 🎸 **Guitar** - Plucked acoustic guitar with body resonance
- 🎸 **Bass** - Deep, punchy bass guitar
- 🥁 **Drums** - Kick, snare, and hi-hat with genre-specific patterns
- 🎛️ **Synth Lead** - Sawtooth wave synthesizer with vibrato
- 🌊 **Pad** - Ambient atmospheric sounds

## New Features

### 1. **Realistic Instrument Synthesis**

Each instrument uses advanced synthesis techniques:

- **ADSR Envelopes**: Attack, Decay, Sustain, Release for natural sound shaping
- **Harmonic Overtones**: Multiple harmonics for rich, realistic timbres
- **Physical Modeling**: Guitar pluck simulation, drum pitch envelopes
- **Detuning**: Slight pitch variations for organic warmth

### 2. **Genre-Specific Arrangements**

The generator automatically selects appropriate instruments for each genre:

| Genre    | Default Instruments          |
|----------|------------------------------|
| Pop      | Piano, Bass, Drums, Synth    |
| Jazz     | Piano, Bass, Drums           |
| EDM      | Synth, Bass, Drums, Pad      |
| Lo-fi    | Piano, Bass, Drums           |
| Acoustic | Guitar, Bass, Drums          |
| Rock     | Guitar, Bass, Drums          |

### 3. **Custom Instrument Selection**

You can now manually select which instruments to include in your track!

**Frontend UI**: Toggle buttons for each instrument
**API Parameter**: `instruments` array (e.g., `['piano', 'guitar', 'drums']`)

### 4. **Advanced Drum Patterns**

Genre-specific drum patterns with:
- **Kick drum**: Synthesized with pitch envelope (150Hz → 40Hz)
- **Snare**: Tone + noise blend for realistic snap
- **Hi-hat**: High-pass filtered noise with open/closed variations

Patterns adapt to genre:
- **EDM**: Four-on-the-floor kick pattern
- **Jazz**: Swing rhythm
- **Pop**: Standard backbeat
- **Lo-fi**: Laid-back groove

### 5. **Musical Intelligence**

- **Chord Progressions**: Genre and mood-specific progressions
  - Happy Pop: I-V-vi-IV
  - Sad: i-VI-iv-V
  - Jazz: i-iv-V-ii
  
- **Scales**: Automatic major/minor scale selection
- **Voicing**: Piano plays chords, guitar arpeggios, bass plays roots
- **Melody**: Synth generates melodic lines based on scale

## Usage

### Python API

```python
from ml.music_generator_v2 import EnhancedMusicGenerator

gen = EnhancedMusicGenerator(outputs_dir="outputs")

# Generate with specific instruments
result = gen.generate_music(
    genre="Rock",
    tempo=140,
    duration=10,
    mood="Energetic",
    instruments=['guitar', 'bass', 'drums']  # Custom selection
)

# Or let it auto-select based on genre
result = gen.generate_music(
    genre="EDM",
    tempo=128,
    duration=15,
    mood="Energetic"
    # instruments=None will use EDM defaults: synth, bass, drums, pad
)
```

### REST API

**Endpoint**: `POST /generate-music`

**Request Body**:
```json
{
  "genre": "Pop",
  "tempo": 120,
  "mood": "Happy",
  "duration": 10,
  "instruments": ["piano", "bass", "drums", "synth"]
}
```

**Response**:
```json
{
  "genre": "Pop",
  "audio_url": "http://localhost:8000/outputs/pop_happy_1234.wav",
  "midi_url": "http://localhost:8000/outputs/pop_happy_1234.mid",
  "instruments": ["piano", "bass", "drums", "synth"]
}
```

### Frontend UI

1. Navigate to the **Music Generator** page
2. Select your **Genre** (Pop, Jazz, EDM, etc.)
3. Choose a **Mood** (Happy, Sad, Energetic, etc.)
4. Adjust **Tempo** (60-180 BPM) and **Duration** (5-60 seconds)
5. **Toggle instruments** - Click to select/deselect instruments
6. Click **GENERATE TRACK**

The UI will show which instruments are active with highlighted buttons!

## Technical Details

### Synthesis Architecture

```
InstrumentSynthesizer
├── Piano: Harmonic synthesis + detuning
├── Guitar: Harmonic synthesis + pluck noise
├── Bass: Low harmonics + punchy envelope
├── Synth: Sawtooth wave + vibrato
├── Pad: Multi-harmonic + long attack/release
└── Drums
    ├── Kick: Pitch envelope + click transient
    ├── Snare: Tone + noise blend
    └── Hi-hat: Filtered noise
```

### Audio Processing Pipeline

1. **Note Generation**: MIDI-based note events
2. **Synthesis**: Per-instrument waveform generation
3. **Envelope Shaping**: ADSR applied to each note
4. **Track Mixing**: Individual instrument tracks
5. **Normalization**: Per-track and master limiting
6. **Export**: WAV (audio) + MIDI (notation)

### Sample Rate & Quality

- **Sample Rate**: 44.1 kHz (CD quality)
- **Bit Depth**: 16-bit PCM
- **Format**: WAV (uncompressed)
- **MIDI**: Standard MIDI File Format

## MIDI Dataset Integration

The generator is designed to work with MIDI datasets:

```python
gen = EnhancedMusicGenerator(
    outputs_dir="outputs",
    midi_dataset_dir="path/to/midi/files"  # Optional
)
```

When a MIDI dataset directory is provided:
- Loads up to 50 MIDI files for pattern analysis
- Can be extended to learn chord progressions
- Future: ML-based pattern generation from dataset

## File Structure

```
pytune/
├── ml/
│   ├── music_generator.py          # Original simple generator
│   ├── music_generator_v2.py       # NEW: Enhanced multi-instrument
│   └── data/                        # Your MIDI dataset goes here
├── backend/
│   └── app.py                       # Updated to use v2 generator
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── MusicGenerator.tsx   # Updated with instrument UI
│       └── services/
│           └── api.ts               # Updated API interface
└── outputs/                         # Generated music files
```

## Examples

### Rock Track
```python
gen.generate_music(
    genre="Rock",
    tempo=140,
    mood="Energetic",
    instruments=['guitar', 'bass', 'drums']
)
```
- Guitar: Arpeggiated power chords
- Bass: Root notes on beats
- Drums: Driving rock pattern

### Ambient Pad
```python
gen.generate_music(
    genre="EDM",
    tempo=90,
    mood="Chill",
    instruments=['pad', 'bass']
)
```
- Pad: Lush atmospheric chords
- Bass: Subtle low-end support

### Jazz Piano Trio
```python
gen.generate_music(
    genre="Jazz",
    tempo=110,
    mood="Chill",
    instruments=['piano', 'bass', 'drums']
)
```
- Piano: Jazz chord voicings
- Bass: Walking bass lines
- Drums: Swing pattern

## Future Enhancements

Potential additions:
- [ ] Sample-based synthesis using your MIDI dataset
- [ ] ML-based melody generation
- [ ] Rhythm variation and fills
- [ ] More instrument types (strings, brass, etc.)
- [ ] Effects processing (reverb, delay, compression)
- [ ] Multi-section song structure (intro, verse, chorus)
- [ ] Real-time MIDI playback in browser

## Performance

- **Generation Speed**: ~1-3 seconds for 10-second track
- **File Size**: ~1-2 MB per minute (WAV)
- **CPU Usage**: Moderate (synthesis is CPU-bound)
- **Memory**: Low (~50-100 MB during generation)

## Troubleshooting

**Issue**: No sound in generated file
- Check that at least one instrument is selected
- Verify output directory exists and is writable

**Issue**: Distorted audio
- Reduce number of simultaneous instruments
- Lower individual instrument volumes in code

**Issue**: MIDI file won't open
- Ensure midiutil is installed: `pip install midiutil`
- Try different MIDI player software

## Credits

- **Synthesis Engine**: Custom Python implementation
- **MIDI Generation**: MIDIUtil library
- **Audio Export**: SciPy wavfile
- **Signal Processing**: NumPy, SciPy

---

**Enjoy creating music with PYTUNE!** 🎵🎸🎹🥁
