import logging
import os
import time
import json
from typing import Type, TypeVar
from dotenv import load_dotenv
from openai import OpenAI, APIError
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class LiteLLMClient:
    def __init__(self):
        self.api_key = os.getenv("LITELLM_API_KEY")
        if not self.api_key:
            raise ValueError("LITELLM_API_KEY environment variable not set")
            
        self.base_url = os.getenv("LITELLM_BASE_URL", "http://3.110.18.218")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def chat(self, messages, model="gemini-2.5-flash", max_retries=5):
        """Standard chat completion - returns raw text."""
        base_delay = 1
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                return response.choices[0].message.content
            except APIError as e:
                if e.status_code == 429:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise e
        raise Exception("Max retries exceeded")

    def chat_structured(
        self,
        messages,
        response_model: Type[T],
        model="gemini-2.5-flash",
        max_retries=5
    ) -> T:
        """
        Structured chat completion with JSON schema enforcement.
        Returns a validated Pydantic model instance.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            response_model: Pydantic model class defining the expected response structure
            model: LLM model to use
            max_retries: Number of retry attempts for rate limiting
            
        Returns:
            Instance of response_model with validated data
        """
        base_delay = 1
        
        # Generate JSON schema from Pydantic model
        schema = response_model.model_json_schema()
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format={
                        "type": "json_object",
                        "schema": schema
                    }
                )
                content = response.choices[0].message.content
                
                # Parse and validate with Pydantic
                return response_model.model_validate_json(content)
                
            except APIError as e:
                if e.status_code == 429:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                raise ValueError(f"LLM returned invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise e
                
        raise Exception("Max retries exceeded")


llm_client = LiteLLMClient()
