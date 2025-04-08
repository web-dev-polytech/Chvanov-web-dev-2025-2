from bs4 import BeautifulSoup as soup
import datetime

def test_counter(client):
    request_1 = client.get('/counter')
    assert request_1.status_code == 200
    with client.session_transaction() as session:
        session_counter_1 = session.get('counter', '')

    request_2 = client.get('/counter')
    assert request_2.status_code == 200
    with client.session_transaction() as session:
        session_counter_2 = session.get('counter', '')

    data_1 = soup(request_1.get_data(as_text=True), 'html.parser')
    data_2 = soup(request_2.get_data(as_text=True), 'html.parser')

    page_counter_1 = int(data_1.find('h1').text.strip().split()[-2])
    page_counter_2 = int(data_2.find('h1').text.strip().split()[-2])

    assert page_counter_1 == session_counter_1
    assert page_counter_2 == session_counter_2
    assert page_counter_1 != page_counter_2

def test_counter_multiuser(client, client_misc):
    user1_request_1 = client.get('/counter')
    assert user1_request_1.status_code == 200
    user1_request_2 = client.get('/counter')
    assert user1_request_2.status_code == 200
    with client.session_transaction() as session:
        user1_session_counter_2 = session.get('counter', '')

    user2_request_1 = client_misc.get('/counter')
    assert user2_request_1.status_code == 200
    with client_misc.session_transaction() as session:
        user2_session_counter_1 = session.get('counter', '')
    
    user1_data_2 = soup(user1_request_2.get_data(as_text=True), 'html.parser')
    user2_data_1 = soup(user2_request_1.get_data(as_text=True), 'html.parser')

    user1_page_counter_2 = int(user1_data_2.find('h1').text.strip().split()[-2])
    user2_page_counter_1 = int(user2_data_1.find('h1').text.strip().split()[-2])

    assert user1_page_counter_2 == user1_session_counter_2
    assert user2_page_counter_1 == user2_session_counter_1
    assert user1_page_counter_2 != user2_page_counter_1

def test_successful_auth(client, correct_creds):
    response = client.post('/login', data=correct_creds, follow_redirects=True)
    assert response.history[0].status_code == 302
    assert response.status_code == 200
    assert response.request.path == '/'

    assert 'Вы успешно аутентифицированы' in response.text
    
    
def test_unsuccessful_auth(client, incorrect_creds):
    response = client.post('/login', data=incorrect_creds, follow_redirects=True)
    assert len(response.history) == 0  # не должно быть редиректов
    assert response.status_code == 200
    assert response.request.path == '/login'
    assert 'Пользователь не найден, попробуйте снова.' in response.text

def test_secret_auth_available(client, correct_creds):
    auth_response = client.post('/login', data=correct_creds, follow_redirects=True)
    assert auth_response.status_code == 200

    secret_response = client.get('/secret')
    assert secret_response.status_code == 200
    assert secret_response.request.path == '/secret'
    assert 'Эта страница доступна только авторизованным пользователям' in secret_response.text

def test_secret_unauth_available(client):
    response = client.get('/secret', follow_redirects=True)
    assert len(response.history) == 1
    assert response.history[0].status_code == 302
    assert response.request.path == '/login'
    assert 'Для доступа к запрашиваемой странице необходима аутентификация' in response.text

def test_redirect_to_secret_after_auth(client, correct_creds):
    response = client.get('/secret', follow_redirects=True)
    assert response.request.path == '/login'
    assert 'Для доступа к запрашиваемой странице необходима аутентификация' in response.text

    auth_response = client.post('/login', data=correct_creds, follow_redirects=True)
    assert auth_response.request.path == '/secret'
    assert 'Эта страница доступна только авторизованным пользователям' in auth_response.text

def test_remember_me_turned_on(client, correct_creds):
    correct_creds['remember_me'] = 'on'
    response = client.post('/login', data=correct_creds, follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно аутентифицированы' in response.text

    remember_token = client.get_cookie('remember_token')

    assert remember_token != ''
    assert remember_token.key == 'remember_token'
    assert remember_token.value != ''
    assert remember_token.expires > datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=364)
    
def test_remember_me_turned_off(client, correct_creds):
    response = client.post('/login', data=correct_creds, follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно аутентифицированы' in response.text

    remember_token = client.get_cookie('remember_token')
    assert not remember_token

def test_correct_navbar_auth(client, correct_creds):
    response = client.post('/login', data=correct_creds, follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно аутентифицированы' in response.text

    assert 'Выйти' in response.text
    
def test_correct_navbar_unauth(client, correct_creds):
    response = client.post('/login', data=correct_creds, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы вышли из аккаунта' in response.text

    assert 'Войти' in response.text and 'Выйти' not in response.text
