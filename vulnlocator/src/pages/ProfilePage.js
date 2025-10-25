// Moved from src/ProfilePage.js
import React from 'react';
import { Container, Typography, Box, Card, CardContent, Avatar } from '@mui/material';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
    const { user } = useAuth();

    const initials = user && user.name ? user.name.split(' ').map(n => n[0]).slice(0, 2).join('') : 'G';

    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Your profile
            </Typography>
            <Box sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
                <Avatar sx={{ width: 80, height: 80 }}>{initials}</Avatar>
                <Card sx={{ flex: 1 }}>
                    <CardContent>
                        {user ? (
                            <>
                                <Typography variant="h6">{user.name || 'User'}</Typography>
                                {user.email && <Typography variant="body2">{user.email}</Typography>}
                                {user.provider && <Typography variant="body2">Signed in with: {user.provider}</Typography>}
                            </>
                        ) : (
                            <>
                                <Typography variant="h6">Guest User</Typography>
                                <Typography variant="body2">No account connected.</Typography>
                            </>
                        )}
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}
