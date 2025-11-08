// index.js
// Entrypoint that bootstraps the React tree, wires up routing, theming,
// and authentication context before rendering <App />.
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import LoginOverlay from './components/LoginOverlay';
import { ThemeProvider } from '@mui/material/styles';
import theme from './utils/theme';
import CssBaseline from '@mui/material/CssBaseline';

//index.js
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ThemeProvider theme={theme}>
    {/* CssBaseline + ThemeProvider give a consistent MUI surface */}
    <CssBaseline />
    <BrowserRouter>
      {/* AuthProvider exposes token/user helpers to everything inside App */}
      <AuthProvider>
        <App />
        <LoginOverlay />
      </AuthProvider>
    </BrowserRouter>
  </ThemeProvider>
);