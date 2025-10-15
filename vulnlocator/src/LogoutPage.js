import React, { useEffect } from 'react';
import { Container, Typography, Box, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export default function LogoutPage() {
    const navigate = useNavigate();

    useEffect(() => {
        // Simulate logout action: clear any auth (placeholder)
        const t = setTimeout(() => {
            // In a real app you'd clear tokens and user state here
            navigate('/');
        }, 1200);
        return () => clearTimeout(t);
    }, [navigate]);

    return (
        <Container>
            <Box sx={{ mt: 6, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                <Typography variant="h4">Logging out...</Typography>
                <CircularProgress />
            </Box>
        </Container>
    );
}
