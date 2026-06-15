# MIDI Dataset Integration Guide

## Overview

This guide explains how to use your MIDI files to enhance the music generator.

## Current Implementation

The `EnhancedMusicGenerator` class already has MIDI dataset support built-in:

```python
class EnhancedMusicGenerator:
    def __init__(self, outputs_dir="outputs", midi_dataset_dir=None):
        self.midi_dataset_dir = midi_dataset_dir
        self.midi_patterns = []
        
        if midi_dataset_dir and os.path.exists(midi_dataset_dir):
            self._load_midi_patterns()
```

## How to Use Your MIDI Files

### Step 1: Organize Your MIDI Files

Create a folder structure like this:

```
pytune/
└── ml/
    └── data/
        └── midi/
            ├── piano/
            │   ├── pattern1.mid
            │   ├── pattern2.mid
            │   └── ...
            ├── guitar/
            │   ├── riff1.mid
            │   ├── riff2.mid
            │   └── ...
            ├── drums/
            │   ├── beat1.mid
            │   ├── beat2.mid
            │   └── ...
            └── bass/
                ├── line1.mid
                ├── line2.mid
                └── ...
```

### Step 2: Initialize Generator with Dataset

```python
from ml.music_generator_v2 import EnhancedMusicGenerator

gen = EnhancedMusicGenerator(
    outputs_dir="outputs",
    midi_dataset_dir=r"c:\Users\chinn\OneDrive\Documents\Gen music\pytune\ml\data\midi"
)

# The generator will automatically load MIDI files
# Output: "Found 150 MIDI files in dataset"
```

### Step 3: Generate Music

The generator will use patterns from your MIDI files:

```python
result = gen.generate_music(
    genre="Pop",
    tempo=120,
    mood="Happy",
    instruments=['piano', 'bass', 'drums']
)
```

## Advanced: MIDI Pattern Analysis

### Reading MIDI Files

To analyze and use MIDI patterns, you can extend the generator:

```python
from mido import MidiFile

def analyze_midi_pattern(midi_path):
    """Extract notes, timing, and patterns from MIDI file"""
    mid = MidiFile(midi_path)
    
    notes = []
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on':
                notes.append({
                    'note': msg.note,
                    'velocity': msg.velocity,
                    'time': msg.time
                })
    
    return notes

# Use in generator
def _load_midi_patterns(self):
    midi_files = glob.glob(os.path.join(self.midi_dataset_dir, "**/*.mid"), recursive=True)
    
    for midi_file in midi_files:
        pattern = analyze_midi_pattern(midi_file)
        self.midi_patterns.append({
            'file': midi_file,
            'pattern': pattern,
            'instrument': self._detect_instrument(midi_file)
        })
```

### Pattern-Based Generation

You can modify the generator to use learned patterns:

```python
def generate_from_pattern(self, pattern_type='chord_progression'):
    """Generate music based on learned MIDI patterns"""
    
    # Select random pattern from dataset
    pattern = random.choice(self.midi_patterns)
    
    # Extract chord progression
    chords = self._extract_chords(pattern)
    
    # Generate new music with similar structure
    return self.generate_music_from_chords(chords)
```

## MIDI File Requirements

### Supported Formats
- ✅ Standard MIDI File (.mid, .midi)
- ✅ Type 0 (single track) and Type 1 (multi-track)
- ✅ Any tempo/time signature

### Recommended Structure
- **Piano MIDI**: Chord progressions, melodies
- **Guitar MIDI**: Riffs, arpeggios
- **Drum MIDI**: Rhythm patterns
- **Bass MIDI**: Bass lines

### Quality Tips
1. **Clean MIDI**: Remove unnecessary tracks
2. **Quantize**: Align notes to grid for pattern extraction
3. **Normalize**: Consistent velocity ranges
4. **Label**: Use descriptive filenames (e.g., `pop_happy_progression.mid`)

## Example: Using MIDI Patterns

### 1. Extract Chord Progressions

```python
def extract_chord_progression(midi_file):
    """Extract chord progression from MIDI file"""
    from mido import MidiFile
    
    mid = MidiFile(midi_file)
    chords = []
    
    for track in mid.tracks:
        current_chord = []
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                current_chord.append(msg.note)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if current_chord:
                    chords.append(sorted(current_chord))
                    current_chord = []
    
    return chords
```

### 2. Learn Drum Patterns

```python
def extract_drum_pattern(midi_file):
    """Extract drum pattern from MIDI file"""
    from mido import MidiFile
    
    mid = MidiFile(midi_file)
    
    # MIDI drum mapping (General MIDI)
    drum_map = {
        36: 'kick',
        38: 'snare',
        42: 'hihat_closed',
        46: 'hihat_open'
    }
    
    pattern = {drum: [] for drum in drum_map.values()}
    
    current_time = 0
    for track in mid.tracks:
        for msg in track:
            current_time += msg.time
            if msg.type == 'note_on' and msg.note in drum_map:
                drum_type = drum_map[msg.note]
                pattern[drum_type].append(current_time)
    
    return pattern
```

