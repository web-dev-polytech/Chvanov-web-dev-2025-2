import pytest

def test_args_rendering(client):
    url = '/args?name=John&age=30&city=New+York'
    response = client.get(url)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert all(('name' in html, 'John' in html))
    assert all(('age' in html, '30' in html))
    assert all(('city' in html, 'New York' in html))
    
def test_hesaders_rendering(client):
    test_headers = {
        'Host': '127.0.0.1:43000',
        'Connection': 'keep-alive',
        'Test-Header': 'Help the world',
        'Test-Header1': 'Python is the best'
    }
    request = client.get('/headers', headers=test_headers)
    html = request.get_data(as_text=True)
    for header, value in test_headers.items():
        assert all((header in html, value in html))

def test_cookie_rendering(client):
    request_1 = client.get('/cookies')
    request_2 = client.get('/cookies')
    html_1 = request_1.get_data(as_text=True)
    html_2 = request_2.get_data(as_text=True)

    cookie_key, cookie_value = 'name', 'Zadira Bob'
    cookie_in_req_1 = all((cookie_key in html_1, cookie_value in html_1))
    cookie_in_req_2 = all((cookie_key in html_2, cookie_value in html_2))

    if cookie_in_req_1:
        assert not cookie_in_req_2
    else:
        assert cookie_in_req_2
    
def test_form_rendering(client):
    data = {
        'theme': 'reinforcement learning',
        'test': "its cool!!!",
    }
    request = client.post('/form', data=data)
    html = request.get_data(as_text=True)
    for name, value in data.items():
        assert all((name in html, value in html))

def test_phone_validation_correct(phone_check):
    assert phone_check('+7 (123) 456-78-90') == True
    assert phone_check('8(123)4567890') == True
    assert phone_check('123.456.78.90') == True

def test_phone_validation_incorrect(phone_check):
    with pytest.raises(ValueError, match='Недопустимый ввод'):
        phone_check('12345')
    with pytest.raises(ValueError, match='Недопустимый ввод'):
        phone_check('+7 (123) 456-78-90 extra')
    with pytest.raises(ValueError, match='Недопустимый ввод'):
        phone_check('812345678901')

def test_phone_formatting(client):
    response = client.post('/phone', data={'phone': '+7 (123) 456-78-90'})
    assert '8-123-456-78-90' in response.text
    response = client.post('/phone', data={'phone': '8(123)4567890'})
    assert '8-123-456-78-90' in response.text
    response = client.post('/phone', data={'phone': '123.456.78.90'})
    assert '8-123-456-78-90' in response.text

def test_phone_error_message(client):
    response = client.post('/phone', data={'phone': '12345'})
    assert 'Недопустимый ввод' in response.text

    assert 'invalid-feedback' in response.text
    assert 'class="form-control is-invalid"' in response.text

def test_phone_formatted_display(client):
    response = client.post('/phone', data={'phone': '+7 (123) 456-78-90'})
    assert '8-123-456-78-90' in response.text
    assert 'Недопустимый ввод' not in response.text