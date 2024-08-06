from typing import Optional
import strawberry


@strawberry.type
class Goal:
    priority_grade: int
    value: str
    sentiment: str
    goal_id: str


@strawberry.type
class ActionMetadata:
    location: Optional[str] = None
    timeframe: Optional[str] = None
    current_expenses: Optional[str] = None
    goal_timeframe: Optional[str] = None
    belief: Optional[str] = None


@strawberry.type
class Action:
    type: Optional[str] = None
    value: Optional[str] = None
    sentiment: Optional[str] = None
    goal_id: Optional[str] = None
    metadata: ActionMetadata | None = None


@strawberry.type
class Belief:
    type: Optional[str] = None
    value: Optional[str] = None
    sentiment: Optional[str] = None


@strawberry.type
class Preference:
    type: Optional[str] = None
    value: Optional[str] = None
    sentiment: Optional[str] = None


@strawberry.type
class Location:
    type: Optional[str] = None
    value: Optional[str] = None
    location_type: Optional[str] = None
    country: Optional[str] = None


@strawberry.type
class Date:
    type: Optional[str] = None
    value: Optional[str] = None
    action: Optional[str] = None


@strawberry.type
class Focus:
    vision: Optional[str] = None
    goals: list[Goal]
    actions: list[Action]
    beliefs: list[Belief]
    preferences: list[Preference]
    locations: list[Location]
    dates: list[Date]


def convert_dict_to_focus(data):
    return Focus(
        vision=data["vision"],
        goals=[Goal(**goal) for goal in data["goals"]],
        actions=[Action(**action) for action in data["actions"]],
        beliefs=[Belief(**belief) for belief in data["beliefs"]],
        preferences=[Preference(**preference) for preference in data["preferences"]],
        locations=[Location(**location) for location in data["locations"]],
        dates=[Date(**date) for date in data["dates"]],
    )
