# Comprehensive Instrument Dataset Documentation

## Overview

The PYTUNE project now includes a **comprehensive instrument dataset** with detailed profiles for **20+ musical instruments** across all major categories. Each instrument has scientifically-accurate specifications for realistic music generation.

## Instrument Categories

### 1. **Keyboard Instruments** (3 instruments)
- **Piano** - Acoustic grand piano with rich harmonics
- **Electric Piano** - Classic electric piano (Rhodes/Wurlitzer style)
- **Organ** - Drawbar organ with sustained tones

### 2. **String Instruments** (4 instruments)
- **Acoustic Guitar** - Nylon/steel string guitar
- **Electric Guitar** - Clean electric guitar
- **Violin** - Classical violin with vibrato
- **Cello** - Deep, warm cello tones

### 3. **Bass Instruments** (2 instruments)
- **Bass Guitar** - Electric bass (finger style)
- **Upright Bass** - Acoustic double bass

### 4. **Brass Instruments** (3 instruments)
- **Trumpet** - Bright, brassy trumpet
- **Trombone** - Warm trombone tones
- **Saxophone** - Alto/tenor saxophone

### 5. **Woodwind Instruments** (2 instruments)
- **Flute** - Airy, bright flute
- **Clarinet** - Warm clarinet with odd harmonics

### 6. **Synthesizers** (2 instruments)
- **Synth Lead** - Electronic lead synthesizer
- **Synth Pad** - Atmospheric pad sounds

### 7. **Percussion** (3 instruments)
- **Drum Kit** - Complete drum set (kick, snare, hi-hat)
- **Congas** - Latin percussion
- **Marimba** - Wooden mallet percussion

---

## Instrument Profile Structure

Each instrument has the following specifications:

```python
@dataclass
class InstrumentProfile:
    name: str                          # Display name
    category: str                      # melodic, harmonic, bass, percussion
    frequency_range: Tuple[float, float]  # Min/max frequency in Hz
    harmonics: List[Tuple[int, float]]    # Harmonic series
    adsr: Dict[str, float]                # Envelope (Attack, Decay, Sustain, Release)
    timbre_characteristics: Dict          # Brightness, warmth, etc.
    midi_program: int                     # General MIDI program number
    typical_genres: List[str]             # Associated genres
    velocity_sensitivity: float           # 0.0 to 1.0
```

---

## Example: Piano Profile

```python
instruments['piano'] = InstrumentProfile(
    name='Piano',
    category='harmonic',
    frequency_range=(27.5, 4186.0),  # A0 to C8
    harmonics=[
        (1, 1.0),   # Fundamental
        (2, 0.6),   # 2nd harmonic
        (3, 0.4),   # 3rd harmonic
        (4, 0.25),  # 4th harmonic
        (5, 0.15),  # 5th harmonic
        (6, 0.1),   # 6th harmonic
    ],
    adsr={'attack': 0.01, 'decay': 0.1, 'sustain': 0.7, 'release': 0.3},
    timbre_characteristics={
        'brightness': 0.7,
        'warmth': 0.6,
        'percussiveness': 0.8,
        'resonance': 0.9
    },
    midi_program=0,  # Acoustic Grand Piano
    typical_genres=['Classical', 'Jazz', 'Pop', 'Blues'],
    velocity_sensitivity=0.9
)
```

---

## Usage

### 1. **Import the Dataset**

```python
from ml.instrument_dataset import INSTRUMENT_DATASET

# List all instruments
instruments = INSTRUMENT_DATASET.list_all_instruments()
print(instruments)
# Output: ['piano', 'electric_piano', 'organ', 'guitar', ...]
```

### 2. **Get Instrument Information**

```python
# Get detailed info about an instrument
piano_info = INSTRUMENT_DATASET.get_instrument_info('piano')
print(piano_info)

# Get instrument profile
piano = INSTRUMENT_DATASET.get_instrument('piano')
print(f"Frequency range: {piano.frequency_range}")
print(f"MIDI program: {piano.midi_program}")
```

