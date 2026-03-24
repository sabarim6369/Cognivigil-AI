// API Service for Cognivigil AI Backend

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('adminToken');
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if token exists
    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }));
        throw new Error(error.message || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Admin Authentication
  async adminLogin(credentials) {
    const response = await this.request('/admin/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    // Store token
    this.token = response.access_token;
    localStorage.setItem('adminToken', this.token);
    
    return response;
  }

  // Admin logout
  logout() {
    this.token = null;
    localStorage.removeItem('adminToken');
  }

  // Test Management (Admin)
  async getAllTests() {
    return this.request('/admin/tests');
  }

  async getTest(testId) {
    return this.request(`/admin/tests/${testId}`);
  }

  async createTest(testData) {
    return this.request('/admin/tests', {
      method: 'POST',
      body: JSON.stringify(testData),
    });
  }

  async updateTest(testId, testData) {
    return this.request(`/admin/tests/${testId}`, {
      method: 'PUT',
      body: JSON.stringify(testData),
    });
  }

  async deleteTest(testId) {
    return this.request(`/admin/tests/${testId}`, {
      method: 'DELETE',
    });
  }

  async getTestDetails(testId) {
    return this.request(`/admin/tests/${testId}/details`);
  }

  // User Management (Admin)
  async getAllUsers() {
    return this.request('/admin/users');
  }

  async getUserDetails(userId) {
    return this.request(`/admin/users/${userId}`);
  }

  async getDashboardOverview() {
    return this.request('/admin/dashboard/overview');
  }

  // Tests (Public/Student)
  async getAvailableTests() {
    return this.request('/tests');
  }

  async getTestById(testId) {
    return this.request(`/tests/${testId}`);
  }

  // Session Management
  async startSession(sessionData) {
    return this.request('/sessions/start', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  }

  async endSession(sessionId, finalScore, finalRiskScore) {
    return this.request(`/sessions/${sessionId}/end?final_score=${finalScore}&final_risk_score=${finalRiskScore}`, {
      method: 'POST',
    });
  }

  async getSession(sessionId) {
    return this.request(`/sessions/${sessionId}`);
  }

  async getUserSessions(userId, limit = 10) {
    return this.request(`/sessions/user/${userId}?limit=${limit}`);
  }

  async getTestSessions(testId, limit = 50) {
    return this.request(`/sessions/test/${testId}?limit=${limit}`);
  }

  // Detection API
  async processFrame(frameData, sessionId) {
    return this.request('/process-frame', {
      method: 'POST',
      body: JSON.stringify({
        frame: frameData,
        session_id: sessionId,
        timestamp: new Date().toISOString(),
      }),
    });
  }

  async getSessionEvents(sessionId, limit = 50) {
    return this.request(`/detection/session/${sessionId}/events?limit=${limit}`);
  }

  async getSessionRiskScore(sessionId) {
    return this.request(`/detection/session/${sessionId}/risk-score`);
  }

  // User Registration
  async registerUser(userData) {
    return this.request('/users/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getUserProfile(userId) {
    return this.request(`/users/${userId}`);
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
