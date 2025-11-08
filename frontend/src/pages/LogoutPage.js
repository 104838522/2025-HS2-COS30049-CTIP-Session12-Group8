// LogoutPage.js - shows a spinner while AuthContext is cleared, then redirects home.
import { useEffect } from 'react';
import { Container, Typography, Box, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LogoutPage() {
    const navigate = useNavigate();
    const { logout } = useAuth();

    useEffect(() => {
        // Gentle spinner delay so the user sees feedback before theyre kicked home.
        const t = setTimeout(() => {
            // Clear user state via AuthContext
            logout && logout();
            navigate('/');
        }, 1200);
        return () => clearTimeout(t);
    }, [navigate, logout]);

    return (
        <Container>
            <Box sx={{ mt: 6, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                <Typography variant="h4">Logging out...</Typography>
                <CircularProgress />
            </Box>
        </Container>
    );
}
