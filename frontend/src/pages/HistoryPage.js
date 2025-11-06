// HistoryPage.js
// Role: Displays past AI analysis results, supports data sorting, and allows clearing all records.

import React, { useEffect, useState, useMemo } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Button,
  Alert,
  ButtonGroup
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import HistoryConfidenceChart from "../components/HistoryConfidenceChart";
// *two API requests: fetch history and delete history.

export default function HistoryPage() {
  // ======== Authentication Context ========
  // Provides access to logged-in user info and token
  const { user, token } = useAuth();

  // ======== Local States ========
  const [history, setHistory] = useState([]);         // Stores user history data
  const [loading, setLoading] = useState(true);        // Controls loading spinner
  const [message, setMessage] = useState('');         // Success message
  const [error, setError] = useState('');              // Error message
  const [sortType, setSortType] = useState("date");   // Sorting criteria: date , high , low

  // ======== Fetch History Data from API ========(Done)
  // Fetches user specific analysis history 
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

  // ======== Delete All History Records ========(Done)
  // Sends DELETE request to clear user's stored history
  const handleClearHistory = async () => {
    if (!window.confirm("Are you sure you want to clear all analysis history?")) return;

    try {
      const res = await axios.delete("http://127.0.0.1:8000/api/history/delete", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setHistory([]); // Instantly clear local UI
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

  // ======== Sorting Logic ========
  // resorts history data based on selected sortType
  const sortedHistory = useMemo(() => {
    if (!Array.isArray(history)) return [];

    const copy = [...history];
    if (sortType === "high") {
      // Sort descending by confidence
      return copy.sort((a, b) => b.confidence - a.confidence);
    } 
    else if (sortType === "low") {
      // Sort ascending by confidence
      return copy.sort((a, b) => a.confidence - b.confidence);
    } 
    else {
      // Sort by timestamp (default)
      return copy.sort(
        (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
      );
    }
  }, [history, sortType]);

  // ======== Handle Unauthenticated State ========
  if (!user) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography variant="body1">
          Not signed in. Please sign in to view your past analyses.
        </Typography>
      </Container>
    );
  }

  // ======== Render UI ========
  return (
    <Container sx={{ mt: 4 }}>
      {/* Page Title */}
      <Typography variant="h3" component="h1" gutterBottom>
        Past Analyses
      </Typography>

      {/* Success or Error Alerts */}
      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Clear All History Button */}
      <Button
        variant="outlined"
        color="error"
        onClick={handleClearHistory}
        sx={{ mb: 3 }}
        disabled={loading || history.length === 0}
      >
        Clear History
      </Button>

      {/* ======== Confidence Trend Chart Section ======== */}
      <Box sx={{ mb: 3 }}>
        {history.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Confidence Trend
            </Typography>

            {/* Sorting Buttons */}
            <ButtonGroup sx={{ mb: 2 }}>
              <Button
                variant={sortType === "date" ? "contained" : "outlined"}
                onClick={() => setSortType("date")}
              >
                Date
              </Button>
              <Button
                variant={sortType === "high" ? "contained" : "outlined"}
                onClick={() => setSortType("high")}
              >
                High to Low
              </Button>
              <Button
                variant={sortType === "low" ? "contained" : "outlined"}
                onClick={() => setSortType("low")}
              >
                Low to High
              </Button>
            </ButtonGroup>

            {/* Chart Visualization */}
            <HistoryConfidenceChart data={sortedHistory} />
          </Box>
        )}
      </Box>

      {/* ======== Conditional Rendering: Loading, Empty, or Results ======== */}
      {loading ? (
        // Loading Spinner
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : history.length === 0 ? (
        // No history available
        <Typography>
          No past analyses found for {user.name || user.email}.
        </Typography>
      ) : (
        // Display each record in a card
        <Box sx={{ mt: 2 }}>
          {sortedHistory.map((entry, index) => (
            <Card id={`history-${index}`} key={index} sx={{ mb: 2, boxShadow: 3 }}>
              <CardContent>
                {/* Result Title */}
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
                    ? "Potentially vulnerable code detected"
                    : "No vulnerability detected"}
                </Typography>

                {/* Record Details */}
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
