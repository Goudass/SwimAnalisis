"""Dziennik treningowy: sesje, serie, powtórzenia (HR, laktat, czas)

Revision ID: b7e2a1c9d4f3
Revises: 4418e77d069d
Create Date: 2026-05-11

"""
from alembic import op
import sqlalchemy as sa


revision = "b7e2a1c9d4f3"
down_revision = "4418e77d069d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "training_session",
        sa.Column("id_session", sa.Integer(), nullable=False),
        sa.Column("id_club", sa.Integer(), nullable=False),
        sa.Column("id_user", sa.Integer(), nullable=False),
        sa.Column("id_created_by", sa.Integer(), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("training_type", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_club"], ["club.id_club"]),
        sa.ForeignKeyConstraint(["id_user"], ["user.id_user"]),
        sa.ForeignKeyConstraint(["id_created_by"], ["user.id_user"]),
        sa.PrimaryKeyConstraint("id_session"),
    )
    op.create_table(
        "training_block",
        sa.Column("id_block", sa.Integer(), nullable=False),
        sa.Column("id_session", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("distance_m", sa.Integer(), nullable=True),
        sa.Column("planned_repetitions", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_session"], ["training_session.id_session"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_block"),
    )
    op.create_table(
        "training_rep",
        sa.Column("id_rep", sa.Integer(), nullable=False),
        sa.Column("id_block", sa.Integer(), nullable=False),
        sa.Column("rep_index", sa.Integer(), nullable=False),
        sa.Column("time_seconds", sa.Float(), nullable=True),
        sa.Column("formatted_time", sa.String(length=24), nullable=True),
        sa.Column("heart_rate", sa.Integer(), nullable=True),
        sa.Column("lactate_mmol", sa.Float(), nullable=True),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["id_block"], ["training_block.id_block"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_rep"),
        sa.UniqueConstraint("id_block", "rep_index", name="uq_training_rep_block_index"),
    )


def downgrade():
    op.drop_table("training_rep")
    op.drop_table("training_block")
    op.drop_table("training_session")
