import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Alert,
  CircularProgress,
  Fade,
  Zoom
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DateTimePicker } from '@mui/x-date-pickers';
import { format, addHours } from 'date-fns';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { apiUrl } from '../config';

const ACTIVITY_TYPES = [
  { value: 'upvote_received', label: 'Upvote Received' },
  { value: 'upvote_sent', label: 'Upvote Sent' },
  { value: 'comment', label: 'Comment' },
  { value: 'post_created', label: 'Post Created' }
];

function AnalysisTool() {
  const [userInfo, setUserInfo] = useState({
    user_id: '',
    account_age_days: ''
  });

  const [activities, setActivities] = useState([]);
  const [currentActivity, setCurrentActivity] = useState({
    type: '',
    content: '',
    from_user: '',
    from_user_age_days: '',
    to_user: '',
    to_user_age_days: '',
    timestamp: new Date(),
    source: 'web'
  });

  const [jsonPreview, setJsonPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const handleUserInfoChange = (e) => {
    setUserInfo({
      ...userInfo,
      [e.target.name]: e.target.value
    });
  };

  const handleActivityChange = (e) => {
    setCurrentActivity({
      ...currentActivity,
      [e.target.name]: e.target.value
    });
  };

  const getActivityFields = (type) => {
    switch (type) {
      case 'upvote_received':
        return ['from_user', 'from_user_age_days'];
      case 'upvote_sent':
        return ['to_user', 'to_user_age_days'];
      case 'comment':
      case 'post_created':
        return ['content'];
      default:
        return [];
    }
  };

  const addActivity = () => {
    const newActivity = {
      activity_id: `act_${activities.length + 1}`,
      type: currentActivity.type,
      timestamp: format(currentActivity.timestamp, "yyyy-MM-dd'T'HH:mm:ss'Z'"),
      source: 'web'
    };

    // Add fields based on activity type
    const fields = getActivityFields(currentActivity.type);
    fields.forEach(field => {
      if (currentActivity[field]) {
        newActivity[field] = currentActivity[field];
      }
    });
    
    setActivities([...activities, newActivity]);
    setCurrentActivity({
      type: '',
      content: '',
      from_user: '',
      from_user_age_days: '',
      to_user: '',
      to_user_age_days: '',
      timestamp: addHours(currentActivity.timestamp, 1),
      source: 'web'
    });
    updateJsonPreview([...activities, newActivity]);
  };

  const removeActivity = (index) => {
    const newActivities = activities.filter((_, i) => i !== index);
    setActivities(newActivities);
    updateJsonPreview(newActivities);
  };

  const updateJsonPreview = (activitiesList) => {
    const preview = {
      user_id: userInfo.user_id,
      karma_log: activitiesList
    };
    setJsonPreview(JSON.stringify(preview, null, 2));
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          setUserInfo({ user_id: data.user_id });
          setActivities(data.karma_log);
          setJsonPreview(JSON.stringify(data, null, 2));
        } catch (err) {
          setError('Invalid JSON file');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userInfo.user_id,
          karma_log: activities
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getChartData = (result) => {
    if (!result) return [];
    
    // Count activities by type
    const activityCounts = activities.reduce((acc, activity) => {
      acc[activity.type] = (acc[activity.type] || 0) + 1;
      return acc;
    }, {});

    // Convert to chart data format
    return Object.entries(activityCounts).map(([type, count]) => ({
      name: ACTIVITY_TYPES.find(t => t.value === type)?.label || type,
      value: count
    }));
  };

  const getSuspiciousActivityData = (result) => {
    if (!result?.suspicious_activities) return [];
    
    return result.suspicious_activities.map(activity => {
      let label = activity.reason;
      
      // Format upvote-related labels
      if (label.includes('Upvote from new account')) {
        label = 'New Account Vote';
      } else if (label.includes('Unusual burst of karma gain')) {
        label = 'Vote Burst';
      } else if (label.includes('Upvote from bot-like account')) {
        label = 'Bot-like Vote';
      } else if (label.includes('Spam word')) {
        // Extract just the word from "Spam word 'word' detected"
        const word = label.match(/'([^']+)'/)?.[1] || '';
        label = `${word}`;
      } else if (label.includes('Vague word')) {
        // Extract just the word from "Vague word 'word' detected"
        const word = label.match(/'([^']+)'/)?.[1] || '';
        label = `${word}`;
      }

      return {
        name: label,
        score: activity.score
      };
    });
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Analysis Section */}
      <Typography variant="h4" gutterBottom sx={{ mb: 4, textAlign: 'center', fontWeight: 'bold' }}>
        Analyze User Activity
      </Typography>

      <Grid container spacing={3}>
        {/* User Info Form */}
        <Grid item xs={12} md={6}>
          <Zoom in={true}>
            <Card elevation={3} sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                  User Information
                </Typography>
                <TextField
                  fullWidth
                  label="User ID"
                  name="user_id"
                  value={userInfo.user_id}
                  onChange={handleUserInfoChange}
                  margin="normal"
                  variant="outlined"
                />
                <TextField
                  fullWidth
                  label="Account Age (days)"
                  name="account_age_days"
                  type="number"
                  value={userInfo.account_age_days}
                  onChange={handleUserInfoChange}
                  margin="normal"
                  variant="outlined"
                />
              </CardContent>
            </Card>
          </Zoom>
        </Grid>

        {/* Activity Builder */}
        <Grid item xs={12} md={6}>
          <Zoom in={true}>
            <Card elevation={3} sx={{ height: '100%',maxWidth:'500px'}}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                  Add Activity
                </Typography>
                <FormControl fullWidth margin="normal" width='440px'>
                  <InputLabel>Activity Type</InputLabel>
                  <Select
                    name="type"
                    value={currentActivity.type}
                    onChange={handleActivityChange}
                    label="Activity Type"
                    variant="outlined"
                  >
                    {ACTIVITY_TYPES.map(type => (
                      <MenuItem key={type.value} value={type.value}>{type.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {currentActivity.type === 'upvote_received' && (
                  <Fade in={true}>
                    <Box>
                      <TextField
                        fullWidth
                        label="From User"
                        name="from_user"
                        value={currentActivity.from_user}
                        onChange={handleActivityChange}
                        margin="normal"
                        variant="outlined"
                      />
                      <TextField
                        fullWidth
                        label="From User Age (days)"
                        name="from_user_age_days"
                        type="number"
                        value={currentActivity.from_user_age_days}
                        onChange={handleActivityChange}
                        margin="normal"
                        variant="outlined"
                      />
                    </Box>
                  </Fade>
                )}

                {currentActivity.type === 'upvote_sent' && (
                  <Fade in={true}>
                    <Box>
                      <TextField
                        fullWidth
                        label="To User"
                        name="to_user"
                        value={currentActivity.to_user}
                        onChange={handleActivityChange}
                        margin="normal"
                        variant="outlined"
                      />
                      <TextField
                        fullWidth
                        label="To User Age (days)"
                        name="to_user_age_days"
                        type="number"
                        value={currentActivity.to_user_age_days}
                        onChange={handleActivityChange}
                        margin="normal"
                        variant="outlined"
                      />
                    </Box>
                  </Fade>
                )}

                {(currentActivity.type === 'comment' || currentActivity.type === 'post_created') && (
                  <Fade in={true}>
                    <Box sx={{ width: '440px' }}>
                      <TextField
                        fullWidth
                        label="Content"
                        name="content"
                        value={currentActivity.content}
                        onChange={handleActivityChange}
                        margin="normal"
                        variant="outlined"
                        multiline
                        rows={2}
                        sx={{
                          '& .MuiInputBase-root': {
                            height: '100px',
                            overflow: 'auto'
                          }
                        }}
                      />
                    </Box>
                  </Fade>
                )}

                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DateTimePicker
                    label="Timestamp"
                    value={currentActivity.timestamp}
                    onChange={(newValue) => {
                      handleActivityChange({
                        target: {
                          name: 'timestamp',
                          value: newValue
                        }
                      });
                    }}
                    renderInput={(params) => (
                      <TextField {...params} fullWidth margin="normal" variant="outlined" />
                    )}
                  />
                </LocalizationProvider>

                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={addActivity}
                  sx={{ mt: 2 }}
                  fullWidth
                  size="large"
                >
                  Add Activity
                </Button>
              </CardContent>
            </Card>
          </Zoom>
        </Grid>

        {/* Activities List and JSON Preview */}
        <Grid item xs={12} md={8}>
          <Zoom in={true}>
            <Card elevation={3} sx={{ height: activities.length > 0 ? '400px' : '150px', width: activities.length > 0 ? '400px' : '200px' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                  Activities List
                </Typography>
                <Box sx={{ 
                  height: activities.length > 0 ? '320px' : '70px',
                  width: '100%',
                  overflow: 'auto',
                  bgcolor: 'background.paper',
                  borderRadius: 1,
                  p: 1
                }}>
                  <List>
                    {activities.map((activity, index) => (
                      <React.Fragment key={activity.activity_id}>
                        <ListItem>
                          <ListItemText
                            primary={
                              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                {ACTIVITY_TYPES.find(t => t.value === activity.type)?.label} ({activity.activity_id})
                              </Typography>
                            }
                            secondary={
                              <Box sx={{ mt: 1 }}>
                                {activity.content && (
                                  <Typography variant="body2" color="text.secondary">
                                    Content: {activity.content}
                                  </Typography>
                                )}
                                {activity.from_user && (
                                  <Typography variant="body2" color="text.secondary">
                                    From: {activity.from_user} (Age: {activity.from_user_age_days} days)
                                  </Typography>
                                )}
                                {activity.to_user && (
                                  <Typography variant="body2" color="text.secondary">
                                    To: {activity.to_user} (Age: {activity.to_user_age_days} days)
                                  </Typography>
                                )}
                                <Typography variant="body2" color="text.secondary">
                                  Time: {activity.timestamp}
                                </Typography>
                              </Box>
                            }
                          />
                          <ListItemSecondaryAction>
                            <IconButton edge="end" onClick={() => removeActivity(index)} color="error">
                              <DeleteIcon />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                        {index < activities.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </Box>
              </CardContent>
            </Card>
          </Zoom>
        </Grid>

        <Grid item xs={12} md={8}>
          <Zoom in={true}>
            <Card elevation={3} sx={{ height: activities.length > 0 ? '400px' : '150px', width: activities.length > 0 ? '400px' : '200px' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                  JSON Preview
                </Typography>
                <Box sx={{ 
                  height: activities.length > 0 ? '320px' : '50px',
                  width: '100%',
                  overflow: activities.length > 0 ? 'auto' : 'hidden',
                  bgcolor: 'background.paper',
                  borderRadius: 1,
                  p: 1
                }}>
                  <TextField
                    fullWidth
                    multiline
                    value={jsonPreview}
                    InputProps={{
                      readOnly: true,
                      sx: {
                        fontFamily: 'monospace',
                        fontSize: '0.9rem',
                        backgroundColor: 'transparent',
                        '& .MuiInputBase-input': {
                          padding: 2
                        }
                      }
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Zoom>
        </Grid>

        {/* Upload and Analyze Buttons */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 4 }}>
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadIcon />}
              sx={{ 
                minWidth: '200px',
                height: '48px'
              }}
            >
              Upload JSON
              <input
                type="file"
                hidden
                accept=".json"
                onChange={handleFileUpload}
              />
            </Button>
            <Button
              variant="contained"
              onClick={handleAnalyze}
              disabled={loading || activities.length === 0}
              sx={{ 
                minWidth: '200px',
                height: '48px'
              }}
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze'}
            </Button>
          </Box>
        </Grid>
      </Grid>

      {/* Results Dashboard Section */}
      <Typography variant="h4" gutterBottom sx={{ mt: 6, mb: 4, textAlign: 'center', fontWeight: 'bold' }}>
        Analysis Results
      </Typography>

      {result ? (
      <Grid
        item
        xs={12}
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 4,
        }}
        >
        <Grid
          container
          spacing={4}
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            flexDirection: 'row',
            alignItems: 'flex-start',
            justifyContent: 'center',
            gap: 4,
          }}
          >
          {/* Top Row - Fraud Score and Raw JSON */}
          <Grid
            item
            xs={12}
            md={5}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            >
            <Card sx={{ width: 300, display: 'flex', flexDirection: 'column' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Fraud Score
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 2,
                    py: 4,
                  }}
                >
                  <Box
                    sx={{
                      width: 150,
                      height: 150,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor:
                        result.fraud_score > 0.5
                          ? 'error.main'
                          : result.fraud_score > 0.25
                          ? 'warning.main'
                          : 'success.main',
                      color: 'white',
                      fontSize: '2rem',
                      fontWeight: 'bold',
                      boxShadow: 3,
                      aspectRatio: '1/1',
                      minWidth: 150,
                      minHeight: 150,
                      overflow: 'hidden'
                    }}
                  >
                    {result.fraud_score}
                  </Box>
                  <Typography variant="h6" color="text.secondary">
                    Status: {result.status.charAt(0).toUpperCase() + result.status.slice(1)}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" align="center">
                    {result.fraud_score > 0.5
                      ? 'High risk of fraudulent activity'
                      : result.fraud_score > 0.25
                      ? 'Moderate risk detected'
                      : 'Low risk profile'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
      
          <Grid
            item
            xs={12}
            md={5}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Card elevation={3} sx={{ width: 400, height: 400 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Raw Results
                </Typography>
                <Box
                  sx={{
                    height: 300,
                    width: '100%',
                    alignItems: 'center',
                    overflow: 'auto',
                    bgcolor: 'background.paper',
                    borderRadius: 1,
                    border: '1px solid',
                    borderColor: 'divider',
                    p: 1,
                  }}
                >
                  <TextField
                    fullWidth
                    multiline
                    value={JSON.stringify(result, null, 2)}
                    InputProps={{
                      readOnly: true,
                      sx: {
                        fontFamily: 'monospace',
                        fontSize: '0.9rem',
                        backgroundColor: 'transparent',
                        '& .MuiInputBase-input': {
                          padding: 2,
                        },
                      },
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      
        {/* Bottom Row - Visualizations */}
        <Grid
          item
          xs={12}
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            flexDirection: 'row',
            alignItems: 'flex-start',
            justifyContent: 'center',
            gap: 4,
            mt: 2,
          }}
          >
          {/* Activity Distribution Card */}
          <Grid item xs={12} md={6} sx={{ display: 'flex', justifyContent: 'center' }}>
            <Card elevation={3} sx={{ width: 400, height: 400 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Activity Distribution
                </Typography>
                <Box sx={{ height: 300, width: '80%', mt: 2 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getChartData(result)}
                        cx="50%"
                        cy="40%"
                        labelLine={false}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {getChartData(result).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend 
                        layout="horizontal" 
                        verticalAlign="bottom" 
                        align="center"
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
      
          {/* Suspicious Activities Chart */}
          {result.suspicious_activities && result.suspicious_activities.length > 0 && (
            <Grid item xs={12} md={6} sx={{ display: 'flex', justifyContent: 'center' }}>
              <Card elevation={3} sx={{ width: 400, height: 400 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Suspicious Activities
                  </Typography>
                  <Box sx={{ height: 300, width: '100%', mt: 2 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={getSuspiciousActivityData(result)}
                        margin={{ top: 10, right: 5, left: 10, bottom: 15 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="name"
                          angle={-35}
                          textAnchor="end"
                          height={20}
                          interval={0}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis domain={[0, 1.5]} />
                        <Tooltip />
                        <Legend />
                        <Bar 
                          dataKey="score" 
                          fill="#8884d8" 
                          name="Risk Score"
                          barSize={30}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Grid>
      ) : (
        <Card elevation={3}>
          <CardContent>
            <Box sx={{ 
              height: 400,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'background.paper',
              borderRadius: 1,
              border: '1px dashed',
              borderColor: 'divider'
            }}>
              <Typography variant="body1" color="text.secondary">
                Analysis results will appear here
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}

export default AnalysisTool; 