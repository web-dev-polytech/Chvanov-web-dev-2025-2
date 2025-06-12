# Enter the Flask app context
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, User

app = create_app()

# Create 10 simple users with easy passwords
users = [
    ('user01', 'Test123', 'Иван', 'Петров', None),
    ('user02', 'User123', 'Мария', 'Иванова', None),
    ('user03', 'Pass123', 'Алексей', 'Сидоров', None),
    ('user04', 'Easy123', 'Анна', 'Козлова', None),
    ('user05', 'Test123', 'Сергей', 'Волков', None),
    ('user06', 'User123', 'Елена', 'Новикова', None),
    ('user07', 'Pass123', 'Дмитрий', 'Морозов', None),
    ('user08', 'Easy123', 'Ольга', 'Федорова', None),
    ('user09', 'Test123', 'Андрей', 'Лебедев', None),
    ('user10', 'User123', 'Татьяна', 'Романова', None)
]

# Add each user
with app.app_context():
    for login, password, first_name, last_name, middle_name in users:
        if not db.session.query(User).filter_by(login=login).first():
            user = User(login=login, first_name=first_name, last_name=last_name, middle_name=middle_name, role_id=2)
            user.set_password(password)
            db.session.add(user)
            print(f"Added: {login} / {password}")

    # Commit changes
    db.session.commit()
    print("All users created!")
