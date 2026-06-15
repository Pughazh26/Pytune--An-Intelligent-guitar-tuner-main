
"""
AI Music Generator V4 - Model-Powered Generation
Uses trained Markov models to generate unique genre-specific music
"""

import numpy as np
import scipy.io.wavfile as wav
from midiutil import MIDIFile
import os
import random
import joblib
from typing import List, Dict, Tuple, Optional
from instrument_dataset import INSTRUMENT_DATASET, InstrumentProfile
from music_generator_v3 import AdvancedInstrumentSynthesizer

# Constants
SAMPLE_RATE = 44100

class AIMusicGeneratorV4:
    """AI Music Generator using trained statistical models"""
    
    def __init__(self, outputs_dir="outputs"):
        self.outputs_dir = outputs_dir
        os.makedirs(outputs_dir, exist_ok=True)
        
        self.synthesizer = AdvancedInstrumentSynthesizer()
        self.dataset = INSTRUMENT_DATASET
        
        # Load the trained AI model
        model_path = os.path.join(os.path.dirname(__file__), "models", "music_ai_model.pkl")
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"AI Music Model loaded from {model_path}")
        else:
            self.model = {}
            print("Warning: AI Music Model not found. Using fallback logic.")
            
        self.scales = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10],
            'pentatonic': [0, 2, 4, 7, 9],
            'blues': [0, 3, 5, 6, 7, 10],
        }
        
        # Genre specific progressions
        self.genre_progressions = {
            'Pop': [[[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]],
            'Jazz': [[[2, 5, 9, 12], [7, 11, 14, 17], [0, 4, 7, 11]]],
            'Rock': [[[0, 7, 12], [5, 12, 17], [7, 14, 19]]],
            'EDM': [[[0, 3, 7], [5, 8, 12], [10, 14, 17]]],
            'Classical': [[[0, 4, 7], [5, 9, 12], [7, 11, 14]]]
        }

    def _get_next_ai_state(self, genre, mood, instrument, curr_state):
        genre_model = self.model.get(genre, {})
        mood_model = genre_model.get(mood, {})
        inst_model = mood_model.get(instrument, {})
        transitions = inst_model.get(curr_state, {})
        
        if not transitions:
            return None
        
        # Weighted random choice based on probabilities
        next_states = list(transitions.keys())
        probs = list(transitions.values())
        return random.choices(next_states, weights=probs)[0]

    def generate_music(self, 
                      genre: str = "Pop",
                      tempo: int = 120,
                      duration: int = 10,
                      mood: str = "Happy",
                      instruments: Optional[List[str]] = None,
                      root_note: int = 60) -> Dict:
        
        if instruments is None or len(instruments) == 0:
            instruments = self._select_instruments_for_genre(genre)
            
        print(f"\nAI V4: Generating {genre} music ({mood})...")
        
        beat_duration = 60.0 / tempo
        num_bars = max(1, int(duration / (beat_duration * 4)))
        
        midi = MIDIFile(len(instruments))
        instrument_tracks = {}
        
        # Logic for each instrument
        for track_idx, instrument_name in enumerate(instruments):
            profile = self.dataset.get_instrument(instrument_name)
            midi.addTrackName(track_idx, 0, profile.name)
            midi.addProgramChange(track_idx, 0, 0, profile.midi_program)
            midi.addTempo(track_idx, 0, tempo)
            
            # Use AI model for melodic instruments
            if profile.category in ['melodic', 'harmonic']:
                audio = self._generate_ai_melodic_track(instrument_name, genre, mood, num_bars, beat_duration, root_note)
            elif profile.category == 'bass':
                audio = self._generate_bass_track(instrument_name, genre, num_bars, beat_duration, root_note)
            else:  # percussion
                audio = self._generate_drum_track(instrument_name, genre, num_bars, beat_duration)
                
            instrument_tracks[instrument_name] = audio
            
        # Mix and save
        mixed_audio = self._mix_tracks(instrument_tracks)
        timestamp = int(np.random.random() * 1000000)
        audio_filename = f"AI_{genre}_{timestamp}.wav"
        midi_filename = f"AI_{genre}_{timestamp}.mid"
        
        audio_path = os.path.join(self.outputs_dir, audio_filename)
        midi_path = os.path.join(self.outputs_dir, midi_filename)
        wav.write(audio_path, SAMPLE_RATE, mixed_audio)
        with open(midi_path, 'wb') as f:
            midi.writeFile(f)
        
        return {
            'audio_url': f'/outputs/{audio_filename}',
            'midi_url': f'/outputs/{midi_filename}',
            'audio_path': audio_path,
            'midi_path': midi_path,
            'genre': genre,
            'instruments': instruments
        }

    def _generate_ai_melodic_track(self, instrument_name, genre, mood, num_bars, beat_duration, root_note):
        total_samples = int(num_bars * 4 * beat_duration * SAMPLE_RATE)
        audio = np.zeros(total_samples)
        
        # Start state
        curr_state = (0, 0.5)
        curr_time = 0.0
        
        scale_type = self._get_scale_for_mood(mood, genre)
        scale = self.scales.get(scale_type, self.scales['major'])
        
        while curr_time < (num_bars * 4 * beat_duration):
            next_state = self._get_next_ai_state(genre, mood, 'melodic', curr_state)
            
            if next_state is None:
                # Fallback: Pick a random note from scale
                note_off = random.choice(scale)
                dur = random.choice([0.25, 0.5, 1.0])
                next_state = (note_off, dur)
            
            note_off, dur = next_state
            freq = 440.0 * (2.0 ** ((root_note + note_off + 12 - 69) / 12.0))
            
            note_audio = self.synthesizer.synthesize(instrument_name, freq, dur * beat_duration * 0.9, 0.7)
            
            start_idx = int(curr_time * SAMPLE_RATE)
            end_idx = min(start_idx + len(note_audio), len(audio))
            audio[start_idx:end_idx] += note_audio[:end_idx-start_idx]
            
            curr_time += dur * beat_duration
            curr_state = next_state # Move forward in Markox chain
            
        return audio

    def _generate_bass_track(self, instrument_name, genre, num_bars, beat_duration, root_note):
        # Bass often plays roots. Simple logic but keeps it distinct.
        audio = np.zeros(int(num_bars * 4 * beat_duration * SAMPLE_RATE))
        for bar in range(num_bars):
            note = root_note - 12 # Octave lower
            freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
            for beat in range(4):
                dur = beat_duration
                if genre == 'Rock': dur = beat_duration / 2
                
                note_audio = self.synthesizer.synthesize(instrument_name, freq, dur * 0.8, 0.8)
                start = int((bar * 4 * beat_duration + beat * beat_duration) * SAMPLE_RATE)
                end = min(start + len(note_audio), len(audio))
                audio[start:end] += note_audio[:end-start]
        return audio

    def _generate_drum_track(self, instrument_name, genre, num_bars, beat_duration):
        audio = np.zeros(int(num_bars * 4 * beat_duration * SAMPLE_RATE))
        pattern = []
        if genre == 'EDM':
            pattern = [('kick', 0), ('hihat', 2), ('snare', 4), ('hihat', 6), ('kick', 8), ('hihat', 10), ('snare', 12), ('hihat', 14)]
        elif genre == 'Rock':
            pattern = [('kick', 0), ('hihat', 2), ('snare', 4), ('hihat', 6), ('kick', 8), ('hihat', 10), ('snare', 12), ('hihat', 14)]
        elif genre == 'Jazz':
            pattern = [('hihat', 0), ('kick', 2), ('hihat', 4), ('snare', 6), ('hihat', 8), ('kick', 10), ('hihat', 12), ('snare', 14)]
        else:  # Pop and generic
            pattern = [('kick', 0), ('hihat', 2), ('snare', 4), ('hihat', 6), ('kick', 8), ('hihat', 10), ('snare', 12), ('hihat', 14)]

        for bar in range(num_bars):
            for sound, step in pattern:
                time = (bar * 4 + (step / 4)) * beat_duration
                start = int(time * SAMPLE_RATE)
                if sound == 'kick':
                    piece = self.synthesizer.synthesize(instrument_name, 60, 0.12, 0.95)
                    audio[start:start+len(piece)] += piece * 0.85
                elif sound == 'snare':
                    piece = self.synthesizer.synthesize(instrument_name, 220, 0.12, 0.75)
                    audio[start:start+len(piece)] += piece * 0.55
                elif sound == 'hihat':
                    piece = self.synthesizer.synthesize(instrument_name, 5000, 0.06, 0.6)
                    audio[start:start+len(piece)] += piece * 0.35
        return audio

    def _select_instruments_for_genre(self, genre: str):
        if genre == 'Jazz': return ['piano', 'upright_bass', 'drums', 'saxophone']
        if genre == 'Pop': return ['electric_piano', 'bass', 'drums', 'synth']
        if genre == 'Rock': return ['electric_guitar', 'bass', 'drums', 'organ']
        if genre == 'EDM': return ['synth', 'pad', 'bass', 'drums']
        if genre == 'Classical': return ['piano', 'violin', 'cello', 'flute']
        return ['piano', 'bass', 'drums']

    def _get_scale_for_mood(self, mood: str, genre: str) -> str:
        if genre == 'Jazz':
            return 'dorian' if mood in ['Calm', 'Sad'] else 'mixolydian'
        if genre == 'EDM':
            return 'minor' if mood in ['Dark', 'Energetic'] else 'major'
        if mood == 'Happy':
            return 'major'
        if mood == 'Sad':
            return 'minor'
        if mood == 'Energetic':
            return 'pentatonic'
        if mood == 'Calm':
            return 'lydian'
        return 'major'

    def _mix_tracks(self, tracks: Dict[str, np.ndarray]) -> np.ndarray:
        max_len = max(len(t) for t in tracks.values())
        mixed = np.zeros(max_len)
        for t in tracks.values():
            mixed[:len(t)] += t
        
        max_v = np.max(np.abs(mixed))
        if max_v > 0: mixed = mixed / max_v * 0.9
        return (mixed * 32767).astype(np.int16)

if __name__ == "__main__":
    gen = AIMusicGeneratorV4()
    for g in ['Pop', 'Jazz', 'Rock', 'EDM', 'Classical']:
        gen.generate_music(genre=g, duration=5)
