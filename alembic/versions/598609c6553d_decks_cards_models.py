"""decks_cards_models

Revision ID: 598609c6553d
Revises: 0b32a17d1242
Create Date: 2026-02-24 17:02:01.613737

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '598609c6553d'
down_revision: Union[str, Sequence[str], None] = '0b32a17d1242'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('tokens_user_id_fkey', 'tokens', type_='foreignkey')
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE UUID USING id::uuid")
    op.execute("ALTER TABLE tokens ALTER COLUMN id TYPE UUID USING id::uuid")
    op.execute("ALTER TABLE tokens ALTER COLUMN user_id TYPE UUID USING user_id::uuid")

    op.create_table('decks',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False, default=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decks_user_id'), 'decks', ['user_id'], unique=False)
    op.create_table('cards',
    sa.Column('term', sa.String(), nullable=False),
    sa.Column('definition', sa.String(), nullable=False),
    sa.Column('deck_id', sa.Uuid(), nullable=False),
    sa.Column('additional_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cards_deck_id'), 'cards', ['deck_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_cards_deck_id'), table_name='cards')
    op.drop_table('cards')
    op.drop_index(op.f('ix_decks_user_id'), table_name='decks')
    op.drop_table('decks')

    op.execute("ALTER TABLE tokens ALTER COLUMN user_id TYPE VARCHAR(255) USING user_id::text")
    op.execute("ALTER TABLE tokens ALTER COLUMN id TYPE VARCHAR(255) USING id::text")
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE VARCHAR(255) USING id::text")