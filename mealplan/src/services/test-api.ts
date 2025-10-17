// Test if we can reach the Flask server
export const testConnection = async () => {
  try {
    console.log('Testing connection to Flask server...');
    const response = await fetch('http://127.0.0.1:5000/api/health');
    const data = await response.json();
    console.log('Connection successful:', data);
    return true;
  } catch (error) {
    console.error('Connection failed:', error);
    return false;
  }
};