### 3. **Filter by Category**

```python
# Get all melodic instruments
melodic = INSTRUMENT_DATASET.get_instruments_by_category('melodic')
for inst in melodic:
    print(inst.name)
# Output: Violin, Cello, Trumpet, Trombone, Saxophone, Flute, Clarinet, Synth Lead
```

### 4. **Filter by Genre**

```python
# Get instruments suitable for Jazz
jazz_instruments = INSTRUMENT_DATASET.get_instruments_by_genre('Jazz')
for inst in jazz_instruments:
    print(inst.name)
# Output: Piano, Electric Piano, Organ, Saxophone, Trumpet, Bass Guitar, etc.
```

---

## Music Generation with All Instruments

### Using the Comprehensive Generator

```python
from ml.music_generator_v3 import ComprehensiveMusicGenerator

gen = ComprehensiveMusicGenerator(outputs_dir="outputs")

# Generate Pop music with specific instruments
result = gen.generate_music(
    genre="Pop",
    tempo=120,
    duration=15,
    mood="Happy",
    instruments=['piano', 'bass', 'drums', 'synth']
)

# Generate Jazz with brass section
result = gen.generate_music(
    genre="Jazz",
    tempo=140,
    duration=15,
    mood="Energetic",
    instruments=['piano', 'bass', 'drums', 'saxophone', 'trumpet']
)

# Generate Classical with strings
result = gen.generate_music(
    genre="Classical",
    tempo=90,
    duration=15,
    mood="Calm",
    instruments=['piano', 'violin', 'cello', 'flute']
)
```

### Auto-Select Instruments by Genre

```python
# Let the generator choose instruments based on genre
result = gen.generate_music(genre="Rock", tempo=130, duration=15)
# Automatically uses: electric_guitar, bass, drums, organ
```

---

## Genre-Instrument Mapping

| Genre | Default Instruments |
|-------|-------------------|
| **Pop** | piano, bass, drums, synth |
| **Jazz** | piano, bass, drums, saxophone, trumpet |
| **Rock** | electric_guitar, bass, drums, organ |
| **Classical** | piano, violin, cello, flute |
| **EDM** | synth, bass, drums, pad |
| **Blues** | guitar, bass, drums, saxophone |
| **Funk** | electric_guitar, bass, drums, electric_piano |
| **Ambient** | pad, piano, flute |

---

## Advanced Features

### 1. **Harmonic Synthesis**

Each instrument uses its unique harmonic series for realistic timbre:

```python
# Piano has 6 harmonics with decreasing amplitude
harmonics=[
    (1, 1.0),   # Fundamental (100%)
    (2, 0.6),   # 2nd harmonic (60%)
    (3, 0.4),   # 3rd harmonic (40%)
    ...
]

# Clarinet emphasizes odd harmonics (characteristic of reed instruments)
harmonics=[
    (1, 1.0),   # Fundamental
    (3, 0.6),   # 3rd harmonic (no 2nd!)
    (5, 0.4),   # 5th harmonic
    (7, 0.2),   # 7th harmonic
]
```

### 2. **ADSR Envelope**

Each instrument has a unique envelope shape:

```python
# Piano: Quick attack, medium decay
adsr={'attack': 0.01, 'decay': 0.1, 'sustain': 0.7, 'release': 0.3}

# Pad: Slow attack, long release (atmospheric)
adsr={'attack': 0.3, 'decay': 0.2, 'sustain': 0.9, 'release': 0.5}

# Drums: Instant attack, no sustain
adsr={'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.1}
```

### 3. **Timbre Characteristics**

Instruments have unique timbral qualities:

```python
timbre_characteristics={
    'brightness': 0.7,    # High-frequency content
    'warmth': 0.6,        # Low-frequency richness
    'percussiveness': 0.8, # Attack sharpness
    'resonance': 0.9,     # Sustain and reverb
    'vibrato': 0.7        # Pitch modulation (strings)
}
```