### 3. Generate with Learned Patterns

```python
class EnhancedMusicGenerator:
    def generate_with_midi_patterns(self, genre, tempo, duration):
        """Generate music using patterns from MIDI dataset"""
        
        # Find similar patterns
        genre_patterns = [p for p in self.midi_patterns 
                         if genre.lower() in p['file'].lower()]
        
        if genre_patterns:
            # Use learned chord progression
            pattern = random.choice(genre_patterns)
            chords = self._extract_chords(pattern)
            
            # Generate with learned structure
            return self._generate_from_chords(chords, tempo, duration)
        else:
            # Fall back to algorithmic generation
            return self.generate_music(genre, tempo, duration)
```

## Installing MIDI Processing Library

To read MIDI files, install `mido`:

```bash
pip install mido
```

## Dataset Recommendations

### Where to Find MIDI Files

1. **Your own compositions** - Best for your style
2. **Public domain MIDI** - Classical music, folk songs
3. **Creative Commons** - Free MIDI libraries
4. **Generate synthetic** - Use DAW to create training data

### Dataset Size

- **Minimum**: 10-20 files per genre
- **Recommended**: 50-100 files per genre
- **Optimal**: 200+ files per genre

### Organization

```
midi/
├── by_genre/
│   ├── pop/
│   ├── rock/
│   ├── jazz/
│   └── edm/
├── by_instrument/
│   ├── piano/
│   ├── guitar/
│   ├── bass/
│   └── drums/
└── by_mood/
    ├── happy/
    ├── sad/
    ├── energetic/
    └── chill/
```

## Future Enhancements

### ML-Based Pattern Learning

```python
# Train a model on MIDI patterns
from sklearn.cluster import KMeans

def learn_patterns(midi_patterns):
    """Cluster similar patterns"""
    features = [extract_features(p) for p in midi_patterns]
    kmeans = KMeans(n_clusters=10)
    clusters = kmeans.fit_predict(features)
    return clusters

# Generate new patterns
def generate_new_pattern(cluster_id):
    """Generate new pattern similar to cluster"""
    similar_patterns = get_patterns_in_cluster(cluster_id)
    # Interpolate or combine patterns
    return create_variation(similar_patterns)
```

### Markov Chain Generation

```python
def build_markov_chain(midi_patterns):
    """Build Markov chain from chord progressions"""
    transitions = {}
    
    for pattern in midi_patterns:
        chords = extract_chords(pattern)
        for i in range(len(chords) - 1):
            current = chords[i]
            next_chord = chords[i + 1]
            
            if current not in transitions:
                transitions[current] = []
            transitions[current].append(next_chord)
    
    return transitions

def generate_progression(transitions, length=8):
    """Generate new progression using Markov chain"""
    progression = [random.choice(list(transitions.keys()))]
    
    for _ in range(length - 1):
        current = progression[-1]
        if current in transitions:
            next_chord = random.choice(transitions[current])
            progression.append(next_chord)
    
    return progression
```

## Troubleshooting

**Issue**: MIDI files not loading
- Check file path is correct
- Ensure files have `.mid` or `.midi` extension
- Verify files are valid MIDI format

**Issue**: Out of memory
- Limit to 50 files: `self.midi_patterns = midi_files[:50]`
- Process files in batches
- Extract features instead of loading full files

**Issue**: Patterns don't match genre
- Organize files by genre in folders
- Use filename filtering
- Manual curation of dataset

## Example Complete Integration

```python
# Complete example with MIDI dataset
from ml.music_generator_v2 import EnhancedMusicGenerator
import os

# Setup
midi_dir = r"c:\Users\chinn\OneDrive\Documents\Gen music\pytune\ml\data\midi"
output_dir = r"c:\Users\chinn\OneDrive\Documents\Gen music\pytune\outputs"

# Initialize with dataset
gen = EnhancedMusicGenerator(
    outputs_dir=output_dir,
    midi_dataset_dir=midi_dir
)

# Generate music
result = gen.generate_music(
    genre="Pop",
    tempo=120,
    mood="Happy",
    duration=15,
    instruments=['piano', 'bass', 'drums', 'synth']
)

print(f"Generated: {result['audio_url']}")
print(f"MIDI: {result['midi_url']}")
print(f"Instruments: {result['instruments']}")
```

---

**Ready to use your MIDI dataset!** Place your MIDI files in the appropriate folder and start generating! 🎵
