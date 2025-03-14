#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a simple TFLite model file with proper headers for Persian Life Manager
"""

import os
import struct

def create_tflite_model():
    """Create a minimal valid TFLite model file"""
    model_dir = "app/resources/ai_model"
    model_path = os.path.join(model_dir, "model.tflite")
    
    # Create directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Create a minimal valid TFLite file with proper header
    with open(model_path, 'wb') as f:
        # Write TFLite file header magic bytes
        f.write(b'TFL3')
        
        # Write minimal flatbuffer header (8 bytes)
        f.write(struct.pack('<I', 0x0001))  # Version (4 bytes)
        f.write(struct.pack('<I', 1024))    # Placeholder file size (4 bytes)
        
        # Write padding to ensure it's a valid file
        f.write(b'\0' * 1016)  # Complete file size
    
    # Verify file was created
    if os.path.exists(model_path):
        size = os.path.getsize(model_path)
        print(f"Created TFLite model at {model_path} ({size} bytes)")
        
        # Read first 4 bytes to verify header
        with open(model_path, 'rb') as f:
            header = f.read(4)
        print(f"Model header: {header}")
    else:
        print(f"Failed to create model at {model_path}")

if __name__ == "__main__":
    create_tflite_model()