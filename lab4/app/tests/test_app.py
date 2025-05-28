import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lab4.app import create_app
from lab4.app.repositories import UserRepository, RoleRepository
from lab4.app.utils import check_login, check_password


@pytest.fixture
def app():
    """Create application for testing."""
    test_config = {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MYSQL_USER': 'test_user',
        'MYSQL_PASSWORD': 'test_password',
        'MYSQL_HOST': 'localhost',
        'MYSQL_DATABASE': 'test_database'
    }
    app = create_app(test_config)
    return app


@pytest.fixture
def client(app):
    """Test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def mock_db_connector():
    """Mock database connector to avoid real database calls."""
    with patch('lab4.app.db.DBConnector.connect') as mock_connect:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        yield mock_cursor


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        'id': 1,
        'login': 'testuser',
        'first_name': 'Тест',
        'last_name': 'Пользователь',
        'middle_name': 'Тестович',
        'role_id': 1
    }


@pytest.fixture
def sample_role():
    """Sample role data for testing."""
    return {
        'id': 1,
        'name': 'admin',
        'description': 'Administrator'
    }


# --- Main page tests ---

def test_main_page_anonymous(client, mock_db_connector):
    mock_db_connector.fetchall.return_value = []
    response = client.get('/')
    assert response.status_code == 200


def test_main_page_content(client, mock_db_connector):
    mock_db_connector.fetchall.return_value = []
    response = client.get('/')
    assert response.status_code == 200
    # Check for some expected content based on your users index template


# --- Authentication tests ---

def test_login_page_get(client):
    response = client.get('/auth/login')
    assert response.status_code == 200


def test_login_valid_user(client, mock_db_connector, sample_user):
    mock_db_connector.fetchone.return_value = sample_user
    response = client.post('/auth/login', data={
        'login': 'admin',
        'password': 'qwerty'
    }, follow_redirects=True)
    assert "успешно аутентифицированы".encode('utf-8') in response.data


def test_login_invalid_user(client, mock_db_connector):
    mock_db_connector.fetchone.return_value = None
    response = client.post('/auth/login', data={
        'login': 'wronguser',
        'password': 'wrongpass'
    })
    assert "Неправильный логин или пароль".encode('utf-8') in response.data


def test_logout(client, mock_db_connector, sample_user):
    mock_db_connector.fetchone.return_value = sample_user
    client.post('/auth/login', data={
        'login': 'admin',
        'password': 'qwerty'
    })
    
    # Logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200


# --- User creation tests ---

def test_create_user_page_requires_login(client):
    response = client.get('/users/new')
    assert response.status_code == 302


def test_create_user_success(client, mock_db_connector, sample_user, sample_role):
    mock_db_connector.fetchone.side_effect = [sample_user, None]
    mock_db_connector.fetchall.return_value = [sample_role]
    
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.post('/users/new', data={
        'login': 'newuser12345',
        'password': 'ValidPass1!',
        'first_name': 'Анна',
        'last_name': 'Петрова',
        'middle_name': 'Сергеевна',
        'role_id': '1'
    }, follow_redirects=True)
    assert "успешно создана".encode('utf-8') in response.data


def test_create_user_invalid_login_short(client, mock_db_connector, sample_user, sample_role):
    mock_db_connector.fetchone.return_value = sample_user
    mock_db_connector.fetchall.return_value = [sample_role]
    
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.post('/users/new', data={
        'login': 'abc',
        'password': 'ValidPass1!',
        'first_name': 'Тест',
        'last_name': 'Пользователь'
    })
    assert "не менее 5 символов".encode('utf-8') in response.data


def test_create_user_invalid_password(client, mock_db_connector, sample_user, sample_role):
    mock_db_connector.fetchone.return_value = sample_user
    mock_db_connector.fetchall.return_value = [sample_role]
    
    # Login first
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.post('/users/new', data={
        'login': 'validuser123',
        'password': '123',
        'first_name': 'Тест',
        'last_name': 'Пользователь'
    })
    assert "не менее 8 символов".encode('utf-8') in response.data


# --- User viewing tests ---

def test_view_user(client, mock_db_connector, sample_user, sample_role):
    mock_db_connector.fetchone.side_effect = [sample_user, sample_role]
    response = client.get('/users/1')
    assert response.status_code == 200


def test_view_nonexistent_user(client, mock_db_connector):
    mock_db_connector.fetchone.return_value = None
    response = client.get('/users/999')
    assert response.status_code in [302, 404]


# --- User editing tests ---

def test_edit_user_requires_login(client):
    response = client.get('/users/1/edit')
    assert response.status_code == 302


def test_edit_user_form(client, mock_db_connector, sample_user, sample_role):
    mock_db_connector.fetchone.side_effect = [sample_user, sample_user]
    mock_db_connector.fetchall.return_value = [sample_role]
    
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.get('/users/1/edit')
    assert response.status_code == 200


def test_edit_user_database_update(client, mock_db_connector, sample_user, sample_role):
    mock_db_connector.fetchone.side_effect = [sample_user, sample_user]
    mock_db_connector.fetchall.return_value = [sample_role]
    
    # Login first
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    # Edit user
    response = client.post('/users/1/edit', data={
        'first_name': 'Обновленное',
        'last_name': 'Имя',
        'middle_name': 'Тестовое',
        'role_id': '1'
    }, follow_redirects=True)
    
    # Verify the UPDATE query was called
    mock_db_connector.execute.assert_called()
    calls = mock_db_connector.execute.call_args_list
    
    # Check that an UPDATE statement was executed
    update_call = None
    for call in calls:
        if 'UPDATE users SET' in str(call[0][0]):
            update_call = call
            break
    
    assert update_call is not None, "UPDATE query was not executed"
    assert 'first_name = %s' in update_call[0][0]
    assert update_call[0][1] == ('Обновленное', 'Тестовое', 'Имя', '1', 1)


# --- User deletion tests ---

def test_delete_user_requires_login(client):
    response = client.post('/users/1/delete')
    assert response.status_code == 302


def test_delete_user_success(client, mock_db_connector, sample_user):
    mock_db_connector.fetchone.return_value = sample_user
    
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.post('/users/1/delete', follow_redirects=True)
    assert response.status_code == 200


# --- Password change tests ---

def test_change_password_requires_login(client):
    response = client.get('/auth/change_password')
    assert response.status_code == 302


def test_change_password_form(client, mock_db_connector, sample_user):
    mock_db_connector.fetchone.return_value = sample_user
    
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.get('/auth/change_password')
    assert response.status_code == 200


def test_change_password_valid(client, mock_db_connector, sample_user):
    mock_db_connector.fetchone.side_effect = [sample_user, sample_user]
    
    # Login first
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.post('/auth/change_password', data={
        'old_password': 'qwerty',
        'new_password': 'NewPassword1!',
        'confirm_password': 'NewPassword1!'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_change_password_wrong_old(client, mock_db_connector, sample_user):
    mock_db_connector.fetchone.side_effect = [sample_user, None]
    
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.post('/auth/change_password', data={
        'old_password': 'wrongpassword',
        'new_password': 'NewPassword1!',
        'confirm_password': 'NewPassword1!'
    })
    assert response.status_code == 200


def test_change_password_mismatch(client, mock_db_connector, sample_user):
    mock_db_connector.fetchone.return_value = sample_user
    
    client.post('/auth/login', data={'login': 'admin', 'password': 'qwerty'})
    
    response = client.post('/auth/change_password', data={
        'old_password': 'qwerty',
        'new_password': 'NewPassword1!',
        'confirm_password': 'DifferentPassword1!'
    })
    assert response.status_code == 200


# --- Validation utility tests ---

def test_check_login_valid():
    assert check_login('validlogin123') is True


def test_check_login_too_short():
    with pytest.raises(ValueError, match="не менее 5 символов"):
        check_login('abc')


def test_check_login_invalid_chars():
    with pytest.raises(ValueError, match="только латинские буквы и цифры"):
        check_login('invalid-login!')


def test_check_password_valid():
    assert check_password('ValidPass1!') is True


def test_check_password_too_short():
    with pytest.raises(ValueError, match="не менее 8 символов"):
        check_password('Short1!')


def test_check_password_no_uppercase():
    with pytest.raises(ValueError, match="заглавную и одну строчную"):
        check_password('validpass1!')


def test_check_password_no_digits():
    with pytest.raises(ValueError, match="одну арабскую цифру"):
        check_password('ValidPass!')


def test_check_password_with_spaces():
    with pytest.raises(ValueError, match="не должен содержать пробелов"):
        check_password('Valid Pass1!')


# --- Repository tests ---

def test_user_repository_get_by_id(mock_db_connector, sample_user):
    from lab4.app.db import DBConnector
    
    mock_db = MagicMock(spec=DBConnector)
    user_repo = UserRepository(mock_db)
    
    mock_db.connect.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = sample_user
    
    result = user_repo.get_by_id(1)
    assert result == sample_user


def test_user_repository_get_by_login_and_password(mock_db_connector, sample_user):
    """Test UserRepository get_by_login_and_password method."""
    from lab4.app.db import DBConnector
    
    mock_db = MagicMock(spec=DBConnector)
    user_repo = UserRepository(mock_db)
    
    mock_db.connect.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = sample_user
    
    result = user_repo.get_by_login_and_password('testuser', 'password')
    assert result == sample_user


def test_role_repository_all(mock_db_connector, sample_role):
    """Test RoleRepository all method."""
    from lab4.app.db import DBConnector
    
    mock_db = MagicMock(spec=DBConnector)
    role_repo = RoleRepository(mock_db)
    
    mock_db.connect.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = [sample_role]
    
    result = role_repo.all()
    assert len(result) == 1
    assert result[0].id == sample_role['id']
    assert result[0].name == sample_role['name']
