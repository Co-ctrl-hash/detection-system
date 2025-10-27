import React, { useRef, useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Grid, Paper, Chip, Alert
} from '@mui/material';
import { Videocam, VideocamOff, CameraAlt } from '@mui/icons-material';
import io from 'socket.io-client';

const LiveDetection = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [socket, setSocket] = useState(null);
  const [detections, setDetections] = useState([]);
  const [error, setError] = useState('');
  const [mediaStream, setMediaStream] = useState(null);

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    newSocket.on('connection_response', (data) => {
      console.log('Connected to server:', data);
    });

    newSocket.on('detection_result', (data) => {
      setDetections(prev => [data, ...prev].slice(0, 10)); // Keep last 10 detections
      
      // Draw bounding boxes on canvas
      if (data.detections && data.detections.length > 0) {
        drawDetections(data.detections);
      }
    });

    newSocket.on('error', (data) => {
      setError(data.message);
    });

    return () => {
      newSocket.disconnect();
      stopWebcam();
    };
  }, []);

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setMediaStream(stream);
        setIsStreaming(true);
        setError('');
        
        // Start sending frames
        sendFrames();
      }
    } catch (err) {
      setError('Failed to access webcam: ' + err.message);
    }
  };

  const stopWebcam = () => {
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
      setMediaStream(null);
    }
    setIsStreaming(false);
  };

  const sendFrames = () => {
    const interval = setInterval(() => {
      if (!isStreaming || !videoRef.current || !socket) {
        clearInterval(interval);
        return;
      }

      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0);

      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64data = reader.result.split(',')[1];
            socket.emit('video_frame', {
              frame: base64data,
              camera_id: 'webcam'
            });
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.8);
    }, 200); // Send frame every 200ms (5 FPS)
  };

  const drawDetections = (detectionList) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    if (!canvas || !video) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    detectionList.forEach(det => {
      const [x1, y1, x2, y2] = det.bbox;
      
      // Draw box
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      
      // Draw label
      ctx.fillStyle = '#00ff00';
      ctx.font = '16px Arial';
      ctx.fillText(
        `${det.plate_number} (${(det.confidence * 100).toFixed(1)}%)`,
        x1, y1 - 5
      );
    });
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Live Camera Feed
            </Typography>
            
            <Box sx={{ position: 'relative', bgcolor: 'black', minHeight: 400 }}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: 'auto', display: isStreaming ? 'block' : 'none' }}
              />
              <canvas
                ref={canvasRef}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  pointerEvents: 'none'
                }}
              />
              {!isStreaming && (
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: 400,
                    color: 'white'
                  }}
                >
                  <Typography variant="h6">Camera Off</Typography>
                </Box>
              )}
            </Box>

            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              {!isStreaming ? (
                <Button
                  variant="contained"
                  startIcon={<Videocam />}
                  onClick={startWebcam}
                >
                  Start Camera
                </Button>
              ) : (
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<VideocamOff />}
                  onClick={stopWebcam}
                >
                  Stop Camera
                </Button>
              )}
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Detections
            </Typography>
            
            {detections.length === 0 ? (
              <Typography color="text.secondary" sx={{ mt: 2 }}>
                No detections yet. Start the camera to begin detection.
              </Typography>
            ) : (
              <Box sx={{ mt: 2 }}>
                {detections.map((det, idx) => (
                  <Paper
                    key={idx}
                    elevation={1}
                    sx={{ p: 2, mb: 2, bgcolor: '#f5f5f5' }}
                  >
                    <Typography variant="subtitle1" fontWeight="bold">
                      {det.detections[0]?.plate_number || 'Unknown'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Confidence: {(det.detections[0]?.confidence * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(det.timestamp).toLocaleTimeString()}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default LiveDetection;
