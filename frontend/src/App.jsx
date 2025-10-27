import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { 
  AppBar, Toolbar, Typography, Container, Tabs, Tab, Box, CssBaseline,
  ThemeProvider, createTheme
} from '@mui/material';
import DirectionsCar from '@mui/icons-material/DirectionsCar';

import LiveDetection from './components/LiveDetection';
import DetectionHistory from './components/DetectionHistory';
import Statistics from './components/Statistics';
import UploadFile from './components/UploadFile';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <DirectionsCar sx={{ mr: 2 }} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Real-Time Number Plate Detection System
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
              <Tabs value={currentTab} onChange={handleTabChange}>
                <Tab label="Live Detection" component={Link} to="/" />
                <Tab label="Upload File" component={Link} to="/upload" />
                <Tab label="Detection History" component={Link} to="/history" />
                <Tab label="Statistics" component={Link} to="/stats" />
              </Tabs>
            </Box>

            <Routes>
              <Route path="/" element={<LiveDetection />} />
              <Route path="/upload" element={<UploadFile />} />
              <Route path="/history" element={<DetectionHistory />} />
              <Route path="/stats" element={<Statistics />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
