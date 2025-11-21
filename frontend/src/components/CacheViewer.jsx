import React, { useState, useEffect } from 'react';
import { adminApi } from '../api';
import { Trash2, RefreshCw } from 'lucide-react';

const CacheViewer = () => {
    const [cacheData, setCacheData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCache = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/cache');
            if (!response.ok) {
                throw new Error('Failed to fetch cache data');
            }
            const data = await response.json();
            setCacheData(data);
            setError(null);
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

    if (loading && cacheData.length === 0) return <div className="text-center p-4">Loading cache data...</div>;
    if (error) return <div className="text-red-500 p-4">Error: {error}</div>;

    return (
        <div className="container mx-auto p-4">
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold">Cache Contents</h1>
                <div className="space-x-2">
                    <button
                        onClick={fetchCache}
                        className="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2"
                    >
                        <RefreshCw size={16} /> Refresh
                    </button>
                    <button
                        onClick={handleClearCache}
                        className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 flex items-center gap-2"
                    >
                        <Trash2 size={16} /> Clear Cache
                    </button>
                </div>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 shadow-md rounded-lg">
                    <thead className="bg-gray-100">
                        <tr>
                            <th className="py-2 px-4 border-b text-left font-semibold text-gray-700">Key</th>
                            <th className="py-2 px-4 border-b text-left font-semibold text-gray-700">Value (Truncated)</th>
                            <th className="py-2 px-4 border-b text-left font-semibold text-gray-700">Store Time</th>
                            <th className="py-2 px-4 border-b text-left font-semibold text-gray-700">Access Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cacheData.length === 0 ? (
                            <tr>
                                <td colSpan="4" className="text-center py-4 text-gray-500">Cache is empty</td>
                            </tr>
                        ) : (
                            cacheData.map((item) => (
                                <tr key={item.key} className="hover:bg-gray-50">
                                    <td className="py-2 px-4 border-b font-mono text-sm text-gray-600 truncate max-w-xs" title={item.key}>
                                        {item.key}
                                    </td>
                                    <td className="py-2 px-4 border-b text-sm text-gray-800">
                                        <div className="max-h-20 overflow-y-auto">
                                            {item.value.length > 100 ? (
                                                <details>
                                                    <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                                                        {item.value.substring(0, 100)}...
                                                    </summary>
                                                    <p className="mt-2 whitespace-pre-wrap text-gray-700">{item.value}</p>
                                                </details>
                                            ) : (
                                                item.value
                                            )}
                                        </div>
                                    </td>
                                    <td className="py-2 px-4 border-b text-sm text-gray-600">
                                        {new Date(item.store_time * 1000).toLocaleString()}
                                    </td>
                                    <td className="py-2 px-4 border-b text-sm text-gray-600">
                                        {item.access_count}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default CacheViewer;
