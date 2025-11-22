const API_BASE = 'http://localhost:8000';

export const getSessions = async () => {
    const response = await fetch(`${API_BASE}/sessions`);
    return response.json();
};

export const createSession = async (title = "New Chat") => {
    const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });
    return response.json();
};

export const deleteSession = async (sessionId) => {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE'
    });
    return response.json();
};

export const getSessionMessages = async (sessionId) => {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
    return response.json();
};

export const generateSessionTitle = async (sessionId, userMessage) => {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/title`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_message: userMessage })
    });
    return response.json();
};

export const adminApi = {
    getSystemStats: () => fetch(`${API_BASE}/admin/system-stats`).then(res => res.json().then(data => ({ data }))),
    getCacheStats: () => fetch(`${API_BASE}/admin/cache-stats`).then(res => res.json().then(data => ({ data }))),
    clearCache: () => fetch(`${API_BASE}/admin/clear-cache`, { method: 'POST' }).then(res => res.json())
};
