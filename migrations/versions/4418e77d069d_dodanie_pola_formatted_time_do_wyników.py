"""Dodanie pola formatted_time do wyników

Revision ID: 4418e77d069d
Revises: 05cca7a92b0f
Create Date: 2025-02-04 01:26:16.519724

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String

# revision identifiers, used by Alembic.
revision = '4418e77d069d'
down_revision = '05cca7a92b0f'
branch_labels = None
depends_on = None


def upgrade():
    # ### Dodanie kolumny formatted_time z domyślną wartością "" ###
    with op.batch_alter_table('result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('formatted_time', sa.String(length=10), nullable=True, server_default=""))

    # Tworzenie obiektu tabeli "result" do aktualizacji danych
    result_table = table('result',
        column('id_result', sa.Integer),
        column('distance_time', sa.Float),
        column('formatted_time', String(length=10))
    )

    # Aktualizacja istniejących danych: konwersja distance_time na MM:SS.SS
    connection = op.get_bind()
    results = connection.execute(sa.select(result_table.c.id_result, result_table.c.distance_time)).fetchall()

    for result in results:
        id_result = result.id_result
        total_seconds = result.distance_time
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        formatted_time = f"{minutes}:{seconds:05.2f}" if minutes > 0 else f"{seconds:.2f}"

        # Aktualizacja rekordu
        connection.execute(
            result_table.update()
            .where(result_table.c.id_result == id_result)
            .values(formatted_time=formatted_time)
        )

    # Po aktualizacji ustawiamy kolumnę formatted_time na NOT NULL
    with op.batch_alter_table('result', schema=None) as batch_op:
        batch_op.alter_column('formatted_time', nullable=False)


def downgrade():
    # Cofnięcie zmian – usunięcie kolumny formatted_time
    with op.batch_alter_table('result', schema=None) as batch_op:
        batch_op.drop_column('formatted_time')
