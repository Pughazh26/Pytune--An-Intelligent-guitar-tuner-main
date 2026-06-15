"""
Enhanced Music Generator V3 - Using Comprehensive Instrument Dataset
Generates music for all instruments with realistic synthesis
"""

import numpy as np
import scipy.io.wavfile as wav
from midiutil import MIDIFile
import os
import random
from typing import List, Dict, Tuple, Optional
from scipy import signal
from instrument_dataset import INSTRUMENT_DATASET, InstrumentProfile

# Constants
SAMPLE_RATE = 44100


class AdvancedInstrumentSynthesizer:
    """Advanced synthesizer using instrument dataset profiles"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.dataset = INSTRUMENT_DATASET
    
    def _apply_adsr(self, audio: np.ndarray, attack: float, decay: float, 
                    sustain: float, release: float) -> np.ndarray:
        """Apply ADSR envelope to audio signal"""
        n = len(audio)
        envelope = np.ones(n)
        
        # Calculate sample counts for each phase
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        # If total phases > available samples, scale them down proportionally
        total_fixed_samples = attack_samples + decay_samples + release_samples
        if total_fixed_samples > n:
            ratio = n / total_fixed_samples
            attack_samples = int(attack_samples * ratio)
            decay_samples = int(decay_samples * ratio)
            release_samples = n - attack_samples - decay_samples
            sustain_samples = 0
        else:
            sustain_samples = n - attack_samples - decay_samples - release_samples
        
        # Ensure non-negative
        attack_samples = max(0, attack_samples)
        decay_samples = max(0, decay_samples)
        release_samples = max(0, release_samples)
        
        # Re-verify total
        if attack_samples + decay_samples + release_samples > n:
            release_samples = n - attack_samples - decay_samples
            
        # Attack phase
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        if decay_samples > 0:
            start = attack_samples
            end = min(start + decay_samples, n)
            count = end - start
            envelope[start:end] = np.linspace(1, sustain, count)
        
        # Sustain phase (already 1s in initialization, but we need to set value)
        if sustain_samples > 0:
            start = attack_samples + decay_samples
            end = start + sustain_samples
            envelope[start:end] = sustain
        
        # Release phase
        if release_samples > 0:
            start = n - release_samples
            count = n - start
            envelope[start:] = np.linspace(sustain, 0, count)
        
        return audio * envelope
    
    def _generate_harmonic_wave(self, frequency: float, duration: float, 
                               harmonics: List[Tuple[int, float]]) -> np.ndarray:
        """Generate wave with harmonics based on instrument profile"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = np.zeros_like(t)
        
        for harmonic_num, amplitude in harmonics:
            audio += amplitude * np.sin(2 * np.pi * frequency * harmonic_num * t)
        
        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        return audio
    
    def synthesize(self, instrument_name: str, frequency: float, 
                   duration: float, velocity: float = 0.8) -> np.ndarray:
        """Synthesize sound for any instrument using its profile"""
        
        # Get instrument profile
        profile = self.dataset.get_instrument(instrument_name)
        
        # Check frequency is in range
        if not (profile.frequency_range[0] <= frequency <= profile.frequency_range[1]):
            # Transpose to valid range
            while frequency < profile.frequency_range[0]:
                frequency *= 2
            while frequency > profile.frequency_range[1]:
                frequency /= 2
        
        # Generate based on category
        if profile.category == 'percussion':
            audio = self._synthesize_percussion(profile, duration, velocity)
        else:
            audio = self._synthesize_tonal(profile, frequency, duration, velocity)
        
        return audio
    
    def _synthesize_tonal(self, profile: InstrumentProfile, frequency: float,
                         duration: float, velocity: float) -> np.ndarray:
        """Synthesize tonal instruments (melodic, harmonic, bass)"""
        
        # Generate harmonic content
        if profile.harmonics:
            audio = self._generate_harmonic_wave(frequency, duration, profile.harmonics)
        else:
            # Simple sine wave if no harmonics defined
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            audio = np.sin(2 * np.pi * frequency * t)
        
        # Apply timbre characteristics
        audio = self._apply_timbre(audio, profile.timbre_characteristics)
        
        # Apply ADSR envelope
        adsr = profile.adsr
        audio = self._apply_adsr(audio, adsr['attack'], adsr['decay'], 
                                adsr['sustain'], adsr['release'])
        
        # Apply velocity
        velocity_factor = 0.3 + (0.7 * velocity * profile.velocity_sensitivity)
        audio = audio * velocity_factor
        
        return audio
    
    def _synthesize_percussion(self, profile: InstrumentProfile, 
                              duration: float, velocity: float) -> np.ndarray:
        """Synthesize percussion instruments"""
        
        n_samples = int(self.sample_rate * duration)
        
        if 'drum' in profile.name.lower():
            # Drum kit synthesis
            audio = self._synthesize_drum_kit(duration, velocity)
        elif 'conga' in profile.name.lower():
            # Conga synthesis
            audio = self._synthesize_conga(duration, velocity)
        elif 'marimba' in profile.name.lower():
            # Marimba uses tonal synthesis
            freq = 440.0  # Default pitch
            audio = self._synthesize_tonal(profile, freq, duration, velocity)
        else:
            # Generic percussion
            audio = np.random.uniform(-0.5, 0.5, n_samples)
            adsr = profile.adsr
            audio = self._apply_adsr(audio, adsr['attack'], adsr['decay'],
                                    adsr['sustain'], adsr['release'])
        
        return audio * velocity
    
    def _synthesize_drum_kit(self, duration: float, velocity: float) -> np.ndarray:
        """Synthesize drum kit (kick, snare, hihat)"""
        n_samples = int(self.sample_rate * duration)
        audio = np.zeros(n_samples)
        
        # Simple kick drum at start
        kick_duration = min(0.5, duration)
        kick_samples = int(self.sample_rate * kick_duration)
        t = np.linspace(0, kick_duration, kick_samples)
        
        # Kick: pitch envelope from 150Hz to 40Hz
        freq_envelope = 150 * np.exp(-8 * t)
        kick = np.sin(2 * np.pi * np.cumsum(freq_envelope) / self.sample_rate)
        kick *= np.exp(-5 * t)  # Amplitude envelope
        
        audio[:kick_samples] += kick * 0.8
        
        return audio
    
    def _synthesize_conga(self, duration: float, velocity: float) -> np.ndarray:
        """Synthesize conga drum"""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples)
        
        # Pitched noise with resonance
        noise = np.random.uniform(-1, 1, n_samples)
        
        # Resonant frequency around 200Hz
        b, a = signal.butter(4, [180, 220], btype='band', fs=self.sample_rate)
        audio = signal.filtfilt(b, a, noise)
        
        # Envelope
        envelope = np.exp(-5 * t)
        audio *= envelope
        
        return audio
    
    def _apply_timbre(self, audio: np.ndarray, 
                     timbre: Dict[str, float]) -> np.ndarray:
        """Apply timbre characteristics to audio"""
        
        # Brightness: high-pass filter
        if 'brightness' in timbre and timbre['brightness'] > 0.5:
            brightness_factor = (timbre['brightness'] - 0.5) * 2
            cutoff = 500 + (brightness_factor * 1500)
            b, a = signal.butter(2, cutoff, btype='high', fs=self.sample_rate)
            audio = 0.7 * audio + 0.3 * signal.filtfilt(b, a, audio)
        
        # Warmth: low-pass filter
        if 'warmth' in timbre and timbre['warmth'] > 0.5:
            warmth_factor = (timbre['warmth'] - 0.5) * 2
            cutoff = 3000 - (warmth_factor * 1500)
            b, a = signal.butter(2, cutoff, btype='low', fs=self.sample_rate)
            audio = 0.7 * audio + 0.3 * signal.filtfilt(b, a, audio)
        
        # Resonance: add slight reverb
        if 'resonance' in timbre and timbre['resonance'] > 0.7:
            delay_samples = int(0.03 * self.sample_rate)
            delayed = np.pad(audio, (delay_samples, 0), mode='constant')[:len(audio)]
            audio = audio + 0.2 * timbre['resonance'] * delayed
        
        return audio


