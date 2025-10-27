// Moved from src/theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: { main: '#d19d00' },
        secondary: { main: '#4a463b' },
        background: { default: '#f5f5f5' },
        text: { primary: '#333' },
    },
    typography: {
        fontFamily: 'Roboto, Arial, sans-serif',
        h1: { fontSize: '2.5rem', fontWeight: 700 },
        h2: { fontSize: '2rem', fontWeight: 600 },
        body1: { fontSize: '1rem' },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    textTransform: 'none',
                },
            },
        },
    },
});

export default theme;
