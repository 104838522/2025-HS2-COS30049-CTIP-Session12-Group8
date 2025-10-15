import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, FormControlLabel, Switch, Box } from '@mui/material';

export default function SettingsDialog({ open, onClose, darkMode, onToggleDarkMode }) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Settings</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 1 }}>
          <FormControlLabel
            control={<Switch checked={darkMode} onChange={onToggleDarkMode} />}
            label="Dark mode"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