class ComprehensiveMusicGenerator:
    """Music generator supporting all instruments from dataset"""
    
    def __init__(self, outputs_dir="outputs"):
        self.outputs_dir = outputs_dir
        os.makedirs(outputs_dir, exist_ok=True)
        
        self.synthesizer = AdvancedInstrumentSynthesizer()
        self.dataset = INSTRUMENT_DATASET
        
        # Musical scales (MIDI note numbers relative to root)
        self.scales = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10],
            'pentatonic': [0, 2, 4, 7, 9],
            'blues': [0, 3, 5, 6, 7, 10],
            'dorian': [0, 2, 3, 5, 7, 9, 10],
            'mixolydian': [0, 2, 4, 5, 7, 9, 10],
            'lydian': [0, 2, 4, 6, 7, 9, 11],
        }
        
        # Multiple chord progressions for variety
        # Format: list of progressions, each progression is a list of chords (relative to root)
        # Advanced Professional Chord Progressions (Extended Voicings)
        # Format: list of progressions, each progression is a list of chords (relative to root)
        # Notes: 0=Root, 4=Major 3rd, 7=Perfect 5th, 11=Major 7th, 10=Minor 7th, 14=9th
        self.genre_progressions = {
            'Pop': [
                # Imaj9 - V - vi7 - IVmaj7 (Emotional Pop)
                [[0, 4, 7, 11, 14], [7, 11, 14, 2], [9, 12, 16, 19], [5, 9, 12, 16]], 
                # vi7 - IVmaj9 - Iadd9 - V7 (Modern Radio)
                [[9, 12, 16, 19], [5, 9, 12, 16, 19], [0, 4, 7, 14], [7, 11, 14, 17]],
                # Royal Road: IVmaj7 - V7 - iii7 - vi7 (Japanese/City Pop)
                [[5, 9, 12, 16], [7, 11, 14, 17], [4, 7, 11, 14], [9, 12, 16, 19]],
            ],
            'Jazz': [
                # ii9 - V13 - Imaj9 - VI7alt (Neo-Soul/Jazz)
                [[2, 5, 9, 12, 16], [7, 11, 14, 17, 21], [0, 4, 7, 11, 14], [9, 13, 16, 20]],
                # Imaj7 - vi7 - ii7 - V7b9 (Turnaround)
                [[0, 4, 7, 11], [9, 12, 16, 19], [2, 5, 9, 12], [7, 11, 14, 16, 20]],
                # iii7 - VI7 - ii7 - V7 (Circle of 5ths)
                [[4, 7, 11, 14], [9, 13, 16, 19], [2, 5, 9, 12], [7, 11, 14, 17]],
            ],
            'Blues': [
                # 12-Bar Blues with Dominant 7ths
                [[0, 4, 7, 10], [0, 4, 7, 10], [0, 4, 7, 10], [0, 4, 7, 10]], 
                [[5, 9, 12, 15], [5, 9, 12, 15], [0, 4, 7, 10], [0, 4, 7, 10]], 
                [[7, 11, 14, 17], [5, 9, 12, 15], [0, 4, 7, 10], [7, 11, 14, 17]], 
            ],
            'Rock': [
                # Power chords with added 9ths for color
                [[0, 7, 12, 14], [5, 12, 17, 19], [7, 14, 19, 21], [5, 12, 17, 19]], 
                # i - bVII - bVI - bVII (Classic Rock Anthem)
                [[0, 3, 7], [10, 14, 17], [8, 12, 15], [10, 14, 17]], 
            ],
            'EDM': [
                # i7 - VI - III - VII (Melodic House)
                [[0, 3, 7, 10], [8, 12, 15, 19], [3, 7, 10, 14], [10, 14, 17, 21]],
                # i - iv7 - v7 - VImaj7
                [[0, 3, 7], [5, 8, 12, 15], [7, 10, 14, 17], [8, 12, 15, 19]],
            ],
            'Classical': [
                # I - V6/5 - I - IV6/4 (Counterpoint Flow)
                [[0, 4, 7], [11, 14, 17, 2], [0, 4, 7], [0, 5, 9]], 
                # Canon-esque: I - V - vi - iii - IV - I
                [[0, 4, 7], [7, 11, 14], [9, 12, 16], [4, 7, 11], [5, 9, 12], [0, 4, 7]],
            ],
        }
    
    def _freq_from_note_number(self, note: int) -> float:
        """Convert MIDI note number to frequency"""
        return 440.0 * (2.0 ** ((note - 69) / 12.0))
    
    def _get_scale_notes(self, root_note: int, scale_type: str) -> List[int]:
        """Get notes in a scale"""
        scale_intervals = self.scales.get(scale_type, self.scales['major'])
        return [root_note + interval for interval in scale_intervals]
    
    def generate_music(self, 
                      genre: str = "Pop",
                      tempo: int = 120,
                      duration: int = 10,
                      mood: str = "Happy",
                      instruments: Optional[List[str]] = None,
                      root_note: int = None) -> Dict:
        """
        Generate multi-instrument music with genre-specific uniqueness
        Each generation will be unique through randomization
        """
        
        # RANDOMIZATION 1: Randomize root note (key) if not specified
        if root_note is None:
            # Choose from common keys: C, D, E, F, G, A (MIDI 60, 62, 64, 65, 67, 69)
            root_note = random.choice([60, 62, 64, 65, 67, 69])
        
        # RANDOMIZATION 2: Add slight tempo variation (±5 BPM)
        tempo_variation = random.randint(-5, 5)
        actual_tempo = max(60, min(200, tempo + tempo_variation))
        
        # Select instruments based on genre if not specified
        if instruments is None:
            instruments = self._select_instruments_for_genre(genre)
        
        # Validate instruments
        valid_instruments = []
        for inst in instruments:
            try:
                self.dataset.get_instrument(inst)
                valid_instruments.append(inst)
            except ValueError:
                print(f"Warning: Instrument '{inst}' not found, skipping")
        instruments = valid_instruments
        
        # Get note name for display
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_name = note_names[root_note % 12]
        
        print(f"\n{'='*60}")
        print(f"Generating {genre} music - {mood} mood")
        print(f"Key: {key_name} | Tempo: {actual_tempo} BPM | Duration: {duration}s")
        print(f"Instruments: {', '.join(instruments)}")
        print(f"{'='*60}\n")
        
        # Get musical parameters
        scale_type = self._get_scale_for_mood(mood, genre)
        scale_notes = self._get_scale_notes(root_note, scale_type)
        
        # RANDOMIZATION 3: Pick a random progression from the genre's options
        progressions_list = self.genre_progressions.get(genre, self.genre_progressions['Pop'])
        progression = random.choice(progressions_list)
        
        # RANDOMIZATION 4: Randomly apply chord inversions
        if random.random() > 0.5:
            progression = self._apply_random_inversions(progression)
        
        # Calculate timing
        beat_duration = 60.0 / actual_tempo
        beats_per_bar = 4
        bar_duration = beat_duration * beats_per_bar
        num_bars = int(duration / bar_duration)
        if num_bars < 1: num_bars = 1
        
        # RANDOMIZATION 5: Create unique rhythm seed for this generation
        rhythm_seed = random.randint(1, 1000000)
        
        # Initialize MIDI
        midi = MIDIFile(len(instruments))
        
        # Generate audio for each instrument
        instrument_tracks = {}
        
        for track_idx, instrument_name in enumerate(instruments):
            profile = self.dataset.get_instrument(instrument_name)
            
            print(f"Generating {profile.name}...")
            
            midi.addTrackName(track_idx, 0, profile.name)
            midi.addTempo(track_idx, 0, actual_tempo)
            midi.addProgramChange(track_idx, 0, 0, profile.midi_program)
            
            # Generate based on category and genre
            if profile.category == 'percussion':
                audio = self._generate_percussion_track(
                    instrument_name, num_bars, beat_duration, genre, rhythm_seed
                )
                self._add_percussion_to_midi(midi, track_idx, num_bars, beat_duration, genre, rhythm_seed)
            
            elif profile.category == 'bass':
                audio = self._generate_bass_track(
                    instrument_name, progression, scale_notes, 
                    num_bars, bar_duration, beat_duration, root_note, genre, rhythm_seed
                )
                self._add_bass_to_midi(midi, track_idx, progression, 
                                      num_bars, bar_duration, beat_duration, root_note, genre, rhythm_seed)
            
            elif profile.category == 'harmonic':
                audio = self._generate_harmonic_track(
                    instrument_name, progression, num_bars, 
                    bar_duration, beat_duration, root_note, genre, rhythm_seed
                )
                self._add_chords_to_midi(midi, track_idx, progression,
                                        num_bars, bar_duration, beat_duration, root_note, genre, rhythm_seed)
            
            else:  # melodic
                audio = self._generate_melodic_track(
                    instrument_name, scale_notes, num_bars,
                    bar_duration, beat_duration, genre, rhythm_seed
                )
                self._add_melody_to_midi(midi, track_idx, scale_notes,
                                        num_bars, bar_duration, beat_duration, genre, rhythm_seed)
            
            instrument_tracks[instrument_name] = audio
        
        # Mix all tracks
        print("\nMixing tracks...")
        mixed_audio = self._mix_tracks(instrument_tracks)
        
        # Save files
        timestamp = int(np.random.random() * 1000000)
        audio_filename = f"{genre}_{mood}_{tempo}bpm_{timestamp}.wav"
        midi_filename = f"{genre}_{mood}_{tempo}bpm_{timestamp}.mid"
        
        audio_path = os.path.join(self.outputs_dir, audio_filename)
        midi_path = os.path.join(self.outputs_dir, midi_filename)
        
        # Save audio
        wav.write(audio_path, SAMPLE_RATE, mixed_audio)
        
        # Save MIDI
        with open(midi_path, 'wb') as f:
            midi.writeFile(f)
        
        print(f"\n[OK] Audio saved: {audio_filename}")
        print(f"[OK] MIDI saved: {midi_filename}")
        
        return {
            'audio_path': audio_path,
            'midi_path': midi_path,
            'audio_url': f'/outputs/{audio_filename}',
            'midi_url': f'/outputs/{midi_filename}',
            'instruments': instruments,
            'genre': genre,
            'tempo': actual_tempo,
            'key': key_name,
            'duration': len(mixed_audio) / SAMPLE_RATE
        }
    
    def _select_instruments_for_genre(self, genre: str) -> List[str]:
        """Select appropriate instruments for a genre"""
        genre_instruments = {
            'Pop': ['piano', 'bass', 'drums', 'synth'],
            'Jazz': ['piano', 'upright_bass', 'drums', 'saxophone', 'trumpet'],
            'Rock': ['electric_guitar', 'bass', 'drums', 'organ'],
            'Classical': ['piano', 'violin', 'cello', 'flute'],
            'EDM': ['synth', 'bass', 'drums', 'pad'],
            'Blues': ['guitar', 'bass', 'drums', 'saxophone'],
            'Funk': ['electric_guitar', 'bass', 'drums', 'electric_piano'],
            'Ambient': ['pad', 'piano', 'flute'],
        }
        return genre_instruments.get(genre, ['piano', 'bass', 'drums'])
    
    def _get_scale_for_mood(self, mood: str, genre: str) -> str:
        """Select scale based on mood and genre"""
        if genre == 'Blues': return 'blues'
        if genre == 'Jazz': return 'dorian' if mood in ['Sad', 'Calm'] else 'mixolydian'
        
        mood_scales = {
            'Happy': 'major',
            'Sad': 'minor',
            'Energetic': 'pentatonic',
            'Calm': 'pentatonic',
            'Dark': 'minor',
            'Bright': 'lydian' if random.random() > 0.5 else 'major',
        }
        return mood_scales.get(mood, 'major')
    
    def _apply_random_inversions(self, progression: List[List[int]]) -> List[List[int]]:
        """Randomly invert chords for variation"""
        inverted_progression = []
        for chord in progression:
            if len(chord) >= 3 and random.random() > 0.6:
                # Apply random inversion
                inversion = random.choice([0, 1, 2])
                inverted_chord = chord.copy()
                for _ in range(inversion):
                    inverted_chord = inverted_chord[1:] + [inverted_chord[0] + 12]
                inverted_progression.append(inverted_chord)
            else:
                inverted_progression.append(chord)
        return inverted_progression
    
    def _get_humanized_velocity(self, base_velocity: float = 0.8) -> float:
        """Add human-like velocity variation"""
        variation = random.uniform(-0.15, 0.15)
        return max(0.3, min(1.0, base_velocity + variation))
    
    def _generate_percussion_track(self, instrument_name: str, num_bars: int,
                                  beat_duration: float, genre: str, rhythm_seed: int = 0) -> np.ndarray:
        """Generate genre-specific percussion track"""
        
        total_duration = num_bars * 4 * beat_duration
        audio = np.zeros(int(SAMPLE_RATE * total_duration))
        
        # RANDOMIZATION: Create varied rhythm pattern based on seed
        random.seed(rhythm_seed + hash(instrument_name))
        rhythm_variation = random.choice(['standard', 'syncopated', 'sparse'])
        
        for bar in range(num_bars):
            for step in range(16): # 16th notes
                # Add micro-timing variation (±10ms)
                timing_variation = random.uniform(-0.01, 0.01)
                time_offset = (bar * 4 + (step / 4)) * beat_duration + timing_variation
                sample_offset = int(time_offset * SAMPLE_RATE)
                if sample_offset >= len(audio) or sample_offset < 0: continue
                
                # GENRE SPECIFIC DRUM LOGIC with VARIATION
                play_kick = False
                play_snare = False
                play_hihat = False
                
                if genre == 'EDM':
                    if step % 4 == 0: play_kick = True # Four on the floor
                    if step in [4, 12]: play_snare = True
                    if rhythm_variation == 'syncopated' and step in [2, 10]: play_kick = (random.random() > 0.7)
                    if step % 4 == 2: play_hihat = True # Offbeat hihat
                elif genre == 'Rock':
                    if step in [0, 8]: play_kick = True
                    if step in [4, 12]: play_snare = True
                    if rhythm_variation == 'syncopated' and step == 14: play_kick = (random.random() > 0.6)
                    if step % 2 == 0: play_hihat = True
                elif genre == 'Jazz':
                    # Swing feel (triplet approximation)
                    if step % 4 == 0: play_kick = (random.random() < 0.3) # Feathering
                    if step == 4 or step == 12: play_snare = (random.random() < 0.4)
                    if step in [0, 3, 4, 7, 8, 11, 12, 15]: play_hihat = True # Swing pattern
                else: # Default Pop
                    base_pattern = [0, 6, 10] if rhythm_variation != 'syncopated' else [0, 5, 8, 14]
                    if step in base_pattern: play_kick = True
                    if step in [4, 12]: play_snare = True
                    if rhythm_variation == 'sparse':
                        if step % 4 == 0: play_hihat = True
                    else:
                        if step % 2 == 0: play_hihat = True
                
                if play_kick:
                    vel = self._get_humanized_velocity(1.0)
                    kick = self.synthesizer.synthesize(instrument_name, 60, 0.2, vel)
                    end = min(sample_offset + len(kick), len(audio))
                    audio[sample_offset:end] += kick[:end-sample_offset]
                if play_snare:
                    vel = self._get_humanized_velocity(0.8)
                    snare = self.synthesizer.synthesize(instrument_name, 200, 0.15, vel)
                    end = min(sample_offset + len(snare), len(audio))
                    audio[sample_offset:end] += snare[:end-sample_offset] * 0.6
                if play_hihat:
                    vel = self._get_humanized_velocity(0.5)
                    hihat = self.synthesizer.synthesize(instrument_name, 3000, 0.05, vel)
                    end = min(sample_offset + len(hihat), len(audio))
                    audio[sample_offset:end] += hihat[:end-sample_offset] * 0.3
                    
        return audio
    
    def _generate_bass_track(self, instrument_name: str, progression: List[List[int]],
                            scale_notes: List[int], num_bars: int,
                            bar_duration: float, beat_duration: float, root_note: int, genre: str, rhythm_seed: int = 0) -> np.ndarray:
        """Generate genre-specific bass track"""
        
        total_duration = num_bars * bar_duration
        audio = np.zeros(int(SAMPLE_RATE * total_duration))
        
        # RANDOMIZATION: Vary bass pattern
        random.seed(rhythm_seed + hash(instrument_name) + 1)
        bass_style = random.choice(['standard', 'walking', 'syncopated'])
        
        for bar in range(num_bars):
            chord_idx = bar % len(progression)
            chord_base = root_note + progression[chord_idx][0]
            
            # GENRE SPECIFIC BASS LOGIC with VARIATION
            if genre == 'Jazz' or bass_style == 'walking':
                # Walking Bass (Quarter notes)
                for beat in range(4):
                    # Scale-wise movement or chord tones with variation
                    target_note = chord_base - 12
                    if beat == 1: target_note += random.choice([2, 4, 5])
                    if beat == 2: target_note += random.choice([7, 9])
                    if beat == 3: target_note += random.choice([10, 11]) # Leading tone
                    
                    freq = self._freq_from_note_number(target_note)
                    vel = self._get_humanized_velocity(0.7)
                    timing_var = random.uniform(-0.005, 0.005)
                    note_audio = self.synthesizer.synthesize(instrument_name, freq, beat_duration * 0.95, vel)
                    
                    offset = int((bar * bar_duration + beat * beat_duration + timing_var) * SAMPLE_RATE)
                    end = min(offset + len(note_audio), len(audio))
                    if offset >= 0:
                        audio[offset:end] += note_audio[:end-offset]
            elif genre == 'Rock' or bass_style == 'syncopated':
                # Driving 8th notes with variation
                pattern = [0, 2, 4, 5, 6, 7] if bass_style == 'syncopated' else range(8)
                for sub in pattern:
                    freq = self._freq_from_note_number(chord_base - 12)
                    vel = self._get_humanized_velocity(0.8)
                    timing_var = random.uniform(-0.003, 0.003)
                    note_audio = self.synthesizer.synthesize(instrument_name, freq, (beat_duration/2) * 0.9, vel)
                    offset = int((bar * bar_duration + sub * (beat_duration/2) + timing_var) * SAMPLE_RATE)
                    end = min(offset + len(note_audio), len(audio))
                    if offset >= 0:
                        audio[offset:end] += note_audio[:end-offset]
            else:
                # Basic Bass Loop with octave jumps
                octave_shift = random.choice([0, -12]) if random.random() > 0.7 else 0
                freq = self._freq_from_note_number(chord_base - 12 + octave_shift)
                vel = self._get_humanized_velocity(0.8)
                note_audio = self.synthesizer.synthesize(instrument_name, freq, bar_duration * 0.8, vel)
                offset = int(bar * bar_duration * SAMPLE_RATE)
                end = min(offset + len(note_audio), len(audio))
                audio[offset:end] += note_audio[:end-offset]
        
        return audio
    
    def _generate_harmonic_track(self, instrument_name: str, 
                                progression: List[List[int]], num_bars: int,
                                bar_duration: float, beat_duration: float, root_note: int, genre: str, rhythm_seed: int = 0) -> np.ndarray:
        """Generate genre-specific harmonic track"""
        
        total_duration = num_bars * bar_duration
        audio = np.zeros(int(SAMPLE_RATE * total_duration))
        
        # RANDOMIZATION: Vary chord voicing style
        random.seed(rhythm_seed + hash(instrument_name) + 2)
        voicing_style = random.choice(['close', 'open', 'spread'])
        
        for bar in range(num_bars):
            chord_idx = bar % len(progression)
            chord = progression[chord_idx].copy()
            
            # Apply voicing variation
            if voicing_style == 'open' and len(chord) >= 3:
                chord[1] += 12  # Raise middle note an octave
            elif voicing_style == 'spread' and len(chord) >= 3:
                chord[1] += 12
                chord[2] += 12
            
            # GENRE SPECIFIC CHORD LOGIC with VARIATION
            if genre == 'Classical':
                # Arpeggios with varied patterns
                arp_pattern = random.choice([[0, 2, 1, 2], [0, 1, 2, 1], [0, 2, 1, 0]])
                for sub in range(8):
                    note_idx = arp_pattern[sub % 4] if len(chord) >= 3 else sub % len(chord)
                    note = root_note + chord[note_idx % len(chord)]
                    freq = self._freq_from_note_number(note)
                    vel = self._get_humanized_velocity(0.5)
                    timing_var = random.uniform(-0.003, 0.003)
                    chunk = self.synthesizer.synthesize(instrument_name, freq, (beat_duration/2) * 1.1, vel)
                    offset = int((bar * bar_duration + sub * (beat_duration/2) + timing_var) * SAMPLE_RATE)
                    end = min(offset + len(chunk), len(audio))
                    if offset >= 0:
                        audio[offset:end] += chunk[:end-offset]
            elif genre == 'EDM' or genre == 'Pop':
                # Rhythmic Stabs with variation
                rhythm_patterns = [
                    [1, 0, 0, 1, 0, 1, 0, 0],
                    [1, 0, 1, 0, 1, 0, 1, 0],
                    [1, 1, 0, 0, 1, 1, 0, 0]
                ]
                rhythm = random.choice(rhythm_patterns)
                for sub in range(8):
                    if rhythm[sub % len(rhythm)]:
                        for note_offset in chord:
                            freq = self._freq_from_note_number(root_note + note_offset)
                            vel = self._get_humanized_velocity(0.4)
                            timing_var = random.uniform(-0.002, 0.002)
                            chunk = self.synthesizer.synthesize(instrument_name, freq, (beat_duration/2) * 0.7, vel)
                            offset = int((bar * bar_duration + sub * (beat_duration/2) + timing_var) * SAMPLE_RATE)
                            end = min(offset + len(chunk), len(audio))
                            if offset >= 0:
                                audio[offset:end] += chunk[:end-offset] / len(chord)
            else:
                # Sustained Chords with variation
                for note_offset in chord:
                    freq = self._freq_from_note_number(root_note + note_offset)
                    vel = self._get_humanized_velocity(0.4)
                    chunk = self.synthesizer.synthesize(instrument_name, freq, bar_duration * 0.9, vel)
                    offset = int(bar * bar_duration * SAMPLE_RATE)
                    end = min(offset + len(chunk), len(audio))
                    audio[offset:end] += chunk[:end-offset] / len(chord)
        
        return audio
    
    def _generate_melodic_track(self, instrument_name: str, scale_notes: List[int],
                                num_bars: int, bar_duration: float,
                                beat_duration: float, genre: str, rhythm_seed: int = 0) -> np.ndarray:
        """Generate genre-specific melodic track with improved logic"""
        
        total_duration = num_bars * bar_duration
        audio = np.zeros(int(SAMPLE_RATE * total_duration))
        
        # RANDOMIZATION: Vary melodic contour and rhythm
        random.seed(rhythm_seed + hash(instrument_name) + 3)
        melodic_contour = random.choice(['ascending', 'descending', 'arch', 'random'])
        rest_probability = random.uniform(0.15, 0.35)
        
        # Start at random octave
        last_note = random.choice(scale_notes) + random.choice([12, 24])
        
        for bar in range(num_bars):
            # Vary phrase length
            num_notes = random.choice([2, 3, 4, 6, 8]) if genre != 'Classical' else random.choice([6, 8])
            note_duration = bar_duration / num_notes
            
            for n in range(num_notes):
                # ENHANCED MELODY with contour awareness
                if melodic_contour == 'ascending':
                    interval_choices = [-1, 0, 1, 2, 3]
                elif melodic_contour == 'descending':
                    interval_choices = [-3, -2, -1, 0, 1]
                elif melodic_contour == 'arch':
                    # Ascend first half, descend second half
                    if n < num_notes / 2:
                        interval_choices = [0, 1, 2, 3]
                    else:
                        interval_choices = [-3, -2, -1, 0]
                else:  # random
                    interval_choices = [-4, -2, -1, 0, 1, 2, 4]
                
                choices = [last_note + d for d in interval_choices]
                valid_choices = [c for c in choices if any(abs(c - (sn+12)) < 0.1 for sn in scale_notes) or 
                                                        any(abs(c - (sn+24)) < 0.1 for sn in scale_notes)]
                if not valid_choices: 
                    valid_choices = [sn + random.choice([12, 24]) for sn in scale_notes]
                
                note = random.choice(valid_choices)
                # Ensure it's in a good octave
                while note < 60: note += 12
                while note > 84: note -= 12
                
                # Variable rest probability
                if random.random() > rest_probability:
                    freq = self._freq_from_note_number(note)
                    vel = self._get_humanized_velocity(0.7)
                    timing_var = random.uniform(-0.005, 0.005)
                    
                    # Occasionally add note length variation
                    duration_mult = random.choice([0.8, 0.9, 1.0, 1.1]) if random.random() > 0.7 else 0.9
                    
                    note_audio = self.synthesizer.synthesize(instrument_name, freq, note_duration * duration_mult, vel)
                    offset = int((bar * bar_duration + n * note_duration + timing_var) * SAMPLE_RATE)
                    end = min(offset + len(note_audio), len(audio))
                    if offset >= 0:
                        audio[offset:end] += note_audio[:end-offset]
                    last_note = note
        
        return audio
    
    def _mix_tracks(self, tracks: Dict[str, np.ndarray]) -> np.ndarray:
        """Mix multiple instrument tracks with compression/limiting"""
        if not tracks: return np.array([])
        max_length = max(len(track) for track in tracks.values())
        mixed = np.zeros(max_length)
        
        for track in tracks.values():
            if len(track) < max_length:
                track = np.pad(track, (0, max_length - len(track)))
            mixed += track
            
        # Hard limiting/Normalization
        max_val = np.max(np.abs(mixed))
        if max_val > 0.001:
            mixed = mixed / max_val * 0.95
        
        return (mixed * 32767).astype(np.int16)
    
    def _add_percussion_to_midi(self, midi: MIDIFile, track: int,
                                num_bars: int, beat_duration: float, genre: str, rhythm_seed: int = 0):
        """Add genre-specific percussion to MIDI"""
        for bar in range(num_bars):
            for step in range(16):
                time = (bar * 4 + (step / 4))
                if genre == 'EDM':
                    if step % 4 == 0: midi.addNote(track, 9, 36, time, 0.25, 120)
                    if step in [4, 12]: midi.addNote(track, 9, 38, time, 0.25, 100)
                    if step % 4 == 2: midi.addNote(track, 9, 42, time, 0.25, 80)
                elif genre == 'Rock':
                    if step in [0, 8]: midi.addNote(track, 9, 36, time, 0.25, 110)
                    if step in [4, 12]: midi.addNote(track, 9, 38, time, 0.25, 100)
                    if step % 2 == 0: midi.addNote(track, 9, 42, time, 0.25, 90)
                else: # Generic Pop
                    if step in [0, 6, 10]: midi.addNote(track, 9, 36, time, 0.25, 110)
                    if step in [4, 12]: midi.addNote(track, 9, 38, time, 0.25, 100)
    
    def _add_bass_to_midi(self, midi: MIDIFile, track: int,
                         progression: List[List[int]], num_bars: int,
                         bar_duration: float, beat_duration: float, root_note: int, genre: str, rhythm_seed: int = 0):
        """Add genre-specific bass to MIDI"""
        for bar in range(num_bars):
            chord_idx = bar % len(progression)
            chord_base = root_note + progression[chord_idx][0]
            if genre == 'Jazz':
                for beat in range(4):
                    time = bar * 4 + beat
                    midi.addNote(track, 0, chord_base - 12 + beat, time, 1.0, 80)
            elif genre == 'Rock':
                for sub in range(8):
                    time = bar * 4 + (sub * 0.5)
                    midi.addNote(track, 0, chord_base - 12, time, 0.5, 90)
            else:
                midi.addNote(track, 0, chord_base - 12, bar * 4, 4.0, 85)
    
    def _add_chords_to_midi(self, midi: MIDIFile, track: int,
                           progression: List[List[int]], num_bars: int,
                           bar_duration: float, beat_duration: float, root_note: int, genre: str, rhythm_seed: int = 0):
        """Add genre-specific chords to MIDI"""
        for bar in range(num_bars):
            chord_idx = bar % len(progression)
            chord = progression[chord_idx]
            if genre == 'Classical':
                for sub in range(8):
                    note_idx = [0, 2, 1, 2][sub % 4] if len(chord) >= 3 else sub % len(chord)
                    time = bar * 4 + (sub * 0.5)
                    midi.addNote(track, 0, root_note + chord[note_idx], time, 0.5, 60)
            else:
                for note_offset in chord:
                    midi.addNote(track, 0, root_note + note_offset, bar * 4, 4.0, 60)
    
    def _add_melody_to_midi(self, midi: MIDIFile, track: int,
                           scale_notes: List[int], num_bars: int,
                           bar_duration: float, beat_duration: float, genre: str, rhythm_seed: int = 0):
        """Add melody to MIDI"""
        for bar in range(num_bars):
            num_notes = 4 if genre != 'Classical' else 8
            dur = 4.0 / num_notes
            for n in range(num_notes):
                note = random.choice(scale_notes) + 12
                midi.addNote(track, 0, note, bar * 4 + (n * dur), dur, 80)


