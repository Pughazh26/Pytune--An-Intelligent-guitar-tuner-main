import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Mic2, Music, BarChart3, Radio } from 'lucide-react';
import { motion } from 'framer-motion';

const Navigation: React.FC = () => {
    const location = useLocation();

    const links = [
        { path: '/', label: 'Tuner', icon: Mic2 },
        { path: '/generate', label: 'AI Music', icon: Music },
        { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    ];

    return (
        <nav className="fixed bottom-0 left-0 right-0 md:top-0 md:bottom-auto z-50 p-4">
            <div className="glass-panel mx-auto max-w-2xl px-6 py-3 flex justify-between items-center shadow-2xl shadow-indigo-500/20">
                <div className="flex items-center gap-2">
                    <Radio className="text-primary w-6 h-6 animate-pulse" />
                    <span className="font-bold text-xl tracking-tight hidden md:block">PYTUNE</span>
                </div>

                <div className="flex gap-4">
                    {links.map((link) => {
                        const Icon = link.icon;
                        const isActive = location.pathname === link.path;

                        return (
                            <Link to={link.path} key={link.path} className="relative group">
                                {isActive && (
                                    <motion.div
                                        layoutId="nav-pill"
                                        className="absolute inset-0 bg-primary/20 rounded-xl"
                                        transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                    />
                                )}
                                <div className={`relative px-4 py-2 rounded-xl flex items-center gap-2 transition-colors ${isActive ? 'text-primary-foreground' : 'text-muted-foreground hover:text-white'}`}>
                                    <Icon className="w-5 h-5" />
                                    <span className="hidden sm:block font-medium">{link.label}</span>
                                </div>
                            </Link>
                        );
                    })}
                </div>
            </div>
        </nav>
    );
};

export default Navigation;
