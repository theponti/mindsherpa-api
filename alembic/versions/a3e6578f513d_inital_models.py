"""inital models

Revision ID: a3e6578f513d
Revises: 001_create_uuid_ossp
Create Date: 2024-08-05 13:13:19.961363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3e6578f513d'
down_revision: Union[str, None] = '001_create_uuid_ossp'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('profiles',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('provider', sa.String(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('refresh_tokens',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('revoked', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('chats',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('context',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entities',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('attributes', sa.String(), nullable=True),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('memories',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('importance', sa.Float(), nullable=True),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('last_accessed', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notes',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('queues',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('system_state',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('current_focus', sa.String(), nullable=True),
    sa.Column('mood', sa.String(), nullable=True),
    sa.Column('parameters', sa.String(), nullable=True),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('actions',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('queue_id', sa.UUID(), nullable=True),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('deadline', sa.DateTime(), nullable=True),
    sa.Column('result', sa.String(), nullable=True),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.ForeignKeyConstraint(['queue_id'], ['queues.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entity_memories',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=True),
    sa.Column('memory_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ),
    sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('memory_tags',
    sa.Column('memory_id', sa.UUID(), nullable=True),
    sa.Column('tag_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], )
    )
    op.create_table('messages',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('chat_id', sa.UUID(), nullable=True),
    sa.Column('profile_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('note_tags',
    sa.Column('note_id', sa.UUID(), nullable=True),
    sa.Column('tag_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], )
    )
    op.create_table('relationships',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('entity1_id', sa.UUID(), nullable=True),
    sa.Column('entity2_id', sa.UUID(), nullable=True),
    sa.Column('relationship_type', sa.String(), nullable=False),
    sa.Column('strength', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['entity1_id'], ['entities.id'], ),
    sa.ForeignKeyConstraint(['entity2_id'], ['entities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('relationships')
    op.drop_table('note_tags')
    op.drop_table('messages')
    op.drop_table('memory_tags')
    op.drop_table('entity_memories')
    op.drop_table('actions')
    op.drop_table('tags')
    op.drop_table('system_state')
    op.drop_table('queues')
    op.drop_table('notes')
    op.drop_table('memories')
    op.drop_table('entities')
    op.drop_table('context')
    op.drop_table('chats')
    op.drop_table('refresh_tokens')
    op.drop_table('profiles')
    op.drop_table('users')
    # ### end Alembic commands ###