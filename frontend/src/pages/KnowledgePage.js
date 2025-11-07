import { useEffect, useState } from 'react';
import { Container, Typography, Box, Card, CardContent } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import LangDistributionChart from '../components/charts/LangDistributionChart';
import TokenFrequencyChart from '../components/charts/TokenFrequencyChart';

// ========================
// Main Page Component
export default function KnowledgePage() {
  const { user } = useAuth(); // Access authenticated user details

  return (
    <Container>
      {/* Page Title */}
      <Typography variant="h3" component="h1" gutterBottom>
        Knowledge Base
      </Typography>

      {/* Welcome Message Section */}
      <Box sx={{ mt: 2 }}>
        <Card>
          <CardContent>
            {user ? (
              <Typography variant="body1">
                Welcome {user.name || user.email}! Explore articles and resources here.
              </Typography>
            ) : (
              <Typography variant="body1">
                This is the knowledge base. Sign in to see personalised recommendations.
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Visualization Section */}
      <Box sx={{ mt: 4 }}>
        <Card>
          <CardContent>
            <Visualization />
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}

// ========================
// Visualization Component
// Fetches and displays analytical charts for vulnerability data.
const Visualization = () => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    // Fetch data for visualizations from backend API
    fetch("http://localhost:8000/api/visualization")
      .then(res => res.json())
      .then(data => setChartData(data))
      .catch(err => console.error("Failed to fetch visualization data:", err));
  }, []);

  // Show loading message until data is fetched
  if (!chartData) return <p>Loading charts...</p>;

  // Render charts when data is ready
  return (
    <div>
      {/* Page Subtitle */}
      <h1 style={{ textAlign: "center" }}>Code Vulnerabilities Dataset Dashboard</h1>

      {/* Pie Chart: Language Distribution */}
      <h2>Language Distribution</h2>
      <LangDistributionChart data={chartData.language_distribution} />

      {/* Grouped Bar Chart: Token Frequency */}
      <h2>Token Frequency: Safe vs Vulnerable</h2>
      <TokenFrequencyChart data={chartData.token_frequency} />
    </div>
  );
};
