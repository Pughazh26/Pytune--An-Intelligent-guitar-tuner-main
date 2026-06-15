import React, { useState } from 'react';
import { api, MusicGenerationResult } from '../services/api';
import { Play, Download, Wand2, Music4, Disc } from 'lucide-react';



const GENRES = ['Pop', 'Lo-fi', 'Jazz', 'EDM', 'Acoustic', 'Rock'];
const MOODS = ['Happy', 'Sad', 'Energetic', 'Chill', 'Melancholic'];
const INSTRUMENTS = [
    { id: 'piano', name: 'Piano', icon: '🎹' },
    { id: 'guitar', name: 'Guitar', icon: '🎸' },
    { id: 'bass', name: 'Bass', icon: '🎸' },
    { id: 'drums', name: 'Drums', icon: '🥁' },
    { id: 'synth', name: 'Synth', icon: '🎛️' },
    { id: 'pad', name: 'Pad', icon: '🌊' },
];

const MusicGenerator: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<MusicGenerationResult | null>(null);

    // Form State
    const [genre, setGenre] = useState('Pop');
    const [mood, setMood] = useState('Happy');
    const [tempo, setTempo] = useState(120);
    const [duration, setDuration] = useState(10);
    const [selectedInstruments, setSelectedInstruments] = useState<string[]>(['piano', 'bass', 'drums']);

    const toggleInstrument = (instrumentId: string) => {
        setSelectedInstruments(prev =>
            prev.includes(instrumentId)
                ? prev.filter(id => id !== instrumentId)
                : [...prev, instrumentId]
        );
    };

    const handleGenerate = async () => {
        if (selectedInstruments.length === 0) {
            alert("Please select at least one instrument!");
            return;
        }

        setLoading(true);
        try {
            const res = await api.generateMusic(genre, tempo, mood, duration, selectedInstruments);
            setResult(res);
        } catch (e) {
            console.error(e);
            alert("Failed to generate music. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            className="min-h-[80vh] py-10 px-4 flex flex-col items-center justify-center"
        >
            <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

                {/* 1. VISUALIZER SECTION */}
                <div className="relative order-2 lg:order-1">
                    <div className={`relative w-full aspect-square max-w-md mx-auto bg-black/40 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden flex flex-col items-center justify-center transition-all duration-500 hover:border-purple-500/30 group shadow-2xl shadow-black/50`}>

                        {/* Glowing Background Effect */}
                        <div className={`absolute inset-0 bg-gradient-to-tr from-purple-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700`} />

                        {!result ? (
                            <div className="text-center space-y-6 z-10 p-6">
                                <div className="relative">
                                    <div className={`w-32 h-32 rounded-full border-2 border-dashed border-white/20 flex items-center justify-center mx-auto ${loading ? 'animate-spin-slow' : ''}`}>
                                        <Music4 className={`w-12 h-12 text-white/50 ${loading ? 'animate-pulse text-purple-400' : ''}`} />
                                    </div>
                                    {loading && (
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <div className="w-24 h-24 bg-purple-500/20 rounded-full blur-xl animate-pulse" />
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <h3 className="text-xl font-bold tracking-wide text-white">
                                        {loading ? "Synthesizing..." : "AI Composer Ready"}
                                    </h3>
                                    <p className="text-sm text-slate-400 max-w-xs mx-auto">
                                        {loading ? "Generating harmonies and rhythms based on your customized parameters." : "Select your preferences and let the AI build a unique track for you."}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center p-8 z-10 animate-in fade-in zoom-in duration-500">

                                <div className="relative group/disc cursor-pointer">
                                    <div className="absolute inset-0 bg-purple-500 rounded-full blur-2xl opacity-20 group-hover/disc:opacity-40 transition-opacity" />
                                    <div className="w-48 h-48 rounded-full bg-slate-900 border border-white/10 flex items-center justify-center relative overflow-hidden animate-[spin_5s_linear_infinite]">
                                        <div className="absolute inset-0 bg-[conic-gradient(from_0deg,transparent,rgba(168,85,247,0.2),transparent)]" />
                                        <Disc className="w-20 h-20 text-white/80" />
                                    </div>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg shadow-purple-500/50">
                                            <Play className="w-5 h-5 text-purple-900 fill-current ml-1" />
                                        </div>
                                    </div>
                                </div>

                                <div className="text-center mt-8 space-y-1">
                                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                                        {mood} {genre}
                                    </h2>
                                    <div className="flex items-center justify-center gap-2 text-xs font-mono text-purple-400 uppercase tracking-widest">
                                        <span>{tempo} BPM</span>
                                        <span>•</span>
                                        <span>{duration} SEC</span>
                                    </div>
                                </div>

                                <div className="w-full mt-6 bg-white/5 rounded-xl p-2">
                                    <audio controls className="w-full h-8 opacity-80 hover:opacity-100 transition-opacity" src={result.audio_url} />
                                </div>

                                <div className="flex gap-3 mt-6 w-full">
                                    <a href={result.audio_url} download className="flex-1 btn-glass flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold hover:bg-white/10 transition-colors border border-white/5">
                                        <Download size={16} /> WAV
                                    </a>
                                    <a href={result.midi_url} download className="flex-1 btn-glass flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold hover:bg-white/10 transition-colors border border-white/5">
                                        <Download size={16} /> MIDI
                                    </a>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* 2. CONTROLS SECTION */}
                <div className="order-1 lg:order-2 space-y-8">
                    <div className="space-y-4">
                        <h1
                            className="text-5xl md:text-6xl font-black tracking-tighter text-white"
                        >
                            PYTUNE<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-500"> AI</span>
                        </h1>
                        <p className="text-lg text-slate-400 max-w-md border-l-2 border-indigo-500/50 pl-4">
                            Advanced AI music generation powered by neural rhythms. Create unique, professional-grade compositions instantly.
                        </p>
                    </div>

                    <div className="space-y-8 bg-white/5 p-8 rounded-3xl border border-white/10 backdrop-blur-sm">

                        {/* Genre Selection */}
                        <div className="space-y-3">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Genre</label>
                            <div className="flex flex-wrap gap-2">
                                {GENRES.map(g => (
                                    <button
                                        key={g}
                                        onClick={() => setGenre(g)}
                                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 border ${genre === g
                                            ? 'bg-purple-600 border-purple-500 text-white shadow-[0_0_15px_rgba(147,51,234,0.5)] scale-105'
                                            : 'bg-transparent border-white/10 text-slate-400 hover:border-white/30 hover:text-white'
                                            }`}
                                    >
                                        {g}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Mood Dropdown */}
                        <div className="space-y-3">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Mood / Vibe</label>
                            <div className="relative">
                                <select
                                    value={mood}
                                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setMood(e.target.value)}
                                    className="w-full p-4 rounded-xl bg-black/40 border border-white/10 text-white appearance-none focus:outline-none focus:border-purple-500 transition-colors cursor-pointer"
                                >
                                    {MOODS.map(m => <option key={m} value={m} className="bg-slate-900">{m}</option>)}
                                </select>
                                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">▼</div>
                            </div>
                        </div>

                        {/* Sliders Grid */}
                        <div className="grid grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <div className="flex justify-between text-xs font-bold text-purple-300 uppercase">
                                    <span>Tempo</span>
                                    <span>{tempo} BPM</span>
                                </div>
                                <input
                                    type="range"
                                    min="60"
                                    max="180"
                                    value={tempo}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTempo(parseInt(e.target.value))}
                                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500 hover:accent-purple-400 transition-all"
                                />
                            </div>

                            <div className="space-y-4">
                                <div className="flex justify-between text-xs font-bold text-pink-300 uppercase">
                                    <span>Duration</span>
                                    <span>{duration}s</span>
                                </div>
                                <input
                                    type="range"
                                    min="5"
                                    max="60"
                                    value={duration}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDuration(parseInt(e.target.value))}
                                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-pink-500 hover:accent-pink-400 transition-all"
                                />
                            </div>
                        </div>

                        {/* Instrument Selection */}
                        <div className="space-y-3">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Instruments</label>
                            <div className="grid grid-cols-3 gap-2">
                                {INSTRUMENTS.map(inst => (
                                    <button
                                        key={inst.id}
                                        type="button"
                                        onClick={() => toggleInstrument(inst.id)}
                                        className={`px-3 py-3 rounded-xl text-sm font-medium transition-all duration-300 border flex items-center justify-center gap-2 ${selectedInstruments.includes(inst.id)
                                            ? 'bg-indigo-600 border-indigo-500 text-white shadow-[0_0_15px_rgba(99,102,241,0.5)] scale-105'
                                            : 'bg-transparent border-white/10 text-slate-400 hover:border-white/30 hover:text-white'
                                            }`}
                                    >
                                        <span className="text-lg">{inst.icon}</span>
                                        <span className="text-xs">{inst.name}</span>
                                    </button>
                                ))}
                            </div>
                            {selectedInstruments.length === 0 && (
                                <p className="text-xs text-rose-400 mt-1">⚠️ Select at least one instrument</p>
                            )}
                        </div>

                        {/* Generate Button */}
                        <button
                            onClick={handleGenerate}
                            disabled={loading || selectedInstruments.length === 0}
                            className="w-full group relative overflow-hidden bg-white text-black font-bold py-5 rounded-2xl shadow-xl transform transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                            <span className="relative z-10 flex items-center justify-center gap-3 text-lg">
                                {loading ? (
                                    <>Processing <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" /></>
                                ) : (
                                    <><Wand2 size={20} /> GENERATE TRACK</>
                                )}
                            </span>
                        </button>

                    </div>
                </div>

            </div>
        </div>
    );
};

export default MusicGenerator;
