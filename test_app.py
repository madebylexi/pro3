import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Upload an Image" in response.data

def test_upload_page(client):
    response = client.post('/upload')
    assert response.status_code == 400
    assert b"No file uploaded." in response.data
