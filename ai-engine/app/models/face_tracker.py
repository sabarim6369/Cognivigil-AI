import asyncio
import cv2
import numpy as np
import mediapipe as mp
from typing import List, Dict, Any, Optional, Tuple
from app.schemas.models import FaceAnalysis, FaceLandmark
from app.utils.config import settings


class FaceTracker:
    def __init__(self):
        self.face_mesh = None
        self.max_faces = settings.face_max_faces
        self.min_detection_confidence = settings.face_min_detection_confidence
        self.min_tracking_confidence = settings.face_min_tracking_confidence
        self.loaded = False
        self.tracker_lock = asyncio.Lock()
        
        # Face analysis parameters
        self.looking_away_angle_threshold = settings.face_looking_away_angle_threshold
        self.face_absence_threshold_seconds = settings.face_absence_threshold_seconds
        
        # State tracking
        self.last_face_time = None
        self.face_absence_start = None
        
    async def initialize(self):
        """Initialize MediaPipe Face Mesh"""
        async with self.tracker_lock:
            if self.loaded:
                return True
                
            try:
                print(f"👤 Initializing MediaPipe Face Mesh")
                
                # Initialize Face Mesh in thread pool
                loop = asyncio.get_event_loop()
                self.face_mesh = await loop.run_in_executor(
                    None,
                    lambda: mp.solutions.face_mesh.FaceMesh(
                        max_num_faces=self.max_faces,
                        refine_landmarks=True,
                        min_detection_confidence=self.min_detection_confidence,
                        min_tracking_confidence=self.min_tracking_confidence
                    )
                )
                
                self.loaded = True
                print(f"✅ Face Mesh initialized successfully")
                print(f"   Max faces: {self.max_faces}")
                print(f"   Detection confidence: {self.min_detection_confidence}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error initializing Face Mesh: {e}")
                self.loaded = False
                return False
    
    async def analyze_face(self, frame: np.ndarray) -> FaceAnalysis:
        """Analyze face in frame"""
        if not self.loaded or self.face_mesh is None:
            return FaceAnalysis(
                face_detected=False,
                looking_away=False,
                confidence=0.0
            )
        
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process face in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.face_mesh.process(rgb_frame)
            )
            
            current_time = asyncio.get_event_loop().time()
            
            if results.multi_face_landmarks:
                # Face detected
                landmarks = results.multi_face_landmarks[0]  # Use first face
                
                # Convert landmarks to our format
                landmark_list = []
                for landmark in landmarks.landmark:
                    landmark_list.append(FaceLandmark(
                        x=landmark.x,
                        y=landmark.y,
                        z=landmark.z
                    ))
                
                # Analyze gaze direction
                gaze_direction = await self._analyze_gaze_direction(landmarks)
                
                # Analyze head pose
                head_pose = await self._analyze_head_pose(landmarks)
                
                # Check if looking away
                looking_away = await self._check_looking_away(landmarks, gaze_direction)
                
                # Update face presence tracking
                self.last_face_time = current_time
                self.face_absence_start = None
                
                return FaceAnalysis(
                    face_detected=True,
                    landmarks=landmark_list,
                    gaze_direction=gaze_direction,
                    head_pose=head_pose,
                    looking_away=looking_away,
                    face_absence_duration=0.0,
                    confidence=0.9
                )
                
            else:
                # No face detected
                return await self._handle_face_absence(current_time)
                
        except Exception as e:
            print(f"❌ Error in face analysis: {e}")
            return FaceAnalysis(
                face_detected=False,
                looking_away=False,
                confidence=0.0
            )
    
    async def _analyze_gaze_direction(self, landmarks) -> Dict[str, float]:
        """Analyze gaze direction from face landmarks"""
        try:
            # Key eye landmarks (MediaPipe indices)
            left_eye_corner = landmarks.landmark[33]
            right_eye_corner = landmarks.landmark[263]
            left_eye_center = landmarks.landmark[159]
            right_eye_center = landmarks.landmark[386]
            nose_tip = landmarks.landmark[1]
            
            # Calculate eye center
            eye_center_x = (left_eye_center.x + right_eye_center.x) / 2
            eye_center_y = (left_eye_center.y + right_eye_center.y) / 2
            
            # Calculate gaze direction (simplified)
            gaze_x = nose_tip.x - eye_center_x
            gaze_y = nose_tip.y - eye_center_y
            
            # Normalize to -1 to 1 range
            gaze_x = np.clip(gaze_x * 10, -1, 1)
            gaze_y = np.clip(gaze_y * 10, -1, 1)
            
            return {
                "gaze_x": gaze_x,
                "gaze_y": gaze_y,
                "gaze_angle": np.degrees(np.arctan2(gaze_y, gaze_x))
            }
            
        except Exception as e:
            print(f"❌ Error analyzing gaze direction: {e}")
            return {"gaze_x": 0, "gaze_y": 0, "gaze_angle": 0}
    
    async def _analyze_head_pose(self, landmarks) -> Dict[str, float]:
        """Analyze head pose from face landmarks"""
        try:
            # Key points for head pose estimation
            nose_tip = landmarks.landmark[1]
            chin = landmarks.landmark[175]
            left_ear = landmarks.landmark[234]
            right_ear = landmarks.landmark[454]
            
            # Calculate head rotation (simplified)
            ear_center_x = (left_ear.x + right_ear.x) / 2
            nose_offset = nose_tip.x - ear_center_x
            
            # Calculate head tilt
            head_tilt = np.degrees(np.arctan2(chin.y - nose_tip.y, chin.x - nose_tip.x))
            
            return {
                "rotation": np.clip(nose_offset * 100, -45, 45),
                "tilt": head_tilt,
                "up_down": (chin.y - nose_tip.y) * 100
            }
            
        except Exception as e:
            print(f"❌ Error analyzing head pose: {e}")
            return {"rotation": 0, "tilt": 0, "up_down": 0}
    
    async def _check_looking_away(self, landmarks, gaze_direction: Dict[str, float]) -> bool:
        """Check if person is looking away from screen"""
        try:
            gaze_angle = abs(gaze_direction.get("gaze_angle", 0))
            gaze_x = abs(gaze_direction.get("gaze_x", 0))
            
            # Check if gaze angle exceeds threshold
            if gaze_angle > self.looking_away_angle_threshold:
                return True
            
            # Check if horizontal gaze is too far off-center
            if gaze_x > 0.3:  # Looking too far left or right
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking looking away: {e}")
            return False
    
    async def _handle_face_absence(self, current_time: float) -> FaceAnalysis:
        """Handle face absence and calculate duration"""
        if self.face_absence_start is None:
            self.face_absence_start = current_time
        
        absence_duration = current_time - (self.face_absence_start or current_time)
        
        return FaceAnalysis(
            face_detected=False,
            looking_away=False,
            face_absence_duration=absence_duration,
            confidence=0.0
        )
    
    async def get_face_count(self, frame: np.ndarray) -> int:
        """Get number of faces detected"""
        if not self.loaded or self.face_mesh is None:
            return 0
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.face_mesh.process(rgb_frame)
            )
            
            return len(results.multi_face_landmarks) if results.multi_face_landmarks else 0
            
        except Exception as e:
            print(f"❌ Error counting faces: {e}")
            return 0
    
    def is_loaded(self) -> bool:
        """Check if face tracker is loaded"""
        return self.loaded and self.face_mesh is not None
    
    async def cleanup(self):
        """Cleanup resources"""
        async with self.tracker_lock:
            if self.face_mesh is not None:
                self.face_mesh.close()
                self.face_mesh = None
            self.loaded = False
            self.last_face_time = None
            self.face_absence_start = None
            print("🧹 Face tracker cleaned up")
    
    def get_tracker_info(self) -> Dict[str, Any]:
        """Get tracker information"""
        return {
            "loaded": self.loaded,
            "max_faces": self.max_faces,
            "min_detection_confidence": self.min_detection_confidence,
            "min_tracking_confidence": self.min_tracking_confidence,
            "looking_away_angle_threshold": self.looking_away_angle_threshold,
            "face_absence_threshold_seconds": self.face_absence_threshold_seconds
        }
