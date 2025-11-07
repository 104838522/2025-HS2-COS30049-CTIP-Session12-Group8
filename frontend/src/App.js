import React, { useState, useRef } from "react";
import { Route, Routes, Link, useLocation } from "react-router-dom";
import {
  AppBar, Toolbar, Typography, Container, Button, Box,
  Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton,
  TextField, Snackbar, Alert, Dialog, DialogTitle, DialogContent,
  DialogContentText, DialogActions, CircularProgress, LinearProgress,
  Divider, InputAdornment, Select, MenuItem, FormControl, InputLabel
} from "@mui/material";
import {
  Menu as MenuIcon,
  Info as InfoIcon,
  Add as AddIcon,
  History as HistoryIcon,
  AccountCircle as AccountCircleIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Storage as StorageIcon
} from "@mui/icons-material";
import HistoryPage from "./pages/HistoryPage";
import KnowledgePage from "./pages/KnowledgePage";
import ProfilePage from "./pages/ProfilePage";
import LogoutPage from "./pages/LogoutPage";
import SettingsDialog from "./components/SettingsDialog";
import { useAuth } from "./context/AuthContext";
import DatasetInfoPage from "./pages/DatasetInfoPage";
import axios from "axios";
//Data visualization components
import ScoreBarChart  from "./components/charts/ScoreBarChart";
import ConfidencePieChart from "./components/charts/ConfidencePieChart";


// ===== VulnLocator Logo Text ===== 
function LogoText({ small, size }) {
  const variant = small ? "subtitle2" : size === "large" ? "h5" : "h6";
  const px = small ? 1.5 : size === "large" ? 4 : 2.5;
  const py = small ? 0.5 : size === "large" ? 1.25 : 1;
  return (
    <Box
      sx={{
        bgcolor: "#d19d00",
        color: "#2b2b2b",
        px,
        py,
        borderRadius: 1,
        display: "inline-block",
        fontFamily: "Georgia, serif",
        textAlign: "center",
        minWidth: small ? 0 : 160,
      }}
    >
      <Typography
        variant={variant}
        sx={{
          fontWeight: 700,
          fontFamily: "Georgia, serif",
          letterSpacing: 0.5,
          color: "#2b2b2b",
          lineHeight: 1.1,
        }}
      >
        VulnLocator
      </Typography>
    </Box>
  );
}

// ===== About Page =====
function About() {
  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h2" component="h1" gutterBottom>
        About Us
      </Typography>
      <Typography variant="h5" component="h2" gutterBottom>
        This project detects vulnerabilities in C/C++ code using AI-based static analysis.
      </Typography>
    </Container>
  );
}

