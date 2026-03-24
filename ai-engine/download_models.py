#!/usr/bin/env python3
"""
Download AI models for Cognivigil AI Engine
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO


def create_models_directory():
    """Create models directory if it doesn't exist"""
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    print(f"✅ Models directory created/verified: {models_dir.absolute()}")
    return models_dir


def download_yolo_model():
    """Download YOLOv8 model"""
    print("🤖 Downloading YOLOv8 model...")
    
    try:
        # Download YOLOv8n (nano) model - smallest and fastest
        model = YOLO('yolov8n.pt')
        
        # The model will be downloaded automatically to default location
        # Let's copy it to our models directory
        default_model_path = Path.home() / '.ultralytics' / 'models' / 'yolov8n.pt'
        target_model_path = Path("./models/yolov8n.pt")
        
        if default_model_path.exists():
            import shutil
            shutil.copy2(default_model_path, target_model_path)
            print(f"✅ YOLOv8 model copied to: {target_model_path.absolute()}")
        else:
            # Force download by creating a model instance
            model = YOLO('yolov8n.pt')
            print(f"✅ YOLOv8 model downloaded and available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading YOLO model: {e}")
        return False


def verify_models():
    """Verify that required models are present"""
    models_dir = Path("./models")
    required_files = ["yolov8n.pt"]
    
    print("🔍 Verifying models...")
    
    all_present = True
    for file_name in required_files:
        file_path = models_dir / file_name
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✅ {file_name} - {size_mb:.1f} MB")
        else:
            print(f"❌ {file_name} - Missing")
            all_present = False
    
    return all_present


def test_model_loading():
    """Test if models can be loaded successfully"""
    print("🧪 Testing model loading...")
    
    try:
        # Test YOLO model
        yolo_path = "./models/yolov8n.pt"
        if Path(yolo_path).exists():
            model = YOLO(yolo_path)
            print(f"✅ YOLO model loaded successfully")
            print(f"   Model classes: {len(model.names)}")
            print(f"   Target classes: {[name for name in model.names.values() if name in ['person', 'cell phone', 'book', 'laptop']]}")
            return True
        else:
            print(f"❌ YOLO model file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False


def print_model_info():
    """Print information about the models"""
    print("\n📊 Model Information:")
    print("=" * 50)
    
    try:
        model = YOLO('./models/yolov8n.pt')
        
        print(f"🤖 YOLOv8n Model:")
        print(f"   - Size: Nano (smallest, fastest)")
        print(f"   - Classes: {len(model.names)}")
        print(f"   - Input size: 640x640")
        print(f"   - Expected FPS: 30+ (CPU), 100+ (GPU)")
        
        print(f"\n🎯 Target Detection Classes:")
        target_classes = ['person', 'cell phone', 'book', 'laptop', 'mouse', 'phone', 'tablet', 'notebook', 'paper']
        available_classes = [name for name in model.names.values() if name in target_classes]
        print(f"   Available: {available_classes}")
        
    except Exception as e:
        print(f"❌ Error getting model info: {e}")


def main():
    """Main function"""
    print("🚀 Cognivigil AI Engine - Model Setup")
    print("=" * 50)
    
    # Create models directory
    models_dir = create_models_directory()
    
    # Change to models directory for downloads
    os.chdir(models_dir)
    
    # Download models
    success = download_yolo_model()
    
    if not success:
        print("❌ Failed to download models")
        sys.exit(1)
    
    # Verify models
    if not verify_models():
        print("❌ Model verification failed")
        sys.exit(1)
    
    # Test model loading
    if not test_model_loading():
        print("❌ Model loading test failed")
        sys.exit(1)
    
    # Print model info
    print_model_info()
    
    print("\n✅ Model setup complete!")
    print("=" * 50)
    print("🎯 Ready to start AI Engine:")
    print("   python app/main.py")
    print("   Or: uvicorn app.main:app --host 0.0.0.0 --port 8001")


if __name__ == "__main__":
    main()
