import logging

import google.genai as genai

from config_reader import config
from src.services.gen_ai.gen_ai import GenAI


class GeminiGenAI(GenAI):
    __client: genai.Client | None = None

    @staticmethod
    def __get_client() -> genai.Client:
        """Get or create Gemini client instance"""
        if GeminiGenAI.__client is None:
            GeminiGenAI.__client = genai.Client(api_key=config.llm_api_key)
        return GeminiGenAI.__client

    def rephrase_post(self, text: str, additional_instructions: str | None = None) -> str:
        if not text.strip():
            logging.warning("Empty text provided for rephrasing")
            return ""

        try:
            client = GeminiGenAI.__get_client()

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
