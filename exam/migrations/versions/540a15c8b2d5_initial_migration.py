"""Initial migration

Revision ID: 540a15c8b2d5
Revises: 
Create Date: 2025-06-16 15:34:27.418155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '540a15c8b2d5'
down_revision = None
branch_labels = None
depends_on = None

def populate_with_roles():
    roles_table = sa.sql.table('roles', 
        sa.sql.column('name', sa.String),
        sa.sql.column('description', sa.Text)
    )
    op.bulk_insert(roles_table,
        [
            {'name': 'администратор', 'description': 'Суперпользователь, имеет полный доступ к системе, в том числе к созданию и удалению мероприятий'},
            {'name': 'модератор', 'description': 'Может редактировать данные мероприятий и производить модерацию регистраций'},
            {'name': 'пользователь', 'description': 'Может просматривать информацию и регистрироваться на мероприятия'}
        ]
    )

def populate_with_users():
    from werkzeug.security import generate_password_hash
    
    users_table = sa.sql.table('users',
        sa.sql.column('login', sa.String),
        sa.sql.column('password_hash', sa.String),
        sa.sql.column('last_name', sa.String),
        sa.sql.column('first_name', sa.String),
        sa.sql.column('middle_name', sa.String),
        sa.sql.column('role_id', sa.Integer)
    )
    
    op.bulk_insert(users_table, [
        {
            'login': 'admin',
            'password_hash': generate_password_hash('admin'),
            'last_name': 'Пупкин',
            'first_name': 'Василиск',
            'role_id': 1
        },
        {
            'login': 'moderator1',
            'password_hash': generate_password_hash('moderator123'),
            'last_name': 'Модераторов',
            'first_name': 'Иван',
            'middle_name': 'Петрович',
            'role_id': 2
        },
        {
            'login': 'user1',
            'password_hash': generate_password_hash('user123'),
            'last_name': 'Волонтеров',
            'first_name': 'Анна',
            'middle_name': 'Сергеевна',
            'role_id': 3
        },
        {
            'login': 'user2',
            'password_hash': generate_password_hash('user123'),
            'last_name': 'Активистов',
            'first_name': 'Петр',
            'middle_name': 'Иванович',
            'role_id': 3
        },
        {
            'login': 'organizer1',
            'password_hash': generate_password_hash('organizer123'),
            'last_name': 'Организаторов',
            'first_name': 'Мария',
            'middle_name': 'Александровна',
            'role_id': 2
        }
    ])

def populate_with_events():
    from datetime import datetime, timedelta
    
    events_table = sa.sql.table('events',
        sa.sql.column('name', sa.String),
        sa.sql.column('description', sa.Text),
        sa.sql.column('date', sa.DateTime),
        sa.sql.column('location', sa.String),
        sa.sql.column('volunteer_required', sa.Integer),
        sa.sql.column('image', sa.String),
        sa.sql.column('organizer_id', sa.Integer)
    )
    
    future_date1 = datetime.now() + timedelta(days=30)
    future_date2 = datetime.now() - timedelta(days=45)
    future_date3 = datetime.now() + timedelta(days=60)
    future_date4 = datetime.now() + timedelta(days=15)
    future_date5 = datetime.now() + timedelta(days=75)
    future_date6 = datetime.now() + timedelta(days=90)
    future_date7 = datetime.now() + timedelta(days=45)
    future_date8 = datetime.now() + timedelta(days=120)
    future_date9 = datetime.now() + timedelta(days=20)
    future_date10 = datetime.now() + timedelta(days=105)
    future_date11 = datetime.now() + timedelta(days=25)
    future_date12 = datetime.now() + timedelta(days=80)
    future_date13 = datetime.now() + timedelta(days=35)
    
    op.bulk_insert(events_table, [
        {
            'name': 'Уборка парка "Сокольники"',
            'description': 'Экологическая акция по уборке территории парка. Приглашаем всех желающих принять участие в благоустройстве нашего города.',
            'date': future_date1,
            'location': 'Парк Сокольники, главный вход',
            'volunteer_required': 3,
            'image': 'park_cleanup.jpg',
            'organizer_id': 1
        },
        {
            'name': 'Помощь в детском доме',
            'description': 'Благотворительная акция в детском доме №5. Планируется провести мастер-классы, игры и подарить подарки детям.',
            'date': future_date2,
            'location': 'Детский дом №5, ул. Ленина, 123',
            'volunteer_required': 15,
            'image': 'orphanage_help.jpg',
            'organizer_id': 5
        },
        {
            'name': 'Марафон "Здоровый город"',
            'description': 'Спортивное мероприятие для продвижения здорового образа жизни. Нужны волонтеры для организации старта и финиша.',
            'date': future_date3,
            'location': 'Центральная площадь',
            'volunteer_required': 40,
            'image': 'marathon.jpg',
            'organizer_id': 2
        },
        {
            'name': 'Благотворительная ярмарка',
            'description': 'Ярмарка handmade товаров в поддержку местного приюта для животных. Нужны волонтеры для организации торговых мест.',
            'date': future_date4,
            'location': 'Парк Горького, центральная аллея',
            'volunteer_required': 20,
            'image': 'charity_fair.jpg',
            'organizer_id': 5
        },
        {
            'name': 'Посадка деревьев в городском лесу',
            'description': 'Экологическая акция по восстановлению зеленых насаждений. Присоединяйтесь к созданию более зеленого будущего!',
            'date': future_date5,
            'location': 'Измайловский лес, северная часть',
            'volunteer_required': 50,
            'image': 'tree_planting.jpg',
            'organizer_id': 1
        },
        {
            'name': 'Фестиваль уличного искусства',
            'description': 'Организация творческого фестиваля с мастер-классами по граффити и стрит-арту. Нужны волонтеры для координации.',
            'date': future_date6,
            'location': 'Арт-квартал на Флаконе',
            'volunteer_required': 25,
            'image': 'street_art_festival.jpg',
            'organizer_id': 2
        },
        {
            'name': 'Помощь пожилым людям',
            'description': 'Доставка продуктов и лекарств пожилым людям. Волонтерская программа социальной поддержки.',
            'date': future_date7,
            'location': 'Различные районы города',
            'volunteer_required': 30,
            'image': 'elderly_help.jpg',
            'organizer_id': 5
        },
        {
            'name': 'Фестиваль науки для детей',
            'description': 'Интерактивные научные эксперименты и мастер-классы для школьников. Нужны волонтеры-ведущие.',
            'date': future_date8,
            'location': 'Центр современного искусства',
            'volunteer_required': 35,
            'image': 'science_festival.jpg',
            'organizer_id': 1
        },
        {
            'name': 'Городской субботник',
            'description': 'Массовая уборка улиц и дворов города. Каждый может внести свой вклад в чистоту нашего города.',
            'date': future_date9,
            'location': 'Центральные улицы города',
            'volunteer_required': 100,
            'image': 'city_cleanup.jpg',
            'organizer_id': 2
        },
        {
            'name': 'Книжная ярмарка',
            'description': 'Организация благотворительной ярмарки подержанных книг. Средства пойдут на развитие библиотек.',
            'date': future_date10,
            'location': 'Центральная библиотека',
            'volunteer_required': 15,
            'image': 'book_fair.jpg',
            'organizer_id': 5
        },
        {
            'name': 'Спортивная олимпиада для детей',
            'description': 'Организация спортивных соревнований для детей из многодетных семей. Нужны судьи и координаторы.',
            'date': future_date11,
            'location': 'Стадион "Динамо"',
            'volunteer_required': 45,
            'image': 'kids_olympics.jpg',
            'organizer_id': 1
        },
        {
            'name': 'Фестиваль народных промыслов',
            'description': 'Демонстрация традиционных ремесел и мастер-классы по народным промыслам. Сохраняем культурное наследие!',
            'date': future_date12,
            'location': 'Парк искусств Музеон',
            'volunteer_required': 28,
            'image': 'folk_crafts.jpg',
            'organizer_id': 2
        },
        {
            'name': 'Экологический квест',
            'description': 'Интерактивная игра на природе, направленная на экологическое просвещение участников всех возрастов.',
            'date': future_date13,
            'location': 'Парк "Кузьминки"',
            'volunteer_required': 22,
            'image': 'eco_quest.jpg',
            'organizer_id': 5
        }
    ])

def populate_with_registrations():
    registrations_table = sa.sql.table('registrations',
        sa.sql.column('event_id', sa.Integer),
        sa.sql.column('volunteer_id', sa.Integer),
        sa.sql.column('contact_info', sa.String),
        sa.sql.column('date', sa.DateTime),
        sa.sql.column('status', sa.Enum)
    )
    
    from datetime import datetime
    
    op.bulk_insert(registrations_table, [
        # Регистрации на событие 1 (Уборка парка)
        {
            'event_id': 1,
            'volunteer_id': 3,
            'contact_info': 'anna.volunteer@email.com, +7-999-123-45-67',
            'date': datetime.now(),
            'status': 'accepted'
        },
        {
            'event_id': 1,
            'volunteer_id': 4,
            'contact_info': 'petr.activist@email.com, +7-999-876-54-32',
            'date': datetime.now(),
            'status': 'accepted'
        },
        {
            'event_id': 1,
            'volunteer_id': 5,
            'contact_info': 'organizer1@email.com, +7-999-555-11-22',
            'date': datetime.now(),
            'status': 'accepted'
        },
        
        # Регистрации на событие 2 (Помощь в приюте)
        {
            'event_id': 2,
            'volunteer_id': 3,
            'contact_info': 'anna.volunteer@email.com, +7-999-123-45-67',
            'date': datetime.now(),
            'status': 'accepted'
        },
        {
            'event_id': 2,
            'volunteer_id': 4,
            'contact_info': 'petr.activist@email.com, +7-999-876-54-32',
            'date': datetime.now(),
            'status': 'accepted'
        },
        
        # Регистрации на событие 3 (Посадка деревьев)
        {
            'event_id': 3,
            'volunteer_id': 4,
            'contact_info': 'petr.activist@email.com, +7-999-876-54-32',
            'date': datetime.now(),
            'status': 'rejected'
        },
        {
            'event_id': 3,
            'volunteer_id': 3,
            'contact_info': 'anna.volunteer@email.com, +7-999-123-45-67',
            'date': datetime.now(),
            'status': 'pending'
        },
        {
            'event_id': 3,
            'volunteer_id': 5,
            'contact_info': 'organizer1@email.com, +7-999-555-11-22',
            'date': datetime.now(),
            'status': 'accepted'
        }
    ])

def upgrade():
    op.create_table('roles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles'))
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('login', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=200), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('middle_name', sa.String(length=100), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_users_role_id_roles')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('login', name=op.f('uq_users_login'))
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('location', sa.String(length=120), nullable=False),
    sa.Column('volunteer_required', sa.Integer(), nullable=False),
    sa.Column('image', sa.String(length=100), nullable=False),
    sa.Column('organizer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], name=op.f('fk_events_organizer_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_events'))
    )
    op.create_table('registrations',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('volunteer_id', sa.Integer(), nullable=False),
    sa.Column('contact_info', sa.String(length=120), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'accepted', 'rejected', name='registrationstatus'), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_registrations_event_id_events')),
    sa.ForeignKeyConstraint(['volunteer_id'], ['users.id'], name=op.f('fk_registrations_volunteer_id_users')),
    sa.PrimaryKeyConstraint('event_id', 'volunteer_id', name=op.f('pk_registrations'))
    )
    # Наполнение базы данных
    populate_with_roles()
    populate_with_users()
    populate_with_events()
    populate_with_registrations()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('registrations')
    op.drop_table('events')
    op.drop_table('users')
    op.drop_table('roles')
    # ### end Alembic commands ###