// ===== Main App Component =====
function App() {
  const { notify } = useAuth();
  const fileInputRef = useRef(null);
  const [chatInput, setChatInput] = useState("");
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [darkSnackbarOpen, setDarkSnackbarOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [languageWarningOpen, setLanguageWarningOpen] = useState(false);
  const [pendingSubmission, setPendingSubmission] = useState(null);

  const formatConfidence = (value) => {
    if (typeof value === "number" && !Number.isNaN(value)) {
      return `${(value * 100).toFixed(1)}%`;
    }
    return "N/A";
  };

  // ===== Drawer Toggle =====
  const toggleDrawer = (open) => (event) => {
    if (event.type === "keydown" && (event.key === "Tab" || event.key === "Shift")) return;
    setDrawerOpen(open);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    setDarkSnackbarOpen(true);
  };

  // ===== Simple C/C++ detector =====
  function isLikelyCOrCpp(code) {
    const cKeywords = /\b(int|char|float|double|void|struct|typedef|#include|#define|printf|scanf|main|return|NULL|malloc|free|if|else|for|while|do|switch|case|break|continue|enum|union|const|static|unsigned|signed|short|long|volatile|extern|register|goto|inline|namespace|class|public|private|protected|template|new|delete|cout|cin|std::|using namespace)\b/;
    let score = 0;
    if (/#include\s+[<"]/i.test(code)) score++;
    if (/int\s+main\s*\(/.test(code)) score++;
    if (cKeywords.test(code)) score++;
    if (/;\s*$/m.test(code)) score++;
    if (/\{[\s\S]*\}/.test(code)) score++;
    return score >= 2;
  }

  // ======================== FastAPI Request ===================
  const [selectedModel, setSelectedModel] = useState("knn");

  const handleChatSubmit = async (content, force = false) => {
    const payload = typeof content === "string" ? content : chatInput;
    if (!payload || payload.trim() === "") {
      notify && notify("No content to analyse", "warning");
      return;
    }

    if (!force && !isLikelyCOrCpp(payload)) {
      setPendingSubmission(payload);
      setLanguageWarningOpen(true);
      return;
    }

    setLoading(true);
    notify && notify("Analysis started", "info");

    try {
      const token = localStorage.getItem("vulnlocator_token");
      const formData = new FormData();
      formData.append("code", payload);
      formData.append("model", selectedModel);

      const res = await axios.post("http://localhost:8000/api/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          "Authorization": `Bearer ${token}`,
        },
      });

      const data = res.data || {};
      const confidenceValue =
        typeof data.confidence === "number" && !Number.isNaN(data.confidence)
          ? data.confidence
          : null;
      setAnalysisResult({
        code: payload,
        result: data.result ?? "Unknown",
        confidence: confidenceValue,
        time: data.processing_time_sec ?? null,
        timestamp: data.timestamp ?? "",
        highlights: data.highlights ?? [],   //  highlights
      });

      notify && notify("Analysis complete", "success");
      setChatInput("");
    } catch (err) {
      console.error("[Analysis Error]", err);
      if (axios.isAxiosError(err)) {
        notify && notify(err.response?.data?.detail || "Server error", "error");
      } else notify && notify("Unknown error during analysis", "error");
    } finally {
      setLoading(false);
    }
  };

  // ===== Drawer Content =====
  const drawerContent = (
    <Box
      sx={{
        width: 250,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: darkMode ? "#121212" : "background.paper",
        color: darkMode ? "#f5f5f5" : "text.primary",
      }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      <List>
        {[
          { text: "Detect a vulnerability", icon: <MenuIcon />, link: "/" },
          { text: "Past analyses", icon: <HistoryIcon />, link: "/history" },
          { text: "Knowledge base", icon: <InfoIcon />, link: "/knowledge" },
          { text: "Dataset info", icon: <StorageIcon />, link: "/dataset" },
        ].map((item) => {
          const selected = location.pathname === item.link;
          return (
            <ListItem
              button
              key={item.text}
              component={Link}
              to={item.link}
              selected={selected}
              sx={{
                bgcolor: selected
                  ? (darkMode ? "#333333" : "rgba(0,0,0,0.08)")
                  : "transparent",
                "&:hover": {
                  bgcolor: darkMode ? "#2a2a2a" : "rgba(0,0,0,0.04)",
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: darkMode
                    ? (selected ? "#ffd700" : "#e0e0e0")
                    : (selected ? "primary.main" : "inherit"),
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  sx: {
                    fontWeight: selected ? 600 : 400,
                    color: darkMode
                      ? (selected ? "#ffd700" : "#ffffff")
                      : (selected ? "primary.main" : "text.primary"),
                  },
                }}
              />
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ borderColor: darkMode ? "#444" : "divider" }} />

      <Box sx={{ flexGrow: 1 }} />

      <List>
        {[
          { text: "Your profile", icon: <AccountCircleIcon />, link: "/profile" },
          { text: "Settings", icon: <SettingsIcon />, action: () => setSettingsOpen(true) },
          { text: "Log out", icon: <LogoutIcon />, link: "/logout" },
        ].map((item) => {
          const selected = location.pathname === item.link;
          return (
            <ListItem
              button
              key={item.text}
              component={item.link ? Link : "button"}
              to={item.link}
              onClick={item.action}
              selected={selected}
              sx={{
                bgcolor: selected
                  ? (darkMode ? "#333333" : "rgba(0,0,0,0.08)")
                  : "transparent",
                "&:hover": {
                  bgcolor: darkMode ? "#2a2a2a" : "rgba(0,0,0,0.04)",
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: darkMode
                    ? (selected ? "#ffd700" : "#e0e0e0")
                    : (selected ? "primary.main" : "inherit"),
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  sx: {
                    fontWeight: selected ? 600 : 400,
                    color: darkMode
                      ? (selected ? "#ffd700" : "#ffffff")
                      : (selected ? "primary.main" : "text.primary"),
                  },
                }}
              />
            </ListItem>
          );
        })}
      </List>
    </Box>
  );

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        bgcolor: darkMode ? "grey.900" : "background.default",
        color: darkMode ? "common.white" : "common.black",
      }}
    >
      <AppBar position="static" color="primary">
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={toggleDrawer(true)}>
            <MenuIcon />
          </IconButton>
          <Box sx={{ flex: 1, display: "flex", justifyContent: "center" }}>
            <LogoText size="large" />
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
        {drawerContent}
      </Drawer>

      <SettingsDialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        darkMode={darkMode}
        onToggleDarkMode={handleDarkModeToggle}
      />

      {/* ===== Main Page ===== */}
      <Routes>
        <Route
          path="/"
          element={
            <Container
              component="main"
              sx={{
                mt: 2,
                mb: 2,
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "flex-start",
                maxWidth: "lg",
              }}
            >
              <Box
                sx={{
                  width: "100%",
                  flex: 1,
                  bgcolor: darkMode ? "grey.800" : "grey.100",
                  borderRadius: 3,
                  boxShadow: 3,
                  p: 2,
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {loading && <LinearProgress color="secondary" sx={{ mb: 1 }} />}

                <Box sx={{ flex: 1, overflowY: "auto", px: 1 }}>

                  {/* ===== Analysis Result Area =====*/}
                {analysisResult ? (
                  <Box
                    sx={{
                      mt: 3,
                      display: "flex",
                      flexDirection: "row",
                      gap: 3,
                      alignItems: "flex-start",
                    }}
                  >
                    {/* ===== Left: Line-by-line result ===== */}
                    <Box sx={{ flex: 1 }}>
                      <Typography
                        variant="h6"
                        sx={{
                          color:
                            analysisResult.result === "Vulnerable"
                              ? "error.main"
                              : "success.main",
                          fontWeight: 700,
                          mb: 1,
                        }}
                      >
                        {analysisResult.result === "Vulnerable"
                          ? "Vulnerable: Potentially vulnerable code detected!"
                          : "Safe: No vulnerability detected!"}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>{/* ===== hereeeeeeeeeeeeeeeeeeeeeeeeeee ===== */}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        Processing time: {analysisResult.time}s
                      </Typography>

                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          Potentially vulnerable lines:
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                        *Score = the change in the model’s vulnerability probability when that line is removed (Δ probability).
                      </Typography>
                        {analysisResult.highlights && analysisResult.highlights.length > 0 ? (
                          <Box
                            component="ul"
                            sx={{
                              listStyle: "none",
                              pl: 0,
                              mt: 1,
                              fontFamily: "monospace",
                              fontSize: "0.9rem",
                              maxHeight: "400px",
                              overflowY: "auto",
                            }}
                          >
                            {analysisResult.highlights.map((h, i) => (
                              <li
                                key={i}
                                style={{
                                  backgroundColor:
                                    h.score > 0.1
                                      ? "rgba(255, 0, 0, 0.1)"
                                      : "rgba(255, 255, 0, 0.1)",
                                  marginBottom: "6px",
                                  padding: "6px",
                                  borderRadius: "4px",
                                }}
                              >
                                <strong>Line {h.line}</strong> — score {h.score.toFixed(3)}
                                <br />
                                <code>{h.snippet}</code>
                              </li>
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            The model flagged the snippet overall but couldn’t isolate specific
                            lines with enough confidence.
                          </Typography>
                        )}
                      </Box>
                    </Box>

                    {/* ===== Right: Chart Component ===== */}
                    {/* ==Chart 1== */}
                    <Box sx={{ flex: 1, minHeight: 350 }}>
                      <ScoreBarChart data={analysisResult.highlights} />
                    </Box>
                    {/* ==Chart 2== */}
                    <Box sx={{ flex: 1, minHeight: 350 }}>
                      <ConfidencePieChart confidence={analysisResult.confidence} result={analysisResult.result}/>
                    </Box>
                    {/* ==Chart 3== */}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Submit a code snippet or upload a file to see analysis results here.
                  </Typography>
                )}
                </Box>

                {/* ===== Input Area ===== */}
                <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 1 }}>
                  <FormControl sx={{ minWidth: 180 }}>
                    <InputLabel>Model</InputLabel>
                    <Select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      label="Model"
                      sx={{
                        '& .MuiSelect-select': {
                          color: darkMode ? '#fff' : 'inherit',
                        },
                      }}
                      MenuProps={{
                        PaperProps: {
                          sx: {
                            '& .MuiMenuItem-root': {
                              '&:hover': {
                                bgcolor: 'rgba(209, 157, 0, 0.1)',
                              },
                              '&.Mui-selected': {
                                bgcolor: '#d19d00',
                                color: '#2b2b2b',
                                fontWeight: 600,
                                '&:hover': {
                                  bgcolor: '#c18f00',
                                },
                              },
                            },
                          },
                        },
                      }}
                    >
                      <MenuItem value="knn">KNN</MenuItem>
                      <MenuItem value="rf">Random Forest</MenuItem>
                    </Select>
                  </FormControl>
                  <TextField
                    fullWidth
                    placeholder="Paste code or type here..."
                    variant="outlined"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
                        e.preventDefault();
                        handleChatSubmit(chatInput);
                      }
                    }}
                    multiline
                    minRows={4}
                    maxRows={12}
                    sx={{
                      bgcolor: darkMode ? "grey.900" : "white",
                      borderRadius: 2,
                      "& .MuiInputBase-input": {
                        color: darkMode ? "#fff" : "inherit",
                        fontFamily: "monospace",
                      },
                    }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label="attach file"
                            onClick={() => fileInputRef.current?.click()}
                            sx={{
                              bgcolor: "primary.main",
                              color: "#fff",
                              "&:hover": { bgcolor: "primary.dark" },
                              mr: 1,
                            }}
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
                    accept=".txt,.c,.cpp,.py,.java,.js"
                    style={{ display: "none" }}
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      if (file.size > 200 * 1024) {
                        notify && notify("File too large (max 200KB)", "warning");
                        return;
                      }
                      const reader = new FileReader();
                      reader.onload = (ev) => {
                        const text = ev.target.result;
                        setChatInput(String(text));
                        notify && notify(`Loaded ${file.name}`, "success");
                        handleChatSubmit(String(text));
                      };
                      reader.readAsText(file);
                    }}
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    sx={{ px: 4, py: 1.5, fontWeight: "bold", fontSize: "1.1rem", borderRadius: 2 }}
                    onClick={() => handleChatSubmit(chatInput)}
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={20} sx={{ color: "#fff" }} /> : "Send"}
                  </Button>
                </Box>
              </Box>
            </Container>
          }
        />
        <Route path="/about" element={<About />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/logout" element={<LogoutPage />} />
        <Route path="/dataset" element={<DatasetInfoPage />} />
      </Routes>

      {/* ===== Footer ===== */}
      <Box
        component="footer"
        sx={{
          bgcolor: darkMode ? "grey.800" : "background.paper",
          py: 3,
          mt: "auto",
        }}
      >
        <Container maxWidth="lg" sx={{ display: "flex", justifyContent: "space-between" }}>
          <Box>
            <Button component={Link} to="/about">About</Button>
            <Button onClick={() => setDialogOpen(true)}>Contact</Button>
          </Box>
          <Typography variant="body2" color="text.secondary">
            © Swinburne University {new Date().getFullYear()}
          </Typography>
        </Container>
      </Box>

      {/* ===== Language Warning ===== */}
      <Dialog open={languageWarningOpen} onClose={() => setLanguageWarningOpen(false)}>
        <DialogTitle>Language not recommended</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Our models are trained primarily on C/C++ code. Other languages may not yield accurate results.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLanguageWarningOpen(false)}>Cancel</Button>
          <Button
            onClick={() => {
              setLanguageWarningOpen(false);
              if (pendingSubmission) {
                handleChatSubmit(pendingSubmission, true);
                setPendingSubmission(null);
              }
            }}
          >
            Proceed anyway
          </Button>
        </DialogActions>
      </Dialog>

      {/* ===== Dark Mode Snackbar ===== */}
      <Snackbar open={darkSnackbarOpen} autoHideDuration={4000} onClose={() => setDarkSnackbarOpen(false)}>
        <Alert severity="success">{darkMode ? "Dark mode enabled!" : "Light mode enabled!"}</Alert>
      </Snackbar>

      {/* ===== Contact Dialog ===== */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Contact Us</DialogTitle>
        <DialogContent>
          <DialogContentText>Send us feedback or feature requests.</DialogContentText>
          <TextField label="Name" fullWidth variant="standard" margin="dense" />
          <TextField label="Email" fullWidth variant="standard" margin="dense" />
          <TextField label="Message" multiline rows={4} fullWidth variant="standard" margin="dense" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button>Submit</Button>
        </DialogActions>
      </Dialog>
    </Box >
  );
}

export default App;
