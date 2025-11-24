import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [userRole, setUserRole] = useState(() => {
        return localStorage.getItem('pocketllm_role');
    });

    const login = (role) => {
        setUserRole(role);
        localStorage.setItem('pocketllm_role', role);
    };

    const logout = () => {
        setUserRole(null);
        localStorage.removeItem('pocketllm_role');
    };

    return (
        <AuthContext.Provider value={{ userRole, login, logout, isAuthenticated: !!userRole }}>
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
