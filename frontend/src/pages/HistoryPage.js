// HistoryPage.js
// Role: Displays past AI analysis results and allows clearing all history records.

import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Button,
  Alert
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

export default function HistoryPage() {
  // Access auth context
  const { user, token } = useAuth();

  // Local state
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Fetch user history (GET)
  useEffect(() => {
    const fetchHistory = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await axios.get("http://127.0.0.1:8000/api/history", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setHistory(res.data.history || []);
      } catch (err) {
        console.error("Error fetching history:", err);
        setError("Failed to load analysis history.");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [token]);

  // Delete all history (DELETE)
  const handleClearHistory = async () => {
    if (!window.confirm("Are you sure you want to clear all analysis history?")) return;

    try {
      const res = await axios.delete("http://127.0.0.1:8000/api/history/delete", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setHistory([]); // Clear UI immediately
      setMessage(res.data.message);
      setError('');
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to clear history.";
      setError(msg);
      setMessage('');
    }
  };

  //  If user not logged in
  if (!user) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography variant="body1">
          Not signed in. Please sign in to view your past analyses.
        </Typography>
      </Container>
    );
  }

  //  UI rendering
  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Past Analyses
      </Typography>

      {/* Feedback messages */}
      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Clear History button */}
      <Button
        variant="outlined"
        color="error"
        onClick={handleClearHistory}
        sx={{ mb: 3 }}
        disabled={loading || history.length === 0}
      >
        Clear History
      </Button>

      {/* Loading spinner */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : history.length === 0 ? (
        <Typography>
          No past analyses found for {user.name || user.email}.
        </Typography>
      ) : (
        <Box sx={{ mt: 2 }}>
          {history.map((entry, index) => (
            <Card key={index} sx={{ mb: 2, boxShadow: 3 }}>
              <CardContent>
                {/* Result title with color */}
                <Typography
                  variant="h6"
                  sx={{
                    color:
                      entry.result === "Vulnerable"
                        ? "error.main"
                        : "success.main",
                    fontWeight: 700,
                    mb: 1,
                  }}
                >
                  {entry.result === "Vulnerable"
                    ? "⚠️ Vulnerable code detected"
                    : "✅ No vulnerability detected"}
                </Typography>

                {/* Details */}
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Confidence: {entry.confidence !== null ? entry.confidence.toFixed(3) : "N/A"}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Processing time: {entry.processing_time_sec} sec
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
                  Timestamp: {entry.timestamp}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Container>
  );
}
