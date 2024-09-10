import json
from datetime import datetime
from typing import Annotated, Any, List, Optional

from fastapi.params import Form
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import Dict

from src.services.file_service import get_file_contents
from src.services.groq_service import groq_chat


class Intent(BaseModel):
    function_name: str = Field(description="The name of the function to call")
    parameters: Dict[str, Any] = Field(description="The parameters to pass to the function")


class Intents(BaseModel):
    intents: List[Intent]


class Task(BaseModel):
    task_name: str = Field(..., description="The name or description of the task")
    due_date: Optional[datetime] = Field(None, description="The optional due date for the task")
    related_tasks: Optional[List[str]] = Field(None, description="The name of the related tasks")


class CreateTasksParameters(BaseModel):
    tasks: List[Task] = Field(..., description="An array of tasks to be added to the list")


class CreateTasksFunction(BaseModel):
    name: str = Field("create_tasks", description="Create a new list of tasks")
    description: str = Field("Create a new list of tasks")
    parameters: CreateTasksParameters


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


user_intent_examples = [
    {
        "input": "I have to go to the grocery store and buy milk, email my boss, and check my email for updates.",
        "output": json.dumps(
            [
                {
                    "name": "create_tasks",
                    "parameters": {
                        "tasks": [
                            {"task_name": "Buy groceries"},
                            {"task_name": "Finish report", "due_date": "2024-07-24"},
                        ]
                    },
                },
                {"name": "search_tasks", "parameters": {"keyword": "email"}},
            ]
        ),
    },
    {
        "input": "Who I need to do today?",
        "output": json.dumps([{"name": "search_tasks", "parameters": {"due_before": "2024-07-24"}}]),
    },
    {
        "input": "Current Date: 2024-07-24 \n What tasks are due this week?",
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
        "input": "Remind me to call mom tomorrow.",
        "output": json.dumps(
            [
                {
                    "name": "create_tasks",
                    "parameters": {"tasks": [{"task_name": "Call mom", "due_date": "2024-07-24"}]},
                }
            ]
        ),
    },
    {
        "input": "Change the due date of my report to Friday.",
        "output": json.dumps(
            [{"name": "edit_task", "parameters": {"task_query": "report_id", "new_due_date": "2024-07-24"}}]
        ),
    },
    {
        "input": "Mark the groceries as done.",
        "output": json.dumps(
            [{"name": "edit_task", "parameters": {"task_id": "groceries_id", "new_status": "completed"}}]
        ),
    },
    {
        "input": "I have to go to the grocery store and buy milk.",
        "output": json.dumps(
            [
                {
                    "name": "create_tasks",
                    "parameters": {
                        "tasks": [
                            {"task_name": "Go to the grocery store"},
                            {"task_name": "Buy milk", "related_tasks": ["Go to the grocery store"]},
                        ]
                    },
                }
            ]
        ),
    },
]


system_prompt = get_file_contents("src/routers/user_intent/user_intent_prompt.md")


def get_user_intent(user_input: Annotated[str, Form()]) -> Intents:
    groq_chat.bind_tools(
        [
            CreateTasksFunction,
            SearchTasksFunction,
            EditTaskFunction,
        ]
    )

    structured_llm = groq_chat.with_structured_output(Intents)

    # Define the prompt template
    chat_prompt = ChatPromptTemplate(
        [
            ("system", system_prompt),
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
        | structured_llm
    )

    result = chain.invoke({"user_input": user_input, "current_date": datetime.now().strftime("%Y-%m-%d")})
    intents: List[Intent] | None = getattr(result, "intents", None)

    if intents is None:
        return Intents(intents=[])

    return Intents(intents=intents)
