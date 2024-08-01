from enum import Enum
import json
from src.utils.ai_models import open_source_models
from src.services.file_service import get_file_contents
from src.utils.logger import logger
from src.utils.generation_statistics import GenerationStatistics
from src.services.groq_service import groq_client


class AvailablePrompts(Enum):
    v1 = "user_input_formatter_v1.md"
    v2 = "user_input_formatter_v2.md"


def get_prompt(prompt: AvailablePrompts):
    return get_file_contents(f"src/prompts/{prompt.value}")


def analyze_user_input(transcript: str, model: str = "llama3-70b-8192"):
    system_prompt = get_prompt(AvailablePrompts.v2)

    if model in open_source_models:

        try:
            completion = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": transcript,
                        # This should be the actual paragraph from which tasks need to be extracted
                    },
                ],
                temperature=0.3,
                max_tokens=8000,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None,
            )

            usage = completion.usage
            # print("------ USAGE ---", usage)

        except Exception as e:
            logger.error(f" ********* API error ********: {e} ***** ")
            return None, {"error": str(e)}

        try:
            if usage:
                statistics_to_return = GenerationStatistics(
                    input_time=int(usage.prompt_time) if usage.prompt_time else 0,
                    output_time=(
                        int(usage.completion_time) if usage.completion_time else 0
                    ),
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens,
                    total_time=int(usage.total_time) if usage.total_time else 0,
                    model_name=model,
                )
                logger.info("focus_stats", statistics_to_return.get_stats())

                return (
                    json.loads(completion.choices[0].message.content)
                    if completion.choices[0].message.content
                    else None
                )
        except Exception as e:
            logger.error(f" ********* STATISTICS GENERATION error ******* : {e} ")
            return None, {"error": str(e)}
