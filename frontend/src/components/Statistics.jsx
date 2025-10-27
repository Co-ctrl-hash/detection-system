import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Paper, Alert
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const Statistics = () => {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/stats');
      setStats(response.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to fetch statistics');
    }
  };

  const StatCard = ({ title, value, color = 'primary' }) => (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        textAlign: 'center',
        bgcolor: color === 'primary' ? '#e3f2fd' : color === 'success' ? '#e8f5e9' : '#fff3e0'
      }}
    >
      <Typography variant="h4" fontWeight="bold" color={color}>
        {value || 0}
      </Typography>
      <Typography variant="body1" color="text.secondary">
        {title}
      </Typography>
    </Paper>
  );

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!stats) {
    return <Typography>Loading statistics...</Typography>;
  }

  const cameraData = stats.cameras.map(cam => ({
    camera: cam,
    detections: Math.floor(Math.random() * 100) // Placeholder - replace with actual data
  }));

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        System Statistics
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Detections"
            value={stats.total_detections}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unique Plates"
            value={stats.unique_plates}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Cameras"
            value={stats.cameras.length}
            color="warning"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Last 24 Hours"
            value={stats.recent_24h}
            color="primary"
          />
        </Grid>
      </Grid>

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detections by Camera
          </Typography>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cameraData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="camera" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="detections" fill="#1976d2" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Camera List
          </Typography>
          
          <Grid container spacing={2}>
            {stats.cameras.map((camera, idx) => (
              <Grid item xs={12} sm={6} md={4} key={idx}>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="body1" fontWeight="bold">
                    {camera}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Active
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Statistics;
