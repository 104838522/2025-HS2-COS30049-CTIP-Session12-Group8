import React, { useState } from 'react';
import { Box, Paper, Typography, TextField, Button, Stack, Divider, IconButton } from '@mui/material';
import EmailIcon from '@mui/icons-material/Email';


import { useAuth } from './AuthContext';
import { useTheme } from '@mui/material/styles';

export default function LoginOverlay() {
    const { user, loginWithEmail, notify } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const theme = useTheme();

    if (user) return null; // don't render overlay when logged in

    const submitEmail = async () => {
        setLoading(true);
        setError(null);
        try {
            await loginWithEmail({ email, password });
            notify('Signed in successfully', 'success');
        } catch (err) {
            setError(err.message || 'Login failed');
        } finally {
            setLoading(false);
        }
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
                    <Typography variant="body1" color="text.secondary" gutterBottom sx={{ color: theme.palette.secondary.main }}>
                        Welcome! Please sign in with your email
                    </Typography>

                    <Divider sx={{ my: 2, bgcolor: theme.palette.secondary.main }} />

                    <Stack spacing={2}>
                        <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                        <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                        {error && <Typography color="error">{error}</Typography>}
                        <Button variant="contained" onClick={submitEmail} disabled={loading} startIcon={<EmailIcon />} sx={{ bgcolor: theme.palette.secondary.main }}>Sign in with Email</Button>
                    </Stack>

                    <Typography variant="caption" display="block" sx={{ mt: 2, color: theme.palette.secondary.main }}>Or create a new account</Typography>
                </Paper>
            </Box>

            {/* Global auth messages are shown by App via AuthContext.message */}
        </>
    );
}
