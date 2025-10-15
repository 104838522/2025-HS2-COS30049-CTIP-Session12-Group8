import React from 'react';
import { Container, Typography, Box, Card, CardContent } from '@mui/material';

export default function HistoryPage() {
    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Past analyses
            </Typography>
            <Box sx={{ mt: 2 }}>
                <Card>
                    <CardContent>
                        <Typography variant="body1">No past analyses yet. Your previously analyzed code snippets will appear here.</Typography>
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}
