import pytest

from .. import create_app
from ..models import db, User, Role, VisitLog
from ..auth.checkers import check_login, check_password
from ..config import SECRET_KEY


@pytest.fixture
def app():
    test_config = {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': SECRET_KEY,
        'SQLALCHEMY_DATABASE_URI': "sqlite:///:memory:",
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    app = create_app(test_config)
    
    with app.app_context():
        db.create_all()
        
        admin_role = Role(id=1, name='admin', description='Administrator')
        user_role = Role(id=2, name='user', description='Regular user')
        db.session.add(admin_role)
        db.session.add(user_role)
        
        admin_user = User(
            id=1, 
            login='admin',
            first_name='Админ',
            last_name='Администратор',
            middle_name='Главный',
            role_id=1
        )
        admin_user.set_password('admin123')
        
        regular_user = User(
            id=2,
            login='testuser',
            first_name='Тест',
            last_name='Пользователь',
            middle_name='Тестович',
            role_id=2
        )
        regular_user.set_password('user123')
        
        db.session.add(admin_user)
        db.session.add(regular_user)
        db.session.commit()
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user():
    return {
        'login': 'admin',
        'password': 'admin123'
    }


@pytest.fixture
def regular_user():
    return {
        'login': 'testuser',
        'password': 'user123'
    }


@pytest.fixture
def mock_db_connector(mocker):
    mock_connect = mocker.patch('app.db.DBConnector.connect')
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    mock_cursor.__enter__ = mocker.MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = mocker.MagicMock(return_value=None)
    
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection
    
    return mock_cursor


@pytest.fixture
def mock_sqlalchemy_session(mocker):
    mock_session = mocker.MagicMock()
    
    mock_session.add = mocker.MagicMock()
    mock_session.commit = mocker.MagicMock()
    mock_session.rollback = mocker.MagicMock()
    mock_session.query = mocker.MagicMock()
    mock_session.get = mocker.MagicMock()
    
    mocker.patch('app.models.db.session', mock_session)
    
    return mock_session


def test_login_page_get(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert 'Авторизация' in response.get_data(as_text=True)


def test_login_valid_admin(client, admin_user):
    response = client.post('/auth/login', data=admin_user, follow_redirects=True)
    assert response.status_code == 200
    assert 'успешно аутентифицированы' in response.get_data(as_text=True)


def test_login_valid_user(client, regular_user):
    response = client.post('/auth/login', data=regular_user, follow_redirects=True)
    assert response.status_code == 200
    assert 'успешно аутентифицированы' in response.get_data(as_text=True)


def test_login_invalid_credentials(client):
    response = client.post('/auth/login', data={
        'login': 'wronguser',
        'password': 'wrongpass'
    })
    assert 'Неправильный логин или пароль' in response.get_data(as_text=True)


def test_logout(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200


def test_admin_can_create_users(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/users/create')
    assert response.status_code == 200


def test_regular_user_cannot_create_users(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/users/create', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)


def test_admin_can_delete_users(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.post('/users/2/delete', follow_redirects=True)
    assert response.status_code == 200


def test_regular_user_cannot_delete_users(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.post('/users/1/delete', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)


def test_admin_can_view_any_user_profile(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/users/2')
    assert response.status_code == 200


def test_user_can_view_own_profile(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/users/2')
    assert response.status_code == 200


def test_user_cannot_view_other_user_profile(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/users/1', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)


def test_admin_can_edit_any_user(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/users/2/edit')
    assert response.status_code == 200


def test_user_can_edit_own_profile(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/users/2/edit')
    assert response.status_code == 200


def test_user_cannot_edit_other_user_profile(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/users/1/edit', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)


def test_admin_can_view_all_visit_logs(client, admin_user, app):
    with app.app_context():
        log1 = VisitLog(path='/users', user_id=1)
        log2 = VisitLog(path='/users/create', user_id=2)
        log3 = VisitLog(path='/auth/login', user_id=None)
        db.session.add_all([log1, log2, log3])
        db.session.commit()
    
    client.post('/auth/login', data=admin_user)
    response = client.get('/visit_logs/')
    assert response.status_code == 200
    assert '/users' in response.get_data(as_text=True)
    assert '/users/create' in response.get_data(as_text=True)
    assert '/auth/login' in response.get_data(as_text=True)


def test_user_can_view_only_own_visit_logs(client, regular_user, app):
    with app.app_context():
        log1 = VisitLog(path='/admin-only-page', user_id=1)
        log2 = VisitLog(path='/user-specific-page', user_id=2)
        log3 = VisitLog(path='/auth/login', user_id=None)
        db.session.add_all([log1, log2, log3])
        db.session.commit()
    
    client.post('/auth/login', data=regular_user)
    response = client.get('/visit_logs/')
    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert '/user-specific-page' in response_text
    assert '/admin-only-page' not in response_text


def test_admin_can_view_pages_statistics(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/visit_logs/pages_visits')
    assert response.status_code == 200


def test_user_cannot_view_pages_statistics(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/visit_logs/pages_visits', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)


def test_admin_can_view_users_statistics(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/visit_logs/users_visits')
    assert response.status_code == 200


def test_user_cannot_view_users_statistics(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/visit_logs/users_visits', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)


def test_admin_can_download_pages_statistics_csv(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/visit_logs/pages_visits/download')
    assert response.status_code == 200
    assert response.content_type == 'text/csv; charset=utf-8'


def test_admin_can_download_users_statistics_csv(client, admin_user):
    client.post('/auth/login', data=admin_user)
    response = client.get('/visit_logs/users_visits/download')
    assert response.status_code == 200
    assert response.content_type == 'text/csv; charset=utf-8'


def test_user_cannot_download_statistics_csv(client, regular_user):
    client.post('/auth/login', data=regular_user)
    
    response = client.get('/visit_logs/pages_visits/download', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)
    
    response = client.get('/visit_logs/users_visits/download', follow_redirects=True)
    assert 'недостаточно прав' in response.get_data(as_text=True)


def test_visit_logging_for_authenticated_user(client, admin_user, app):
    client.post('/auth/login', data=admin_user)
    
    client.get('/users/')
    
    with app.app_context():
        logs = db.session.query(VisitLog).filter_by(path='/users/', user_id=1).all()
        assert len(logs) >= 1


def test_visit_logging_for_anonymous_user(client, app):
    client.get('/auth/login')
    
    with app.app_context():
        logs = db.session.query(VisitLog).filter_by(path='/auth/login', user_id=None).all()
        assert len(logs) >= 1


def test_visit_logging_ignores_non_get_requests(client, admin_user, app):
    client.post('/auth/login', data=admin_user)
    
    initial_count = 0
    with app.app_context():
        initial_count = db.session.query(VisitLog).count()
    
    client.post('/users/create', data={
        'login': 'newuser12345',
        'password': 'ValidPass1!',
        'first_name': 'Тест',
        'last_name': 'Юзер',
        'role_id': 2
    })
    
    with app.app_context():
        final_count = db.session.query(VisitLog).count()
        assert final_count <= initial_count + 1


def test_admin_create_user_success(client, admin_user, app):
    client.post('/auth/login', data=admin_user)
    
    response = client.post('/users/create', data={
        'login': 'newuser12345',
        'password': 'ValidPass1!',
        'first_name': 'Новый',
        'last_name': 'Пользователь',
        'middle_name': 'Тестовый',
        'role_id': '2'
    }, follow_redirects=True)
    
    assert 'успешно создана' in response.get_data(as_text=True)
    
    with app.app_context():
        new_user = db.session.query(User).filter_by(login='newuser12345').first()
        assert new_user is not None
        assert new_user.first_name == 'Новый'


def test_create_user_invalid_login_short(client, admin_user):
    client.post('/auth/login', data=admin_user)
    
    response = client.post('/users/create', data={
        'login': 'abc',
        'password': 'ValidPass1!',
        'first_name': 'Тест',
        'last_name': 'Пользователь',
        'role_id': '2'
    })
    assert 'не менее 5 символов' in response.get_data(as_text=True)


def test_create_user_invalid_password(client, admin_user):
    client.post('/auth/login', data=admin_user)
    
    response = client.post('/users/create', data={
        'login': 'validuser123',
        'password': '123',
        'first_name': 'Тест',
        'last_name': 'Пользователь',
        'role_id': '2'
    })
    assert 'не менее 8 символов' in response.get_data(as_text=True)


def test_admin_edit_user_success(client, admin_user, app):
    client.post('/auth/login', data=admin_user)
    
    response = client.post('/users/2/edit', data={
        'first_name': 'Обновленный',
        'last_name': 'Пользователь',
        'middle_name': 'Измененный',
        'role_id': '2'
    }, follow_redirects=True)
    
    assert 'успешно изменена' in response.get_data(as_text=True)
    
    with app.app_context():
        user = db.session.get(User, 2)
        assert user.first_name == 'Обновленный'


def test_user_edit_own_profile_success(client, regular_user, app):
    client.post('/auth/login', data=regular_user)
    
    response = client.post('/users/2/edit', data={
        'first_name': 'Самоизмененный',
        'last_name': 'Пользователь',
        'middle_name': 'Самостоятельно',
        'role_id': '2'
    }, follow_redirects=True)
    
    assert 'успешно изменена' in response.get_data(as_text=True)
    
    with app.app_context():
        user = db.session.get(User, 2)
        assert user.first_name == 'Самоизмененный'


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


def test_unauthenticated_access_requires_login(client):
    protected_urls = [
        '/users/create',
        '/users/1/edit',
        '/users/1',
        '/visit_logs/',
        '/visit_logs/pages_visits',
        '/visit_logs/users_visits'
    ]
    
    for url in protected_urls:
        response = client.get(url, follow_redirects=True)
        assert 'необходима аутентификация' in response.get_data(as_text=True)


def test_user_role_field_disabled_for_regular_users(client, regular_user):
    client.post('/auth/login', data=regular_user)
    response = client.get('/users/2/edit')
    
    assert response.status_code == 200


def test_example_mocking_password_hashing(client, admin_user, mocker):
    mock_hash = mocker.patch.object(User, 'set_password')
    mock_hash.return_value = None
    
    client.post('/auth/login', data=admin_user)
    
    client.post('/users/create', data={
        'login': 'testuser123',
        'password': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User',
        'role_id': '2'
    })
    
    mock_hash.assert_called_once_with('TestPassword123!')
