import React, { useState } from 'react';
import { Box, Paper, Typography, TextField, Button, Stack, Divider, Snackbar, Alert, CircularProgress } from '@mui/material';
import EmailIcon from '@mui/icons-material/Email';


import { useAuth } from './AuthContext';
import { useTheme } from '@mui/material/styles';

export default function LoginOverlay() {
    const { user, loginWithEmail, notify } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showSignup, setShowSignup] = useState(false);
    // Signup form state
    const [signupName, setSignupName] = useState('');
    const [signupEmail, setSignupEmail] = useState('');
    const [signupPassword, setSignupPassword] = useState('');
    const [signupConfirm, setSignupConfirm] = useState('');
    const [signupError, setSignupError] = useState(null);
    const [signupLoading, setSignupLoading] = useState(false);
    const theme = useTheme();
    const [signupSuccess, setSignupSuccess] = useState(false);

    if (user) return null; // don't render overlay when logged in

    // Basic sanitization
    const sanitize = (str) => String(str).replace(/[<>"'`]/g, '').trim();

    // Email regex (simple)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const submitEmail = async () => {
        setError(null);
        const cleanEmail = sanitize(email);
        const cleanPassword = sanitize(password);
        if (!cleanEmail || !cleanPassword) {
            setError('Email and password are required.');
            return;
        }
        if (!emailRegex.test(cleanEmail)) {
            setError('Please enter a valid email address.');
            return;
        }
        setLoading(true);
        try {
            // Backend authentication logic (replace URL as needed)
            // Example:
            // const res = await fetch('http://localhost:8000/api/auth/login', {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json' },
            //   body: JSON.stringify({ email: cleanEmail, password: cleanPassword }),
            // });
            // if (!res.ok) throw new Error('Login failed');
            // const data = await res.json();
            // await loginWithEmail({ email: cleanEmail, password: cleanPassword, userData: data });
            await loginWithEmail({ email: cleanEmail, password: cleanPassword });
            notify('Signed in successfully', 'success');
        } catch (err) {
            setError(err.message || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    const handleSignup = async () => {
        setSignupError(null);
        // Validation
        const name = sanitize(signupName);
        const email = sanitize(signupEmail);
        const password = signupPassword;
        const confirm = signupConfirm;
        if (!name || !email || !password || !confirm) {
            setSignupError('All fields are required.');
            return;
        }
        if (!emailRegex.test(email)) {
            setSignupError('Please enter a valid email address.');
            return;
        }
        if (password.length < 8) {
            setSignupError('Password must be at least 8 characters.');
            return;
        }
        if (password !== confirm) {
            setSignupError('Passwords do not match.');
            return;
        }
        // Optionally: check for strong password (letters, numbers, special chars)
        if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
            setSignupError('Password must contain letters and numbers.');
            return;
        }
        setSignupLoading(true);
        // Simulate signup (replace with backend call)
        setTimeout(() => {
            setSignupLoading(false);
            setSignupSuccess(true);
            notify('Account created! Please sign in.', 'success');
            setShowSignup(false);
            // Optionally, clear signup fields
            setSignupName(''); setSignupEmail(''); setSignupPassword(''); setSignupConfirm('');
        }, 1200);
    };

    return (
        <>
            <Box sx={{
                position: 'fixed',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'rgba(0,0,0,0.55)',
                zIndex: 1400,
                backdropFilter: 'blur(2px)'
            }}>
                <Paper sx={{ p: 4, width: 520, borderRadius: 3, textAlign: 'center', bgcolor: theme.palette.primary.main }} elevation={8}>
                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                        <Box sx={{ bgcolor: '#d19d00', color: '#2b2b2b', px: 4, py: 1, borderRadius: 1 }}>
                            <Typography variant="h6" sx={{ fontFamily: 'Georgia, serif', fontWeight: 600 }}>VulnLocator</Typography>
                        </Box>
                    </Box>
                    {!showSignup ? (
                        <>
                            <Typography variant="body1" color="text.secondary" gutterBottom sx={{ color: theme.palette.secondary.main }}>
                                Welcome! Please sign in with your email
                            </Typography>

                            <Divider sx={{ my: 2, bgcolor: theme.palette.secondary.main }} />

                            <Stack spacing={2}>
                                <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
                                <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
                                {error && <Typography color="error">{error}</Typography>}
                                <Button
                                    variant="contained"
                                    onClick={submitEmail}
                                    disabled={loading}
                                    startIcon={loading ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : <EmailIcon />}
                                    sx={{ bgcolor: theme.palette.secondary.main }}
                                >
                                    {loading ? 'Signing in...' : 'Sign in with Email'}
                                </Button>
                            </Stack>

                            <Typography variant="caption" display="block" sx={{ mt: 2, color: theme.palette.secondary.main }}>
                                Or <Button variant="text" size="small" sx={{ color: theme.palette.secondary.main, textTransform: 'none', p: 0, minWidth: 0 }} onClick={() => setShowSignup(true)}>create a new account</Button>
                            </Typography>
                        </>
                    ) : (
                        <>
                            <Typography variant="body1" color="text.secondary" gutterBottom sx={{ color: theme.palette.secondary.main }}>
                                Create a new account
                            </Typography>
                            <Divider sx={{ my: 2, bgcolor: theme.palette.secondary.main }} />
                            <Stack spacing={2}>
                                <TextField label="Name" value={signupName} onChange={e => setSignupName(e.target.value)} autoFocus />
                                <TextField label="Email" value={signupEmail} onChange={e => setSignupEmail(e.target.value)} />
                                <TextField label="Password" type="password" value={signupPassword} onChange={e => setSignupPassword(e.target.value)} helperText="At least 8 characters, letters and numbers" />
                                <TextField label="Confirm Password" type="password" value={signupConfirm} onChange={e => setSignupConfirm(e.target.value)} />
                                {signupError && <Typography color="error">{signupError}</Typography>}
                                <Button variant="contained" onClick={handleSignup} disabled={signupLoading} sx={{ bgcolor: theme.palette.secondary.main }}>Sign up</Button>
                            </Stack>
                            <Typography variant="caption" display="block" sx={{ mt: 2, color: theme.palette.secondary.main }}>
                                Already have an account?{' '}
                                <Button variant="text" size="small" sx={{ color: theme.palette.secondary.main, textTransform: 'none', p: 0, minWidth: 0 }} onClick={() => setShowSignup(false)}>Sign in</Button>
                            </Typography>
                        </>
                    )}
                </Paper>
                <Snackbar
                    open={signupSuccess}
                    autoHideDuration={4000}
                    onClose={() => setSignupSuccess(false)}
                    anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
                >
                    <Alert onClose={() => setSignupSuccess(false)} severity="success" sx={{ width: '100%' }}>
                        Account created! Please sign in.
                    </Alert>
                </Snackbar>
            </Box>

            {/* Global auth messages are shown by App via AuthContext.message */}
        </>
    );
}
