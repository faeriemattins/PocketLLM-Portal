const API_BASE = 'http://127.0.0.1:8000';

const getHeaders = () => {
    const token = localStorage.getItem('pocketllm_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
};

export const loginUser = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });

    if (!response.ok) {
        throw new Error('Login failed');
    }
    return response.json();
};

export const getSessions = async () => {
    const response = await fetch(`${API_BASE}/sessions`, {
        headers: getHeaders()
    });
    return response.json();
};

export const createSession = async (title = "New Chat") => {
    const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ title })
    });
    return response.json();
};

export const deleteSession = async (sessionId) => {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: getHeaders()
    });
    return response.json();
};

export const getSessionMessages = async (sessionId) => {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
        headers: getHeaders()
    });
    return response.json();
};

export const generateSessionTitle = async (sessionId, userMessage) => {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/title`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ user_message: userMessage })
    });
    return response.json();
};

export const adminApi = {
    getSystemStats: () => fetch(`${API_BASE}/admin/system-stats`, { headers: getHeaders() }).then(res => res.json().then(data => ({ data }))),
    getCacheStats: () => fetch(`${API_BASE}/admin/cache-stats`, { headers: getHeaders() }).then(res => res.json().then(data => ({ data }))),
    clearCache: () => fetch(`${API_BASE}/admin/clear-cache`, { method: 'POST', headers: getHeaders() }).then(res => res.json()),
    getSessionConfig: () => fetch(`${API_BASE}/admin/session-config`, { headers: getHeaders() }).then(res => res.json().then(data => ({ data }))),
    setSessionConfig: (max_prompts) => fetch(`${API_BASE}/admin/session-config`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ max_prompts })
    }).then(res => res.json()),
    getCacheSessionConfig: () => fetch(`${API_BASE}/admin/cache-session-config`, { headers: getHeaders() }).then(res => res.json().then(data => ({ data }))),
    setCacheSessionConfig: (max_cached_sessions) => fetch(`${API_BASE}/admin/cache-session-config`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ max_cached_sessions })
    }).then(res => res.json()),
    getModels: () => fetch(`${API_BASE}/admin/models`, { headers: getHeaders() }).then(res => res.json().then(data => ({ data }))),
    selectModel: (model_filename) => fetch(`${API_BASE}/admin/models/select`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ model_filename })
    }).then(res => res.json())
};
