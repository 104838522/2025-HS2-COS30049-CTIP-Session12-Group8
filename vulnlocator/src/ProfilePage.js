import React from 'react';
import { Container, Typography, Box, Card, CardContent, Avatar } from '@mui/material';

export default function ProfilePage() {
    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Your profile
            </Typography>
            <Box sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
                <Avatar sx={{ width: 80, height: 80 }}>U</Avatar>
                <Card sx={{ flex: 1 }}>
                    <CardContent>
                        <Typography variant="h6">Guest User</Typography>
                        <Typography variant="body2">No account connected.</Typography>
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}
