// API Configuration
const config = {
  // Development - use local backend
  development: {
    apiUrl: 'http://localhost:8000'
  },
  // Production - use Render backend
  production: {
    apiUrl: process.env.REACT_APP_API_URL || 'https://karma-fraud-bck.onrender.com'
  }
};

// Get current environment
const environment = process.env.NODE_ENV || 'development';

// Export the appropriate config
export const apiUrl = config[environment].apiUrl;

export default config[environment]; 