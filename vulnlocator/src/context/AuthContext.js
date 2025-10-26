// AuthContext.js (Business Logic Layer)
// Role: Provides authentication context and methods for login, signup, logout, and state update.

import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Read initial user data from LocalStorage
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem("vulnlocator_user");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  // Manage token state separately (used by authenticated API calls)
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem("vulnlocator_token") || null;
    } catch {
      return null;
    }
  });

  const [message, setMessage] = useState(null);

  // Notification helper
  const notify = (text, severity = "info") => {
    setMessage({ text, severity });
    setTimeout(() => setMessage(null), 4000);
  };

  //  Login with email and password
  const loginWithEmail = async (email, password) => {
    if (!email || !password) throw new Error("Email and password required");

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/auth/login", {
        email,
        password,
      });

      const data = res.data; // Expected: { message, token, user }
      if (!data?.token || !data?.user)
        throw new Error("Invalid response from server.");

      const loggedInUser = { ...data.user, token: data.token };
      setUser(loggedInUser);
      setToken(data.token);

      // Save to LocalStorage
      localStorage.setItem("vulnlocator_user", JSON.stringify(loggedInUser));
      localStorage.setItem("vulnlocator_token", data.token);

      notify("Signed in successfully", "success");
      return loggedInUser;
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response) {
          const detail = err.response.data?.detail || "Login failed.";
          notify(`Server error: ${detail}`, "error");
        } else if (err.request) {
          notify("No response from server. Please try again later.", "error");
        } else {
          notify(`Request error: ${err.message}`, "error");
        }
      } else {
        notify(`Login failed: ${err.message}`, "error");
      }
      console.error("[Login Error]", err);
      throw err;
    }
  };

  //  Signup with name, email, and password
  const signupWithEmail = async (name, email, password) => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/api/auth/signup", {
        name,
        email,
        password,
      });

      const data = res.data;
      if (!data?.user?.email) throw new Error("Invalid response from server.");

      notify("Account created successfully", "success");
      return data.user;
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response) {
          const detail = err.response.data?.detail || "Signup failed.";
          notify(`Server error: ${detail}`, "error");
        } else if (err.request) {
          notify("No response from server. Please try again later.", "error");
        } else {
          notify(`Request error: ${err.message}`, "error");
        }
      } else {
        notify(`Signup failed: ${err.message}`, "error");
      }
      console.error("[Signup Error]", err);
      throw err;
    }
  };

  //  Logout and clear user data
  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("vulnlocator_user");
    localStorage.removeItem("vulnlocator_token");
    notify("Logged out", "info");
  };

  //  Restore user and token from LocalStorage on reload
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem("vulnlocator_user");
      const storedToken = localStorage.getItem("vulnlocator_token");
      if (storedUser) setUser(JSON.parse(storedUser));
      if (storedToken) setToken(storedToken);
    } catch (err) {
      console.error("Failed to restore user/token from storage:", err);
    }
  }, []);

  //  Save user updates to LocalStorage whenever user state changes
  useEffect(() => {
    if (user) {
      localStorage.setItem("vulnlocator_user", JSON.stringify(user));
    }
  }, [user]);

  //  Provide context values
  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        setUser,       //  added for immediate profile updates
        setToken,      //  allows refreshing token later
        loginWithEmail,
        signupWithEmail,
        logout,
        message,
        notify,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export default AuthContext;
