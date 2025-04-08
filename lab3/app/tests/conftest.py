import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_users

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        return client

@pytest.fixture
def client_misc():
    app.config['TESTING'] = True
    with app.test_client() as client:
        return client
    
@pytest.fixture
def correct_creds():
    return {
        'login': get_users()[0]['login'],
        'password': get_users()[0]['password']
    }
    
@pytest.fixture
def incorrect_creds():
    return {
        'login': 'hihik',
        'password': "it's a secret"
    }