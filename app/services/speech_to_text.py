"""
Speech to Text conversion service for Persian Life Manager
"""
import os
import base64
import io
import logging
import tempfile
from openai import OpenAI

logger = logging.getLogger(__name__)

class SpeechToTextService:
    """Service for converting speech to text and text to speech"""
    
    def __init__(self):
        """Initialize the service"""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.client = None
        
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully for Speech-to-Text")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client for Speech-to-Text: {str(e)}")
                self.client = None
    
    def transcribe_audio(self, audio_base64, language="fa"):
        """Transcribe audio to text using OpenAI Whisper API
        
        Args:
            audio_base64 (str): Base64 encoded audio data
            language (str, optional): Language code. Defaults to "fa" (Persian).
            
        Returns:
            str: Transcribed text
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        try:
            # Decode base64 to binary
            audio_data = base64.b64decode(audio_base64)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                temp_file_name = temp_file.name
                temp_file.write(audio_data)
            
            # Transcribe using OpenAI
            with open(temp_file_name, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            # Clean up the temporary file
            os.unlink(temp_file_name)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def text_to_speech(self, text, voice="alloy"):
        """Convert text to speech using OpenAI TTS API
        
        Args:
            text (str): Text to convert to speech
            voice (str, optional): Voice to use. Defaults to "alloy".
            
        Returns:
            str: Base64 encoded audio data
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Get the audio data as bytes
            audio_data = io.BytesIO()
            for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                audio_data.write(chunk)
            audio_data.seek(0)
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_data.read()).decode('utf-8')
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            return None