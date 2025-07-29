import logging

from google import genai

from config_reader import config
from src.services.gen_ai.gen_ai import GenAI


class GeminiGenAI(GenAI):
    __client = genai.Client(api_key=config.llm_api_key)

    def rephrase_post(self, text: str, additional_instructions: str | None = None) -> str:
        try:
            response = GeminiGenAI.__client.models.generate_content(
                model=config.gemini_model,
                contents=config.text_rephrasing_prompt.format(additional_instructions, text)
            )

            return response.text
        except Exception as e:
            logging.error(f"Error while rephrasing post: {e}")
            return ''
