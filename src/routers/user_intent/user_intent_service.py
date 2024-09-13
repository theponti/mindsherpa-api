import json
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
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
from typing_extensions import Dict, TypedDict

from src.data.db import SessionLocal
from src.data.focus_repository import create_focus_items, search_focus_items
from src.data.models.focus import FocusItem, FocusItemBase, FocusItemBaseV2, FocusState
from src.services.file_service import get_file_contents
from src.services.openai_service import openai_chat


class EditTaskParameters(BaseModel):
    task_query: str = Field(..., description="A query to search for the task to be edited")
    new_task_name: Optional[str] = Field(None, description="The new name or description of the task")
    new_due_date: Optional[datetime] = Field(None, description="The new due date for the task")
    new_status: Optional[str] = Field(
        None, description="The updated status of the task", enum=["pending", "completed", "in-progress"]
    )


class EditTaskFunction(BaseModel):
    name: str = Field("edit_task", description="Edit an existing task in a task list")
    description: str = Field("Edit an existing task in a task list")
    parameters: EditTaskParameters


class IntentOutput(pydantic.BaseModel):
    function_name: str = pydantic.Field(description="The name of the function to call")
    parameters: Dict[str, Any] = pydantic.Field(description="The parameters to pass to the function")


@tool("create_tasks")
def create_tasks(
    profile_id: uuid.UUID = Field(description="The user's Profile ID"),
    tasks: List[FocusItemBase] = Field(description="An array of tasks to be added to the list"),
) -> List[FocusItem]:
    """
    This tool is used to create to-do list items for the user.

    This tool should only be used for items that can be completed. Anything else should should
    use the `chat` tool.
    """
    session = SessionLocal()
    created_items = create_focus_items(focus_items=tasks, session=session, profile_id=profile_id)
    return [item.to_model() for item in created_items]


@tool("search_tasks")
def search_tasks(
    keyword: str,
    due_on: Optional[datetime],
    due_after: Optional[datetime],
    due_before: Optional[datetime],
    status: Optional[FocusState],
) -> List[FocusItem]:
    """Search for tasks based on a keyword or specific attributes."""
    return search_focus_items(
        keyword=keyword,
        due_on=due_on,
        due_after=due_after,
        due_before=due_before,
        status=status,
    )


@tool("edit_task")
def edit_task(task_query: str, new_task_name: str, new_due_date: str, new_status: str) -> bool:
    """Edit an existing task in a task list"""
    return True


@tool("chat")
def chat(message: str) -> str:
    """
    This tool is used to begin a chat with the user.

    This should be used if the user says something that does not match any of the other tools.
    """
    return message


def get_user_intent(user_input: str, profile_id: uuid.UUID) -> Dict[str, Any]:
    system_prompt = get_file_contents("src/routers/user_intent/user_intent_prompt.md")
    tools = [
        create_tasks,
        search_tasks,
        edit_task,
    ]
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


class SearchIntentParameters(TypedDict):
    keyword: str
    due_on: Optional[datetime]
    due_after: Optional[datetime]
    due_before: Optional[datetime]
    status: Optional[str]


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

    print("input", json.dumps(create_task[0].tool_input, indent=4))
    return CreateIntentsResponse(
        input={
            "tasks": create_task[0].tool_input["tasks"],  # type: ignore
            "profile_id": create_task[0].tool_input["profile_id"],  # type: ignore
        },
        output=create_tasks[0][1],
    )


class GeneratedIntentsResponse(pydantic.BaseModel):
    output: str | None
    create: CreateIntentsResponse | None
    search: SearchIntentsResponse | None


def generate_intent_result(intent) -> GeneratedIntentsResponse:
    steps = intent["intermediate_steps"]
    output = intent["output"]
    search_output = get_search_tasks(steps)

    if search_output and len(search_output.output) > 0:
        output = None

    return GeneratedIntentsResponse(
        output=output,
        create=get_create_tasks(steps),
        search=search_output,
    )
