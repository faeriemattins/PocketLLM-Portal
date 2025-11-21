import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
});

export const chatApi = {
    // Chat is handled via EventSource for streaming, but we might need other endpoints
};

export const adminApi = {
    getSystemStats: () => api.get('/admin/system-stats'),
    getCacheStats: () => api.get('/admin/cache-stats'),
    clearCache: () => api.post('/admin/clear-cache'),
};
