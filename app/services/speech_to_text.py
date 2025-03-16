"""
Speech to Text conversion service for Persian Life Manager
"""

import logging
import os
import tempfile
import base64
from openai import OpenAI

logger = logging.getLogger(__name__)

class SpeechToTextService:
    """Service for converting speech to text and text to speech"""
    
    def __init__(self):
        """Initialize the service"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def transcribe_audio(self, audio_base64, language="fa"):
        """Transcribe audio to text using OpenAI Whisper API
        
        Args:
            audio_base64 (str): Base64 encoded audio data
            language (str, optional): Language code. Defaults to "fa" (Persian).
            
        Returns:
            str: Transcribed text
        """
        try:
            # Decode base64 to binary
            audio_data = base64.b64decode(audio_base64)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # Transcribe using OpenAI
            with open(tmp_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return "خطا در تبدیل صدا به متن. لطفاً دوباره تلاش کنید."
    
    def text_to_speech(self, text, voice="alloy"):
        """Convert text to speech using OpenAI TTS API
        
        Args:
            text (str): Text to convert to speech
            voice (str, optional): Voice to use. Defaults to "alloy".
            
        Returns:
            str: Base64 encoded audio data
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                response.stream_to_file(tmp_file.name)
                tmp_file_path = tmp_file.name
            
            # Read and encode as base64
            with open(tmp_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
            return base64.b64encode(audio_data).decode("utf-8")
            
        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            return None