// Moved from src/HistoryPage.js
import React from 'react';
import { Container, Typography, Box, Card, CardContent } from '@mui/material';
import { useAuth } from '../context/AuthContext';

export default function HistoryPage() {
    const { user } = useAuth();

    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Past analyses
            </Typography>
            <Box sx={{ mt: 2 }}>
                <Card>
                    <CardContent>
                        {user ? (
                            <Typography variant="body1">No past analyses yet for {user.name || user.email}. Your previously analyzed code snippets will appear here.</Typography>
                        ) : (
                            <Typography variant="body1">Not signed in. Please sign in to view your past analyses.</Typography>
                        )}
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}
