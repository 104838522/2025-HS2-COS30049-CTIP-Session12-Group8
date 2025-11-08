// LoginOverlay.js
// Blocking overlay that handles email/password auth (login + signup) before
// letting users interact with the rest of the app.
import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  Divider,
  Snackbar,
  Alert,
  CircularProgress,
} from "@mui/material";
import EmailIcon from "@mui/icons-material/Email";
import { useTheme } from "@mui/material/styles";
import { useAuth } from "../context/AuthContext";

export default function LoginOverlay() {
  const { user, loginWithEmail, signupWithEmail, notify } = useAuth();
  const theme = useTheme();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [signupName, setSignupName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupConfirm, setSignupConfirm] = useState("");
  const [signupError, setSignupError] = useState(null);
  const [signupLoading, setSignupLoading] = useState(false);
  const [signupSuccess, setSignupSuccess] = useState(false);

  // Hide the overlay entirely once the user has an active session.
  if (user) return null;

  const sanitize = (str) => String(str).replace(/[<>"'`]/g, "").trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // login (happy path only, errors handled simply)
  const handleLogin = async () => {
    setError(null);
    const cleanEmail = sanitize(email);
    const cleanPassword = sanitize(password);

    if (!cleanEmail || !cleanPassword) {
      setError("Email and password are required.");
      return;
    }
    if (!emailRegex.test(cleanEmail)) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);
    try {
      await loginWithEmail(cleanEmail, cleanPassword);
    } catch (err) {
      setError("Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  // signup (happy path only, errors handled simply)
  const handleSignup = async () => {
    setSignupError(null);
    const name = sanitize(signupName);
    const email = sanitize(signupEmail);
    const password = signupPassword;
    const confirm = signupConfirm;

    if (!name || !email || !password || !confirm) {
      setSignupError("All fields are required.");
      return;
    }
    if (!emailRegex.test(email)) {
      setSignupError("Please enter a valid email address.");
      return;
    }
    if (password.length < 8) {
      setSignupError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setSignupError("Passwords do not match.");
      return;
    }
    if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      setSignupError("Password must contain both letters and numbers.");
      return;
    }

    setSignupLoading(true);
    try {
      await signupWithEmail(name, email, password);
      setSignupSuccess(true);
      notify("Account created! Please sign in.", "success");
      setShowSignup(false);
      setSignupName("");
      setSignupEmail("");
      setSignupPassword("");
      setSignupConfirm("");
    } catch (err) {
      setSignupError("Signup failed. Please try again.");
    } finally {
      setSignupLoading(false);
    }
  };

  return (
    <>
      <Box
        sx={{
          position: "fixed",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "rgba(0,0,0,0.55)",
          zIndex: 1400,
          backdropFilter: "blur(2px)",
        }}
      >
        <Paper
          sx={{
            p: 4,
            width: 520,
            borderRadius: 3,
            textAlign: "center",
            bgcolor: theme.palette.primary.main,
          }}
          elevation={8}
        >
          <Box sx={{ display: "flex", justifyContent: "center", mb: 2 }}>
            <Box
              sx={{
                bgcolor: "#d19d00",
                color: "#2b2b2b",
                px: 4,
                py: 1,
                borderRadius: 1,
              }}
            >
              <Typography variant="h6" sx={{ fontFamily: "Georgia, serif", fontWeight: 600 }}>
                VulnLocator
              </Typography>
            </Box>
          </Box>

          {!showSignup ? (
            <>
              <Typography sx={{ color: theme.palette.secondary.main }} gutterBottom>
                Welcome! Please sign in with your email
              </Typography>

              <Divider sx={{ my: 2, bgcolor: theme.palette.secondary.main }} />

              <Stack spacing={2}>
                <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                <TextField
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                {error && <Typography color="error">{error}</Typography>}
                <Button
                  variant="contained"
                  onClick={handleLogin}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <EmailIcon />}
                  sx={{ bgcolor: theme.palette.secondary.main }}
                >
                  {loading ? "Signing in..." : "Sign in with Email"}
                </Button>
              </Stack>

              <Typography variant="caption" sx={{ mt: 2, color: theme.palette.secondary.main }}>
                Or{" "}
                <Button
                  variant="text"
                  size="small"
                  sx={{ color: theme.palette.secondary.main }}
                  onClick={() => setShowSignup(true)}
                >
                  create a new account
                </Button>
              </Typography>
            </>
          ) : (
            <>
              <Typography sx={{ color: theme.palette.secondary.main }}>
                Create a new account
              </Typography>
              <Divider sx={{ my: 2, bgcolor: theme.palette.secondary.main }} />
              <Stack spacing={2}>
                <TextField label="Name" value={signupName} onChange={(e) => setSignupName(e.target.value)} />
                <TextField label="Email" value={signupEmail} onChange={(e) => setSignupEmail(e.target.value)} />
                <TextField
                  label="Password"
                  type="password"
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                />
                <TextField
                  label="Confirm Password"
                  type="password"
                  value={signupConfirm}
                  onChange={(e) => setSignupConfirm(e.target.value)}
                />
                {signupError && <Typography color="error">{signupError}</Typography>}
                <Button
                  variant="contained"
                  onClick={handleSignup}
                  disabled={signupLoading}
                  sx={{ bgcolor: theme.palette.secondary.main }}
                >
                  {signupLoading ? "Signing up..." : "Sign up"}
                </Button>
              </Stack>
              <Typography variant="caption" sx={{ mt: 2, color: theme.palette.secondary.main }}>
                Already have an account?{" "}
                <Button
                  variant="text"
                  size="small"
                  sx={{ color: theme.palette.secondary.main }}
                  onClick={() => setShowSignup(false)}
                >
                  Sign in
                </Button>
              </Typography>
            </>
          )}
        </Paper>

        <Snackbar
          open={signupSuccess}
          autoHideDuration={4000}
          onClose={() => setSignupSuccess(false)}
          anchorOrigin={{ vertical: "top", horizontal: "center" }}
        >
          <Alert severity="success">Account created! Please sign in.</Alert>
        </Snackbar>
      </Box>
    </>
  );
}
