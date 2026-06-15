import { Routes, Route, useLocation } from 'react-router-dom';
import Navigation from './components/Navigation';
import Tuner from './pages/Tuner';
import MusicGenerator from './pages/MusicGenerator';
import Dashboard from './pages/Dashboard';
import { AnimatePresence } from 'framer-motion';

function App() {
    const location = useLocation();

    return (
        <div className="min-h-screen relative overflow-x-hidden bg-slate-950 text-white selection:bg-purple-500/30">

            {/* Global Animated Background */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-purple-900/20 rounded-full blur-[120px] animate-pulse-slow" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-indigo-900/20 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
                <div className="absolute top-[40%] left-[40%] w-[20%] h-[20%] bg-blue-900/10 rounded-full blur-[100px] animate-pulse" />
            </div>

            <Navigation />

            <main className="relative z-10 pb-24 pt-4 md:pb-4 md:pt-20 max-w-7xl mx-auto">
                <AnimatePresence mode="wait">
                    <Routes location={location} key={location.pathname}>
                        <Route path="/" element={<Tuner />} />
                        <Route path="/generate" element={<MusicGenerator />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                    </Routes>
                </AnimatePresence>
            </main>
        </div>
    );
}

export default App;
