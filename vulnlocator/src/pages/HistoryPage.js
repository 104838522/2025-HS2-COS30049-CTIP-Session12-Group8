import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

export default function HistoryPage() {
  const { user, token } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("[DEBUG] Current token:", token);
    const fetchHistory = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await axios.get("http://127.0.0.1:8000/api/history", {
          headers: { Authorization: `Bearer ${token}` },
        });

        // FastAPI response: { email, total_records, history: [ ... ] }
        setHistory(res.data.history || []);
      } catch (err) {
        console.error("Error fetching history:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [token]);

  if (!user) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography variant="body1">
          Not signed in. Please sign in to view your past analyses.
        </Typography>
      </Container>
    );
  }

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Past Analyses
      </Typography>

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

                <Typography variant="body2" sx={{ mb: 1 }}>
                  Confidence: {entry.confidence !== null ? entry.confidence.toFixed(3) : "N/A"}
                </Typography>

                <Typography variant="body2" sx={{ mb: 1 }}>
                  Processing time: {entry.processing_time_sec} sec
                </Typography>

                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: "block" }}
                >
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
