import base64
import cv2
import numpy as np
from typing import Tuple, Optional
import asyncio


class ImageProcessor:
    """Utility class for image processing operations"""
    
    @staticmethod
    async def decode_base64_frame(frame_data: str) -> np.ndarray:
        """Decode base64 frame to numpy array"""
        try:
            # Remove data URL prefix if present
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            # Decode base64
            decoded = base64.b64decode(frame_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(decoded, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Failed to decode image")
            
            return frame
            
        except Exception as e:
            print(f"❌ Error decoding frame: {e}")
            # Return dummy frame for demo
            return np.zeros((480, 640, 3), dtype=np.uint8)
    
    @staticmethod
    async def encode_frame_to_base64(frame: np.ndarray, format: str = 'jpg') -> str:
        """Encode numpy array frame to base64 string"""
        try:
            success, encoded = cv2.imencode(f'.{format}', frame)
            if not success:
                raise ValueError("Failed to encode image")
            
            # Convert to base64
            base64_str = base64.b64encode(encoded).decode('utf-8')
            
            # Add data URL prefix
            return f"data:image/{format};base64,{base64_str}"
            
        except Exception as e:
            print(f"❌ Error encoding frame: {e}")
            return ""
    
    @staticmethod
    async def resize_frame(frame: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Resize frame to target size"""
        try:
            return cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
        except Exception as e:
            print(f"❌ Error resizing frame: {e}")
            return frame
    
    @staticmethod
    async def normalize_frame(frame: np.ndarray) -> np.ndarray:
        """Normalize frame pixel values to 0-1 range"""
        try:
            return frame.astype(np.float32) / 255.0
        except Exception as e:
            print(f"❌ Error normalizing frame: {e}")
            return frame
    
    @staticmethod
    async def enhance_frame(frame: np.ndarray) -> np.ndarray:
        """Enhance frame quality for better detection"""
        try:
            # Apply basic enhancements
            enhanced = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            
            # Apply denoising
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
            
            return enhanced
            
        except Exception as e:
            print(f"❌ Error enhancing frame: {e}")
            return frame
    
    @staticmethod
    async def crop_face_region(frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Crop face region from frame"""
        try:
            x1, y1, x2, y2 = bbox
            
            # Ensure coordinates are within frame bounds
            h, w = frame.shape[:2]
            x1 = max(0, min(x1, w))
            y1 = max(0, min(y1, h))
            x2 = max(0, min(x2, w))
            y2 = max(0, min(y2, h))
            
            # Crop region
            face_region = frame[y1:y2, x1:x2]
            
            return face_region if face_region.size > 0 else None
            
        except Exception as e:
            print(f"❌ Error cropping face region: {e}")
            return None
    
    @staticmethod
    async def draw_detections(frame: np.ndarray, detections: list) -> np.ndarray:
        """Draw detection bounding boxes on frame"""
        try:
            annotated_frame = frame.copy()
            
            for detection in detections:
                bbox = detection.bbox
                class_name = detection.class_name
                confidence = detection.confidence
                
                x1, y1, x2, y2 = map(int, bbox)
                
                # Draw bounding box
                color = (0, 255, 0) if class_name == 'person' else (0, 0, 255)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - label_size[1] - 10),
                    (x1 + label_size[0], y1),
                    color,
                    -1
                )
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )
            
            return annotated_frame
            
        except Exception as e:
            print(f"❌ Error drawing detections: {e}")
            return frame
    
    @staticmethod
    async def calculate_frame_quality(frame: np.ndarray) -> dict:
        """Calculate frame quality metrics"""
        try:
            # Calculate sharpness (Laplacian variance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast
            contrast = np.std(gray)
            
            # Calculate noise level
            noise = np.std(cv2.absdiff(gray, cv2.GaussianBlur(gray, (5, 5), 0)))
            
            return {
                "sharpness": float(sharpness),
                "brightness": float(brightness),
                "contrast": float(contrast),
                "noise": float(noise),
                "quality_score": float(sharpness * contrast / (noise + 1))
            }
            
        except Exception as e:
            print(f"❌ Error calculating frame quality: {e}")
            return {
                "sharpness": 0.0,
                "brightness": 0.0,
                "contrast": 0.0,
                "noise": 0.0,
                "quality_score": 0.0
            }
    
    @staticmethod
    async def preprocess_for_detection(frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for optimal detection"""
        try:
            # Resize to standard size if needed
            h, w = frame.shape[:2]
            if max(h, w) > 1280:
                scale = 1280 / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                frame = await ImageProcessor.resize_frame(frame, (new_w, new_h))
            
            # Enhance frame
            frame = await ImageProcessor.enhance_frame(frame)
            
            return frame
            
        except Exception as e:
            print(f"❌ Error preprocessing frame: {e}")
            return frame
