const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

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

interface Recipe {
  id?: number | string;
  title?: string;
  name?: string;
  description?: string;
  time?: string;
  servings?: number;
  image?: string;
  ingredients?: string[];
  instructions?: string[];
  prep_time?: number;
  cook_time?: number;
  difficulty?: string;
  tags?: string[];
}

interface RecipeResponse {
  recipe: Recipe;
  message: string;
}

interface RecipesResponse {
  recipes: Recipe[];
  message: string;
}

class ApiService {
  private isBackendAvailable = true;
  
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }
  
  async checkHealth(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000); // 2 second timeout
      
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      this.isBackendAvailable = response.ok;
      return response.ok;
    } catch (error) {
      // Don't log AbortError as it's expected when timeout occurs
      if (!(error instanceof DOMException && error.name === 'AbortError')) {
        console.warn('Health check failed silently - continuing in offline mode');
      }
      this.isBackendAvailable = false;
      return false;
    }
  }

  async register(data: LoginData): Promise<AuthResponse> {
    if (!this.isBackendAvailable) {
      // If we already know backend is unavailable, fail fast
      throw new Error('Backend server is not available. Please try again later.');
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Registration failed');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        this.isBackendAvailable = false;
        throw new Error('Cannot connect to server. Please check your internet connection or try again later.');
      }
      throw error;
    }
  }

  async login(data: LoginData): Promise<AuthResponse> {
    if (!this.isBackendAvailable) {
      // If we already know backend is unavailable, fail fast
      throw new Error('Backend server is not available. Please try again later.');
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Login failed');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        this.isBackendAvailable = false;
        throw new Error('Cannot connect to server. Please check your internet connection or try again later.');
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

  async updateProfile(data: ProfileData): Promise<{ message: string; user: { id: string; email: string; name?: string; phone?: string; location?: string; bio?: string } }> {
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

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        throw new Error('Cannot connect to server');
      }
      throw error;
    }
  }

  async getRecipes(): Promise<RecipesResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/recipes`, {
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch recipes');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        throw new Error('Cannot connect to server');
      }
      throw error;
    }
  }

  async createRecipe(recipe: Recipe): Promise<RecipeResponse> {
    try {
      // Transform recipe data to match backend expectations
      const recipeData = {
        title: recipe.title || recipe.name || 'Untitled Recipe',
        name: recipe.name || recipe.title || 'Untitled Recipe',
        description: recipe.description || '',
        ingredients: recipe.ingredients || [],
        instructions: recipe.instructions || [],
        prep_time: recipe.prep_time,
        cook_time: recipe.cook_time,
        servings: recipe.servings,
        difficulty: recipe.difficulty || 'medium',
        tags: recipe.tags || []
      };

      const response = await fetch(`${API_BASE_URL}/recipes`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(recipeData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create recipe');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        throw new Error('Cannot connect to server');
      }
      throw error;
    }
  }

  async deleteRecipe(recipeId: number | string): Promise<{ message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to delete recipe');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError) {
        throw new Error('Cannot connect to server');
      }
      throw error;
    }
  }
}

export const apiService = new ApiService();
export { recipeService } from './recipeService';