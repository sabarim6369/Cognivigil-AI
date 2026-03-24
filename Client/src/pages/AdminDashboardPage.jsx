import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const AdminDashboardPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [tests, setTests] = useState([]);
  const [users, setUsers] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    total_users: 0,
    total_tests: 0,
    total_sessions: 0,
    average_score: 0,
    average_risk: 0,
    high_risk_users: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [showCreateTest, setShowCreateTest] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [showTestDetails, setShowTestDetails] = useState(false);
  const [testDetails, setTestDetails] = useState(null);
  const [loadingTestDetails, setLoadingTestDetails] = useState(false);
  const [newTest, setNewTest] = useState({
    title: '',
    duration: '',
    questions: '',
    difficulty: 'Medium',
    description: ''
  });

  // Check authentication and load data
  useEffect(() => {
    const isAuthenticated = localStorage.getItem('isAdminAuthenticated');
    if (!isAuthenticated) {
      navigate('/admin/login');
      return;
    }
    loadInitialData();
  }, [navigate]);

  const loadInitialData = async () => {
    try {
      // Load dashboard data from API
      const [testsData, usersData, overviewData] = await Promise.all([
        apiService.getAllTests(),
        apiService.getAllUsers(),
        apiService.getDashboardOverview()
      ]);

      setTests(testsData.tests || []);
      setUsers(usersData.users || []);
      
      // Transform overview data if needed
      if (overviewData.stats) {
        setDashboardStats(overviewData.stats);
      }
      
      if (overviewData.recent_activity) {
        setRecentActivity(overviewData.recent_activity);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Don't load sample data - show empty state instead
      setTests([]);
      setUsers([]);
      setDashboardStats({
        total_users: 0,
        total_tests: 0,
        total_sessions: 0,
        average_score: 0,
        average_risk: 0,
        high_risk_users: 0
      });
      setRecentActivity([]);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('isAdminAuthenticated');
    navigate('/admin/login');
  };

  const handleCreateTest = async (e) => {
    e.preventDefault();
    try {
      // Prepare test data for backend
      const testPayload = {
        title: newTest.title,
        description: newTest.description,
        duration: parseInt(newTest.duration),
        difficulty: newTest.difficulty.toLowerCase(),
        questions: [] // You may want to add a UI for questions later
      };
      
      await apiService.createTest(testPayload);
      
      // Reload all data from backend
      await loadInitialData();
      
      // Reset form
      setNewTest({
        title: '',
        duration: '',
        questions: '',
        difficulty: 'Medium',
        description: ''
      });
      setShowCreateTest(false);
    } catch (err) {
      console.error('Failed to create test:', err);
      alert('Failed to create test. Please try again.');
    }
  };

  const handleViewTestDetails = async (test) => {
    try {
      setSelectedTest(test);
      setShowTestDetails(true);
      setLoadingTestDetails(true);
      
      // Fetch detailed test information from API
      const details = await apiService.getTestDetails(test.test_id);
      setTestDetails(details);
    } catch (error) {
      console.error('Failed to load test details:', error);
      // Still show modal with basic test info
      setSelectedTest(test);
      setShowTestDetails(true);
      setTestDetails(null);
    } finally {
      setLoadingTestDetails(false);
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'Low': return 'text-green-600 bg-green-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'High': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 bg-green-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'Hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-indigo-600">Admin Panel</h1>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/" className="text-gray-600 hover:text-gray-900">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </a>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('tests')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'tests'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Tests
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'users'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Users
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'analytics'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Analytics
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h2>
            
            {/* Stats Cards */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Tests</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardStats.total_tests}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Users</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardStats.total_users}</p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Avg Score</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardStats.average_score}%</p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">High Risk</p>
                    <p className="text-2xl font-bold text-red-600">{dashboardStats.high_risk_users}</p>
                  </div>
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold text-gray-900">Recent Test Activity</h3>
              </div>
              <div className="p-6">
                {recentActivity.length > 0 ? (
                  <div className="space-y-4">
                    {recentActivity.map((activity, index) => (
                      <div key={index} className="flex items-center justify-between py-3 border-b">
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                            <span className="text-indigo-600 font-semibold">{activity.user_name?.charAt(0) || 'U'}</span>
                          </div>
                          <div>
                            <p className="text-gray-900 font-medium">{activity.user_name} - {activity.test_name}</p>
                            <p className="text-gray-500 text-sm">Score: {activity.score}% • Risk: {activity.risk_score}%</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(activity.risk_score > 50 ? 'High' : activity.risk_score > 25 ? 'Medium' : 'Low')}`}>
                            {activity.risk_score > 50 ? 'High Risk' : activity.risk_score > 25 ? 'Medium Risk' : 'Low Risk'}
                          </div>
                          <p className="text-gray-500 text-sm mt-1">{new Date(activity.date).toLocaleDateString()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No recent activity found</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tests Tab */}
        {activeTab === 'tests' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Test Management</h2>
              <button
                onClick={() => setShowCreateTest(true)}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
              >
                Create New Test
              </button>
            </div>

            {/* Create Test Modal */}
            {showCreateTest && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 w-full max-w-md">
                  <h3 className="text-lg font-semibold mb-4">Create New Test</h3>
                  <form onSubmit={handleCreateTest} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Test Title</label>
                      <input
                        type="text"
                        value={newTest.title}
                        onChange={(e) => setNewTest({...newTest, title: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
                        <input
                          type="number"
                          value={newTest.duration}
                          onChange={(e) => setNewTest({...newTest, duration: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Questions</label>
                        <input
                          type="number"
                          value={newTest.questions}
                          onChange={(e) => setNewTest({...newTest, questions: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                      <select
                        value={newTest.difficulty}
                        onChange={(e) => setNewTest({...newTest, difficulty: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <option value="Easy">Easy</option>
                        <option value="Medium">Medium</option>
                        <option value="Hard">Hard</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <textarea
                        value={newTest.description}
                        onChange={(e) => setNewTest({...newTest, description: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        rows="3"
                      />
                    </div>
                    <div className="flex space-x-3">
                      <button
                        type="submit"
                        className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
                      >
                        Create Test
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowCreateTest(false)}
                        className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {/* Tests List */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="overflow-x-auto">
                {tests.length > 0 ? (
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Test Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Questions</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulty</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Attempts</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {tests.map((test) => (
                        <tr key={test.test_id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{test.title}</div>
                              <div className="text-sm text-gray-500">Created: {new Date(test.created_at).toLocaleDateString()}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{test.duration} min</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{test.questions_count || test.questions?.length || 0}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(test.difficulty)}`}>
                              {test.difficulty}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{test.attempts || 0}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              test.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                              {test.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button 
                              onClick={() => handleViewTestDetails(test)}
                              className="text-indigo-600 hover:text-indigo-900 mr-3"
                            >
                              View Details
                            </button>
                            <button className="text-gray-600 hover:text-gray-900 mr-3">Edit</button>
                            <button className="text-red-600 hover:text-red-900">Delete</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No tests created</h3>
                    <p className="text-gray-500 mb-4">Get started by creating your first test.</p>
                    <button
                      onClick={() => setShowCreateTest(true)}
                      className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
                    >
                      Create New Test
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">User Management</h2>
            
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="overflow-x-auto">
                {users.length > 0 ? (
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Tests</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Score</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Active</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.user_id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                                <span className="text-indigo-600 font-semibold">{user.name?.charAt(0) || 'U'}</span>
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">{user.name}</div>
                                <div className="text-sm text-gray-500">{user.email}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.total_tests || 0}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.average_score || 0}%</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(user.risk_level)}`}>
                              {user.risk_level || 'Low'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {user.last_active ? new Date(user.last_active).toLocaleDateString() : 'Never'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button 
                              onClick={() => {
                                // Show user details modal
                                alert(`User Details:\n\nName: ${user.name}\nEmail: ${user.email}\nTotal Tests: ${user.total_tests || 0}\nAverage Score: ${user.average_score || 0}%\nRisk Level: ${user.risk_level || 'Low'}`);
                              }}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No users registered</h3>
                    <p className="text-gray-500">Users will appear here once they register for the system.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Analytics Dashboard</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Score Distribution */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">Score Distribution</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">90-100%</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{width: '30%'}}></div>
                    </div>
                    <span className="text-sm font-medium">30%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">80-89%</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{width: '40%'}}></div>
                    </div>
                    <span className="text-sm font-medium">40%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">70-79%</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-500 h-2 rounded-full" style={{width: '20%'}}></div>
                    </div>
                    <span className="text-sm font-medium">20%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Below 70%</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div className="bg-red-500 h-2 rounded-full" style={{width: '10%'}}></div>
                    </div>
                    <span className="text-sm font-medium">10%</span>
                  </div>
                </div>
              </div>

              {/* Risk Analysis */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">Risk Analysis</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Low Risk (0-25%)</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{width: '60%'}}></div>
                    </div>
                    <span className="text-sm font-medium">60%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Medium Risk (26-50%)</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-500 h-2 rounded-full" style={{width: '30%'}}></div>
                    </div>
                    <span className="text-sm font-medium">30%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">High Risk (51-100%)</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div className="bg-red-500 h-2 rounded-full" style={{width: '10%'}}></div>
                    </div>
                    <span className="text-sm font-medium">10%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Test Details Modal */}
        {showTestDetails && selectedTest && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden">
              <div className="p-6 border-b">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-bold text-gray-900">{selectedTest.title} - Detailed Report</h3>
                  <button
                    onClick={() => setShowTestDetails(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
                {loadingTestDetails ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    <span className="ml-3 text-gray-600">Loading test details...</span>
                  </div>
                ) : testDetails ? (
                  <>
                    {/* Test Statistics */}
                    <div className="mb-8">
                      <h4 className="text-lg font-semibold mb-4">Test Statistics</h4>
                      <div className="grid md:grid-cols-4 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">
                            {testDetails?.stats?.total_attendees || 0}
                          </div>
                          <div className="text-sm text-gray-600">Total Attendees</div>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {testDetails?.stats?.average_score || 0}%
                          </div>
                          <div className="text-sm text-gray-600">Average Score</div>
                        </div>
                        <div className="bg-yellow-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-yellow-600">
                            {testDetails?.stats?.average_risk || 0}%
                          </div>
                          <div className="text-sm text-gray-600">Average Risk</div>
                        </div>
                        <div className="bg-purple-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-purple-600">
                            {testDetails?.stats?.pass_rate || 0}%
                          </div>
                          <div className="text-sm text-gray-600">Pass Rate</div>
                        </div>
                      </div>
                    </div>

                    {/* Risk Distribution */}
                    <div className="mb-8">
                      <h4 className="text-lg font-semibold mb-4">Risk Distribution</h4>
                      <div className="grid md:grid-cols-3 gap-4">
                        <div className="bg-green-100 p-4 rounded-lg text-center">
                          <div className="text-2xl font-bold text-green-700">
                            {testDetails?.stats?.low_risk_count || 0}
                          </div>
                          <div className="text-sm text-green-600">Low Risk (0-25%)</div>
                        </div>
                        <div className="bg-yellow-100 p-4 rounded-lg text-center">
                          <div className="text-2xl font-bold text-yellow-700">
                            {testDetails?.stats?.medium_risk_count || 0}
                          </div>
                          <div className="text-sm text-yellow-600">Medium Risk (26-50%)</div>
                        </div>
                        <div className="bg-red-100 p-4 rounded-lg text-center">
                          <div className="text-2xl font-bold text-red-700">
                            {testDetails?.stats?.high_risk_count || 0}
                          </div>
                          <div className="text-sm text-red-600">High Risk (51-100%)</div>
                        </div>
                      </div>
                    </div>

                    {/* Attendees List */}
                    <div>
                      <h4 className="text-lg font-semibold mb-4">User Performance Details</h4>
                      <div className="bg-white border rounded-lg overflow-hidden">
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Score</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Level</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {testDetails?.attendees?.length === 0 ? (
                                <tr>
                                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                                    No users have attended this test yet
                                  </td>
                                </tr>
                              ) : (
                                testDetails?.attendees?.map((attendee) => (
                                  <tr key={`${attendee.user_id}-${attendee.date}`}>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                      <div className="flex items-center">
                                        <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                                          <span className="text-indigo-600 text-sm font-semibold">{attendee.name?.charAt(0) || 'U'}</span>
                                        </div>
                                        <div className="text-sm font-medium text-gray-900">{attendee.name}</div>
                                      </div>
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{attendee.email}</td>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                      <div className="flex items-center">
                                        <span className={`text-sm font-medium ${
                                          attendee.score >= 70 ? 'text-green-600' : 
                                          attendee.score >= 50 ? 'text-yellow-600' : 'text-red-600'
                                        }`}>
                                          {attendee.score}%
                                        </span>
                                      </div>
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                      <div className="flex items-center">
                                        <span className={`text-sm font-medium ${
                                          attendee.risk_score <= 25 ? 'text-green-600' : 
                                          attendee.risk_score <= 50 ? 'text-yellow-600' : 'text-red-600'
                                        }`}>
                                          {attendee.risk_score}%
                                        </span>
                                      </div>
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(attendee.risk_level)}`}>
                                        {attendee.risk_level}
                                      </span>
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                                      {new Date(attendee.date).toLocaleDateString()}
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                        attendee.status === 'Passed' ? 'bg-green-100 text-green-800' : 
                                        attendee.status === 'Borderline' ? 'bg-yellow-100 text-yellow-800' : 
                                        'bg-red-100 text-red-800'
                                      }`}>
                                        {attendee.status}
                                      </span>
                                    </td>
                                  </tr>
                                ))
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500">No test details available</p>
                  </div>
                )}
              </div>   {/* Performance Summary Chart */}
                <div className="mt-8">
                  <h4 className="text-lg font-semibold mb-4">Performance Summary</h4>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="text-sm font-medium text-gray-700 mb-3">Score Distribution</h5>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Excellent (90-100%)</span>
                          <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                            <div className="bg-green-500 h-2 rounded-full" style={{width: '25%'}}></div>
                          </div>
                          <span className="text-sm font-medium">25%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Good (80-89%)</span>
                          <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                            <div className="bg-blue-500 h-2 rounded-full" style={{width: '35%'}}></div>
                          </div>
                          <span className="text-sm font-medium">35%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Average (70-79%)</span>
                          <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                            <div className="bg-yellow-500 h-2 rounded-full" style={{width: '25%'}}></div>
                          </div>
                          <span className="text-sm font-medium">25%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Below Average (&lt;70%)</span>
                          <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                            <div className="bg-red-500 h-2 rounded-full" style={{width: '15%'}}></div>
                          </div>
                          <span className="text-sm font-medium">15%</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="text-sm font-medium text-gray-700 mb-3">Risk Level Breakdown</h5>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Low Risk Users</span>
                          <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                            <div className="bg-green-500 h-2 rounded-full" style={{width: '0%'}}></div>
                          </div>
                          <span className="text-sm font-medium">{testDetails?.stats?.low_risk_count || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Medium Risk Users</span>
                          <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                            <div className="bg-yellow-500 h-2 rounded-full" style={{width: '0%'}}></div>
                          </div>
                          <span className="text-sm font-medium">{testDetails?.stats?.medium_risk_count || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">High Risk Users</span>
                          <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                            <div className="bg-red-500 h-2 rounded-full" style={{width: '0%'}}></div>
                          </div>
                          <span className="text-sm font-medium">{testDetails?.stats?.high_risk_count || 0}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboardPage;
