"""
Speech to Text conversion service for Persian Life Manager using Hugging Face
"""
import os
import base64
import io
import logging
import tempfile
import requests

logger = logging.getLogger(__name__)

class SpeechToTextServiceHF:
    """Service for converting speech to text using Hugging Face"""
    
    def __init__(self):
        """Initialize the service"""
        self.api_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.model = "facebook/wav2vec2-large-960h" # Good base model for English
        self.farsi_model = "m3hrdadfi/wav2vec2-large-xlsr-persian" # Persian-specific model
        
        if not self.api_key:
            logger.warning("Hugging Face API key not found in any environment variable (HUGGINGFACE_API_KEY, XAI_API_KEY, or OPENAI_API_KEY)")
        else:
            logger.info("Hugging Face client initialized successfully for Speech-to-Text")
    
    def transcribe_audio(self, audio_base64, language="fa"):
        """Transcribe audio to text using Hugging Face
        
        Args:
            audio_base64 (str): Base64 encoded audio data
            language (str, optional): Language code. Defaults to "fa" (Persian).
            
        Returns:
            str: Transcribed text
        """
        if not self.api_key:
            logger.error("Hugging Face API key not set")
            return None
        
        try:
            # Decode base64 to binary
            audio_data = base64.b64decode(audio_base64)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                temp_file_name = temp_file.name
                temp_file.write(audio_data)
            
            # Read file as binary
            with open(temp_file_name, "rb") as audio_file:
                # Choose model based on language
                selected_model = self.farsi_model if language == "fa" else self.model
                
                # Make API request
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{selected_model}",
                    headers=headers,
                    data=audio_file
                )
                
                # Clean up temp file
                try:
                    os.unlink(temp_file_name)
                except Exception as e:
                    logger.warning(f"Could not delete temporary file: {str(e)}")
                
                # Parse response
                if response.status_code != 200:
                    logger.error(f"Error from Hugging Face API: {response.text}")
                    return "خطا در تبدیل صدا به متن"
                
                result = response.json()
                
                # Extract text from the response
                if isinstance(result, dict) and "text" in result:
                    return result["text"]
                elif isinstance(result, list) and len(result) > 0 and "text" in result[0]:
                    return result[0]["text"]
                else:
                    return str(result)
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return f"خطا در تبدیل صدا به متن: {str(e)}"