import React, { createContext, useContext, useState } from 'react';

// Simple AuthContext for prototype purposes
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    // initialize from localStorage if present
    const [user, setUser] = useState(() => {
        try {
            const raw = localStorage.getItem('vulnlocator_user');
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    });
    const [message, setMessage] = useState(null);

    const notify = (text, severity = 'info') => {
        setMessage({ text, severity });
        // clear after a short while; components can also clear when they read it
        setTimeout(() => setMessage(null), 4000);
    };

    // Placeholder login with email/password (no backend yet)
    const loginWithEmail = async ({ email, password }) => {
        // In a real app you'd POST to an auth endpoint. Here we accept any non-empty email.
        if (!email) throw new Error('Email required');
        // return a placeholder user object
        const placeholderUser = { id: 'user-1', name: 'Placeholder User', email };
        setUser(placeholderUser);
        try { localStorage.setItem('vulnlocator_user', JSON.stringify(placeholderUser)); } catch (e) { }
        notify('Signed in successfully', 'success');

        // Example FastAPI call (commented out - replace URL and remove comments to enable):
        // try {
        //   const res = await fetch('http://localhost:8000/api/auth/login', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ email, password }),
        //   });
        //   if (!res.ok) throw new Error('Login failed');
        //   const data = await res.json();
        //   // set auth token, user, etc. from data
        // }

        return placeholderUser;
    };


    const logout = () => {
        setUser(null);
        try { localStorage.removeItem('vulnlocator_user'); } catch (e) { }
    };

    return (
        <AuthContext.Provider value={{ user, loginWithEmail, logout, message, notify }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}

export default AuthContext;
