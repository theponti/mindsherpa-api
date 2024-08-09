import json
from typing import List
from sqlalchemy.orm import Session

from src.data.models.focus import Focus
from src.services.prompt_service import AvailablePrompts, get_prompt
from src.services.groq_service import groq_client
from src.utils.ai_models import open_source_models
from src.utils.logger import logger
from src.utils.generation_statistics import GenerationStatistics


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


def generate_user_context(
    transcript: str,
    session: Session,
    model: str = "llama3-70b-8192",
) -> List[Focus] | None:
    system_prompt = get_prompt(AvailablePrompts.v3)

    if model in open_source_models:
        try:
            completion = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript},
                ],
                temperature=0.3,
                max_tokens=8000,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None,
            )

            if completion.usage:
                log_usage(model, completion.usage)
        except Exception as e:
            logger.error(f" ********* API error ********: {e} ***** ")
            return None

        try:
            created_items = []
            if completion.choices[0].message.content:
                formatted: dict = json.loads(completion.choices[0].message.content)

                for item in formatted["items"]:
                    create_item = Focus(
                        type=item["type"],
                        state=item["state"],
                        task_size=item["task_size"],
                        text=item["text"],
                        category=item["category"],
                        priority=item["priority"],
                        sentiment=item["sentiment"],
                        due_date=item["due_date"],
                        profile_id=item["profile_id"],
                        created_at=item["created_at"],
                        updated_at=item["updated_at"],
                    )
                    session.add(create_item)
                    created_items.append(create_item)

                session.commit()
                return created_items
        except Exception as e:
            logger.error(f" ********* STATISTICS GENERATION error ******* : {e} ")
            return None
