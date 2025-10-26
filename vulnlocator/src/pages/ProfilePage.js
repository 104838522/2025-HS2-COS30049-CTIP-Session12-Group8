// ProfilePage.js
// Role: Displays user profile information and allows updating name or password.

import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Avatar,
  TextField,
  Button,
  Alert,
} from '@mui/material';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  // Access authentication context (user, token, and updater)
  const { user, token, setUser } = useAuth();

  // Local state for form inputs and messages
  const [name, setName] = useState(user?.name || '');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Display first letters as avatar initials
  const initials =
    user && user.name
      ? user.name
          .split(' ')
          .map((n) => n[0])
          .slice(0, 2)
          .join('')
      : 'U';

  // Function: Handle profile update request
  const handleUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    try {
      const payload = {
        name: name.trim() || null,
        password: password.trim() || null,
      };

      const res = await axios.put('http://127.0.0.1:8000/api/user/update', payload, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      // Display success message
      setMessage(res.data.message);
      setPassword(''); // Clear password input

      //  Update local AuthContext immediately (so UI updates instantly)
      if (res.data.updated_user) {
        setUser((prev) => ({
          ...prev,
          name: res.data.updated_user.name,
          email: res.data.updated_user.email,
        }));
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Failed to update profile.';
      setError(msg);
    }
  };

  // UI Rendering
  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Your Profile
      </Typography>

      <Box sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <Avatar sx={{ width: 80, height: 80 }}>{initials}</Avatar>

        <Card sx={{ flex: 1 }}>
          <CardContent>
            {user ? (
              <>
                {/* Display user info */}
                <Typography variant="h6">{user.name || 'User'}</Typography>
                {user.email && (
                  <Typography variant="body2" color="text.secondary">
                    {user.email}
                  </Typography>
                )}

                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  You can update your name or password below.
                </Typography>

                {/* Update form */}
                <Box
                  component="form"
                  onSubmit={handleUpdate}
                  sx={{
                    mt: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                  }}
                >
                  <TextField
                    label="New Name"
                    variant="outlined"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    fullWidth
                  />
                  <TextField
                    label="New Password"
                    type="password"
                    variant="outlined"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    fullWidth
                  />
                  <Button type="submit" variant="contained" color="primary">
                    Update Profile
                  </Button>
                </Box>

                {/* Feedback messages */}
                {message && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    {message}
                  </Alert>
                )}
                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}
              </>
            ) : (
              <>
                {/* Fallback for guest users */}
                <Typography variant="h6">Guest User</Typography>
                <Typography variant="body2">No account connected.</Typography>
              </>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}
