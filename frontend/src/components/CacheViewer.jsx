import React, { useState, useEffect } from 'react';
import { adminApi } from '../api';
import { Trash2, RefreshCw, Database, Clock, Hash, Eye, AlertCircle } from 'lucide-react';

const CacheViewer = () => {
    const [cacheData, setCacheData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedKeys, setExpandedKeys] = useState(new Set());

    const fetchCache = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('pocketllm_token');
            const response = await fetch('http://127.0.0.1:8000/admin/cache-items', {
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                }
            });
            if (!response.ok) {
                throw new Error('Failed to fetch cache data');
            }
            const data = await response.json();
            setCacheData(data);
            setError(null);
            setCurrentPage(1); // Reset to first page on refresh
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCache();
    }, []);

    const handleClearCache = async () => {
        if (window.confirm("Are you sure you want to clear the cache? This action cannot be undone.")) {
            try {
                await adminApi.clearCache();
                await fetchCache();
            } catch (err) {
                alert("Failed to clear cache: " + err.message);
            }
        }
    };

    const toggleExpand = (key) => {
        const newExpanded = new Set(expandedKeys);
        if (newExpanded.has(key)) {
            newExpanded.delete(key);
        } else {
            newExpanded.add(key);
        }
        setExpandedKeys(newExpanded);
    };

    if (loading && cacheData.length === 0) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <RefreshCw className="animate-spin text-primary mx-auto mb-4" size={48} />
                    <p className="text-gray-400">Loading cache data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="glass-card p-8 rounded-2xl text-center max-w-md">
                    <AlertCircle className="text-red-400 mx-auto mb-4" size={48} />
                    <h3 className="text-xl font-semibold text-white mb-2">Error Loading Cache</h3>
                    <p className="text-red-400">{error}</p>
                    <button
                        onClick={fetchCache}
                        className="mt-4 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl transition-all"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full overflow-auto p-8">
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-heading font-bold text-white mb-2">Cache Management</h1>
                        <p className="text-gray-400">View and manage cached responses</p>
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={fetchCache}
                            disabled={loading}
                            className="flex items-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 text-white rounded-xl transition-all duration-300 border border-white/10 hover:border-white/20 disabled:opacity-50"
                        >
                            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                            <span className="font-medium">Refresh</span>
                        </button>
                        <button
                            onClick={handleClearCache}
                            className="flex items-center gap-2 px-4 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl transition-all duration-300 border border-red-500/20 hover:border-red-500/40"
                        >
                            <Trash2 size={18} />
                            <span className="font-medium">Clear Cache</span>
                        </button>
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="glass-card p-6 rounded-2xl">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-3 bg-primary/10 rounded-xl text-primary">
                                <Database size={20} />
                            </div>
                            <span className="text-gray-400 text-sm font-medium">Total Items</span>
                        </div>
                        <h3 className="text-3xl font-bold text-white">{cacheData.length}</h3>
                    </div>
                    <div className="glass-card p-6 rounded-2xl">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400">
                                <Eye size={20} />
                            </div>
                            <span className="text-gray-400 text-sm font-medium">Total Access</span>
                        </div>
                        <h3 className="text-3xl font-bold text-white">
                            {cacheData.reduce((sum, item) => sum + item.access_count, 0)}
                        </h3>
                    </div>
                    <div className="glass-card p-6 rounded-2xl">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-3 bg-accent/10 rounded-xl text-accent">
                                <Hash size={20} />
                            </div>
                            <span className="text-gray-400 text-sm font-medium">Avg Access</span>
                        </div>
                        <h3 className="text-3xl font-bold text-white">
                            {cacheData.length > 0
                                ? (cacheData.reduce((sum, item) => sum + item.access_count, 0) / cacheData.length).toFixed(1)
                                : '0'}
                        </h3>
                    </div>
                </div>

                {/* Cache Items */}
                <div className="space-y-3">
                    {cacheData.length === 0 ? (
                        <div className="glass-card p-12 rounded-2xl text-center">
                            <Database className="text-gray-600 mx-auto mb-4" size={64} />
                            <h3 className="text-xl font-semibold text-gray-400 mb-2">Cache is Empty</h3>
                            <p className="text-gray-500">No cached responses yet. Start chatting to populate the cache.</p>
                        </div>
                    ) : (
                        cacheData.map((item) => {
                            const isExpanded = expandedKeys.has(item.key);
                            return (
                                <div key={item.key} className="glass-card rounded-2xl overflow-hidden group hover:border-primary/30 transition-all duration-300">
                                    <div className="p-6">
                                        <div className="flex items-start justify-between gap-4 mb-4">
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <Hash size={16} className="text-primary shrink-0" />
                                                    <code className="text-sm font-mono text-gray-300 truncate">
                                                        {item.key}
                                                    </code>
                                                </div>
                                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                                    <div className="flex items-center gap-1">
                                                        <Clock size={14} />
                                                        <span>{new Date(item.store_time * 1000).toLocaleString()}</span>
                                                    </div>
                                                    <div className="flex items-center gap-1">
                                                        <Eye size={14} />
                                                        <span>{item.access_count} access{item.access_count !== 1 ? 'es' : ''}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => toggleExpand(item.key)}
                                                className="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white rounded-lg transition-all text-sm font-medium shrink-0"
                                            >
                                                {isExpanded ? 'Collapse' : 'Expand'}
                                            </button>
                                        </div>

                                        <div className={`bg-black/20 rounded-xl p-4 border border-white/5 transition-all duration-300 ${isExpanded ? 'max-h-96 overflow-y-auto' : 'max-h-24 overflow-hidden'}`}>
                                            <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
                                                {item.value}
                                            </pre>
                                        </div>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </div>

            {/* Pagination controls */}
            {totalPages > 1 && (
                <div className="mt-4 flex justify-center items-center gap-4">
                    <button
                        onClick={goToPrevPage}
                        disabled={currentPage === 1}
                        className={`p-2 rounded-lg transition-colors flex items-center gap-2 ${currentPage === 1
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200 shadow-sm'
                            }`}
                    >
                        <ChevronLeft size={20} />
                        <span className="text-sm font-medium">Previous</span>
                    </button>

                    <span className="text-sm font-medium text-gray-600 bg-gray-50 px-3 py-1 rounded-md border border-gray-200">
                        Page {currentPage} of {totalPages}
                    </span>

                    <button
                        onClick={goToNextPage}
                        disabled={currentPage === totalPages}
                        className={`p-2 rounded-lg transition-colors flex items-center gap-2 ${currentPage === totalPages
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200 shadow-sm'
                            }`}
                    >
                        <span className="text-sm font-medium">Next</span>
                        <ChevronRight size={20} />
                    </button>
                </div>
            )}
        </div>
    );
};

export default CacheViewer;
