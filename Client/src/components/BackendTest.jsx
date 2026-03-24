import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const BackendTest = () => {
  const [status, setStatus] = useState('loading');
  const [healthData, setHealthData] = useState(null);
  const [aiEngineStatus, setAiEngineStatus] = useState('unknown');
  const [error, setError] = useState(null);

  useEffect(() => {
    testBackendConnection();
  }, []);

  const testBackendConnection = async () => {
    try {
      // Test backend health
      const healthResponse = await fetch('http://localhost:8000/health');
      const health = await healthResponse.json();
      
      setHealthData(health);
      setStatus('connected');
      
      // Test AI Engine connection through backend
      if (health.ai_engine_available) {
        setAiEngineStatus('connected');
      } else {
        setAiEngineStatus('disconnected');
      }
      
    } catch (error) {
      console.error('Backend connection failed:', error);
      setError(error.message);
      setStatus('disconnected');
    }
  };

  const testAdminLogin = async () => {
    try {
      const result = await apiService.adminLogin('admin', 'admin123');
      console.log('Admin login successful:', result);
      alert('Admin login successful!');
    } catch (error) {
      console.error('Admin login failed:', error);
      alert('Admin login failed: ' + error.message);
    }
  };

  const testFetchTests = async () => {
    try {
      const tests = await apiService.getTests();
      console.log('Tests fetched:', tests);
      alert(`Found ${tests.length} tests`);
    } catch (error) {
      console.error('Fetch tests failed:', error);
      alert('Fetch tests failed: ' + error.message);
    }
  };

  const testAIEngineDirectly = async () => {
    try {
      const response = await fetch('http://localhost:8001/health');
      const data = await response.json();
      console.log('AI Engine direct:', data);
      alert('AI Engine connected directly!');
    } catch (error) {
      console.error('AI Engine direct connection failed:', error);
      alert('AI Engine not accessible directly: ' + error.message);
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'text-green-600';
      case 'disconnected': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  const getAiEngineColor = () => {
    switch (aiEngineStatus) {
      case 'connected': return 'text-green-600';
      case 'disconnected': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">
          🔧 Backend Integration Test
        </h1>
        
        {/* Connection Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Connection Status</h2>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-medium">Backend Server:</span>
              <span className={`font-bold ${getStatusColor()}`}>
                {status === 'connected' ? '✅ Connected' : 
                 status === 'disconnected' ? '❌ Disconnected' : '⏳ Loading...'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="font-medium">AI Engine:</span>
              <span className={`font-bold ${getAiEngineColor()}`}>
                {aiEngineStatus === 'connected' ? '✅ Connected' : 
                 aiEngineStatus === 'disconnected' ? '❌ Disconnected' : '❓ Unknown'}
              </span>
            </div>
          </div>
          
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        {/* Health Data */}
        {healthData && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Health Information</h2>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {JSON.stringify(healthData, null, 2)}
            </pre>
          </div>
        )}

        {/* Test Buttons */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Integration Tests</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={testAdminLogin}
              className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              🔐 Test Admin Login
            </button>
            
            <button
              onClick={testFetchTests}
              className="bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              📚 Fetch Tests
            </button>
            
            <button
              onClick={testAIEngineDirectly}
              className="bg-purple-500 hover:bg-purple-600 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              🤖 Test AI Engine Direct
            </button>
            
            <button
              onClick={testBackendConnection}
              className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              🔄 Refresh Status
            </button>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 mb-2">📋 Test Instructions:</h3>
          <ol className="list-decimal list-inside text-blue-700 space-y-1">
            <li>Make sure Backend is running on <code>http://localhost:8000</code></li>
            <li>Make sure AI Engine is running on <code>http://localhost:8001</code></li>
            <li>Test Admin Login with credentials: admin/admin123</li>
            <li>Verify AI Engine connection both through backend and directly</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default BackendTest;
