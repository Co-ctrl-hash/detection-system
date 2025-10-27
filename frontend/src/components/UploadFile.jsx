import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Alert, LinearProgress,
  List, ListItem, ListItemText, Chip, Grid, Paper
} from '@mui/material';
import { CloudUpload, Image, VideoLibrary } from '@mui/icons-material';
import axios from 'axios';

const UploadFile = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setResults(null);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('camera_id', 'upload');

    try {
      const isVideo = selectedFile.type.startsWith('video/');
      const endpoint = isVideo ? '/api/detect/video' : '/api/detect';
      
      const response = await axios.post(`http://localhost:5000${endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = () => {
    if (!selectedFile) return <CloudUpload />;
    return selectedFile.type.startsWith('video/') ? <VideoLibrary /> : <Image />;
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upload Image or Video
            </Typography>

            <Box sx={{ mt: 3 }}>
              <input
                accept="image/*,video/*"
                style={{ display: 'none' }}
                id="file-upload"
                type="file"
                onChange={handleFileSelect}
              />
              <label htmlFor="file-upload">
                <Button
                  variant="outlined"
                  component="span"
                  startIcon={getFileIcon()}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Choose File
                </Button>
              </label>

              {selectedFile && (
                <Paper elevation={0} sx={{ p: 2, mb: 2, bgcolor: '#f5f5f5' }}>
                  <Typography variant="body2">
                    <strong>File:</strong> {selectedFile.name}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Size:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </Typography>
                  <Typography variant="body2">
                    <strong>Type:</strong> {selectedFile.type}
                  </Typography>
                </Paper>
              )}

              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                fullWidth
                startIcon={<CloudUpload />}
              >
                {uploading ? 'Processing...' : 'Upload and Detect'}
              </Button>

              {uploading && <LinearProgress sx={{ mt: 2 }} />}

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Detection Results
            </Typography>

            {!results ? (
              <Typography color="text.secondary" sx={{ mt: 2 }}>
                Upload a file to see detection results here.
              </Typography>
            ) : (
              <Box sx={{ mt: 2 }}>
                <Paper elevation={0} sx={{ p: 2, mb: 2, bgcolor: '#e3f2fd' }}>
                  <Typography variant="h6" color="primary">
                    {results.count || results.unique_plates || 0} Plate(s) Detected
                  </Typography>
                  {results.total_frames && (
                    <Typography variant="body2" color="text.secondary">
                      Processed {results.processed_frames} of {results.total_frames} frames
                    </Typography>
                  )}
                </Paper>

                <List>
                  {(results.detections || []).map((det, idx) => (
                    <ListItem
                      key={idx}
                      sx={{
                        bgcolor: '#f5f5f5',
                        mb: 1,
                        borderRadius: 1
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="h6">
                              {det.plate_number || det}
                            </Typography>
                            {det.confidence && (
                              <Chip
                                label={`${(det.confidence * 100).toFixed(1)}%`}
                                size="small"
                                color="primary"
                              />
                            )}
                          </Box>
                        }
                        secondary={
                          det.bbox ? `BBox: [${det.bbox.join(', ')}]` : null
                        }
                      />
                    </ListItem>
                  ))}
                </List>

                {results.success && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    Detection completed successfully!
                  </Alert>
                )}
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default UploadFile;
