from enum import Enum

from src.services.file_service import get_file_contents


class AvailablePrompts(Enum):
    v1 = "user_input_formatter_v1.md"
    v2 = "user_input_formatter_v2.md"
    v3 = "user_input_formatter_v3.md"


def get_prompt(prompt: AvailablePrompts):
    return get_file_contents(f"src/prompts/{prompt.value}")
