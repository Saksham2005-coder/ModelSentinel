"""add symbol dependencies

Revision ID: a8d8e58a74e5
Revises: 5a96859dc921
Create Date: 2026-10-07 17:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a8d8e58a74e5'
down_revision = '5a96859dc921'
branch_labels = None
depends_on = None

def upgrade():
    # We add columns for symbol-level tracking
    op.add_column('repository_dependencies', sa.Column('source_symbol_name', sa.String(), nullable=True))
    op.add_column('repository_dependencies', sa.Column('target_symbol_name', sa.String(), nullable=True))
    op.add_column('repository_dependencies', sa.Column('resolved_target_symbol_id', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_repository_dependencies_source_symbol_name'), 'repository_dependencies', ['source_symbol_name'], unique=False)
    op.create_index(op.f('ix_repository_dependencies_target_symbol_name'), 'repository_dependencies', ['target_symbol_name'], unique=False)
    # SQLite alter table ADD CONSTRAINT FOREIGN KEY is tricky. Usually we rely on logical foreign keys or explicit alter if dialect supports.
    # We just define the columns for now. If using postgres, we can create the FK. We'll skip formal FK for SQLite compatibility and use application-level logic.

def downgrade():
    op.drop_index(op.f('ix_repository_dependencies_target_symbol_name'), table_name='repository_dependencies')
    op.drop_index(op.f('ix_repository_dependencies_source_symbol_name'), table_name='repository_dependencies')
    op.drop_column('repository_dependencies', 'resolved_target_symbol_id')
    op.drop_column('repository_dependencies', 'target_symbol_name')
    op.drop_column('repository_dependencies', 'source_symbol_name')
