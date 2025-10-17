const API_BASE_URL = 'http://127.0.0.1:5000/api';

interface AuthResponse {
  message: string;
  token: string;
  user: {
    id: string;
    email: string;
  };
}

interface LoginData {
  email: string;
  password: string;
}

interface ProfileData {
  name?: string;
  phone?: string;
  location?: string;
  bio?: string;
}

class ApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  async register(data: LoginData): Promise<AuthResponse> {
    try {
      console.log('Attempting to register with URL:', `${API_BASE_URL}/auth/register`);
      console.log('Request data:', data);
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data)
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const error = await response.json();
        console.error('Server error:', error);
        throw new Error(error.error || 'Registration failed');
      }

      const result = await response.json();
      console.log('Registration successful:', result);
      return result;
    } catch (error) {
      console.error('Registration error:', error);
      if (error instanceof TypeError) {
        throw new Error('Cannot connect to server. Make sure Flask backend is running on port 5000.');
      }
      throw error;
    }
  }

  async login(data: LoginData): Promise<AuthResponse> {
    try {
      console.log('Attempting to login with URL:', `${API_BASE_URL}/auth/login`);
      console.log('Request data:', data);
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data)
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const error = await response.json();
        console.error('Server error:', error);
        throw new Error(error.error || 'Login failed');
      }

      const result = await response.json();
      console.log('Login successful:', result);
      return result;
    } catch (error) {
      console.error('Login error:', error);
      if (error instanceof TypeError) {
        throw new Error('Cannot connect to server. Make sure Flask backend is running on port 5000.');
      }
      throw error;
    }
  }

  async verifyToken(): Promise<{ user: { id: string; email: string; name?: string; phone?: string; location?: string; bio?: string } }> {
    const response = await fetch(`${API_BASE_URL}/auth/verify`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Token verification failed');
    }

    return response.json();
  }

  async updateProfile(data: ProfileData): Promise<{ message: string; user: any }> {
    try {
      const response = await fetch(`${API_BASE_URL}/profile/update`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Profile update failed');
      }

      return response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        throw new Error('Cannot connect to server. Make sure Flask backend is running on port 5000.');
      }
      throw error;
    }
  }
}

export const apiService = new ApiService();