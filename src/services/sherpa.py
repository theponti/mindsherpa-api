from datetime import datetime
from typing import List

import pydantic
from langchain.pydantic_v1 import BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough

from src.data.models.focus import FocusItemBase, FocusItemBaseV2
from src.services.groq_service import groq_chat
from src.services.prompt_service import AvailablePrompts, get_prompt
from src.utils.generation_statistics import GenerationStatistics
from src.utils.logger import logger


def log_usage(model: str, usage):
    statistics_to_return = GenerationStatistics(
        input_time=int(usage.prompt_time) if usage.prompt_time else 0,
        output_time=(int(usage.completion_time) if usage.completion_time else 0),
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        total_time=int(usage.total_time) if usage.total_time else 0,
        model_name=model,
    )
    logger.info("focus_stats", statistics_to_return.get_stats())


class ProcessUserInputResponse(BaseModel):
    items: List[FocusItemBase]


class ProcessUserInputResponseV2(pydantic.BaseModel):
    items: List[FocusItemBaseV2]


def process_user_input(user_input: str) -> ProcessUserInputResponseV2:
    """
    Process user input and return a list of focus items

    **Args:**
    - user_input (str): User input

    **Returns:**
    - LLMFocusOutput: List of focus items
    """
    try:
        # 👇 Create LLM output parser
        parser = JsonOutputParser(pydantic_object=ProcessUserInputResponse)

        # 👇 Create LLM prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    template=get_prompt(AvailablePrompts.v4),
                    partial_variables={"format_instructions": parser.get_format_instructions()},
                ),
                ("human", "{user_input}"),
            ]
        )

        # 👇 Create the LLM chain
        chain = {"user_input": RunnablePassthrough()} | prompt | groq_chat | parser

        # 👇 Get the LLM response
        llm_response = chain.invoke(
            {"user_input": f"Current Date: {datetime.now().strftime('%A %B %d, %Y')}\n\n{user_input}"}
        )

        return ProcessUserInputResponseV2(items=[FocusItemBaseV2(**item) for item in llm_response["items"]])
    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        raise e
