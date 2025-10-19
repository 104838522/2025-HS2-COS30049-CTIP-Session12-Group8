import React, { useState, useRef } from 'react';
import { Route, Routes, Link, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Container, Button, Box,
  Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton, TextField,
  Switch, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogContentText,
  DialogActions, CircularProgress, LinearProgress, Avatar, Divider
  , InputAdornment
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
import HistoryPage from './HistoryPage';
import KnowledgePage from './KnowledgePage';
import ProfilePage from './ProfilePage';
import LogoutPage from './LogoutPage';
import SettingsDialog from './SettingsDialog';
import { useAuth } from './AuthContext';

function LogoText({ small, size }) {
  // Match LoginOverlay: yellow (#d19d00) bg, dark text, Georgia, bold, rounded, centered
  const variant = small ? 'subtitle2' : (size === 'large' ? 'h5' : 'h6');
  const px = small ? 1.5 : (size === 'large' ? 4 : 2.5);
  const py = small ? 0.5 : (size === 'large' ? 1.25 : 1);
  return (
    <Box sx={{
      bgcolor: '#d19d00',
      color: '#2b2b2b',
      px,
      py,
      borderRadius: 1,
      display: 'inline-block',
      fontFamily: 'Georgia, serif',
      textAlign: 'center',
      minWidth: small ? 0 : 160,
    }}>
      <Typography
        variant={variant}
        sx={{
          fontWeight: 700,
          fontFamily: 'Georgia, serif',
          letterSpacing: 0.5,
          color: '#2b2b2b',
          lineHeight: 1.1,
        }}
      >
        VulnLocator
      </Typography>
    </Box>
  );
}
// About page component
function About() {
  return (
    <Container sx={{ mt: 4 }}>
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
  const { user, message, notify } = useAuth();
  const fileInputRef = useRef(null);
  const [chatInput, setChatInput] = useState('');
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [darkSnackbarOpen, setDarkSnackbarOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setDrawerOpen(open);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    setDarkSnackbarOpen(true);
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') return;
    setDarkSnackbarOpen(false);
  };

  const handleDialogOpen = () => {
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  const handleSettingsOpen = (event) => {
    // prevent drawer closing navigation if called from inside the drawer
    event && event.stopPropagation && event.stopPropagation();
    setSettingsOpen(true);
  };

  const handleSettingsClose = () => {
    setSettingsOpen(false);
  };

  const handleSubmit = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      handleDialogClose();
      setDarkSnackbarOpen(true);
    }, 2000);
  };

  const handleChatSubmit = (content) => {
    const payload = typeof content === 'string' ? content : chatInput;
    if (!payload || payload.trim() === '') {
      notify && notify('No content to analyse', 'warning');
      return;
    }
    setLoading(true);
    notify && notify('Analysis started', 'info');
    // placeholder analysis simulation
    setTimeout(() => {
      setLoading(false);
      notify && notify('Analysis complete (placeholder)', 'success');
      // set a placeholder analysis result with per-line severities
      const lines = payload.split('\n');
      // simple heuristic: mark lines containing 'eval' as Medium, 'select' or 'sql' as High
      const lineResults = lines.map((ln, idx) => {
        const l = ln.toLowerCase();
        if (l.includes('eval(') || l.includes('eval ')) return { line: idx + 1, severity: 'Medium' };
        if (l.includes('select') || l.includes('sql') || l.includes("-- sql") || l.includes('exec(')) return { line: idx + 1, severity: 'High' };
        return { line: idx + 1, severity: 'None' };
      });

      const issues = lineResults.filter(r => r.severity !== 'None').map((r, i) => ({ id: i + 1, desc: `Potential issue on line ${r.line}`, severity: r.severity, line: r.line }));

      setAnalysisResult({ summary: 'Placeholder analysis result', code: payload, lineResults, issues });
      // clear the input after submission so user isn't confused
      setChatInput('');
    }, 1500);
  };

  const drawerContent = (
    <Box sx={{ width: 250, height: '100%', display: 'flex', flexDirection: 'column' }} role="presentation" onClick={toggleDrawer(false)} onKeyDown={toggleDrawer(false)}>
      {/** determine selection and colors per-item */}
      {(() => {
        const path = location?.pathname || '/';
        const getColor = (selected) => {
          if (darkMode) return selected ? 'common.white' : 'rgba(255,255,255,0.7)';
          return selected ? 'text.primary' : 'rgba(0,0,0,0.65)';
        };

        return (
          <List>
            <ListItem button component={Link} to="/" selected={path === '/'}>
              <ListItemIcon sx={{ color: getColor(path === '/') }}><MenuIcon sx={{ color: getColor(path === '/') }} /></ListItemIcon>
              <ListItemText primary="Detect a vulnerability" sx={{ color: getColor(path === '/') }} />
            </ListItem>
            <ListItem button component={Link} to="/history" selected={path === '/history'}>
              <ListItemIcon sx={{ color: getColor(path === '/history') }}><HistoryIcon sx={{ color: getColor(path === '/history') }} /></ListItemIcon>
              <ListItemText primary="Past analyses" sx={{ color: getColor(path === '/history') }} />
            </ListItem>
            <ListItem button component={Link} to="/knowledge" selected={path === '/knowledge'}>
              <ListItemIcon sx={{ color: getColor(path === '/knowledge') }}><InfoIcon sx={{ color: getColor(path === '/knowledge') }} /></ListItemIcon>
              <ListItemText primary="Knowledge base" sx={{ color: getColor(path === '/knowledge') }} />
            </ListItem>
          </List>
        );
      })()}
      <Divider />
      <Box sx={{ flexGrow: 1 }} />
      {(() => {
        const path = location?.pathname || '/';
        const getColor = (selected) => {
          if (darkMode) return selected ? 'common.white' : 'rgba(255,255,255,0.7)';
          return selected ? 'text.primary' : 'rgba(0,0,0,0.65)';
        };

        return (
          <List>
            <ListItem button component={Link} to="/profile" selected={path === '/profile'}>
              <ListItemIcon sx={{ color: getColor(path === '/profile') }}><AccountCircleIcon sx={{ color: getColor(path === '/profile') }} /></ListItemIcon>
              <ListItemText primary="Your profile" sx={{ color: getColor(path === '/profile') }} />
            </ListItem>
            <ListItem button onClick={handleSettingsOpen}>
              <ListItemIcon sx={{ color: getColor(false) }}><SettingsIcon sx={{ color: getColor(false) }} /></ListItemIcon>
              <ListItemText primary="Settings" sx={{ color: getColor(false) }} />
            </ListItem>
            <ListItem button component={Link} to="/logout" selected={path === '/logout'}>
              <ListItemIcon sx={{ color: getColor(path === '/logout') }}><LogoutIcon sx={{ color: getColor(path === '/logout') }} /></ListItemIcon>
              <ListItemText primary="Log out" sx={{ color: getColor(path === '/logout') }} />
            </ListItem>
          </List>
        );
      })()}
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
          <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <LogoText size="large" />
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        PaperProps={{
          sx: {
            bgcolor: darkMode ? 'grey.900' : 'background.paper',
            color: darkMode ? 'common.white' : 'text.primary',
          }
        }}
      >
        {drawerContent}
      </Drawer>

      <SettingsDialog open={settingsOpen} onClose={handleSettingsClose} darkMode={darkMode} onToggleDarkMode={handleDarkModeToggle} />

      <Routes>
        <Route path="/" element={
          <Container component="main" sx={{
            mt: 2,
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
              mt: 0,
              mb: 4,
              p: 2,
              minHeight: 0,
              height: '100%',
              maxHeight: '100%',
              overflow: 'hidden',
            }}>
              {loading && <LinearProgress color="secondary" sx={{ mb: 1 }} />}
              {/* Code viewer area (shows submitted code with per-line highlighting) */}
              <Box sx={{
                flex: 1,
                overflowY: 'auto',
                px: 1,
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                minHeight: 0,
              }}>
                {analysisResult ? (
                  <>
                    <Typography variant="subtitle1">{analysisResult.summary}</Typography>
                    <Box component="pre" sx={{ mt: 1, p: 2, bgcolor: darkMode ? 'grey.900' : '#f7f7f7', borderRadius: 1, overflowX: 'auto', fontFamily: 'monospace', fontSize: '0.95rem' }}>
                      {analysisResult.code.split('\n').map((ln, idx) => {
                        const res = analysisResult.lineResults[idx];
                        const severity = res ? res.severity : 'None';
                        const bg = severity === 'High' ? 'rgba(255,0,0,0.08)' : severity === 'Medium' ? 'rgba(255,200,0,0.06)' : 'transparent';
                        return (
                          <Box key={idx} component="div" sx={{ background: bg, display: 'flex', gap: 2 }}>
                            <Box sx={{ width: 48, textAlign: 'right', pr: 1, color: darkMode ? 'grey.400' : 'grey.600' }}>{idx + 1}</Box>
                            <Box component="span" sx={{ whiteSpace: 'pre-wrap', flex: 1 }}>{ln || '\u00A0'}</Box>
                          </Box>
                        );
                      })}
                    </Box>
                  </>
                ) : (
                  <Typography variant="body2" color="text.secondary">Submit a code snippet or upload a file to see analysis results here.</Typography>
                )}
              </Box>
              {/* Chat input area at the bottom */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Paste code or type here..."
                  variant="outlined"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  multiline
                  minRows={4}
                  maxRows={12}
                  sx={{
                    bgcolor: darkMode ? 'grey.900' : 'white',
                    borderRadius: 2,
                    '& .MuiInputBase-input': {
                      color: darkMode ? '#fff' : 'inherit',
                      fontFamily: 'monospace',
                      whiteSpace: 'pre',
                      overflow: 'auto',
                    },
                    '& .MuiInputBase-input::placeholder': {
                      color: darkMode ? '#bbb' : '#888',
                      opacity: 1,
                    },
                  }}
                  InputProps={{
                    style: { color: darkMode ? '#fff' : undefined },
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="attach file"
                          onClick={() => fileInputRef.current && fileInputRef.current.click()}
                          sx={{ bgcolor: 'primary.main', color: '#fff', '&:hover': { bgcolor: 'primary.dark' }, mr: 1 }}
                          size="small"
                        >
                          <AddIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.js,.py,.java,.c,.cpp,.json,.md,.html,.css"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    const file = e.target.files && e.target.files[0];
                    if (!file) return;
                    if (file.size > 200 * 1024) {
                      notify && notify('File too large (max 200KB)', 'warning');
                      e.target.value = null;
                      return;
                    }
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                      const text = ev.target.result;
                      // set input briefly so user can see it if desired, but we'll clear after submission
                      setChatInput(String(text));
                      notify && notify(`Loaded ${file.name}`, 'success');
                      // auto-submit loaded file content and then clear the input
                      handleChatSubmit(String(text));
                      // ensure the file input value is cleared for future uploads
                      if (e.target) e.target.value = null;
                    };
                    reader.onerror = () => {
                      notify && notify('Failed to read file', 'error');
                      if (e.target) e.target.value = null;
                    };
                    reader.readAsText(file);
                  }}
                />
                <Button variant="contained" color="primary" sx={{ px: 4, py: 1.5, fontWeight: 'bold', fontSize: '1.1rem', borderRadius: 2 }} onClick={() => handleChatSubmit(chatInput)} disabled={loading}>
                  {loading ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : 'Send'}
                </Button>
              </Box>
            </Box>
            {/* results are displayed inline above */}
          </Container>
        } />
        <Route path="/about" element={<About />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/logout" element={<LogoutPage />} />
      </Routes>

      <Box component="footer" sx={{ bgcolor: darkMode ? 'grey.800' : 'background.paper', py: 3, mt: 'auto' }}>
        <Container maxWidth="lg" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
          <Box>
            <Button component={Link} to="/about">About</Button>
            <Button onClick={handleDialogOpen}>Contact</Button>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {'Copyright © Swinburne University '}
            {new Date().getFullYear()}
            {'.'}
          </Typography>
        </Container>
      </Box>


      <Snackbar open={darkSnackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          {darkMode ? 'Dark mode enabled!' : 'Light mode enabled!'}
        </Alert>
      </Snackbar>

      {/* Auth messages from AuthContext */}
      <Snackbar open={Boolean(message)} autoHideDuration={4000} onClose={() => { }} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert severity={message?.severity || 'info'} sx={{ width: '100%' }}>
          {message?.text}
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