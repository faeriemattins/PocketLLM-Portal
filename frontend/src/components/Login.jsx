import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Shield, ArrowRight, Cpu, Lock } from 'lucide-react';
import { clsx } from 'clsx';

const Login = () => {
    const [mode, setMode] = useState(null); // 'user' | 'admin' | null
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('admin123');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleLogin = (e) => {
        e.preventDefault();
        // Mock validation - accept anything for now as requested
        if (username && password) {
            login(mode);
            navigate(mode === 'admin' ? '/admin' : '/');
        }
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden font-sans">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-noise opacity-20 pointer-events-none mix-blend-overlay" />
            <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-accent/20 rounded-full blur-[120px] pointer-events-none" />

            <div className="w-full max-w-md relative z-10">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/25 mb-4">
                        <Cpu className="text-white" size={32} />
                    </div>
                    <h1 className="text-4xl font-heading font-bold text-white mb-2 tracking-tight">PocketLLM</h1>
                    <p className="text-gray-400">Local Inference Portal</p>
                </div>

                <div className="glass rounded-2xl p-1 border border-white/10 shadow-2xl backdrop-blur-xl">
                    {!mode ? (
                        <div className="p-6 space-y-4">
                            <h2 className="text-xl font-medium text-white mb-6 text-center">Select Access Mode</h2>

                            <button
                                onClick={() => setMode('user')}
                                className="w-full group relative flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-primary/50 transition-all duration-300"
                            >
                                <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <User className="text-blue-400" size={24} />
                                </div>
                                <div className="text-left flex-1">
                                    <h3 className="text-white font-medium">User Mode</h3>
                                    <p className="text-sm text-gray-400">Access Chat Interface</p>
                                </div>
                                <ArrowRight className="text-gray-500 group-hover:text-white transition-colors" size={20} />
                            </button>

                            <button
                                onClick={() => setMode('admin')}
                                className="w-full group relative flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-purple/50 transition-all duration-300"
                            >
                                <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <Shield className="text-purple-400" size={24} />
                                </div>
                                <div className="text-left flex-1">
                                    <h3 className="text-white font-medium">Admin Mode</h3>
                                    <p className="text-sm text-gray-400">System Dashboard & Cache</p>
                                </div>
                                <ArrowRight className="text-gray-500 group-hover:text-white transition-colors" size={20} />
                            </button>
                        </div>
                    ) : (
                        <div className="p-8">
                            <button
                                onClick={() => setMode(null)}
                                className="text-sm text-gray-400 hover:text-white mb-6 flex items-center gap-2 transition-colors"
                            >
                                ← Back to modes
                            </button>

                            <h2 className="text-2xl font-heading font-bold text-white mb-6">
                                {mode === 'admin' ? 'Admin Login' : 'User Login'}
                            </h2>

                            <form onSubmit={handleLogin} className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300">Username</label>
                                    <div className="relative">
                                        <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                                        <input
                                            type="text"
                                            value={username}
                                            onChange={(e) => setUsername(e.target.value)}
                                            className="w-full bg-black/20 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
                                            placeholder="Enter username"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300">Password</label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            className="w-full bg-black/20 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
                                            placeholder="Enter password"
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    className={clsx(
                                        "w-full text-white font-medium py-3 rounded-xl transition-all duration-300 shadow-lg mt-6",
                                        mode === 'admin'
                                            ? "bg-purple-600 hover:bg-purple-500 shadow-purple-500/25"
                                            : "bg-primary hover:bg-primary/90 shadow-primary/25"
                                    )}
                                >
                                    {mode === 'admin' ? 'Access Dashboard' : 'Login to Chat'}
                                </button>
                            </form>
                        </div>
                    )}
                </div>

                <p className="text-center text-gray-600 text-sm mt-8">
                    PocketLLM v1.0.0 • Secure Local Environment
                </p>
            </div>
        </div>
    );
};

export default Login;
