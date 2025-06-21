import React, { useState } from 'react';
import { CssBaseline, ThemeProvider, createTheme, Box, AppBar, Toolbar, Typography, Container, IconButton, Switch, Button, Grid, Card, CardContent, Alert, Paper } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import EmailIcon from '@mui/icons-material/Email';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import InfoIcon from '@mui/icons-material/Info';
import AnalysisTool from './components/AnalysisTool';
import { apiUrl } from './config';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [apiResponse, setApiResponse] = useState(null);
  const [apiError, setApiError] = useState(null);

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: { main: '#1976d2' },
      secondary: { main: '#00bcd4' },
    },
  });

  const handleThemeToggle = () => setDarkMode(!darkMode);

  const scrollToAnalyze = () => {
    const element = document.getElementById('analyze');
    element.scrollIntoView({ behavior: 'smooth' });
  };

  const handleHealth = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setApiResponse({
        endpoint: 'Health Status',
        data: data
      });
      setApiError(null);
    } catch (error) {
      console.error('Health check error:', error);
      setApiError('Error checking health status');
      setApiResponse(null);
    }
  };

  const handleVersion = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/version`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setApiResponse({
        endpoint: 'API Version',
        data: data
      });
      setApiError(null);
    } catch (error) {
      console.error('Version check error:', error);
      setApiError('Error getting version');
      setApiResponse(null);
    }
  };

  const renderApiResponse = () => {
    if (!apiResponse) return null;
    
    const formatValue = (value) => {
      if (typeof value === 'object') {
        return (
          <Box sx={{ pl: 2, borderLeft: '2px solid', borderColor: 'primary.main' }}>
            {Object.entries(value).map(([key, val]) => (
              <Box key={key}>
                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'bold' }}>
                  {key}:
                </Typography>
                <Typography variant="body2">
                  {typeof val === 'object' ? formatValue(val) : val.toString()}
                </Typography>
              </Box>
            ))}
          </Box>
        );
      }
      return value.toString();
    };

    return (
      <Box sx={{ 
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
        maxWidth: '350px'
      }}>
        <Paper 
          elevation={3} 
          sx={{ 
            p: 3, 
            width: '100%',
            bgcolor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2
          }}
        >
          <Typography variant="h6" color="primary" gutterBottom>
            {apiResponse.endpoint} Response
          </Typography>
          <Box sx={{ 
            bgcolor: 'grey.50', 
            p: 2, 
            width: '100%',
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider'
          }}>
            {formatValue(apiResponse.data)}
          </Box>
        </Paper>
      </Box>
    );
  };

  const renderApiError = () => {
    if (!apiError) return null;
    
    return (
      <Box sx={{ 
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
        maxWidth: '350px'
      }}>
        <Alert 
          severity="error" 
          sx={{ 
            width: '100%',
            borderRadius: 2
          }}
        >
          {apiError}
        </Alert>
      </Box>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Karma Fraud Detector
          </Typography>
          <IconButton color="inherit" onClick={handleThemeToggle}>
            {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          <Switch checked={darkMode} onChange={handleThemeToggle} color="default" />
        </Toolbar>
      </AppBar>
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', color: 'text.primary' }}>
        {/* Hero Section */}
        <Box sx={{ py: 8, textAlign: 'center', bgcolor: 'primary.main', color: 'primary.contrastText' }}>
          <Typography variant="h2" fontWeight={700} gutterBottom>Karma Fraud Detector</Typography>
          <Typography variant="h5" gutterBottom>AI-powered detection of suspicious karma activity</Typography>
          <Button 
            variant="contained" 
            color="secondary" 
            size="large" 
            sx={{ mt: 3 }}
            onClick={scrollToAnalyze}
          >
            Try it Now
          </Button>
        </Box>
        {/* About Section */}
        <Container sx={{ py: 6 }} id="about">
          <Typography variant="h4" gutterBottom>About the Project</Typography>
          <Typography variant="body1" paragraph>
            Karma Fraud Detector is a cutting-edge tool designed to identify and flag suspicious karma manipulation on social platforms. Leveraging machine learning and advanced analytics, it helps maintain the integrity of online communities by detecting fraudulent upvotes, comments, and other activities.
          </Typography>
          <Typography variant="body1" paragraph>
            <b>Features:</b> Real-time analysis, user-friendly interface, detailed activity breakdown, and robust fraud scoring.
          </Typography>
        </Container>
        {/* Analysis Tool */}
        <Container sx={{ py: 6 }} id="analyze">
          <AnalysisTool />
        </Container>
        {/* API Documentation Section */}
        <Box sx={{ 
          my: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2
          }}>
          <Typography variant="h4" gutterBottom>
            API Documentation
          </Typography>
          <Box sx={{ 
            display: 'flex',
            justifyContent:'center',
            alignItems: 'center',
            gap: 2,
            width: '100%',
            maxWidth: '1000px'
              }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} md={4}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Health Check
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Check the API health status
                    </Typography>
                    <Button 
                      variant="contained" 
                      onClick={handleHealth}
                      startIcon={<HealthAndSafetyIcon />}
                    >
                      Check Health
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Version Info
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Get the current API version
                    </Typography>
                    <Button 
                      variant="contained" 
                      onClick={handleVersion}
                      startIcon={<InfoIcon />}
                    >
                      Get Version
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
          {renderApiError()}
          {renderApiResponse()}
        </Box>
        {/* Footer */}
        <Box component="footer" sx={{ py: 4, textAlign: 'center', bgcolor: 'grey.900', color: 'grey.100', mt: 8 }}>
          <Typography variant="body2" paragraph>
            Made with ❤️ by Vision Ventures
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Typography variant="body2">
              <a href="mailto:pavan@turtilintern.com" style={{ color: '#fff', textDecoration: 'none' }}>
                <EmailIcon sx={{ verticalAlign: 'middle', mr: 0.5 }} /> Email
              </a>
            </Typography>
            <Typography variant="body2">
              <a href="https://github.com/pavanmahi" target="_blank" rel="noopener noreferrer" style={{ color: '#fff', textDecoration: 'none' }}>
                <GitHubIcon sx={{ verticalAlign: 'middle', mr: 0.5 }} /> GitHub
              </a>
            </Typography>
            <Typography variant="body2">
              <a href="https://www.linkedin.com/in/pavan-bejawada-81b59a23a" target="_blank" rel="noopener noreferrer" style={{ color: '#fff', textDecoration: 'none' }}>
                <LinkedInIcon sx={{ verticalAlign: 'middle', mr: 0.5 }} /> LinkedIn
              </a>
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mt: 2 }}>
            © {new Date().getFullYear()} Vision Ventures. All rights reserved.
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
