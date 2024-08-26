"""set chat state to string

Revision ID: 5c4454081178
Revises: e790245feccb
Create Date: 2024-08-23 11:04:12.916176

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c4454081178"
down_revision: Union[str, None] = "e790245feccb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "chats",
        "state",
        existing_type=postgresql.ENUM("ACTIVE", "INACTIVE", "ENDED", name="chatstate"),
        type_=sa.String(),
        existing_nullable=False,
        existing_server_default=sa.text("'ACTIVE'::chatstate"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "chats",
        "state",
        existing_type=sa.String(),
        type_=postgresql.ENUM("ACTIVE", "INACTIVE", "ENDED", name="chatstate"),
        existing_nullable=False,
        existing_server_default=sa.text("'ACTIVE'::chatstate"),
    )
    # ### end Alembic commands ###