---

## API Integration

### Backend Endpoint

The backend now supports all instruments:

```python
POST /api/generate-music
{
    "genre": "Jazz",
    "tempo": 140,
    "duration": 15,
    "mood": "Energetic",
    "instruments": ["piano", "saxophone", "trumpet", "bass", "drums"]
}
```

### Response

```json
{
    "audio_url": "/outputs/Jazz_Energetic_140bpm_123456.wav",
    "midi_url": "/outputs/Jazz_Energetic_140bpm_123456.mid",
    "instruments": ["piano", "saxophone", "trumpet", "bass", "drums"],
    "genre": "Jazz",
    "tempo": 140,
    "duration": 15.2
}
```

---

## Testing the Dataset

Run the instrument dataset demo:

```bash
cd ml
python instrument_dataset.py
```

Output:
```
============================================================
COMPREHENSIVE INSTRUMENT DATASET
============================================================

Total Instruments: 20

--- All Instruments ---
  • Bass Guitar        [bass        ] - Rock, Jazz, Funk
  • Cello              [melodic     ] - Classical, Film Score
  • Clarinet           [melodic     ] - Classical, Jazz, Klezmer
  ...

--- Instruments by Category ---

MELODIC: 8 instruments
  • Violin
  • Cello
  • Trumpet
  ...
```

---

## Testing the Generator

Run the comprehensive generator:

```bash
cd ml
python music_generator_v3.py
```

This will generate 4 test tracks:
1. **Pop** - piano, bass, drums, synth
2. **Jazz** - piano, bass, drums, saxophone, trumpet
3. **Classical** - piano, violin, cello, flute
4. **Rock** - electric_guitar, bass, drums, organ

---

## Complete Instrument List

```
Keyboard:
  • piano
  • electric_piano
  • organ

Strings:
  • guitar
  • electric_guitar
  • violin
  • cello

Bass:
  • bass
  • upright_bass

Brass:
  • trumpet
  • trombone
  • saxophone

Woodwinds:
  • flute
  • clarinet

Synthesizers:
  • synth
  • pad

Percussion:
  • drums
  • congas
  • marimba
```

---

## Future Enhancements

### Planned Features

1. **More Instruments**
   - Harp, Banjo, Ukulele
   - French Horn, Tuba
   - Oboe, Bassoon
   - Steel Drums, Timpani

2. **Advanced Synthesis**
   - Physical modeling
   - Sample-based synthesis
   - FM synthesis for electric pianos

3. **Articulations**
   - Staccato, legato, pizzicato
   - Vibrato control
   - Glissando, bends

4. **Effects**
   - Reverb, delay, chorus
   - Distortion for guitars
   - Compression

---

## Technical Details

### Frequency Ranges

| Instrument | Range (Hz) | MIDI Notes |
|------------|-----------|------------|
| Piano | 27.5 - 4186 | A0 - C8 |
| Guitar | 82.4 - 880 | E2 - A5 |
| Bass | 41.2 - 392 | E1 - G4 |
| Violin | 196 - 3520 | G3 - A7 |
| Trumpet | 164.8 - 1046.5 | E3 - C6 |
| Flute | 261.6 - 2093 | C4 - C7 |

### Sample Rate

All audio generated at **44,100 Hz** (CD quality)

### MIDI Compatibility

All instruments mapped to General MIDI standard for maximum compatibility.

---

## Conclusion

The comprehensive instrument dataset provides:

✅ **20+ instruments** across all major categories  
✅ **Scientifically accurate** harmonic profiles  
✅ **Realistic synthesis** with ADSR and timbre shaping  
✅ **Genre-aware** instrument selection  
✅ **Full MIDI support** for external use  
✅ **Extensible architecture** for adding more instruments  

**Start creating music with any combination of instruments!** 🎵🎸🎹🎺🥁
