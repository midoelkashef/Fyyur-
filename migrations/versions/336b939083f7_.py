"""empty message

Revision ID: 336b939083f7
Revises: 0ada50b904dd
Create Date: 2020-07-17 21:28:50.060440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '336b939083f7'
down_revision = '0ada50b904dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_image_link', sa.String(length=500), nullable=True))
    op.add_column('Show', sa.Column('artist_name', sa.String(), nullable=True))
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_name'], ['name'])
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_image_link'], ['image_link'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'artist_name')
    op.drop_column('Show', 'artist_image_link')
    # ### end Alembic commands ###
