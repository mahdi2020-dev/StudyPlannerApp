"""
Speech to Text conversion service for Persian Life Manager
"""
import os
import base64
import logging
import tempfile
from openai import OpenAI

logger = logging.getLogger(__name__)

class SpeechToTextService:
    """Service for converting speech to text and text to speech"""
    
    def __init__(self):
        """Initialize the service"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)
        logger.info("Speech-to-Text Service initialized")
        
    def transcribe_audio(self, audio_base64, language="fa"):
        """Transcribe audio to text using OpenAI Whisper API
        
        Args:
            audio_base64 (str): Base64 encoded audio data
            language (str, optional): Language code. Defaults to "fa" (Persian).
            
        Returns:
            str: Transcribed text
        """
        if not self.api_key:
            return "متأسفانه، در حال حاضر دسترسی به سرویس تبدیل صدا به متن امکان‌پذیر نیست."
        
        try:
            # Save base64 audio to a temporary file
            audio_data = base64.b64decode(audio_base64)
            
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(audio_data)
            
            # Transcribe using OpenAI Whisper API
            with open(temp_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {str(e)}")
            return None
    
    def text_to_speech(self, text, voice="alloy"):
        """Convert text to speech using OpenAI TTS API
        
        Args:
            text (str): Text to convert to speech
            voice (str, optional): Voice to use. Defaults to "alloy".
            
        Returns:
            str: Base64 encoded audio data
        """
        if not self.api_key:
            return None
        
        try:
            # Use OpenAI TTS API
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Get binary audio data
            audio_data = response.content
            
            # Encode as base64
            return base64.b64encode(audio_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            return None