// Moved from src/KnowledgePage.js
import React from 'react';
import { Container, Typography, Box, Card, CardContent } from '@mui/material';
import { useAuth } from '../context/AuthContext';

export default function KnowledgePage() {
    const { user } = useAuth();

    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Knowledge base
            </Typography>
            <Box sx={{ mt: 2 }}>
                <Card>
                    <CardContent>
                        {user ? (
                            <Typography variant="body1">Welcome {user.name || user.email}! Explore articles and resources here.</Typography>
                        ) : (
                            <Typography variant="body1">This is the knowledge base. Sign in to see personalised recommendations.</Typography>
                        )}
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}
