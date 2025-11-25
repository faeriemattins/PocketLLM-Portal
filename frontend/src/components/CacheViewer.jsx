import React, { useState, useEffect } from 'react';
import { adminApi } from '../api';
import { Trash2, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';

const CacheViewer = () => {
    const [cacheData, setCacheData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 5;

    const fetchCache = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('pocketllm_token');
            const response = await fetch('http://127.0.0.1:8001/admin/cache-items', {
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

    // Pagination logic
    const totalPages = Math.ceil(cacheData.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentItems = cacheData.slice(startIndex, endIndex);

    const goToNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(currentPage + 1);
        }
    };

    const goToPrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
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

            {/* Pagination info */}
            <div className="mb-4 text-sm text-gray-600">
                Showing {startIndex + 1}-{Math.min(endIndex, cacheData.length)} of {cacheData.length} items
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
                        {currentItems.length === 0 ? (
                            <tr>
                                <td colSpan="4" className="text-center py-4 text-gray-500">Cache is empty</td>
                            </tr>
                        ) : (
                            currentItems.map((item) => (
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
