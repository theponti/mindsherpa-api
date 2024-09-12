import json
from datetime import datetime
from typing import Annotated, Any, List, Optional

import pydantic
from fastapi.params import Form
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import Dict

from src.data.models.focus import FocusItemBase
from src.services.file_service import get_file_contents
from src.services.openai_service import openai_chat


class CreateTasksParameters(BaseModel):
    tasks: List[FocusItemBase]


class CreateTasksFunction(BaseModel):
    name: str = Field("create_tasks", description="Create a new list of tasks")
    description: str = Field("Create a new list of tasks")
    parameters: CreateTasksParameters = Field(..., description="An array of tasks to be added to the list")


class SearchTasksParameters(BaseModel):
    keyword: str = Field(..., description="Keyword to search for in task names or descriptions")
    due_before: Optional[datetime] = Field(
        None, description="Filter tasks that are due before a specific date"
    )
    status: Optional[str] = Field(
        None, description="Filter tasks by their current status", enum=["pending", "completed", "in-progress"]
    )


class SearchTasksFunction(BaseModel):
    name: str = Field(
        "search_tasks", description="Search for tasks based on a keyword or specific attributes"
    )
    description: str = Field("Search for tasks based on a keyword or specific attributes")
    parameters: SearchTasksParameters


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


class Intent(BaseModel):
    function_name: str = Field(description="The name of the function to call")
    parameters: CreateTasksParameters | SearchTasksParameters | EditTaskParameters = Field(
        description="The parameters to pass to the function"
    )


class Intents(BaseModel):
    intents: List[Intent]


user_intent_examples = [
    {
        "input": "I have to go to the grocery store and buy milk.",
        "output": json.dumps(
            [
                {
                    "name": "create_tasks",
                    "parameters": {
                        "tasks": [
                            {
                                "name": "Go to the grocery store",
                                "type": "task",
                                "task_size": "small",
                                "text": "Go to the grocery store",
                                "category": "shopping",
                                "priority": 1,
                                "sentiment": "neutral",
                                "due_date": None,
                            },
                            {
                                "type": "task",
                                "task_size": "small",
                                "text": "Buy milk",
                                "category": "shopping",
                                "priority": 1,
                                "sentiment": "neutral",
                                "due_date": None,
                            },
                        ],
                    },
                }
            ]
        ),
    },
    {
        "input": "Remind me to call mom tomorrow.",
        "output": json.dumps(
            [
                {
                    "name": "create_tasks",
                    "parameters": {
                        "tasks": [
                            {
                                "type": "task",
                                "task_size": "small",
                                "text": "Call mom",
                                "category": "personal_development",
                                "priority": 1,
                                "sentiment": "neutral",
                                "due_date": "2024-07-24",
                            }
                        ],
                    },
                }
            ]
        ),
    },
    {
        "input": "I have to go to the grocery store and buy milk, email my boss, and check my email for updates.",
        "output": json.dumps(
            [
                {
                    "name": "create_tasks",
                    "parameters": {
                        "tasks": [
                            {
                                "type": "task",
                                "task_size": "small",
                                "text": "Buy groceries",
                                "category": "shopping",
                                "priority": 1,
                                "sentiment": "neutral",
                                "due_date": None,
                            },
                            {
                                "type": "task",
                                "task_size": "small",
                                "text": "Finish report",
                                "category": "personal_development",
                                "priority": 1,
                                "sentiment": "neutral",
                                "due_date": "2024-07-24",
                            },
                        ],
                    },
                },
                {"name": "search_tasks", "parameters": {"keyword": "email"}},
            ]
        ),
    },
    {
        "input": "What do I need to do today?",
        "output": json.dumps([{"name": "search_tasks", "parameters": {"due_on": "2024-07-24"}}]),
    },
    {
        "input": "What tasks are due this week?",
        "output": json.dumps([{"name": "search_tasks", "parameters": {"due_before": "2024-07-31"}}]),
    },
    {
        "input": "What's the status of my report?",
        "output": json.dumps([{"name": "search_tasks", "parameters": {"keyword": "report"}}]),
    },
    {
        "input": "When is my dentist appointment?",
        "output": json.dumps([{"name": "search_tasks", "parameters": {"keyword": "dentist"}}]),
    },
    {
        "input": "Change the due date of my report to Friday.",
        "output": json.dumps(
            [{"name": "edit_task", "parameters": {"task_query": "report", "new_due_date": "2024-07-24"}}]
        ),
    },
    {
        "input": "Mark the groceries as done.",
        "output": json.dumps(
            [{"name": "edit_task", "parameters": {"task_query": "groceries", "new_status": "completed"}}]
        ),
    },
]


class IntentOutput(pydantic.BaseModel):
    function_name: str = pydantic.Field(description="The name of the function to call")
    parameters: Dict[str, Any] = pydantic.Field(description="The parameters to pass to the function")


class IntentsResponse(pydantic.BaseModel):
    intents: List[IntentOutput]


def get_user_intent(user_input: Annotated[str, Form()]) -> IntentsResponse:
    system_prompt = get_file_contents("src/routers/user_intent/user_intent_prompt.md")
    openai_chat.bind_tools(
        [
            CreateTasksFunction,
            SearchTasksFunction,
            EditTaskFunction,
        ]
    )

    parser = JsonOutputParser(pydantic_object=Intents)
    chat_prompt = ChatPromptTemplate(
        [
            SystemMessagePromptTemplate.from_template(
                template=system_prompt,
                partial_variables={
                    "format_instructions": parser.get_format_instructions(),
                },
            ),
            FewShotChatMessagePromptTemplate(
                example_prompt=ChatPromptTemplate(
                    [
                        ("human", "{input}"),
                        ("ai", "{output}"),
                    ]
                ),
                examples=user_intent_examples,
            ),
            ("human", "Today's Date: {current_date} \n\n {user_input}"),
        ]
    )

    chain = (
        {
            "user_input": RunnablePassthrough(),
            "current_date": RunnablePassthrough(),
        }
        | chat_prompt
        | openai_chat
        | parser
    )

    result = chain.invoke({"user_input": user_input, "current_date": datetime.now().strftime("%Y-%m-%d")})
    intents: List[Intent] | None = result["intents"]

    if intents is None:
        return IntentsResponse(intents=[])

    return IntentsResponse(intents=[IntentOutput(**intent) for intent in intents])  # type: ignore