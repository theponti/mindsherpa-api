import uuid
from datetime import datetime
from typing import Any, List, Optional, Tuple

import pydantic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.schema import AgentAction
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.tools import tool
from typing_extensions import Dict, TypedDict

from src.data.db import SessionLocal
from src.data.focus_repository import create_focus_items, search_focus_items
from src.data.models.focus import FocusItem, FocusItemBaseV2, FocusState, UserIntentCreateTask
from src.services.file_service import get_file_contents
from src.services.openai_service import openai_chat


class IntentOutput(pydantic.BaseModel):
    function_name: str = pydantic.Field(description="The name of the function to call")
    parameters: Dict[str, Any] = pydantic.Field(description="The parameters to pass to the function")


@tool("create_tasks")
def create_tasks(
    profile_id: uuid.UUID,
    tasks: List[UserIntentCreateTask],
) -> List[FocusItem]:
    """
    This tool is used to create to-do list items for the user.

    This tool should only be used for items that can be completed. Anything else should should
    use the `chat` tool.

    Args:
        profile_id (uuid.UUID): The user's Profile ID
        tasks (List[FocusItemBase]): An array of tasks to be added to the list
    """
    session = SessionLocal()
    created_items = create_focus_items(focus_items=tasks, session=session, profile_id=profile_id)
    return [item.to_model() for item in created_items]


@tool("search_tasks")
def search_tasks(
    keyword: str,
    profile_id: uuid.UUID,
    due_on: Optional[datetime],
    due_after: Optional[datetime],
    due_before: Optional[datetime],
    status: Optional[FocusState],
) -> List[FocusItem]:
    """
    Search for tasks based on a keyword or specific attributes.

    Args:
        keyword (str): The keyword to search for tasks
        profile_id (uuid.UUID): The user's Profile ID
        due_on (Optional[datetime]): The due date in ISO Date Time Format for the task. Example: "2023-01-01T12:00" | None
        due_after (Optional[datetime]): A ISO Date Time Format date used when the users wants to search for tasks after a specific date. Example: "2023-01-01T12:00" | None
        due_before (Optional[datetime]): A ISO Date Time Format date used when the users wants to search for tasks before a specific date. Example: "2023-01-01T12:00" | None
        status (Optional[FocusState]): The status of the task
    """
    focus_items = search_focus_items(
        keyword=keyword,
        due_on=due_on,
        due_after=due_after,
        due_before=due_before,
        status=status,
        profile_id=profile_id,
    )

    return [focus_item.to_model() for focus_item in focus_items]


@tool("edit_task")
def edit_task(task_query: str, new_task_name: str, new_due_date: str, new_status: str) -> bool:
    """
    Edit an existing task in a task list

    Args:
        task_query (str): The task query to search for the task to be edited
        new_task_name (str): The new name or description of the task
        new_due_date (str): The new due date in ISO Date Time Format for the task
        new_status (str): The updated status of the task
    """
    return True


@tool("chat")
def start_chat(user_message: str) -> str:
    """
    This tool is used to begin a chat with the user.

    This should be used if the user says something that does not match any of the other tools.

    Args:
        user_message (str): The user's message
    """
    return user_message


def get_user_intent(user_input: str, profile_id: uuid.UUID) -> Dict[str, Any]:
    system_prompt = get_file_contents("src/services/user_intent/user_intent_prompt.md")
    tools = [create_tasks, search_tasks, edit_task, start_chat]
    chat_prompt = ChatPromptTemplate(
        [
            SystemMessagePromptTemplate.from_template(
                template=system_prompt,
            ),
            (
                "human",
                ("Profile ID: {profile_id} \n\n" + "Today's Date: {current_date} \n\n" + "{user_input}"),
            ),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(openai_chat, tools, chat_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
    )
    result = agent_executor.invoke(
        {
            "profile_id": profile_id,
            "user_input": user_input,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        }
    )
    return result


class SearchIntentParameters(pydantic.BaseModel):
    keyword: str
    profile_id: uuid.UUID
    due_on: Optional[datetime] | None = pydantic.Field(
        None, description="The due date in ISO Date Time Format for the task"
    )
    due_after: Optional[datetime] | None = pydantic.Field(
        None,
        description="A ISO Date Time Format date used when the users wants to search for tasks after a specific date",
    )
    due_before: Optional[datetime] | None = pydantic.Field(
        None,
        description="A ISO Date Time Format date used when the users wants to search for tasks before a specific date",
    )
    status: Optional[str] | None = pydantic.Field(None, description="The status of the task")


class SearchIntentsResponse(pydantic.BaseModel):
    input: SearchIntentParameters
    output: List[FocusItem]


def get_search_tasks(intermediate_steps) -> SearchIntentsResponse | None:
    search_tasks: List[Tuple[AgentAction, List[FocusItem]]] = list(
        filter(lambda x: x[0].tool == "search_tasks", intermediate_steps)
    )

    if len(search_tasks) == 0:
        return None

    search_task = search_tasks[0]
    if search_task[0].tool_input is None:
        return None

    return SearchIntentsResponse(
        input=search_task[0].tool_input,  # type: ignore
        output=search_tasks[0][1],
    )


class CreateTasksParameters(TypedDict):
    profile_id: uuid.UUID
    tasks: List[FocusItemBaseV2]


class CreateIntentsResponse(pydantic.BaseModel):
    input: CreateTasksParameters
    output: List[FocusItem]


def get_create_tasks(intermediate_steps) -> CreateIntentsResponse | None:
    create_tasks: List[Tuple[AgentAction, List[FocusItem]]] = list(
        filter(lambda x: x[0].tool == "create_tasks", intermediate_steps)
    )

    if len(create_tasks) == 0:
        return None

    create_task = create_tasks[0]
    if create_task[0].tool_input is None:
        return None

    return CreateIntentsResponse(
        input={
            "tasks": create_task[0].tool_input["tasks"],  # type: ignore
            "profile_id": create_task[0].tool_input["profile_id"],  # type: ignore
        },
        output=create_tasks[0][1],
    )


class ChatParameters(TypedDict):
    user_message: str


class ChatResponse(pydantic.BaseModel):
    input: ChatParameters
    output: str


def get_chat_tool_call(intermediate_steps) -> ChatResponse | None:
    chat_calls: List[Tuple[AgentAction, str]] = list(
        filter(lambda x: x[0].tool == "chat", intermediate_steps)
    )

    if len(chat_calls) == 0:
        return None

    create_task = chat_calls[0]
    if create_task[0].tool_input is None:
        return None

    return ChatResponse(
        input=create_task[0].tool_input,  # type: ignore
        output=chat_calls[0][1],
    )


class GeneratedIntentsResponse(pydantic.BaseModel):
    input: str | None
    output: str | None
    chat: ChatResponse | None
    create: CreateIntentsResponse | None
    search: SearchIntentsResponse | None


def generate_intent_result(intent) -> GeneratedIntentsResponse:
    steps = intent["intermediate_steps"]
    output = intent["output"]
    search_output = get_search_tasks(steps)

    return GeneratedIntentsResponse(
        input=intent["user_input"],
        output=output,
        chat=get_chat_tool_call(steps),
        create=get_create_tasks(steps),
        search=search_output,
    )
