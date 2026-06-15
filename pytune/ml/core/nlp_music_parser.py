"""
Natural Language Music Parser
Converts natural language descriptions into music generation parameters
"""

import re
from typing import Dict, List, Optional, Tuple


class NLPMusicParser:
    """Parse natural language descriptions into music generation parameters"""
    
    # Genre keywords and mappings
    GENRE_KEYWORDS = {
        'pop': ['pop', 'popular', 'mainstream', 'radio'],
        'rock': ['rock', 'guitar', 'electric', 'heavy', 'metal'],
        'jazz': ['jazz', 'swing', 'bebop', 'smooth jazz', 'saxophone'],
        'classical': ['classical', 'orchestra', 'symphony', 'baroque', 'piano concerto'],
        'edm': ['edm', 'electronic', 'dance', 'techno', 'house', 'dubstep', 'trance'],
        'hip-hop': ['hip hop', 'hip-hop', 'rap', 'trap', 'beats'],
        'lo-fi': ['lo-fi', 'lofi', 'chill', 'study', 'relaxing beats'],
        'ambient': ['ambient', 'atmospheric', 'soundscape', 'drone'],
        'folk': ['folk', 'acoustic', 'country', 'bluegrass'],
        'r&b': ['r&b', 'rnb', 'soul', 'rhythm and blues'],
        'reggae': ['reggae', 'ska', 'dub'],
        'blues': ['blues', 'delta blues', 'chicago blues'],
        'latin': ['latin', 'salsa', 'bossa nova', 'samba', 'tango'],
        'indie': ['indie', 'alternative', 'underground']
    }
    
    # Mood keywords
    MOOD_KEYWORDS = {
        'happy': ['happy', 'joyful', 'cheerful', 'upbeat', 'bright', 'positive', 'energetic'],
        'sad': ['sad', 'melancholic', 'sorrowful', 'depressing', 'gloomy', 'blue'],
        'calm': ['calm', 'peaceful', 'serene', 'tranquil', 'relaxing', 'soothing', 'meditation'],
        'energetic': ['energetic', 'powerful', 'intense', 'dynamic', 'vigorous', 'pumped'],
        'romantic': ['romantic', 'love', 'passionate', 'tender', 'intimate'],
        'dark': ['dark', 'ominous', 'mysterious', 'haunting', 'eerie', 'sinister'],
        'epic': ['epic', 'cinematic', 'dramatic', 'heroic', 'grand', 'majestic'],
        'playful': ['playful', 'fun', 'quirky', 'whimsical', 'bouncy'],
        'aggressive': ['aggressive', 'angry', 'fierce', 'brutal', 'harsh'],
        'dreamy': ['dreamy', 'ethereal', 'floating', 'surreal', 'hypnotic']
    }
    
    # Tempo keywords (BPM ranges)
    TEMPO_KEYWORDS = {
        'very slow': (40, 60, ['very slow', 'extremely slow', 'grave']),
        'slow': (60, 80, ['slow', 'largo', 'adagio', 'ballad']),
        'moderate': (80, 110, ['moderate', 'medium', 'andante', 'moderato']),
        'fast': (110, 140, ['fast', 'allegro', 'quick', 'upbeat']),
        'very fast': (140, 180, ['very fast', 'presto', 'rapid', 'blazing'])
    }
    
    # Instrument keywords
    INSTRUMENT_KEYWORDS = {
        'piano': ['piano', 'keys', 'keyboard'],
        'guitar': ['guitar', 'acoustic guitar', 'electric guitar'],
        'bass': ['bass', 'bass guitar', 'double bass'],
        'drums': ['drums', 'percussion', 'drum kit'],
        'violin': ['violin', 'fiddle'],
        'saxophone': ['saxophone', 'sax'],
        'trumpet': ['trumpet', 'horn'],
        'flute': ['flute'],
        'synth': ['synth', 'synthesizer', 'electronic'],
        'strings': ['strings', 'string section', 'orchestra'],
        'brass': ['brass', 'brass section'],
        'choir': ['choir', 'vocals', 'voice']
    }
    
    # Duration keywords (in seconds)
    DURATION_KEYWORDS = {
        'short': 10,
        'medium': 20,
        'long': 30,
        'very long': 45,
        'extended': 60
    }
    
    def __init__(self):
        """Initialize the NLP parser"""
        pass
    
    def parse(self, description: str) -> Dict:
        """
        Parse natural language description into music parameters
        
        Args:
            description: Natural language description of desired music
            
        Returns:
            Dictionary with genre, mood, tempo, instruments, duration
        """
        description_lower = description.lower()
        
        # Extract parameters
        genre = self._extract_genre(description_lower)
        mood = self._extract_mood(description_lower)
        tempo = self._extract_tempo(description_lower, mood)
        instruments = self._extract_instruments(description_lower, genre)
        duration = self._extract_duration(description_lower)
        
        # Build result
        result = {
            'genre': genre,
            'mood': mood,
            'tempo': tempo,
            'duration': duration,
            'instruments': instruments,
            'description': description
        }
        
        return result
    
    def _extract_genre(self, text: str) -> str:
        """Extract genre from text"""
        for genre, keywords in self.GENRE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return genre.title()
        
        # Default genre
        return 'Pop'
    
    def _extract_mood(self, text: str) -> str:
        """Extract mood from text"""
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return mood.title()
        
        # Default mood
        return 'Happy'
    
    def _extract_tempo(self, text: str, mood: str = None) -> int:
        """Extract tempo from text or infer from mood"""
        # First try to find explicit tempo keywords
        for tempo_name, (min_bpm, max_bpm, keywords) in self.TEMPO_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return random.randint(min_bpm, max_bpm)
        
        # Try to extract numeric BPM
        bpm_match = re.search(r'(\d+)\s*bpm', text)
        if bpm_match:
            return int(bpm_match.group(1))
        
        # Infer from mood if no explicit tempo found
        mood_tempo_map = {
            'calm': 80,
            'sad': 70,
            'happy': 120,
            'energetic': 140,
            'romantic': 90,
            'dark': 85,
            'epic': 110,
            'playful': 130,
            'aggressive': 150,
            'dreamy': 75
        }
        
        if mood and mood.lower() in mood_tempo_map:
            return mood_tempo_map[mood.lower()]
        
        # Default tempo
        return 120
    
    def _extract_instruments(self, text: str, genre: str = None) -> List[str]:
        """Extract instruments from text or suggest based on genre"""
        found_instruments = []
        
        # Look for explicit instrument mentions
        for instrument, keywords in self.INSTRUMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    if instrument not in found_instruments:
                        found_instruments.append(instrument)
        
        # If no instruments found, suggest based on genre
        if not found_instruments and genre:
            genre_instruments = {
                'Pop': ['piano', 'guitar', 'bass', 'drums'],
                'Rock': ['guitar', 'bass', 'drums'],
                'Jazz': ['piano', 'saxophone', 'bass', 'drums'],
                'Classical': ['piano', 'violin', 'strings'],
                'Edm': ['synth', 'bass', 'drums'],
                'Hip-Hop': ['bass', 'drums', 'synth'],
                'Lo-Fi': ['piano', 'bass', 'drums'],
                'Ambient': ['synth', 'piano'],
                'Folk': ['guitar', 'violin'],
                'R&B': ['piano', 'bass', 'drums'],
                'Blues': ['guitar', 'piano', 'bass'],
                'Latin': ['piano', 'brass', 'drums']
            }
            
            found_instruments = genre_instruments.get(genre, ['piano', 'guitar', 'bass', 'drums'])
        
        return found_instruments if found_instruments else None
    
    def _extract_duration(self, text: str) -> int:
        """Extract duration from text"""
        # Look for explicit duration keywords
        for duration_name, seconds in self.DURATION_KEYWORDS.items():
            if duration_name in text:
                return seconds
        
        # Try to extract numeric duration
        # Match patterns like "30 seconds", "2 minutes", "1 min"
        seconds_match = re.search(r'(\d+)\s*(?:second|sec|s)\b', text)
        if seconds_match:
            return int(seconds_match.group(1))
        
        minutes_match = re.search(r'(\d+)\s*(?:minute|min|m)\b', text)
        if minutes_match:
            return int(minutes_match.group(1)) * 60
        
        # Default duration
        return 15
    
    def get_suggestions(self, partial_text: str) -> Dict[str, List[str]]:
        """
        Get suggestions for completing a partial description
        
        Args:
            partial_text: Partial text input
            
        Returns:
            Dictionary with suggested genres, moods, instruments
        """
        text_lower = partial_text.lower()
        
        suggestions = {
            'genres': [],
            'moods': [],
            'instruments': [],
            'examples': [
                "a calm piano melody for meditation",
                "upbeat jazz with saxophone and drums",
                "dark electronic music with heavy bass",
                "romantic classical piano piece",
                "energetic rock guitar solo",
                "peaceful ambient soundscape",
                "happy pop song with bright synths",
                "slow sad ballad with violin"
            ]
        }
        
        # Suggest genres
        for genre, keywords in self.GENRE_KEYWORDS.items():
            if any(kw.startswith(text_lower) for kw in keywords):
                suggestions['genres'].append(genre.title())
        
        # Suggest moods
        for mood, keywords in self.MOOD_KEYWORDS.items():
            if any(kw.startswith(text_lower) for kw in keywords):
                suggestions['moods'].append(mood.title())
        
        # Suggest instruments
        for instrument, keywords in self.INSTRUMENT_KEYWORDS.items():
            if any(kw.startswith(text_lower) for kw in keywords):
                suggestions['instruments'].append(instrument.title())
        
        return suggestions


# Import random for tempo generation
import random


if __name__ == "__main__":
    # Test the parser
    parser = NLPMusicParser()
    
    test_descriptions = [
        "a calm piano melody for meditation",
        "upbeat jazz with saxophone at 140 bpm",
        "dark electronic music with heavy bass, 30 seconds",
        "romantic classical piece with violin and piano",
        "energetic rock guitar solo, very fast",
        "peaceful ambient soundscape, long duration",
        "happy pop song with bright synths and drums"
    ]
    
    print("=== NLP Music Parser Test Results ===\n")
    for desc in test_descriptions:
        result = parser.parse(desc)
        print(f"Input: '{desc}'")
        print(f"  -> Genre: {result['genre']}")
        print(f"  -> Mood: {result['mood']}")
        print(f"  -> Tempo: {result['tempo']} BPM")
        print(f"  -> Duration: {result['duration']}s")
        print(f"  -> Instruments: {result['instruments']}")
        print()
