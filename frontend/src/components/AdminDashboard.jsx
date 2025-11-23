import React, { useEffect, useState } from 'react';
import { adminApi } from '../api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, Database, Cpu, Trash2, RefreshCw, Zap, Server, Save } from 'lucide-react';

const AdminDashboard = () => {
    const [systemStats, setSystemStats] = useState(null);
    const [cacheStats, setCacheStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [cacheConfig, setCacheConfig] = useState({ size_limit_mb: 0 });
    const [modelData, setModelData] = useState({ models: [], current_model: '' });
    const [newCacheLimit, setNewCacheLimit] = useState(0);

    const fetchData = async () => {
        try {
            const [sysRes, cacheRes] = await Promise.all([
                adminApi.getSystemStats(),
                adminApi.getCacheStats()
            ]);
            setSystemStats(sysRes.data);
            setCacheStats(cacheRes.data);

            setHistory(prev => {
                const newPoint = {
                    time: new Date().toLocaleTimeString(),
                    cpu: sysRes.data.cpu_percent,
                    mem: sysRes.data.memory_percent
                };
                const newHistory = [...prev, newPoint];
                if (newHistory.length > 20) newHistory.shift();
                return newHistory;
            });
        } catch (error) {
            console.error("Failed to fetch stats", error);
        }
    };

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const [configRes, modelsRes] = await Promise.all([
                    adminApi.getCacheConfig(),
                    adminApi.getModels()
                ]);
                setCacheConfig(configRes.data);
                setNewCacheLimit(configRes.data.size_limit_mb);
                setModelData(modelsRes.data);
            } catch (error) {
                console.error("Failed to fetch config", error);
            }
        };

        fetchConfig();
        fetchData();
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    const handleSaveCacheConfig = async () => {
        try {
            await adminApi.setCacheConfig(parseInt(newCacheLimit));
            setCacheConfig(prev => ({ ...prev, size_limit_mb: parseInt(newCacheLimit) }));
            alert("Cache size limit updated!");
        } catch (error) {
            console.error("Failed to update cache config", error);
            alert("Failed to update cache config");
        }
    };

    const handleModelChange = async (e) => {
        const model = e.target.value;
        if (!model) return;
        try {
            await adminApi.selectModel(model);
            setModelData(prev => ({ ...prev, current_model: model }));
            alert(`Model changed to ${model}`);
        } catch (error) {
            console.error("Failed to change model", error);
            alert("Failed to change model");
        }
    };

    const handleClearCache = async () => {
        if (window.confirm("Are you sure you want to clear the cache?")) {
            try {
                await adminApi.clearCache();
                await fetchData();
                alert("Cache cleared successfully!");
            } catch (error) {
                console.error("Failed to clear cache:", error);
                alert("Failed to clear cache. Check console for details.");
            }
        }
    };

    if (!systemStats) return (
        <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                <p className="text-gray-400 animate-pulse">Connecting to system...</p>
            </div>
        </div>
    );

    return (
        <div className="p-8 space-y-8 h-full overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-3xl font-heading font-bold text-white tracking-tight">System Overview</h2>
                    <p className="text-gray-400 mt-1">Real-time performance monitoring</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium shadow-lg shadow-emerald-500/5">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    Live Monitoring
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={<Cpu className="text-primary" />}
                    label="CPU Usage"
                    value={`${systemStats.cpu_percent}%`}
                    trend={systemStats.cpu_percent > 80 ? 'high' : 'normal'}
                />
                <StatCard
                    icon={<Activity className="text-emerald-400" />}
                    label="Memory Usage"
                    value={`${systemStats.memory_percent}%`}
                    subValue={`${systemStats.memory_used_gb} / ${systemStats.memory_total_gb} GB`}
                />
                <StatCard
                    icon={<Database className="text-accent" />}
                    label="Cache Size"
                    value={`${(cacheStats.size_bytes / (1024 * 1024)).toFixed(2)} MB`}
                    subValue={`${cacheStats.count} items`}
                />
                <div className="glass-card p-6 rounded-2xl flex flex-col justify-between group relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-3 bg-red-500/10 rounded-xl text-red-400">
                                <Server size={20} />
                            </div>
                            <span className="text-gray-400 text-sm font-medium">Maintenance</span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-1">Actions</h3>
                    </div>
                    <button
                        onClick={handleClearCache}
                        className="mt-4 flex items-center justify-center gap-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 py-3 px-4 rounded-xl transition-all duration-300 border border-red-500/20 hover:border-red-500/40 hover:shadow-lg hover:shadow-red-500/10"
                    >
                        <Trash2 size={18} /> Clear Cache
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[400px]">
                <div className="lg:col-span-2 glass-card p-6 rounded-2xl flex flex-col">
                    <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                        <Zap size={18} className="text-yellow-400" />
                        Real-time Performance
                    </h3>
                    <div className="flex-1 w-full min-h-0">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={history}>
                                <defs>
                                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)' }}
                                    itemStyle={{ color: '#e2e8f0' }}
                                />
                                <Area type="monotone" dataKey="cpu" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorCpu)" />
                                <Area type="monotone" dataKey="mem" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorMem)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-card p-6 rounded-2xl flex flex-col relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
                    <h3 className="text-lg font-semibold text-white mb-4">System Health</h3>
                    <div className="space-y-6 mt-2">
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">CPU Load</span>
                                <span className="text-white font-medium">{systemStats.cpu_percent}%</span>
                            </div>
                            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary rounded-full transition-all duration-500"
                                    style={{ width: `${systemStats.cpu_percent}%` }}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">RAM Usage</span>
                                <span className="text-white font-medium">{systemStats.memory_percent}%</span>
                            </div>
                            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                                    style={{ width: `${systemStats.memory_percent}%` }}
                                />
                            </div>
                        </div>

                        <div className="pt-6 border-t border-white/5">
                            <div className="flex items-center gap-3 text-sm text-gray-400">
                                <div className="w-2 h-2 rounded-full bg-green-500" />
                                All systems operational
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Settings Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-card p-6 rounded-2xl">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Database size={18} className="text-accent" />
                        Cache Configuration
                    </h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Max Cache Size (MB)</label>
                            <div className="flex items-center gap-4">
                                <input
                                    type="range"
                                    min="100"
                                    max="10240"
                                    step="100"
                                    value={newCacheLimit}
                                    onChange={(e) => setNewCacheLimit(e.target.value)}
                                    className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-accent"
                                />
                                <span className="text-white font-mono w-20 text-right">{newCacheLimit} MB</span>
                            </div>
                        </div>
                        <button
                            onClick={handleSaveCacheConfig}
                            className="flex items-center gap-2 px-4 py-2 bg-accent/10 text-accent rounded-lg hover:bg-accent/20 transition-colors border border-accent/20"
                        >
                            <Save size={16} /> Save Configuration
                        </button>
                    </div>
                </div>

                <div className="glass-card p-6 rounded-2xl">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Cpu size={18} className="text-primary" />
                        Model Selection
                    </h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Active LLM Model</label>
                            <select
                                value={modelData.current_model}
                                onChange={handleModelChange}
                                className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/50"
                            >
                                {modelData.models.length === 0 && <option value="">No models found</option>}
                                {modelData.models.map(model => (
                                    <option key={model} value={model}>{model}</option>
                                ))}
                            </select>
                            <p className="text-xs text-gray-500 mt-2">
                                Selected model will be used for all new chat sessions.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ icon, label, value, subValue, trend }) => (
    <div className="glass-card p-6 rounded-2xl relative overflow-hidden group hover:-translate-y-1 transition-all duration-300">
        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity transform group-hover:scale-110 duration-500">
            {React.cloneElement(icon, { size: 80 })}
        </div>
        <div className="flex items-center gap-3 mb-4 relative z-10">
            <div className="p-3 bg-white/5 rounded-xl border border-white/5 backdrop-blur-sm group-hover:bg-white/10 transition-colors">
                {icon}
            </div>
            <span className="text-gray-400 text-sm font-medium tracking-wide">{label}</span>
        </div>
        <div className="text-3xl font-mono font-bold text-white tracking-tight relative z-10">{value}</div>
        {subValue && <div className="text-sm text-gray-500 mt-1 font-medium relative z-10">{subValue}</div>}
    </div>
);

export default AdminDashboard;
