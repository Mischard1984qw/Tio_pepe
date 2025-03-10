"""Voice processing agent for the Tío Pepe system."""

from typing import Dict, Any
import logging
import speech_recognition as sr
from gtts import gTTS
import os

class VoiceAgent:
    """Specialized agent for voice processing tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.recognizer = sr.Recognizer()

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a voice task based on its type."""
        task_type = task.get('voice_type')
        
        if not task_type:
            raise ValueError("No voice task type provided")

        try:
            if task_type == 'speech_to_text':
                return self._speech_to_text(task)
            elif task_type == 'text_to_speech':
                return self._text_to_speech(task)
            else:
                raise ValueError(f"Unsupported voice task type: {task_type}")

        except Exception as e:
            self.logger.error(f"Voice processing error: {str(e)}")
            raise

    def _speech_to_text(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert speech from an audio file to text."""
        audio_path = task.get('audio_path')
        if not audio_path:
            raise ValueError("No audio path provided")

        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return {'text': text}
        except Exception as e:
            self.logger.error(f"Speech to text error: {str(e)}")
            raise

    def _text_to_speech(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert text to speech and save as audio file."""
        text = task.get('text')
        output_path = task.get('output_path')
        language = task.get('language', 'en')

        if not text or not output_path:
            raise ValueError("Text and output path are required")

        try:
            tts = gTTS(text=text, lang=language)
            tts.save(output_path)
            return {
                'output_path': output_path,
                'duration': None  # Could be implemented with additional audio analysis
            }
        except Exception as e:
            self.logger.error(f"Text to speech error: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Cleanup resources used by the agent."""
        self.logger.info("Voice agent cleaned up")