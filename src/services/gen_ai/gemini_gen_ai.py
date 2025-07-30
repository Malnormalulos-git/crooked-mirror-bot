import logging

from google import genai

from config_reader import config
from src.services.gen_ai.gen_ai import GenAI


class GeminiGenAI(GenAI):
    _client: genai.Client | None

    @classmethod
    def _get_client(cls) -> genai.Client:
        """Get or create Gemini client instance"""
        if cls._client is None:
            cls._client = genai.Client(api_key=config.llm_api_key)
        return cls._client

    def rephrase_post(self, text: str, additional_instructions: str | None = None) -> str:
        if not text.strip():
            logging.warning("Empty text provided for rephrasing")
            return ""

        try:
            client = self._get_client()

            prompt = config.text_rephrasing_prompt.format(additional_instructions, text)

            response = client.models.generate_content(
                model=config.gemini_model,
                contents=prompt
            )

            if not response.text:
                logging.error("Empty response from Gemini API")
                return ""

            return response.text
        except Exception as e:
            logging.error(f"Error while rephrasing post with Gemini API: {e}")
            return ''
