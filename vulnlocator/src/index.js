import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './AuthContext';
import LoginOverlay from './LoginOverlay';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import theme from './theme';
import CssBaseline from '@mui/material/CssBaseline';

//index.js
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <BrowserRouter>
      <AuthProvider>
        <App />
        <LoginOverlay />
      </AuthProvider>
    </BrowserRouter>
  </ThemeProvider>
);