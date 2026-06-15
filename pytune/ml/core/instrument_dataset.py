from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

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

class InstrumentDataset:
    def __init__(self):
        self.instruments = {}
        self._initialize_dataset()
    
    def _initialize_dataset(self):
        # ==========================================
        # PROFESSIONAL STUDIO QUALITY INSTRUMENTS
        # ==========================================

        # 1. Concert Grand Piano (Steinway Style)
        # Rich, full-bodied with complex resonances
        self.instruments['piano'] = InstrumentProfile(
            name='Concert Grand Piano', category='harmonic', frequency_range=(27.5, 4186.0),
            harmonics=[
                (1, 1.0), (2, 0.45), (3, 0.32), (4, 0.18), (5, 0.12),
                (6, 0.07), (7, 0.04), (8, 0.02)
            ],
            adsr={'attack': 0.005, 'decay': 0.28, 'sustain': 0.42, 'release': 0.9},
            timbre_characteristics={'brightness': 0.68, 'warmth': 0.82, 'resonance': 0.98},
            midi_program=0, typical_genres=['Classical', 'Jazz', 'Pop', 'Ballad'],
            velocity_sensitivity=0.95
        )

        # 2. Electric Piano (Rhodes Mark I)
        # Bell-like attack, warm sustain
        self.instruments['electric_piano'] = InstrumentProfile(
            name='Vintage Electric Piano', category='harmonic', frequency_range=(27.5, 4186.0),
            harmonics=[(1, 1.0), (2, 0.18), (3, 0.08), (4, 0.03), (7, 0.12)],
            adsr={'attack': 0.01, 'decay': 0.35, 'sustain': 0.65, 'release': 0.45},
            timbre_characteristics={'brightness': 0.53, 'warmth': 0.88, 'resonance': 0.45},
            midi_program=4, typical_genres=['Jazz', 'Neo-Soul', 'Funk'],
            velocity_sensitivity=0.85
        )

        # 3. Hammond B3 Organ
        # Percussive key click, sustained tone
        self.instruments['organ'] = InstrumentProfile(
            name='Hammond B3 Organ', category='harmonic', frequency_range=(32.7, 4186.0),
            harmonics=[(1, 1.0), (2, 0.54), (3, 0.82), (4, 0.42), (6, 0.18), (8, 0.22)],
            adsr={'attack': 0.02, 'decay': 0.0, 'sustain': 1.0, 'release': 0.12},
            timbre_characteristics={'brightness': 0.72, 'warmth': 0.82, 'resonance': 0.62},
            midi_program=16, typical_genres=['Jazz', 'Rock', 'Gospel', 'Blues'],
            velocity_sensitivity=0.1
        )

        # 4. Martin Acoustic Guitar
        # Bright steel string sound with body resonance
        self.instruments['guitar'] = InstrumentProfile(
            name='Studio Acoustic Guitar', category='harmonic', frequency_range=(82.4, 880.0),
            harmonics=[(1, 1.0), (2, 0.75), (3, 0.45), (4, 0.35), (5, 0.22), (6, 0.12)],
            adsr={'attack': 0.015, 'decay': 0.32, 'sustain': 0.33, 'release': 0.5},
            timbre_characteristics={'brightness': 0.78, 'warmth': 0.68, 'resonance': 0.75},
            midi_program=24, typical_genres=['Pop', 'Folk', 'Indie', 'Acoustic'],
            velocity_sensitivity=0.9
        )

        # 5. Fender Strat Electric Guitar
        # Clean, chimy tone with smooth sustain
        self.instruments['electric_guitar'] = InstrumentProfile(
            name='Clean Strat Guitar', category='harmonic', frequency_range=(82.4, 880.0),
            harmonics=[(1, 1.0), (2, 0.45), (3, 0.65), (4, 0.25), (5, 0.28), (6, 0.12)],
            adsr={'attack': 0.006, 'decay': 0.18, 'sustain': 0.62, 'release': 0.38},
            timbre_characteristics={'brightness': 0.82, 'warmth': 0.58, 'resonance': 0.58},
            midi_program=27, typical_genres=['Rock', 'Funk', 'Pop', 'Blues'],
            velocity_sensitivity=0.85
        )

        # 6. Precision Bass
        # Example of solid low end
        self.instruments['bass'] = InstrumentProfile(
            name='Precision Bass', category='bass', frequency_range=(30.0, 392.0),
            harmonics=[(1, 1.0), (2, 0.85), (3, 0.45), (4, 0.25), (5, 0.08)],
            adsr={'attack': 0.01, 'decay': 0.18, 'sustain': 0.72, 'release': 0.18},
            timbre_characteristics={'brightness': 0.35, 'warmth': 0.92, 'resonance': 0.35},
            midi_program=34, typical_genres=['Rock', 'Pop', 'Funk'],
            velocity_sensitivity=0.85
        )

        # 7. Upright Bass (Jazz)
        # Woody thrum with fast decay
        self.instruments['upright_bass'] = InstrumentProfile(
            name='Double Bass', category='bass', frequency_range=(30.0, 392.0),
            harmonics=[(1, 1.0), (2, 0.4), (3, 0.2), (4, 0.1)],
            adsr={'attack': 0.08, 'decay': 0.4, 'sustain': 0.3, 'release': 0.5}, # Bowing/Pluck swell
            timbre_characteristics={'brightness': 0.3, 'warmth': 0.95, 'resonance': 0.8},
            midi_program=32, typical_genres=['Jazz', 'Classical', 'Folk'],
            velocity_sensitivity=0.85
        )

        # 8. Solo Violin (Stradivarius style)
        # Expressive vibrato range (simulated)
        self.instruments['violin'] = InstrumentProfile(
            name='Solo Violin', category='melodic', frequency_range=(196.0, 3520.0),
            harmonics=[(1, 1.0), (2, 0.9), (3, 0.8), (4, 0.7), (5, 0.5), (6, 0.3)], # Sawtooth-like but smoother
            adsr={'attack': 0.15, 'decay': 0.1, 'sustain': 0.9, 'release': 0.4}, # Slow bow attack
            timbre_characteristics={'brightness': 0.85, 'warmth': 0.6, 'resonance': 0.8},
            midi_program=40, typical_genres=['Classical', 'Cinematic', 'Pop'],
            velocity_sensitivity=0.9
        )

        # 9. Cello Section
        # Deep, resonant, emotive
        self.instruments['cello'] = InstrumentProfile(
            name='Cello Section', category='melodic', frequency_range=(65.4, 1046.5),
            harmonics=[(1, 1.0), (2, 0.6), (3, 0.5), (4, 0.3)],
            adsr={'attack': 0.2, 'decay': 0.2, 'sustain': 0.85, 'release': 0.5},
            timbre_characteristics={'brightness': 0.4, 'warmth': 0.9, 'resonance': 0.9},
            midi_program=42, typical_genres=['Classical', 'Cinematic'],
            velocity_sensitivity=0.85
        )

        # 10. Jazz Trumpet
        # Bright, brassy core
        self.instruments['trumpet'] = InstrumentProfile(
            name='Jazz Trumpet', category='melodic', frequency_range=(164.8, 1046.5),
            harmonics=[(1, 1.0), (2, 1.2), (3, 0.9), (4, 0.7), (5, 0.5)], # Strong upper mids
            adsr={'attack': 0.03, 'decay': 0.1, 'sustain': 0.8, 'release': 0.15},
            timbre_characteristics={'brightness': 0.95, 'warmth': 0.5, 'resonance': 0.4},
            midi_program=56, typical_genres=['Jazz', 'Pop', 'Classical'],
            velocity_sensitivity=0.9
        )

        # 11. Orchestral Trombone
        self.instruments['trombone'] = InstrumentProfile(
            name='Trombone', category='melodic', frequency_range=(82.4, 523.3),
            harmonics=[(1, 1.0), (2, 0.9), (3, 0.7)],
            adsr={'attack': 0.1, 'decay': 0.15, 'sustain': 0.8, 'release': 0.2},
            timbre_characteristics={'brightness': 0.5, 'warmth': 0.85, 'resonance': 0.6},
            midi_program=57, typical_genres=['Jazz', 'Classical'],
            velocity_sensitivity=0.8
        )

        # 12. Tenor Saxophone
        # Breath, reed sound
        self.instruments['saxophone'] = InstrumentProfile(
            name='Tenor Saxophone', category='melodic', frequency_range=(138.6, 880.0),
            harmonics=[(1, 1.0), (2, 0.8), (3, 0.7), (4, 0.6), (5, 0.4)], # Complex reed physics
            adsr={'attack': 0.05, 'decay': 0.1, 'sustain': 0.85, 'release': 0.2},
            timbre_characteristics={'brightness': 0.6, 'warmth': 0.7, 'resonance': 0.5},
            midi_program=65, typical_genres=['Jazz', 'Pop', 'Blues'],
            velocity_sensitivity=0.9
        )

        # 13. Concert Flute
        # Pure sine-like but with breath (high harmonics)
        self.instruments['flute'] = InstrumentProfile(
            name='Concert Flute', category='melodic', frequency_range=(261.6, 2093.0),
            harmonics=[(1, 1.0), (2, 0.05), (3, 0.02)], # Almost sine
            adsr={'attack': 0.08, 'decay': 0.1, 'sustain': 0.75, 'release': 0.15},
            timbre_characteristics={'brightness': 0.7, 'warmth': 0.4, 'resonance': 0.6},
            midi_program=73, typical_genres=['Classical', 'Jazz', 'Ambient'],
            velocity_sensitivity=0.7
        )

        # 14. Clarinet
        self.instruments['clarinet'] = InstrumentProfile(
            name='Clarinet', category='melodic', frequency_range=(146.8, 1568.0),
            harmonics=[(1, 1.0), (3, 0.7), (5, 0.5), (7, 0.3)], # Dominant odd harmonics (closed cylinder)
            adsr={'attack': 0.05, 'decay': 0.1, 'sustain': 0.8, 'release': 0.2},
            timbre_characteristics={'brightness': 0.5, 'warmth': 0.8, 'resonance': 0.4},
            midi_program=71, typical_genres=['Classical', 'Jazz'],
            velocity_sensitivity=0.75
        )

        # 15. Analog Synth Lead (Moog Style)
        self.instruments['synth'] = InstrumentProfile(
            name='Moog Lead', category='melodic', frequency_range=(20.0, 5000.0),
            harmonics=[(1, 1.0), (2, 0.85), (3, 0.7), (4, 0.55), (5, 0.35), (6, 0.15)],
            adsr={'attack': 0.02, 'decay': 0.22, 'sustain': 0.65, 'release': 0.4},
            timbre_characteristics={'brightness': 0.82, 'warmth': 0.78, 'resonance': 0.88},
            midi_program=81, typical_genres=['EDM', 'Pop', 'Rock'],
            velocity_sensitivity=0.65
        )

        # 16. Warm Pad (Oberheim Style)
        self.instruments['pad'] = InstrumentProfile(
            name='Warm Analog Pad', category='harmonic', frequency_range=(20.0, 5000.0),
            harmonics=[(1, 1.0), (2, 0.42), (3, 0.18), (4, 0.08)],
            adsr={'attack': 0.9, 'decay': 0.55, 'sustain': 0.92, 'release': 1.4},
            timbre_characteristics={'brightness': 0.35, 'warmth': 0.97, 'resonance': 0.96},
            midi_program=89, typical_genres=['EDM', 'Ambient', 'Cinematic'],
            velocity_sensitivity=0.55
        )

        # 17. Studio Drum Kit
        self.instruments['drums'] = InstrumentProfile(
            name='Studio Drum Kit', category='percussion', frequency_range=(20.0, 20000.0),
            harmonics=[],
            adsr={'attack': 0.002, 'decay': 0.15, 'sustain': 0.0, 'release': 0.1},
            timbre_characteristics={'percussiveness': 1.0},
            midi_program=0, typical_genres=['All'],
            velocity_sensitivity=1.0
        )

        # 18. Latin Percussion (Congas)
        self.instruments['congas'] = InstrumentProfile(
            name='Latin Congas', category='percussion', frequency_range=(100.0, 500.0),
            harmonics=[],
            adsr={'attack': 0.005, 'decay': 0.2, 'sustain': 0.0, 'release': 0.15},
            timbre_characteristics={'percussiveness': 0.9},
            midi_program=0, typical_genres=['Jazz', 'Latin', 'Pop'],
            velocity_sensitivity=0.9
        )

        # 19. Marimba
        self.instruments['marimba'] = InstrumentProfile(
            name='Concert Marimba', category='percussion', frequency_range=(65.4, 2093.0),
            harmonics=[(1, 1.0), (4, 0.5), (10, 0.1)], # Tuned bar harmonics
            adsr={'attack': 0.005, 'decay': 0.4, 'sustain': 0.0, 'release': 0.4},
            timbre_characteristics={'brightness': 0.6, 'warmth': 0.7, 'resonance': 0.6},
            midi_program=12, typical_genres=['Classical', 'Ambient'],
            velocity_sensitivity=0.9
        )

    def get_instrument(self, instrument_id: str) -> InstrumentProfile:
        if instrument_id in self.instruments:
            return self.instruments[instrument_id]
        raise ValueError(f"Instrument {instrument_id} not found")

    def list_all_instruments(self) -> List[str]:
        return list(self.instruments.keys())

    def get_instruments_by_category(self, category: str) -> List[InstrumentProfile]:
        return [inst for inst in self.instruments.values() if inst.category == category]

    def get_instruments_by_genre(self, genre: str) -> List[InstrumentProfile]:
        return [inst for inst in self.instruments.values() if genre in inst.typical_genres or 'All' in inst.typical_genres]

# Singleton instance
INSTRUMENT_DATASET = InstrumentDataset()
