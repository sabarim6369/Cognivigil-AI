import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const TestPage = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [testStarted, setTestStarted] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [riskScore, setRiskScore] = useState(0);
  const [alerts, setAlerts] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});

  // Sample test data
  const testData = {
    1: {
      title: 'Mathematics Assessment',
      duration: 60,
      questions: [
        {
          id: 1,
          question: 'What is the derivative of x² + 3x + 2?',
          options: ['2x + 3', 'x + 3', '2x + 2', 'x² + 3'],
          correct: 0
        },
        {
          id: 2,
          question: 'Solve for x: 2x + 5 = 15',
          options: ['x = 5', 'x = 10', 'x = 7.5', 'x = 3'],
          correct: 0
        },
        {
          id: 3,
          question: 'What is the integral of 2x?',
          options: ['x² + C', '2x² + C', 'x + C', '2x + C'],
          correct: 0
        }
      ]
    },
    2: {
      title: 'Computer Science Fundamentals',
      duration: 90,
      questions: [
        {
          id: 1,
          question: 'What is the time complexity of binary search?',
          options: ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
          correct: 1
        },
        {
          id: 2,
          question: 'Which data structure uses LIFO principle?',
          options: ['Queue', 'Stack', 'Array', 'Linked List'],
          correct: 1
        }
      ]
    },
    3: {
      title: 'English Proficiency',
      duration: 45,
      questions: [
        {
          id: 1,
          question: 'Choose the correct form: "He ___ to school yesterday."',
          options: ['go', 'went', 'gone', 'going'],
          correct: 1
        }
      ]
    }
  };

  const currentTest = testData[testId] || testData[1];

  // Update clock
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Initialize camera
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
        
        // Start sending frames to backend (dummy implementation)
        startFrameCapture();
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Unable to access camera. Please ensure camera permissions are granted.');
    }
  };

  // Capture and send frames to backend
  const startFrameCapture = () => {
    const captureFrame = () => {
      if (videoRef.current && canvasRef.current && testStarted) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        // Get frame data
        const frameData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Send to backend (dummy implementation)
        sendFrameToBackend(frameData);
      }
      
      // Capture frames every 2 seconds
      if (testStarted) {
        setTimeout(captureFrame, 2000);
      }
    };
    
    captureFrame();
  };

  // Dummy backend communication
  const sendFrameToBackend = async (frameData) => {
    try {
      // Simulate backend processing
      const response = await fetch('http://localhost:8000/api/v1/process-frame', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          frame: frameData,
          session_id: `session_${testId}_${Date.now()}`,
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Update risk score
        if (result.risk_score) {
          setRiskScore(result.risk_score);
        }
        
        // Add alerts if any
        if (result.alerts && result.alerts.length > 0) {
          setAlerts(prev => [...prev, ...result.alerts]);
        }
      } else {
        // Dummy response for demo
        const dummyRisk = Math.floor(Math.random() * 30);
        setRiskScore(prev => Math.min(100, prev + dummyRisk));
        
        // Random alerts for demo
        if (Math.random() > 0.8) {
          const dummyAlerts = [
            'Looking away detected',
            'Multiple faces detected',
            'Phone detected',
            'No face detected'
          ];
          const randomAlert = dummyAlerts[Math.floor(Math.random() * dummyAlerts.length)];
          setAlerts(prev => [...prev, {
            message: randomAlert,
            timestamp: new Date().toISOString(),
            severity: Math.random() > 0.5 ? 'high' : 'medium'
          }]);
        }
      }
    } catch (error) {
      console.log('Backend not available - using dummy data');
      
      // Generate dummy risk score
      const dummyRisk = Math.floor(Math.random() * 20);
      setRiskScore(prev => Math.min(100, prev + dummyRisk));
    }
  };

  // Start test
  const startTest = () => {
    setTestStarted(true);
    requestFullscreen();
  };

  // Fullscreen functionality
  const requestFullscreen = () => {
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) {
      elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) {
      elem.msRequestFullscreen();
    }
    setIsFullscreen(true);
  };

  // Handle fullscreen change
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Handle answer selection
  const handleAnswerSelect = (questionId, optionIndex) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: optionIndex
    }));
  };

  // Navigate questions
  const nextQuestion = () => {
    if (currentQuestion < currentTest.questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  // Submit test
  const submitTest = () => {
    const score = calculateScore();
    alert(`Test submitted! Your score: ${score}%\nRisk Score: ${riskScore}%`);
    navigate('/dashboard');
  };

  // Calculate score
  const calculateScore = () => {
    let correct = 0;
    currentTest.questions.forEach(q => {
      if (answers[q.id] === q.correct) {
        correct++;
      }
    });
    return Math.round((correct / currentTest.questions.length) * 100);
  };

  // Exit fullscreen
  const exitFullscreen = () => {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    }
  };

  // Initialize camera on mount
  useEffect(() => {
    startCamera();
    return () => {
      // Cleanup camera on unmount
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Hidden video and canvas elements */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="hidden"
      />
      <canvas
        ref={canvasRef}
        className="hidden"
      />

      {/* Test Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">{currentTest.title}</h1>
            <span className="text-gray-400">
              Question {currentQuestion + 1} of {currentTest.questions.length}
            </span>
          </div>
          
          <div className="flex items-center space-x-6">
            {/* Risk Score */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">Risk Score:</span>
              <span className={`font-bold ${
                riskScore < 25 ? 'text-green-400' :
                riskScore < 50 ? 'text-yellow-400' :
                riskScore < 75 ? 'text-orange-400' : 'text-red-400'
              }`}>
                {riskScore}%
              </span>
            </div>

            {/* Camera Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${cameraActive ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm text-gray-400">
                {cameraActive ? 'Camera Active' : 'Camera Inactive'}
              </span>
            </div>

            {/* Current Time */}
            <div className="text-sm text-gray-400">
              {currentTime.toLocaleTimeString()}
            </div>

            {/* Exit Fullscreen */}
            {isFullscreen && (
              <button
                onClick={exitFullscreen}
                className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
              >
                Exit Fullscreen
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Test Area */}
      <main className="flex h-screen">
        {/* Alerts Panel */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 p-4">
          <h2 className="text-lg font-semibold mb-4">Alerts</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-sm">No alerts yet</p>
            ) : (
              alerts.map((alert, index) => (
                <div
                  key={index}
                  className={`p-3 rounded text-sm ${
                    alert.severity === 'high' 
                      ? 'bg-red-900 border border-red-700' 
                      : 'bg-yellow-900 border border-yellow-700'
                  }`}
                >
                  <div className="font-medium">{alert.message}</div>
                  <div className="text-gray-400 text-xs mt-1">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Camera Preview */}
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Camera Feed</h3>
            <div className="bg-gray-700 rounded aspect-video flex items-center justify-center">
              {cameraActive ? (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover rounded"
                />
              ) : (
                <div className="text-gray-500">Camera initializing...</div>
              )}
            </div>
          </div>
        </div>

        {/* Test Content */}
        <div className="flex-1 flex flex-col">
          {!testStarted ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-2xl px-8">
                <h2 className="text-3xl font-bold mb-4">Ready to Start Test?</h2>
                <p className="text-gray-400 mb-8">
                  Make sure you're in a quiet environment with good lighting. 
                  Your camera will monitor you throughout the test to ensure academic integrity.
                </p>
                
                <div className="bg-gray-800 rounded-lg p-6 mb-8 text-left">
                  <h3 className="font-semibold mb-4">Test Instructions:</h3>
                  <ul className="space-y-2 text-gray-300">
                    <li>• Ensure your face is clearly visible at all times</li>
                    <li>• Do not look away from the screen frequently</li>
                    <li>• No mobile phones or other devices allowed</li>
                    <li>• No other persons should be in the room</li>
                    <li>• Test will be monitored for suspicious behavior</li>
                  </ul>
                </div>

                <button
                  onClick={startTest}
                  className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                >
                  Start Test
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Question */}
              <div className="flex-1 p-8">
                <div className="max-w-4xl mx-auto">
                  <h2 className="text-2xl font-bold mb-6">
                    {currentTest.questions[currentQuestion].question}
                  </h2>
                  
                  <div className="space-y-4">
                    {currentTest.questions[currentQuestion].options.map((option, index) => (
                      <label
                        key={index}
                        className={`block p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                          answers[currentTest.questions[currentQuestion].id] === index
                            ? 'border-indigo-500 bg-indigo-900'
                            : 'border-gray-600 hover:border-gray-500'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <input
                            type="radio"
                            name={`question-${currentTest.questions[currentQuestion].id}`}
                            checked={answers[currentTest.questions[currentQuestion].id] === index}
                            onChange={() => handleAnswerSelect(currentTest.questions[currentQuestion].id, index)}
                            className="w-4 h-4 text-indigo-600"
                          />
                          <span className="text-lg">{option}</span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              {/* Navigation */}
              <div className="bg-gray-800 border-t border-gray-700 px-8 py-4">
                <div className="flex justify-between items-center max-w-4xl mx-auto">
                  <button
                    onClick={prevQuestion}
                    disabled={currentQuestion === 0}
                    className="px-6 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>

                  <div className="flex space-x-2">
                    {currentTest.questions.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentQuestion(index)}
                        className={`w-8 h-8 rounded ${
                          index === currentQuestion
                            ? 'bg-indigo-600 text-white'
                            : answers[currentTest.questions[index].id] !== undefined
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-300'
                        }`}
                      >
                        {index + 1}
                      </button>
                    ))}
                  </div>

                  {currentQuestion === currentTest.questions.length - 1 ? (
                    <button
                      onClick={submitTest}
                      className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                    >
                      Submit Test
                    </button>
                  ) : (
                    <button
                      onClick={nextQuestion}
                      className="px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
                    >
                      Next
                    </button>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default TestPage;