if __name__ == "__main__":
    # Test the comprehensive generator
    gen = ComprehensiveMusicGenerator(
        outputs_dir=r"c:\Users\chinn\OneDrive\Documents\Gen music\pytune\outputs"
    )
    
    print("\n" + "="*60)
    print("COMPREHENSIVE MUSIC GENERATOR - TESTING ALL INSTRUMENTS")
    print("="*60)
    
    # Test 1: Pop with standard instruments
    print("\n[TEST 1] Pop Music")
    result1 = gen.generate_music(
        genre="Pop",
        tempo=120,
        duration=8,
        mood="Happy",
        instruments=['piano', 'bass', 'drums', 'synth']
    )
    
    # Test 2: Jazz with brass
    print("\n[TEST 2] Jazz Music")
    result2 = gen.generate_music(
        genre="Jazz",
        tempo=140,
        duration=8,
        mood="Energetic",
        instruments=['piano', 'bass', 'drums', 'saxophone', 'trumpet']
    )
    
    # Test 3: Classical with strings
    print("\n[TEST 3] Classical Music")
    result3 = gen.generate_music(
        genre="Classical",
        tempo=90,
        duration=8,
        mood="Calm",
        instruments=['piano', 'violin', 'cello', 'flute']
    )
    
    # Test 4: Rock
    print("\n[TEST 4] Rock Music")
    result4 = gen.generate_music(
        genre="Rock",
        tempo=130,
        duration=8,
        mood="Energetic",
        instruments=['electric_guitar', 'bass', 'drums', 'organ']
    )
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)
    print("\nAvailable instruments:")
    for inst in sorted(INSTRUMENT_DATASET.list_all_instruments()):
        print(f"  • {inst}")
