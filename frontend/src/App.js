// App.js
// Main application shell that renders navigation,
// page routes, and the ML analysis workflow.
import React, { useState, useRef } from "react";
import { Route, Routes, Link, useLocation } from "react-router-dom";
import {
  AppBar, Toolbar, Typography, Container, Card, CardContent, Button, Box,
  Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton,
  TextField, Snackbar, Alert, Dialog, DialogTitle, DialogContent,
  DialogContentText, DialogActions, CircularProgress, LinearProgress,
  Divider, InputAdornment, Select, MenuItem, FormControl, InputLabel,
  Tooltip, Popover
} from "@mui/material";
import {
  Menu as MenuIcon,
  Info as InfoIcon,
  Add as AddIcon,
  History as HistoryIcon,
  AccountCircle as AccountCircleIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Storage as StorageIcon,
  HelpOutline as HelpOutlineIcon
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
import ScoreBarChart from "./components/charts/ScoreBarChart";
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


// Programmatically built SVG showing interconnected nodes feeding into a cracked shield.
function VulnerabilityGlyph() {
  const circuits = [
    "30,40 120,40 150,20",
    "30,80 160,80",
    "30,120 120,120 150,140",
  ];
  const nodes = [
    { cx: 30, cy: 40 },
    { cx: 30, cy: 80 },
    { cx: 30, cy: 120 },
    { cx: 160, cy: 80 },
  ];
  const sparks = [
    { x1: 235, y1: 35, x2: 300, y2: 20 },
    { x1: 240, y1: 125, x2: 300, y2: 150 },
  ];
  const cracks = [
    "M210 55 L195 90 L215 120 L205 150",
    "M235 70 L250 100 L240 136",
  ];

  return (
    <Box sx={{ mt: 3, display: "flex", justifyContent: "center" }}>
      <Box
        component="svg"
        viewBox="0 0 320 160"
        width="100%"
        height="160"
        role="img"
        aria-label="signals attacking a shield with a crack"
        sx={{
          maxWidth: 420,
          borderRadius: 3,
          boxShadow: 4,
          background: "radial-gradient(circle at 20% 20%, #1f1f2e, #0b0b12)",
        }}
      >
        <defs>
          <linearGradient id="circuitGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f3c623" />
            <stop offset="100%" stopColor="#ff6f3c" />
          </linearGradient>
          <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2d2f55" />
            <stop offset="100%" stopColor="#131326" />
          </linearGradient>
          <radialGradient id="coreGlow" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor="#ffef9f" stopOpacity="0.9" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>

        <rect width="320" height="160" fill="transparent" rx="16" />
        <circle cx="140" cy="80" r="50" fill="url(#coreGlow)" opacity="0.4" />

        {circuits.map((points, idx) => (
          <polyline
            key={`circuit-${idx}`}
            points={points}
            fill="none"
            stroke="url(#circuitGradient)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity={0.8}
          />
        ))}

        {nodes.map(({ cx, cy }, idx) => (
          <circle
            key={`node-${idx}`}
            cx={cx}
            cy={cy}
            r="6"
            fill="#111"
            stroke="#f3c623"
            strokeWidth="2"
          />
        ))}

        <path
          d="M200 35 L260 60 V110 C260 128 230 150 230 150 C230 150 200 128 200 110 Z"
          fill="url(#shieldGradient)"
          stroke="#4f4f7d"
          strokeWidth="2"
        />

        {cracks.map((d, idx) => (
          <path
            key={`crack-${idx}`}
            d={d}
            fill="none"
            stroke="#f96464"
            strokeDasharray="6 4"
            strokeWidth="3"
            strokeLinecap="round"
          />
        ))}

        {sparks.map(({ x1, y1, x2, y2 }, idx) => (
          <line
            key={`spark-${idx}`}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="#ffcc80"
            strokeWidth="2"
            strokeLinecap="round"
            opacity="0.8"
          />
        ))}

        <text
          x="60"
          y="150"
          fill="#f3f3ff"
          fontSize="12"
          letterSpacing="2"
          opacity="0.5"
        >
          VULNERABILITY DETECTED
        </text>
      </Box>
    </Box>
  );
}

// ===== About Page =====
function About() {
  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h2" component="h1" gutterBottom>
        About Us
      </Typography>
      <Card
        sx={{
          background: "linear-gradient(135deg, rgba(30,30,40,0.95), rgba(8,8,16,0.98))",
          color: "#f5f5ff",
          boxShadow: 6,
        }}
      >
        <CardContent>
          <Typography variant="h5" component="h2" gutterBottom>
            This project detects vulnerabilities in C/C++ code using AI-based static analysis.
          </Typography>
          <Typography variant="body1" sx={{ mt: 2, color: "rgba(255,255,255,0.82)" }}>
            VulnLocator is developed by a team of cybersecurity and machine learning enthusiasts at
            Swinburne University. Our mission is to provide developers with an easy-to-use tool to
            identify potential vulnerabilities in their code, helping to enhance software security
            and reliability.
          </Typography>
          <Typography variant="body1" sx={{ mt: 2, color: "rgba(255,255,255,0.82)" }}>
            Our team consists of 3 students from Swinburne University: Gianni Edwards Hernandez,
            Daehyeon Kim, and Hung Nguyen Phan.
          </Typography>
          <Box sx={{ mt: 2, color: "rgba(255,255,255,0.75)" }}>
            <Typography variant="body1" sx={{ mt: 1 }}>
              For more information, visit our{" "}
              <a
                href="https://github.com/104838522/2025-HS2-COS30049-CTIP-Session12-Group8"
                style={{ color: "#ffd36a" }}
              >
                GitHub repository
              </a>
              .
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              If you have any questions, feedback, or would like to contribute to the project,
              please feel free to contact us.
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Thank you for using VulnLocator!
            </Typography>
          </Box>
        </CardContent>
        <Divider sx={{ borderColor: "rgba(255,255,255,0.15)" }} />
        <Box sx={{ px: 3, pb: 3, pt: 1 }}>
          <Typography variant="caption" sx={{ letterSpacing: 1, color: "rgba(255,255,255,0.7)" }}>
            Signals converging on a cracked shield — a reminder to secure the weakest link.
          </Typography>
          <VulnerabilityGlyph />
        </Box>
      </Card>
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
  const [helpAnchorEl, setHelpAnchorEl] = useState(null);

  // ===== Drawer Toggle =====
  const toggleDrawer = (open) => (event) => {
    if (event.type === "keydown" && (event.key === "Tab" || event.key === "Shift")) return;
    setDrawerOpen(open);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    setDarkSnackbarOpen(true);
  };

  const handleHelpClick = (event) => {
    setHelpAnchorEl((prev) => (prev ? null : event.currentTarget));
  };

  const handleHelpClose = () => setHelpAnchorEl(null);

  const helpPopoverOpen = Boolean(helpAnchorEl);
  const helpPopoverId = helpPopoverOpen ? "analysis-help-popover" : undefined;

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
          <Box sx={{ flex: 1, display: "flex-grow", justifyContent: "center" }}>
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
                  position: "relative",
                }}
              >
                <Tooltip title="How to use VulnLocator">
                  <IconButton
                    size="small"
                    aria-label="How to use VulnLocator"
                    aria-describedby={helpPopoverId}
                    onClick={handleHelpClick}
                    sx={{
                      position: "absolute",
                      top: 8,
                      right: 8,
                      bgcolor: darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.04)",
                      color: darkMode ? "#fff" : "#1f1f1f",
                      "&:hover": {
                        bgcolor: darkMode ? "rgba(255,255,255,0.18)" : "rgba(0,0,0,0.12)",
                      },
                    }}
                  >
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

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
                        <ConfidencePieChart confidence={analysisResult.confidence} result={analysisResult.result} />
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

              <Popover
                id={helpPopoverId}
                open={helpPopoverOpen}
                anchorEl={helpAnchorEl}
                onClose={handleHelpClose}
                anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
                transformOrigin={{ vertical: "top", horizontal: "right" }}
                PaperProps={{
                  sx: {
                    maxWidth: 420,
                    p: 2.25,
                    bgcolor: darkMode ? "grey.900" : "background.paper",
                    color: darkMode ? "grey.100" : "text.primary",
                    borderRadius: 2,
                    boxShadow: 8,
                    border: darkMode
                      ? "1px solid rgba(255,255,255,0.12)"
                      : "1px solid rgba(0,0,0,0.08)",
                  },
                }}
              >
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                  How to use VulnLocator
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  The KNN and Random Forest models behind this page were trained on labeled C/C++ functions,
                  so sticking to compact systems-style snippets keeps inputs close to the dataset distribution
                  and yields the most reliable scores.
                </Typography>
                <Box component="ol" sx={{ pl: 2.75, mb: 1.25 }}>
                  <Typography component="li" variant="body2" sx={{ mb: 0.85 }}>
                    <strong>Pick a model:</strong> KNN mirrors the baseline dataset and reports the highest
                    class probability, while Random Forest outputs a 0–1 risk score and benefits from longer
                    context windows.
                  </Typography>
                  <Typography component="li" variant="body2" sx={{ mb: 0.85 }}>
                    <strong>Prepare code:</strong> Paste C/C++ code or upload a file (≤200 KB). Focus on one
                    function or logical block so the explainer can mask lines and measure the Δ probability
                    accurately.
                  </Typography>
                  <Typography component="li" variant="body2" sx={{ mb: 0.85 }}>
                    <strong>Submit & preprocess:</strong> Hit Send (uploads auto-submit). The backend normalises
                    tokens, strips comments, and vectorises text before inference, so formatting differences will
                    not affect the score.
                  </Typography>
                  <Typography component="li" variant="body2">
                    <strong>Interpret the panels:</strong> The headline label reflects the model verdict, the pie
                    shows confidence/risk, and the bar chart lists the score drop when an indicated line is removed.
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Line-level highlights only appear when the snippet is flagged Vulnerable with ≥35% confidence;
                  otherwise the model cannot isolate trustworthy regions. Signed-in runs are saved automatically to
                  the History page for later review.
                </Typography>
                <Typography variant="caption" color="orange">
                  Treat these predictions as triage guidance—rerun with tighter snippets, compare both models for
                  high-risk files, and always validate manually before relying on the verdict.
                </Typography>
              </Popover>
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
          <Button onClick={() => setDialogOpen(false)}>Submit</Button>
        </DialogActions>
      </Dialog>
    </Box >
  );
}

export default App;
