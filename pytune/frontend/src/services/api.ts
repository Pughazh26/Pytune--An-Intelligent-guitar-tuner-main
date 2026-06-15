import axios from 'axios';

const API_URL = '/api';

export interface TuningResult {
    detected_pitch: string;
    frequency: number;
    tuning_offset_cents: number;
    tuning_status: string;
    confidence: number;
}

export interface MusicGenerationResult {
    genre: string;
    audio_url: string;
    midi_url: string;
    instruments?: string[];
}

export const api = {
    tuneAudio: async (audioBlob: Blob): Promise<TuningResult> => {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');
        const response = await axios.post(`${API_URL}/tune`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    generateMusic: async (genre: string, tempo: number, mood: string, duration: number, instruments?: string[]): Promise<MusicGenerationResult> => {
        const response = await axios.post(`${API_URL}/generate-music`, {
            genre,
            tempo,
            mood,
            duration,
            instruments
        });
        return response.data;
    },

    getDashboardMetrics: async () => {
        const response = await axios.get(`${API_URL}/dashboard-metrics`);
        return response.data;
    }
};
