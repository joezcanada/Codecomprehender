"""LLM service for structured documentation generation using LangChain."""

from typing import Type
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
import logging
import os

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.0")),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", "{system_instructions}"), ("human", "{user_input}")]
        )

    def invoke(
        self, response_model: Type[BaseModel], system_instructions: str, user_input: str
    ) -> BaseModel:
        try:
            chain = self.prompt | self.llm.with_structured_output(response_model)
            return chain.invoke(
                {
                    "system_instructions": system_instructions,
                    "user_input": user_input,
                }
            )
        except Exception as e:
            logger.error(f"Failed to generate structured documentation: {e}")
            raise
