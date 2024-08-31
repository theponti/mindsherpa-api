import uuid
from typing import Annotated, List, Optional, Required

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from pydantic.fields import Field
from sqlalchemy.orm import Session

from src.data.context import get_user_context
from src.data.models.chat import Message
from src.data.models.focus import get_focus_by_profile_id
from src.services.groq_service import groq_chat
from src.services.prompt_service import AvailablePrompts, get_prompt
from src.types.llm_output_types import LLMFocusOutput
from src.utils.generation_statistics import GenerationStatistics
from src.utils.hotdate import convert_due_date
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


def process_user_input(user_input: str) -> LLMFocusOutput:
    """
    Process user input and return a list of focus items

    **Args:**
    - user_input (str): User input

    **Returns:**
    - LLMFocusOutput: List of focus items
    """
    try:
        # 👇 Create output parser
        parser = JsonOutputParser(pydantic_object=LLMFocusOutput)

        # 👇 Create prompt template
        prompt_template = PromptTemplate(
            template=get_prompt(AvailablePrompts.v4),
            input_variables=["user_input"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # 👇 Create the LLM chain
        chain = prompt_template | groq_chat | parser

        # 👇 Get the LLM response
        llm_response = chain.invoke({"user_input": user_input})

        print(llm_response)
        # 👇 Convert due dates use `hotdate`
        with_due_dates = []
        for item in llm_response["items"]:
            if item["due_date"] and item["due_date"] != "None":
                item["due_date"] = convert_due_date(item["due_date"])
            with_due_dates.append(item)

        return LLMFocusOutput(items=with_due_dates)
    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        raise e


class SherpaResponseMetadata(BaseModel):
    user_query_category: str
    related_context_items: List[str] = Field(
        default_factory=list,
        description="List of User Context items that are related to the user query.",
    )


class SherpaResponse(BaseModel):
    message: str
    metadata: Optional[SherpaResponseMetadata] = None


def get_sherpa_response(
    session: Session, message: str, chat_id: uuid.UUID, profile_id: uuid.UUID
) -> SherpaResponse | None:
    try:
        system_prompt = get_prompt(AvailablePrompts.SherpaChatResponse)
        user_context = get_user_context(session, profile_id=profile_id)

        # Create the LLM chain
        parser = JsonOutputParser(pydantic_object=SherpaResponse)
        prompt_template = PromptTemplate(
            template=system_prompt,
            input_variables=["user_context", "chat_history"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Get the LLM response
        chain = prompt_template | groq_chat
        llm_response = chain.invoke(
            {
                "chat_history": "\n".join(user_context.chat_history),
                "user_context": "\n".join(user_context.note_history),
                "user_input": message,
            }
        )

        logger.info("LLM Metadata", llm_response.response_metadata)
        if isinstance(llm_response.content, str):
            try:
                parsed = parser.parse(llm_response.content)
                print(parsed["metadata"])
                return SherpaResponse(message=parsed["message"], metadata=parsed["metadata"])
            except Exception as e:
                return SherpaResponse(message=llm_response.content)
        else:
            raise Exception("LLM Response is not a string")
    except Exception as e:
        logger.error(f"Generating sherpa response: {e}")
        raise e


def get_chat_summary(
    chat_id: Annotated[uuid.UUID, Required],
    profile_id: Annotated[uuid.UUID, Required],
    session: Annotated[Session, Required],
) -> LLMFocusOutput | None:
    messages = session.query(Message).filter(Message.chat_id == chat_id).all()
    existing_focus_items = get_focus_by_profile_id(profile_id=profile_id, session=session)
    transcript = """
    Analyze the chat transcript. Do not include any existing items in the focus list.

    ### Existing Items
    {existing_items}

    ### Chat Transcript
    {chat_history}
    """.format(
        existing_items="\n".join([f"{item.type}: {item.text}" for item in existing_focus_items]),
        chat_history="\n".join([f"{message.role}: {message.message}" for message in messages]),
    )
    return process_user_input(user_input=transcript)
