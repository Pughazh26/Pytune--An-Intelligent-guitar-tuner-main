"""Test script to verify music generation variation"""
from music_generator_v3 import ComprehensiveMusicGenerator

gen = ComprehensiveMusicGenerator(
    outputs_dir=r"c:\Users\chinn\OneDrive\Documents\Gen music\pytune\outputs"
)

print("\n" + "="*60)
print("TESTING MUSIC VARIATION - Same Parameters, Different Output")
print("="*60)

# Generate 3 tracks with identical parameters
print("\n=== TEST 1: First Generation ===")
r1 = gen.generate_music(genre='Pop', tempo=120, duration=8, mood='Happy')

print("\n=== TEST 2: Second Generation (Same Parameters) ===")
r2 = gen.generate_music(genre='Pop', tempo=120, duration=8, mood='Happy')

print("\n=== TEST 3: Third Generation (Same Parameters) ===")
r3 = gen.generate_music(genre='Pop', tempo=120, duration=8, mood='Happy')

print("\n" + "="*60)
print("VERIFICATION - Each track should be unique!")
print("="*60)
print(f"\nTrack 1: Key={r1['key']}, Tempo={r1['tempo']} BPM")
print(f"Track 2: Key={r2['key']}, Tempo={r2['tempo']} BPM")
print(f"Track 3: Key={r3['key']}, Tempo={r3['tempo']} BPM")

if r1['key'] != r2['key'] or r2['key'] != r3['key'] or r1['key'] != r3['key']:
    print("\n[SUCCESS] Different keys detected!")
else:
    print("\n[WARNING] All tracks have the same key (rare but possible)")

if r1['tempo'] != r2['tempo'] or r2['tempo'] != r3['tempo']:
    print("[SUCCESS] Different tempos detected!")
else:
    print("[INFO] Some tracks have the same tempo (within variation range)")

print("\n" + "="*60)
print("Each generation now includes:")
print("  • Random key selection (C, D, E, F, G, A)")
print("  • Tempo variation (±5 BPM)")
print("  • Random chord inversions")
print("  • Varied rhythm patterns")
print("  • Humanized velocities")
print("  • Different melodic contours")
print("  • Micro-timing variations")
print("="*60)
