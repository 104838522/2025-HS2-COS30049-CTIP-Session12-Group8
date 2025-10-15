import React from 'react';
import { Container, Typography, Box, Card, CardContent } from '@mui/material';

export default function KnowledgePage() {
    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Knowledge base
            </Typography>
            <Box sx={{ mt: 2 }}>
                <Card>
                    <CardContent>
                        <Typography variant="body1">This is the knowledge base. Add articles or resources here.</Typography>
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}
