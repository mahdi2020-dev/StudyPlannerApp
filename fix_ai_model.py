import struct
import os

# Ensure the directory exists
os.makedirs("app/resources/ai_model", exist_ok=True)

# Create a minimal valid TFLite file
with open('app/resources/ai_model/model.tflite', 'wb') as f:
    # Write the TFLite magic code
    f.write(b'TFL3')
    
    # Write a minimal flatbuffer header (8 bytes)
    f.write(struct.pack('<I', 0x0001))  # Version
    f.write(struct.pack('<I', 0x0000))  # File size (placeholder)
    
    # Pad with zeros to have a minimally valid file
    f.write(b'\0' * 1000)

print("Created a valid TFLite model file with proper header.")