"""Natural Language Processing agent for the Tío Pepe system."""

from typing import Dict, Any
import logging
from transformers import pipeline
from tools.llm_client import LLMClient

class NLPAgent:
    """Specialized agent for natural language processing tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.models = {}
        self.llm_client = LLMClient()
        self._initialize_models()

    def _initialize_models(self) -> None:
        """Initialize the required NLP models."""
        try:
            # Initialize sentiment analysis pipeline
            self.models['sentiment'] = pipeline('sentiment-analysis')
            
            # Initialize text generation pipeline
            self.models['generation'] = pipeline('text-generation')
            
            # Initialize text classification pipeline
            self.models['classification'] = pipeline('text-classification')
            
            self.logger.info("NLP models initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing NLP models: {str(e)}")

    def process_task(self, task: Any) -> Dict[str, Any]:
        """Process an NLP task based on its type."""
        task_type = task.data.get('nlp_type')
        text = task.data.get('text')

        if not text:
            raise ValueError("No text provided for processing")

        if task_type == 'sentiment':
            return self._analyze_sentiment(text)
        elif task_type == 'generation':
            return self._generate_text(text)
        elif task_type == 'classification':
            return self._classify_text(text)
        else:
            raise ValueError(f"Unsupported NLP task type: {task_type}")

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment of the given text."""
        try:
            result = self.models['sentiment'](text)
            return {'sentiment': result[0]}
        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {str(e)}")
            raise

    async def _generate_text(self, prompt: str) -> Dict[str, Any]:
        """Generate text based on the given prompt using LLM services."""
        try:
            generated_text = await self.llm_client.generate_text(prompt)
            if generated_text is None:
                raise Exception("Failed to generate text from LLM services")
            return {'generated_text': generated_text}
        except Exception as e:
            self.logger.error(f"Text generation error: {str(e)}")
            raise

    def _classify_text(self, text: str) -> Dict[str, Any]:
        """Classify the given text."""
        try:
            result = self.models['classification'](text)
            return {'classification': result[0]}
        except Exception as e:
            self.logger.error(f"Text classification error: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Cleanup resources used by the agent."""
        self.models.clear()
        self.logger.info("NLP agent cleaned up")