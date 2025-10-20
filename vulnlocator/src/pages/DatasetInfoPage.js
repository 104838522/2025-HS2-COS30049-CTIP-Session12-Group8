import React, { useState } from 'react';
import { Container, Card, CardContent, Tabs, Tab, Typography, Box } from '@mui/material';

// Placeholder tab labels
const TAB_LABELS = [
    // Change these to your actual tab names
    'Overview', // Tab 0
    'Sources',  // Tab 1
    'Statistics' // Tab 2
];

export default function DatasetInfoPage() {
    const [tab, setTab] = useState(0);

    // Placeholder content for each tab
    const tabContent = [
        // Overview tab content
        <Box key={0}>
            {/* Replace with your dataset overview text */}
            <Typography variant="h5" gutterBottom>Dataset Overview</Typography>
            <Typography variant="body1">
                {/* Placeholder: dataset description */}
                This dataset contains code samples for vulnerability detection. {/* <-- CHANGE THIS */}
            </Typography>
        </Box>,
        // Sources tab content
        <Box key={1}>
            {/* Replace with your dataset sources */}
            <Typography variant="h5" gutterBottom>Data Sources</Typography>
            <Typography variant="body1">
                {/* Placeholder: list of sources */}
                - Source 1 {/* <-- CHANGE THIS */}<br />
                - Source 2 {/* <-- CHANGE THIS */}<br />
                - Source 3 {/* <-- CHANGE THIS */}
            </Typography>
        </Box>,
        // Statistics tab content
        <Box key={2}>
            {/* Replace with your dataset statistics */}
            <Typography variant="h5" gutterBottom>Statistics</Typography>
            <Typography variant="body1">
                {/* Placeholder: dataset stats */}
                Total samples: 1234 {/* <-- CHANGE THIS */}<br />
                Vulnerable: 567 {/* <-- CHANGE THIS */}<br />
                Non-vulnerable: 667 {/* <-- CHANGE THIS */}
            </Typography>
        </Box>
    ];

    return (
        <Container sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
            <Card sx={{ width: '100%', maxWidth: 700, minHeight: 400, overflow: 'auto' }}>
                <Tabs
                    value={tab}
                    onChange={(_, newTab) => setTab(newTab)}
                    indicatorColor="primary"
                    textColor="primary"
                    variant="fullWidth"
                >
                    {TAB_LABELS.map((label, idx) => (
                        <Tab label={label} key={idx} />
                    ))}
                </Tabs>
                <CardContent sx={{ maxHeight: 500, overflowY: 'auto' }}>
                    {tabContent[tab]}
                </CardContent>
            </Card>
        </Container>
    );
}
