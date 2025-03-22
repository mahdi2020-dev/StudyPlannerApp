#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hugging Face API Service for Persian Life Manager Application
This module provides a service for interacting with Hugging Face API
to enable AI features even without OpenAI API access.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

class HuggingFaceService:
    """Service for interacting with Hugging Face API"""
    
    def __init__(self):
        """Initialize the Hugging Face Service"""
        self.api_key = os.environ.get("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models"
        self.default_model = "mistralai/Mistral-7B-Instruct-v0.2"  # Good alternative to GPT models
        self.vision_model = "llava-hf/llava-1.5-7b-hf"  # For multimodal (text+image) tasks
        self.speech_model = "openai/whisper-large-v3"  # For speech to text
        
        # Check if the API key is valid (not a dummy key)
        if self.api_key and (self.api_key.startswith("sk_dummy") or self.api_key.startswith("hf_dummy")):
            logger.warning("Using dummy Hugging Face API key - AI features will be disabled")
            self.api_key = None
    
    def is_available(self) -> bool:
        """Check if the Hugging Face API is available
        
        Returns:
            bool: True if the API is available, False otherwise
        """
        return self.api_key is not None
    
    def query_model(self, 
                   prompt: str, 
                   model: Optional[str] = None,
                   system_prompt: Optional[str] = None,
                   max_tokens: int = 800,
                   temperature: float = 0.7) -> Optional[str]:
        """Query the Hugging Face model with a prompt
        
        Args:
            prompt (str): The user prompt
            model (str, optional): Model to use. Defaults to None (will use default_model).
            system_prompt (str, optional): System prompt for instruct models. Defaults to None.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 800.
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
            
        Returns:
            Optional[str]: The generated text, or None if an error occurred
        """
        if not self.is_available():
            logger.warning("Hugging Face API key not available - cannot query model")
            return None
        
        model_id = model or self.default_model
        url = f"{self.api_url}/{model_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload based on whether system prompt is provided
        if system_prompt:
            # Format for instruction models that support system prompts
            payload = {
                "inputs": {
                    "system": system_prompt,
                    "prompt": prompt
                },
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        else:
            # Simple format for models that don't support system prompts
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Handle different response formats from different models
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                else:
                    return str(result[0])
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
            else:
                return str(result)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying Hugging Face model: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in query_model: {str(e)}")
            return None
    
    def query_vision_model(self, 
                          prompt: str,
                          image_path: str,
                          max_tokens: int = 800) -> Optional[str]:
        """Query a vision model with text and image
        
        Args:
            prompt (str): Text prompt describing what to analyze in the image
            image_path (str): Path to the image file
            max_tokens (int, optional): Maximum tokens to generate. Defaults to 800.
            
        Returns:
            Optional[str]: The generated description, or None if an error occurred
        """
        if not self.is_available():
            logger.warning("Hugging Face API key not available - cannot query vision model")
            return None
        
        url = f"{self.api_url}/{self.vision_model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            # Read the image file
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Create a multipart/form-data request with both text and image
            files = {
                "file": image_data,
            }
            data = {
                "inputs": prompt,
                "parameters": json.dumps({
                    "max_new_tokens": max_tokens,
                    "return_full_text": False
                })
            }
            
            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                else:
                    return str(result[0])
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
            else:
                return str(result)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying vision model: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in query_vision_model: {str(e)}")
            return None
    
    def speech_to_text(self, audio_file_path: str, language: str = "fa") -> Optional[str]:
        """Convert speech to text using Hugging Face API
        
        Args:
            audio_file_path (str): Path to the audio file
            language (str, optional): Language code (e.g., "fa" for Persian). Defaults to "fa".
            
        Returns:
            Optional[str]: Transcribed text, or None if an error occurred
        """
        if not self.is_available():
            logger.warning("Hugging Face API key not available - cannot convert speech to text")
            return None
        
        url = f"{self.api_url}/{self.speech_model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            # Read the audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Create form-data with the audio file and language parameter
            files = {
                "file": audio_data,
            }
            data = {
                "language": language
            }
            
            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract the transcribed text
            if isinstance(result, dict) and "text" in result:
                return result["text"]
            else:
                return str(result)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in speech to text conversion: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in speech_to_text: {str(e)}")
            return None
    
    def get_chat_response(self, 
                         messages: List[Dict[str, str]],
                         system_message: Optional[str] = None,
                         max_tokens: int = 800) -> Optional[str]:
        """Get a response from the chat model
        
        Args:
            messages (List[Dict[str, str]]): List of message objects with role and content
            system_message (str, optional): System message for the conversation. Defaults to None.
            max_tokens (int, optional): Maximum tokens to generate. Defaults to 800.
            
        Returns:
            Optional[str]: The response text, or None if an error occurred
        """
        if not self.is_available():
            logger.warning("Hugging Face API key not available - cannot get chat response")
            return None
        
        try:
            # Format the conversation into a prompt for the model
            prompt = ""
            if system_message:
                prompt += f"System: {system_message}\n\n"
            
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                # Format based on role
                if role == "system":
                    # System messages were already handled at the beginning
                    continue
                elif role == "user":
                    prompt += f"Human: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
                else:
                    # Unknown role, skip
                    continue
            
            # Add final prompt for the assistant
            prompt += "Assistant: "
            
            # Query the model
            return self.query_model(
                prompt=prompt,
                model="mistralai/Mistral-7B-Instruct-v0.2",  # Mistral is great for conversation
                max_tokens=max_tokens,
                temperature=0.7
            )
                
        except Exception as e:
            logger.error(f"Error in get_chat_response: {str(e)}")
            return None