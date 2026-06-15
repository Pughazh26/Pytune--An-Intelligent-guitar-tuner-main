import React, { useEffect, useRef, useState } from 'react';
import { api, TuningResult } from '../services/api';
import { Mic, Activity, RefreshCcw } from 'lucide-react';
import { motion } from 'framer-motion';

const CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

// WAV Encoding Helper
const encodeWAV = (samples: Float32Array, sampleRate: number) => {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);
    const writeString = (offset: number, str: string) => {
        for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
    };
    writeString(0, 'RIFF');
    view.setUint32(4, 32 + samples.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, samples.length * 2, true);
    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
        const s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return new Blob([view], { type: 'audio/wav' });
};

const Tuner: React.FC = () => {
    const [isListening, setIsListening] = useState(false);
    const [tuningResult, setTuningResult] = useState<TuningResult | null>(null);
    const [smoothedResult, setSmoothedResult] = useState<TuningResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<string>('');
    const [sensitivity, setSensitivity] = useState(2.0);
    const [volume, setVolume] = useState(0);

    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const gainNodeRef = useRef<GainNode | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const lastVolumeCheckRef = useRef<number>(Date.now());
    const dataArrayRef = useRef<Float32Array | null>(null);
    const isListeningRef = useRef(false);

    // Auto-Gain Engine
    useEffect(() => {
        if (!isListening || !gainNodeRef.current) return;

        const adjustGain = () => {
            if (volume > 95) {
                setSensitivity(prev => Math.max(1, prev - 0.2));
            } else if (volume < 30 && volume > 0) {
                setSensitivity(prev => Math.min(10, prev + 0.1));
            }
        };

        const timer = setInterval(adjustGain, 500);
        return () => clearInterval(timer);
    }, [isListening, volume]);

    useEffect(() => {
        if (gainNodeRef.current && audioContextRef.current) {
            gainNodeRef.current.gain.setTargetAtTime(sensitivity, audioContextRef.current.currentTime, 0.1);
        }
    }, [sensitivity]);

    // Initial permissions & Device list
    useEffect(() => {
        const getDevices = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                stream.getTracks().forEach(t => t.stop());
                const devices = await navigator.mediaDevices.enumerateDevices();
                const inputs = devices.filter(d => d.kind === 'audioinput');
                setDevices(inputs);
                if (inputs.length > 0 && !selectedDevice) {
                    const best = inputs.find(d =>
                        !d.label.toLowerCase().includes('stereo mix') &&
                        (d.label.toLowerCase().includes('mic') || d.label.toLowerCase().includes('internal'))
                    );
                    setSelectedDevice(best ? best.deviceId : inputs[0].deviceId);
                }
            } catch (err) {
                console.error("Device access error", err);
                setError("Permission denied. Enable microphone access in your browser settings.");
            }
        };
        getDevices();
        return () => stopListening();
    }, []);

    // Draw Loop
    const drawWaveform = () => {
        if (!analyserRef.current || !canvasRef.current || !isListeningRef.current) {
            console.log("Draw loop halted: ", { analyser: !!analyserRef.current, canvas: !!canvasRef.current, listening: isListeningRef.current });
            return;
        }

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (audioContextRef.current?.state === 'suspended') {
            audioContextRef.current.resume();
        }

        const bufferLength = analyserRef.current.frequencyBinCount;
        if (!dataArrayRef.current) dataArrayRef.current = new Float32Array(bufferLength);

        analyserRef.current.getFloatTimeDomainData(dataArrayRef.current as any);

        let sum = 0;
        for (let i = 0; i < bufferLength; i++) sum += dataArrayRef.current[i] * dataArrayRef.current[i];
        const rms = Math.sqrt(sum / bufferLength);

        setVolume(Math.min(100, Math.floor(rms * 1000 * sensitivity)));

        if (rms < 0.0001) {
            // Volume is effectively zero
        } else {
            lastVolumeCheckRef.current = Date.now();
        }

        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#a78bfa';
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#a78bfa';
        ctx.beginPath();

        const xStep = canvas.width / bufferLength;
        let x = 0;
        for (let i = 0; i < bufferLength; i++) {
            const v = dataArrayRef.current[i] * sensitivity;
            const y = (v + 1) * canvas.height / 2;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
            x += xStep;
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
        requestAnimationFrame(drawWaveform);
    };

    const startListening = async () => {
        try {
            setError(null);
            if (audioContextRef.current) await audioContextRef.current.close();

            const constraints: MediaStreamConstraints = {
                audio: {
                    deviceId: (selectedDevice && selectedDevice !== 'default') ? { exact: selectedDevice } : undefined,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            mediaStreamRef.current = stream;

            // USE DEVICE DEFAULT SAMPLE RATE (Fixes Intel Smart Sound issues)
            audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
            await audioContextRef.current.resume();

            const source = audioContextRef.current.createMediaStreamSource(stream);
            gainNodeRef.current = audioContextRef.current.createGain();
            gainNodeRef.current.gain.value = sensitivity;

            analyserRef.current = audioContextRef.current.createAnalyser();
            analyserRef.current.fftSize = 16384; // Max size for better low-pitch detection (~340ms)

            source.connect(gainNodeRef.current);
            gainNodeRef.current.connect(analyserRef.current);

            const silent = audioContextRef.current.createGain();
            silent.gain.value = 0;
            analyserRef.current.connect(silent);
            silent.connect(audioContextRef.current.destination);

            setIsListening(true);
            isListeningRef.current = true;
            lastVolumeCheckRef.current = Date.now();

            console.log("Audio Engine Started", {
                sampleRate: audioContextRef.current.sampleRate,
                deviceId: selectedDevice
            });

            drawWaveform();
            intervalRef.current = setInterval(captureAndSend, 1500);

        } catch (err) {
            console.error(err);
            setError("Could not start microphone. Try selecting exactly 'Microphone Array' from the dropdown.");
        }
    };

    const stopListening = () => {
        setIsListening(false);
        isListeningRef.current = false;
        if (intervalRef.current) clearInterval(intervalRef.current);
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(t => t.stop());
            mediaStreamRef.current = null;
        }
        if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
            audioContextRef.current.close().then(() => { audioContextRef.current = null; });
        }
    };

    const captureAndSend = async () => {
        if (!analyserRef.current || !audioContextRef.current || !isListeningRef.current) return;

        try {
            // Use the full FFT buffer size for accurate pitch detection
            const bufLen = analyserRef.current.fftSize;
            const samples = new Float32Array(bufLen);
            analyserRef.current.getFloatTimeDomainData(samples as any);

            // 1. Noise Gate: Calculate RMS for the captured chunk
            let sum = 0;
            let peak = 0;
            for (let i = 0; i < samples.length; i++) {
                const absVal = Math.abs(samples[i]);
                sum += absVal * absVal;
                if (absVal > peak) peak = absVal;
            }
            const rms = Math.sqrt(sum / samples.length);

            // Only send if the signal is clearly above background noise (0.01 threshold)
            // AND there's enough peak amplitude to distinguish from hum
            if (rms < 0.008 || peak < 0.02) {
                console.log("Noise Gate: Signal too weak to analyze", { rms, peak });
                return;
            }

            const wavBlob = encodeWAV(samples, audioContextRef.current.sampleRate);
            const res = await api.tuneAudio(wavBlob);

            setTuningResult(res);

            // Apply smoothing for the UI
            setSmoothedResult(prev => {
                if (!prev || res.detected_pitch === '---') return res;
                // If the note changed, jump to it but keep the physics smooth
                if (prev.detected_pitch !== res.detected_pitch) return res;

                // If same note, lerp the frequency and cents for stability
                return {
                    ...res,
                    frequency: prev.frequency * 0.4 + res.frequency * 0.6,
                    tuning_offset_cents: prev.tuning_offset_cents * 0.3 + res.tuning_offset_cents * 0.7
                };
            });
        } catch (err) {
            console.error("API Error", err);
        }
    };

    const hardReset = () => {
        stopListening();
        setTimeout(startListening, 500);
    };

    const getTuningData = () => {
        return smoothedResult || tuningResult;
    };

    const displayResult = getTuningData();
    const getMeterRotation = (c: number) => (Math.max(-50, Math.min(50, c)) / 50) * 45;
    const getStatusColor = (s: string) => s === 'In-Tune' ? 'text-emerald-400 drop-shadow-[0_0_15px_rgba(52,211,153,0.5)]' : s === 'Sharp' ? 'text-amber-400' : s === 'Flat' ? 'text-rose-400' : 'text-slate-500';

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] w-full p-4 relative overflow-hidden bg-slate-950">
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none opacity-20 z-0">
                <div className="absolute top-20 left-20 w-80 h-80 bg-indigo-600 rounded-full blur-[120px] animate-pulse"></div>
                <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-600 rounded-full blur-[150px] animate-pulse-slow"></div>
            </div>

            <div className="z-10 w-full max-w-4xl flex flex-col items-center gap-10 text-white">
                <div className="text-center space-y-3">
                    <h1 className="text-6xl font-black bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-indigo-300 tracking-tight">Precision Tuner</h1>
                    <p className="text-slate-400 text-lg">Intelligent ML-Powered Analysis</p>
                </div>

                <div className="backdrop-blur-xl bg-slate-900/60 border border-white/10 p-10 w-full max-w-xl aspect-square rounded-[3rem] flex flex-col items-center justify-between relative shadow-2xl overflow-hidden">
                    {/* Self-Optimizing Status Indicator */}
                    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 pointer-events-none opacity-40">
                        <div className="flex items-center gap-2 text-[8px] font-black uppercase tracking-[0.4em] text-indigo-300">
                            <RefreshCcw size={8} className="animate-spin-slow" /> Auto-Leveling Active
                        </div>
                    </div>

                    <div className="w-full flex justify-center items-center gap-1 overflow-hidden py-4 px-2 relative">
                        <div className="absolute inset-y-0 left-0 w-16 bg-gradient-to-r from-slate-900 to-transparent z-10"></div>
                        <div className="absolute inset-y-0 right-0 w-16 bg-gradient-to-l from-slate-900 to-transparent z-10"></div>

                        <div className="flex gap-3 transition-transform duration-500 ease-out">
                            {/* Show a window of notes around the detected one, or just a default set */}
                            {[-3, -2, -1, 0, 1, 2, 3].map(offset => {
                                if (!displayResult || displayResult.detected_pitch === '---') {
                                    return (
                                        <div key={offset} className="w-12 h-16 rounded-xl border border-slate-800 flex items-center justify-center text-slate-700 font-bold opacity-30">
                                            {CHROMATIC_SCALE[(offset + 12) % 12]}
                                        </div>
                                    );
                                }

                                // Parse detected note (e.g., "C#4")
                                const match = displayResult.detected_pitch.match(/^([A-G]#?)(\d+)$/);
                                if (!match) return null;

                                const currentNoteName = match[1];
                                const currentOctave = parseInt(match[2]);
                                const nameIdx = CHROMATIC_SCALE.indexOf(currentNoteName);

                                // Calculate adjacent note
                                let targetIdx = nameIdx + offset;
                                let targetOctave = currentOctave;
                                while (targetIdx < 0) { targetIdx += 12; targetOctave--; }
                                while (targetIdx >= 12) { targetIdx -= 12; targetOctave++; }

                                const noteName = CHROMATIC_SCALE[targetIdx];
                                const isCenter = offset === 0;

                                return (
                                    <motion.div
                                        key={`${noteName}${targetOctave}`}
                                        initial={false}
                                        animate={{
                                            scale: isCenter ? 1.2 : 0.8,
                                            opacity: isCenter ? 1 : 0.4,
                                            backgroundColor: isCenter ? 'rgba(99, 102, 241, 0.2)' : 'rgba(30, 41, 59, 0.4)',
                                            borderColor: isCenter ? '#818cf8' : '#334155'
                                        }}
                                        className={`w-14 h-20 rounded-2xl border-2 flex flex-col items-center justify-center transition-colors shadow-lg`}
                                    >
                                        <span className={`text-xs ${isCenter ? 'text-indigo-400' : 'text-slate-600'} font-black`}>{targetOctave}</span>
                                        <span className={`text-xl ${isCenter ? 'text-white' : 'text-slate-400'} font-black`}>{noteName}</span>
                                        {isCenter && <motion.div layoutId="indicator" className="w-1 h-1 bg-indigo-400 rounded-full mt-1" />}
                                    </motion.div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="relative w-72 h-36 mt-4 overflow-hidden">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 border-[12px] border-slate-800/40 rounded-full border-b-0 border-l-0 border-r-0 origin-center rotate-[-45deg]"></div>
                        <motion.div
                            className="absolute bottom-0 left-1/2 w-1.5 h-32 bg-white origin-bottom rounded-full shadow-[0_0_20px_white]"
                            animate={{ rotate: displayResult ? getMeterRotation(displayResult.tuning_offset_cents) : 0 }}
                            transition={{ type: "spring", stiffness: 40, damping: 20 }}
                        />
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-5 h-5 bg-indigo-500 rounded-full z-10 border-4 border-slate-900 shadow-xl"></div>
                    </div>

                    <div className="text-center h-40 flex flex-col justify-center gap-1">
                        {displayResult ? (
                            <>
                                <span className="text-indigo-400 uppercase font-black tracking-[0.3em] text-[10px] mb-1">Detected Note</span>
                                <h2 className="text-7xl font-black text-white tracking-tighter drop-shadow-2xl">{displayResult.detected_pitch}</h2>
                                <h3 className={`text-2xl font-black tracking-widest mt-2 ${getStatusColor(displayResult.tuning_status)}`}>{displayResult.tuning_status.toUpperCase()}</h3>
                                <p className="text-sm text-slate-500 font-mono mt-2">{displayResult.frequency} Hz • {displayResult.tuning_offset_cents > 0 ? '+' : ''}{displayResult.tuning_offset_cents} cents</p>
                            </>
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <p className="text-2xl text-slate-600 font-bold animate-pulse">Waiting for audio</p>
                                <div className="flex gap-1">{[1, 2, 3].map(i => <div key={i} className="w-1.5 h-1.5 bg-slate-700 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.2}s` }}></div>)}</div>
                            </div>
                        )}
                    </div>

                    <div className="w-full space-y-3">
                        <div className="flex justify-between items-end px-1 text-[10px] font-black uppercase text-slate-500 tracking-widest">
                            <span>Input Pulse</span>
                            <span className={volume > 30 ? 'text-emerald-400' : ''}>{volume}%</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-800/50 rounded-full overflow-hidden">
                            <motion.div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500" animate={{ width: `${volume}%` }} />
                        </div>
                        <canvas ref={canvasRef} width="400" height="80" className="w-full h-20 rounded-2xl opacity-80 mix-blend-screen"></canvas>
                    </div>

                    <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-5 mt-4">
                        <div className="flex flex-col gap-1.5">
                            <label className="text-[10px] text-slate-500 uppercase tracking-widest font-black">Hardware Source</label>
                            <select disabled={isListening} value={selectedDevice} onChange={e => setSelectedDevice(e.target.value)} className="bg-slate-800/40 border border-white/5 text-slate-300 text-xs rounded-xl p-3 outline-none backdrop-blur-md">
                                {devices.map(d => <option key={d.deviceId} value={d.deviceId} className="bg-slate-900">{d.label || `Mic ${d.deviceId.slice(0, 5)}`}</option>)}
                            </select>
                        </div>
                        <div className="flex flex-col gap-1.5 opacity-50">
                            <div className="flex justify-between items-center text-[10px] text-slate-500 uppercase tracking-widest font-black">
                                <span>Signal Sensitivity</span>
                                <span className="text-indigo-400">Auto ({sensitivity.toFixed(1)}x)</span>
                            </div>
                            <div className="h-1.5 w-full bg-slate-800 rounded-lg overflow-hidden relative">
                                <div className="absolute top-0 left-0 h-full bg-indigo-500 transition-all duration-500" style={{ width: `${(sensitivity / 10) * 100}%` }}></div>
                            </div>
                        </div>
                    </div>

                </div>

                <div className="flex flex-col items-center gap-6 w-full max-w-sm">
                    <button onClick={isListening ? stopListening : startListening} className={`w-full py-6 rounded-[2rem] font-black text-2xl flex items-center justify-center gap-4 transition-all shadow-2xl ${isListening ? 'bg-rose-500 text-white' : 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'}`}>
                        {isListening ? <><Activity className="animate-pulse" /> Stop Listening</> : <><Mic /> Start Tuning</>}
                    </button>
                    {isListening && <button onClick={hardReset} className="flex items-center gap-2 text-[10px] uppercase font-black text-slate-500 hover:text-white transition-colors"><RefreshCcw size={12} /> Restart Audio Engine</button>}
                    {error && <div className="text-red-400 bg-red-400/10 p-4 rounded-2xl text-[11px] border border-red-400/20">{error}</div>}
                </div>
            </div>
        </div>
    );
};

export default Tuner;
