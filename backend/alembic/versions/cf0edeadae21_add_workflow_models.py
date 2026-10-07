"""Add workflow models

Revision ID: cf0edeadae21
Revises: a8d8e58a74e5
Create Date: 2026-10-07 19:36:01.552651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf0edeadae21'
down_revision: Union[str, Sequence[str], None] = 'a8d8e58a74e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('workflow_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('workflow_type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('entity_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('workflow_step_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_run_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('step_type', sa.String(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('is_automatic', sa.Boolean(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('attempt_count', sa.Integer(), nullable=True),
        sa.Column('max_attempts', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('output_reference_type', sa.String(), nullable=True),
        sa.Column('output_reference_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['workflow_run_id'], ['workflow_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('workflow_approvals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_step_run_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('requested_at', sa.DateTime(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.Column('comments', sa.String(), nullable=True),
        sa.Column('reviewer', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['workflow_step_run_id'], ['workflow_step_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('workflow_approvals')
    op.drop_table('workflow_step_runs')
    op.drop_table('workflow_runs')
