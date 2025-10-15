import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Container, Grid, Card, CardContent, Button, Box,
  Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton, TextField,
  Switch, Snackbar, Alert, Fab, Dialog, DialogTitle, DialogContent, DialogContentText,
  DialogActions, CircularProgress, LinearProgress, Chip, Avatar, Divider
} from '@mui/material';
import {
  Menu as MenuIcon,
  Info as InfoIcon,
  Add as AddIcon,
  History as HistoryIcon,
  AccountCircle as AccountCircleIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';

// About page component
function About() {
  return (
    <Container>
      <Typography variant="h2" component="h1" gutterBottom>
        About Us
      </Typography>
      <Typography variant="h5" component="h2" gutterBottom>
        This is the About page. Here, you can add more information about the project or your team.
      </Typography>
    </Container>
  );
}

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setDrawerOpen(open);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  };

  const handleDialogOpen = () => {
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  const handleSubmit = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      handleDialogClose();
      setSnackbarOpen(true);
    }, 2000);
  };

  const drawerContent = (
    <Box sx={{ width: 250, height: '100%', display: 'flex', flexDirection: 'column' }} role="presentation" onClick={toggleDrawer(false)} onKeyDown={toggleDrawer(false)}>
      <List>
        <ListItem button component={Link} to="/">
          <ListItemIcon><MenuIcon /></ListItemIcon>
          <ListItemText primary="Detect a vulnerability" />
        </ListItem>
        <ListItem button component={Link} to="/history">
          <ListItemIcon><HistoryIcon /></ListItemIcon>
          <ListItemText primary="Past analyses" />
        </ListItem>
        <ListItem button component={Link} to="/knowledge">
          <ListItemIcon><InfoIcon /></ListItemIcon>
          <ListItemText primary="Knowledge base" />
        </ListItem>
      </List>
      <Divider />
      <Box sx={{ flexGrow: 1 }} />
      <List>
        <ListItem button component={Link} to="/profile">
          <ListItemIcon><AccountCircleIcon /></ListItemIcon>
          <ListItemText primary="Your profile" />
        </ListItem>
        <ListItem button component={Link} to="/settings">
          <ListItemIcon><SettingsIcon /></ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
        <ListItem button component={Link} to="/logout">
          <ListItemIcon><LogoutIcon /></ListItemIcon>
          <ListItemText primary="Log out" />
        </ListItem>
      </List>
    </Box>
  );


  return (

    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      bgcolor: darkMode ? 'grey.900' : 'background.default',
      color: darkMode ? 'common.white' : 'common.black',
      height: '100vh',
      overflow: 'hidden',
    }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer(true)}>
            <MenuIcon />
          </IconButton>
          <Box sx={{ flexGrow: 1 }} />
          <Button color="inherit" component={Link} to="/about">About</Button>
          <Button color="inherit" onClick={handleDialogOpen}>Contact</Button>
          <Box sx={{ ml: 2, display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ mr: 1 }}>Dark Mode</Typography>
            <Switch
              checked={darkMode}
              onChange={handleDarkModeToggle}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#4a463b', // secondary.main from theme.js
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: '#4a463b',
                },
              }}
            />
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
        {drawerContent}
      </Drawer>

      <Routes>
        <Route path="/" element={
          <Container component="main" sx={{
            mt: 8,
            mb: 2,
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'flex-start',
            minHeight: 0,
            height: '100%',
            maxHeight: '100%',
            overflow: 'hidden',
          }}>
            <Typography variant="h2" component="h1" gutterBottom>
              VulnLocator - Utilising machine learning models to identify software vulnerabilities
            </Typography>
            <Typography variant="h5" component="h2" gutterBottom>
              Begin by entering a code snippet or uploading a file to analyse for potential vulnerabilities.
            </Typography>

            {/* Chatbox UI */}
            <Box sx={{
              width: '100%',
              maxWidth: 1400,
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              bgcolor: darkMode ? 'grey.800' : 'grey.100',
              borderRadius: 3,
              boxShadow: 3,
              mt: 4,
              mb: 4,
              p: 2,
              minHeight: 0,
              height: '100%',
              maxHeight: '100%',
              overflow: 'hidden',
            }}>
              {/* Chat messages area */}
              <Box sx={{
                flex: 1,
                overflowY: 'auto',
                px: 1,
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                minHeight: 0,
              }}>
                {/* Example messages, replace with state if needed */}
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>U</Avatar>
                  <Box sx={{ bgcolor: darkMode ? 'grey.900' : 'white', p: 1.5, borderRadius: 2, boxShadow: 1, maxWidth: '80%' }}>
                    <Typography variant="body1">How do I use VulnLocator?</Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, flexDirection: 'row-reverse' }}>
                  <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>A</Avatar>
                  <Box sx={{ bgcolor: darkMode ? 'grey.800' : 'grey.200', p: 1.5, borderRadius: 2, boxShadow: 1, maxWidth: '80%' }}>
                    <Typography variant="body1">Just paste your code or upload a file, and VulnLocator will analyze it for vulnerabilities!</Typography>
                  </Box>
                </Box>
              </Box>
              {/* Chat input area at the bottom */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Type your message..."
                  variant="outlined"
                  sx={{
                    bgcolor: darkMode ? 'grey.900' : 'white',
                    borderRadius: 2,
                    '& .MuiInputBase-input': {
                      color: darkMode ? '#fff' : 'inherit',
                    },
                    '& .MuiInputBase-input::placeholder': {
                      color: darkMode ? '#bbb' : '#888',
                      opacity: 1,
                    },
                  }}
                  InputProps={{
                    style: {
                      color: darkMode ? '#fff' : undefined,
                    },
                  }}
                />
                <Button variant="contained" color="primary" sx={{ px: 4, py: 1.5, fontWeight: 'bold', fontSize: '1.1rem', borderRadius: 2 }}>
                  Send
                </Button>
              </Box>
            </Box>
          </Container>
        } />
        <Route path="/about" element={<About />} />
      </Routes>

      <Box component="footer" sx={{ bgcolor: darkMode ? 'grey.800' : 'background.paper', py: 3, mt: 'auto' }}>
        <Container maxWidth="lg">
          <Typography variant="body1">

          </Typography>
          <Typography variant="body2" color="text.secondary">
            {'Copyright © Swinburne University '}
            {new Date().getFullYear()}
            {'.'}
          </Typography>
        </Container>
      </Box>


      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          {darkMode ? 'Dark mode enabled!' : 'Light mode enabled!'}
        </Alert>
      </Snackbar>

      {/* ...existing code... */}
      <Dialog open={dialogOpen} onClose={handleDialogClose}>
        <DialogTitle>Contact Us</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Fill out this form to get in touch with us, or request new languages to be added to the training dataset.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Your Name"
            type="text"
            fullWidth
            variant="standard"
          />
          <TextField
            margin="dense"
            id="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="standard"
          />
          <TextField
            margin="dense"
            id="field"
            label="Your message, feedback, or request"
            type="text"
            fullWidth
            multiline
            rows={4}
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App;