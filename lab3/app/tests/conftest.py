import pytest

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, _phone_check

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        return client
    
@pytest.fixture
def phone_check():
    return _phone_check