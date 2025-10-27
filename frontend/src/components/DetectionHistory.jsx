import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip, IconButton,
  TablePagination, TextField, MenuItem, Alert
} from '@mui/material';
import { Delete, Refresh } from '@mui/icons-material';
import axios from 'axios';

const DetectionHistory = () => {
  const [detections, setDetections] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalCount, setTotalCount] = useState(0);
  const [cameraFilter, setCameraFilter] = useState('all');
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDetections();
  }, [page, rowsPerPage, cameraFilter]);

  const fetchDetections = async () => {
    setLoading(true);
    setError('');
    
    try {
      const params = {
        page: page + 1,
        per_page: rowsPerPage
      };
      
      if (cameraFilter !== 'all') {
        params.camera_id = cameraFilter;
      }

      const response = await axios.get('http://localhost:5000/api/detections', { params });
      
      setDetections(response.data.detections || []);
      setTotalCount(response.data.total || 0);
      
      // Extract unique cameras
      const uniqueCameras = [...new Set(response.data.detections.map(d => d.camera_id))];
      setCameras(uniqueCameras);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to fetch detections');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this detection?')) {
      return;
    }

    try {
      await axios.delete(`http://localhost:5000/api/detections/${id}`);
      fetchDetections();
    } catch (err) {
      setError('Failed to delete detection');
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">
            Detection History
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              select
              label="Camera"
              value={cameraFilter}
              onChange={(e) => setCameraFilter(e.target.value)}
              size="small"
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="all">All Cameras</MenuItem>
              {cameras.map(cam => (
                <MenuItem key={cam} value={cam}>{cam}</MenuItem>
              ))}
            </TextField>

            <IconButton onClick={fetchDetections} color="primary">
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Plate Number</TableCell>
                <TableCell>Camera</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>BBox</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {detections.map((det) => (
                <TableRow key={det.id} hover>
                  <TableCell>{det.id}</TableCell>
                  <TableCell>
                    <Typography variant="body1" fontWeight="bold">
                      {det.plate_number}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={det.camera_id} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${(det.confidence * 100).toFixed(1)}%`}
                      size="small"
                      color={det.confidence > 0.8 ? 'success' : 'warning'}
                    />
                  </TableCell>
                  <TableCell>{formatDate(det.timestamp)}</TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      [{det.bbox.x1}, {det.bbox.y1}, {det.bbox.x2}, {det.bbox.y2}]
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(det.id)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              
              {detections.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary">
                      No detections found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          component="div"
          count={totalCount}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      </CardContent>
    </Card>
  );
};

export default DetectionHistory;
