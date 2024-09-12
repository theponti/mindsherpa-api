import json

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
