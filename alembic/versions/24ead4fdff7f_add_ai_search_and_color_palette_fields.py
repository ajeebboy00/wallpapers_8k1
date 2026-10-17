"""add_ai_search_and_color_palette_fields

Revision ID: 24ead4fdff7f
Revises: b989a6d2804f
Create Date: 2026-09-29 19:19:25.017670

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '24ead4fdff7f'
down_revision: Union[str, None] = 'b989a6d2804f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pg_trgm extension for fast trigram and fuzzy text search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2. Add visual search and AI discovery columns
    op.add_column('wallpapers', sa.Column('dominant_color', sa.String(length=7), nullable=True))
    op.add_column('wallpapers', sa.Column('color_palette', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('wallpapers', sa.Column('perceptual_hash', sa.String(length=64), nullable=True))
    op.add_column('wallpapers', sa.Column('ai_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('wallpapers', sa.Column('ai_description', sa.Text(), nullable=True))
    op.add_column(
        'wallpapers',
        sa.Column('is_ai_generated', sa.Boolean(), server_default=sa.text('false'), nullable=False)
    )

    # 3. Create B-tree indexes
    op.create_index('ix_wallpapers_dominant_color', 'wallpapers', ['dominant_color'], unique=False)
    op.create_index('ix_wallpapers_perceptual_hash', 'wallpapers', ['perceptual_hash'], unique=False)
    op.create_index('ix_wallpapers_is_ai_generated', 'wallpapers', ['is_ai_generated'], unique=False)

    # 4. Create GIN Trigram indexes for high-speed fuzzy search
    op.execute("CREATE INDEX IF NOT EXISTS ix_wallpapers_title_trgm ON wallpapers USING gin (title gin_trgm_ops);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_wallpapers_description_trgm ON wallpapers USING gin (description gin_trgm_ops);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_wallpapers_description_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_wallpapers_title_trgm;")
    op.drop_index('ix_wallpapers_is_ai_generated', table_name='wallpapers')
    op.drop_index('ix_wallpapers_perceptual_hash', table_name='wallpapers')
    op.drop_index('ix_wallpapers_dominant_color', table_name='wallpapers')
    op.drop_column('wallpapers', 'is_ai_generated')
    op.drop_column('wallpapers', 'ai_description')
    op.drop_column('wallpapers', 'ai_tags')
    op.drop_column('wallpapers', 'perceptual_hash')
    op.drop_column('wallpapers', 'color_palette')
    op.drop_column('wallpapers', 'dominant_color')
