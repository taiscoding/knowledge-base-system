import React, { useState, useEffect } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

interface VoiceInputDialogProps {
  open: boolean;
  onClose: () => void;
  onTranscription: (text: string) => void;
}

const VoiceInputDialog: React.FC<VoiceInputDialogProps> = ({ open, onClose, onTranscription }) => {
  const [isListening, setIsListening] = useState(false);
  const [processingText, setProcessingText] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable
  } = useSpeechRecognition();

  useEffect(() => {
    if (open) {
      setError(null);
      resetTranscript();
    }
  }, [open, resetTranscript]);

  useEffect(() => {
    setIsListening(listening);
  }, [listening]);

  const handleStartListening = () => {
    setError(null);
    resetTranscript();
    SpeechRecognition.startListening({
      continuous: true,
      language: 'en-US'
    });
  };

  const handleStopListening = () => {
    SpeechRecognition.stopListening();
  };

  const handleSubmit = async () => {
    if (!transcript.trim()) {
      setError('No transcription to submit.');
      return;
    }
    
    setProcessingText(true);
    try {
      // In a real implementation, you might process the text or enhance it here
      setTimeout(() => {
        onTranscription(transcript);
        setProcessingText(false);
      }, 1000); // Simulate processing
    } catch (err) {
      setError('Error processing transcription.');
      setProcessingText(false);
    }
  };

  // Handle browser support issues
  if (!browserSupportsSpeechRecognition) {
    return (
      <Dialog open={open} onClose={onClose}>
        <DialogTitle>Voice Input Not Available</DialogTitle>
        <DialogContent>
          <Alert severity="error">
            Your browser does not support speech recognition.
            Please try using a modern browser like Chrome.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  // Handle microphone permission issues
  if (!isMicrophoneAvailable) {
    return (
      <Dialog open={open} onClose={onClose}>
        <DialogTitle>Microphone Access Required</DialogTitle>
        <DialogContent>
          <Alert severity="warning">
            Microphone access is required for voice input.
            Please allow microphone access in your browser settings.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Voice Input</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Speak clearly to capture your stream of consciousness. Click the microphone button to start/stop recording.
        </DialogContentText>
        
        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 3 }}>
          <IconButton
            color={isListening ? "error" : "primary"}
            size="large"
            onClick={isListening ? handleStopListening : handleStartListening}
            sx={{ 
              width: 80, 
              height: 80,
              border: '2px solid',
              borderColor: isListening ? 'error.main' : 'primary.main'
            }}
          >
            {isListening ? <StopIcon fontSize="large" /> : <MicIcon fontSize="large" />}
          </IconButton>
          
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            {isListening ? 'Listening... Click to stop' : 'Click to start recording'}
          </Typography>
        </Box>
        
        {isListening && (
          <LinearProgress variant="indeterminate" sx={{ my: 2 }} />
        )}
        
        <Box sx={{ 
          minHeight: 150, 
          maxHeight: 300, 
          overflowY: 'auto',
          borderRadius: 1,
          p: 2,
          bgcolor: 'grey.50'
        }}>
          <Typography>
            {transcript || "Your transcription will appear here..."}
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => { handleStopListening(); onClose(); }}>
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={!transcript.trim() || processingText}
          startIcon={processingText && <CircularProgress size={16} color="inherit" />}
        >
          {processingText ? 'Processing...' : 'Process Text'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default VoiceInputDialog; 