import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { BarChart3, TrendingUp, Music } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Dashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<any>(null);

    useEffect(() => {
        api.getDashboardMetrics().then(setMetrics).catch(console.error);
    }, []);

    const barData = {
        labels: ['Pop', 'Lo-fi', 'Jazz', 'EDM', 'Acoustic'],
        datasets: [
            {
                label: 'Tracks Generated',
                data: [65, 59, 80, 81, 56],
                backgroundColor: 'rgba(139, 92, 246, 0.6)',
                borderColor: 'rgba(139, 92, 246, 1)',
                borderWidth: 1,
            },
        ],
    };

    const doughnutData = {
        labels: ['In-Tune', 'Sharp', 'Flat'],
        datasets: [
            {
                label: '# of Tunings',
                data: [12, 19, 3],
                backgroundColor: [
                    'rgba(74, 222, 128, 0.6)',
                    'rgba(250, 204, 21, 0.6)',
                    'rgba(248, 113, 113, 0.6)',
                ],
                borderColor: [
                    'rgba(74, 222, 128, 1)',
                    'rgba(250, 204, 21, 1)',
                    'rgba(248, 113, 113, 1)',
                ],
                borderWidth: 1,
            },
        ],
    };

    if (!metrics) return <div className="p-20 text-center">Loading Analytics...</div>;

    return (
        <div className="min-h-screen py-24 px-4 w-full max-w-6xl mx-auto">
            <h1 className="text-4xl font-bold mb-8">System Dashboard</h1>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="glass-panel p-6 flex items-center gap-4">
                    <div className="p-3 bg-purple-500/20 rounded-full text-purple-400">
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <p className="text-slate-400 text-sm">Total Tunes</p>
                        <p className="text-2xl font-bold">{metrics.total_tunes}</p>
                    </div>
                </div>
                <div className="glass-panel p-6 flex items-center gap-4">
                    <div className="p-3 bg-green-500/20 rounded-full text-green-400">
                        <BarChart3 size={24} />
                    </div>
                    <div>
                        <p className="text-slate-400 text-sm">Accuracy Rate</p>
                        <p className="text-2xl font-bold">{metrics.average_accuracy}</p>
                    </div>
                </div>
                <div className="glass-panel p-6 flex items-center gap-4">
                    <div className="p-3 bg-blue-500/20 rounded-full text-blue-400">
                        <Music size={24} />
                    </div>
                    <div>
                        <p className="text-slate-400 text-sm">Songs Created</p>
                        <p className="text-2xl font-bold">{metrics.songs_generated}</p>
                    </div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="glass-panel p-6">
                    <h3 className="text-xl font-bold mb-4">Genre Popularity</h3>
                    <div className="h-64">
                        <Bar data={barData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
                    </div>
                </div>

                <div className="glass-panel p-6">
                    <h3 className="text-xl font-bold mb-4">Tuning Accuracy Distribution</h3>
                    <div className="h-64 flex justify-center">
                        <Doughnut data={doughnutData} options={{ responsive: true, maintainAspectRatio: false }} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
