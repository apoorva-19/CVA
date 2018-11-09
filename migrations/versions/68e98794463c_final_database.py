"""final database

Revision ID: 68e98794463c
Revises: 
Create Date: 2018-11-05 23:04:45.036558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68e98794463c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('factory_stalk_collection',
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('date_request', sa.Date(), nullable=True),
    sa.Column('date_fulfilment', sa.Date(), nullable=True),
    sa.Column('bales_stalk', sa.Integer(), nullable=True),
    sa.Column('no_trucks', sa.Integer(), nullable=True),
    sa.Column('amt_received', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('request_id')
    )
    op.create_table('farmer',
    sa.Column('farmer_id', sa.String(length=20), nullable=False),
    sa.Column('farmer_name', sa.String(length=40), nullable=True),
    sa.Column('farm_size', sa.Integer(), nullable=True),
    sa.Column('contact_no', sa.String(length=10), nullable=True),
    sa.Column('adhaar', sa.String(length=12), nullable=True),
    sa.Column('village_name', sa.String(length=20), nullable=True),
    sa.Column('district_name', sa.String(length=25), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('request_harvest', sa.Integer(), server_default='0', nullable=True),
    sa.PrimaryKeyConstraint('farmer_id')
    )
    op.create_table('gram_panchayat',
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=True),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.Column('contact_no', sa.String(length=10), nullable=True),
    sa.Column('email_id', sa.String(length=50), nullable=True),
    sa.Column('village_name', sa.String(length=20), nullable=True),
    sa.Column('district_name', sa.String(length=25), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.PrimaryKeyConstraint('username')
    )
    op.create_table('harvest_aider',
    sa.Column('aider_id', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=270), nullable=True),
    sa.Column('name', sa.String(length=40), nullable=True),
    sa.Column('contact_no', sa.String(length=10), nullable=True),
    sa.Column('district', sa.String(length=20), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('no_villages', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('aider_id')
    )
    op.create_table('harvest_equipment',
    sa.Column('equip_id', sa.String(length=20), nullable=False),
    sa.Column('available', sa.Integer(), server_default='0', nullable=True),
    sa.Column('name_equip', sa.String(length=30), nullable=True),
    sa.Column('type_equip', sa.String(length=20), nullable=True),
    sa.Column('manufac_cmp', sa.String(length=30), nullable=True),
    sa.Column('year_of_purchase', sa.Integer(), nullable=True),
    sa.Column('last_servicing', sa.Date(), nullable=True),
    sa.Column('next_servicing', sa.Date(), nullable=True),
    sa.Column('servicing_comp', sa.String(length=25), nullable=True),
    sa.Column('contact_person', sa.String(length=40), nullable=True),
    sa.Column('contact_number', sa.String(length=10), nullable=True),
    sa.Column('hours_completed_today', sa.Integer(), server_default='0', nullable=True),
    sa.PrimaryKeyConstraint('equip_id')
    )
    op.create_table('patwari',
    sa.Column('patwari_id', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=True),
    sa.Column('patwari_name', sa.String(length=40), nullable=True),
    sa.Column('district_name', sa.String(length=20), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('contact_no', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('patwari_id')
    )
    op.create_table('stalk_collector',
    sa.Column('collector_id', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=True),
    sa.Column('collector_name', sa.String(length=40), nullable=True),
    sa.Column('contact_no', sa.String(length=10), nullable=True),
    sa.Column('district_name', sa.String(length=25), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('hours_of_work', sa.Integer(), server_default='0', nullable=True),
    sa.Column('hours_completed_today', sa.Integer(), server_default='0', nullable=True),
    sa.PrimaryKeyConstraint('collector_id')
    )
    op.create_table('request_harvest',
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('requestor_id', sa.String(length=20), nullable=True),
    sa.Column('no_farmers', sa.Integer(), nullable=True),
    sa.Column('date_request', sa.Date(), nullable=True),
    sa.Column('jobs_completed', sa.Integer(), server_default='0', nullable=True),
    sa.ForeignKeyConstraint(['requestor_id'], ['gram_panchayat.username'], ),
    sa.PrimaryKeyConstraint('request_id')
    )
    op.create_table('request_user_id',
    sa.Column('new_user_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('req_gen_id', sa.String(length=20), nullable=True),
    sa.Column('no_gen', sa.Integer(), nullable=True),
    sa.Column('req_complete', sa.Integer(), server_default='0', nullable=True),
    sa.ForeignKeyConstraint(['req_gen_id'], ['gram_panchayat.username'], ),
    sa.PrimaryKeyConstraint('new_user_id')
    )
    op.create_table('job_list',
    sa.Column('job_no', sa.String(length=15), nullable=False),
    sa.Column('date_job', sa.Date(), nullable=True),
    sa.Column('time', sa.Time(), nullable=True),
    sa.Column('collector_id', sa.String(length=20), nullable=True),
    sa.Column('equip_id', sa.String(length=20), nullable=True),
    sa.Column('farmer_id', sa.String(length=20), nullable=True),
    sa.Column('request_id', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=250), nullable=True),
    sa.Column('farm_size', sa.Integer(), nullable=True),
    sa.Column('fees', sa.Integer(), nullable=True),
    sa.Column('expected_duration', sa.Float(), nullable=True),
    sa.Column('bales_collected', sa.Integer(), server_default='0', nullable=True),
    sa.Column('job_complete', sa.Integer(), server_default='0', nullable=True),
    sa.ForeignKeyConstraint(['collector_id'], ['stalk_collector.collector_id'], ),
    sa.ForeignKeyConstraint(['equip_id'], ['harvest_equipment.equip_id'], ),
    sa.ForeignKeyConstraint(['farmer_id'], ['farmer.farmer_id'], ),
    sa.ForeignKeyConstraint(['request_id'], ['request_harvest.request_id'], ),
    sa.PrimaryKeyConstraint('job_no')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job_list')
    op.drop_table('request_user_id')
    op.drop_table('request_harvest')
    op.drop_table('stalk_collector')
    op.drop_table('patwari')
    op.drop_table('harvest_equipment')
    op.drop_table('harvest_aider')
    op.drop_table('gram_panchayat')
    op.drop_table('farmer')
    op.drop_table('factory_stalk_collection')
    # ### end Alembic commands ###
