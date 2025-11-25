import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser } from '../api';
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [userRole, setUserRole] = useState(() => {
        return localStorage.getItem('pocketllm_role');
    });
    const [token, setToken] = useState(() => {
        return localStorage.getItem('pocketllm_token');
    });

    const login = async (username, password) => {
        try {
            const data = await loginUser(username, password);
            const accessToken = data.access_token;

            // Decode token to get role (assuming role is in token, otherwise we might need another call or just trust the login flow)
            // For now, let's assume the backend puts the role in the token or we infer it.
            // Actually, the backend puts "role" in the token data.
            let role = 'user';
            try {
                const decoded = jwtDecode(accessToken);
                role = decoded.role || 'user';
            } catch (e) {
                console.error("Failed to decode token", e);
            }

            setToken(accessToken);
            setUserRole(role);
            localStorage.setItem('pocketllm_token', accessToken);
            localStorage.setItem('pocketllm_role', role);
            return true;
        } catch (error) {
            console.error("Login failed", error);
            return false;
        }
    };

    const logout = () => {
        setUserRole(null);
        setToken(null);
        localStorage.removeItem('pocketllm_role');
        localStorage.removeItem('pocketllm_token');
    };

    return (
        <AuthContext.Provider value={{ userRole, token, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
