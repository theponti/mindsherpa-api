from sqlalchemy.orm import Session
from typing import Annotated, List, Required

from src.data.models import Focus

def get_focus_by_profile_id(
        session: Session,
        profile_id: Annotated[str, Required]
    ) -> List[Focus]:
    return session.query(Focus).filter(Focus.profile_id == profile_id).all()