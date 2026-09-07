import pytest
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Перевірка завантаження головної сторінки"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'API System Dashboard' in response.data

def test_404_page(client):
    """Перевірка кастомної 404 сторінки"""
    response = client.get('/nonexistent-route-123')
    assert response.status_code == 404
    assert b'404' in response.data

@patch('app.get_db_connection')
def test_get_users(mock_get_db, client):
    """Перевірка GET /api/users"""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{"id": 1, "username": "cyber_ninja"}]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    response = client.get('/api/users')
    assert response.status_code == 200
    assert response.json == [{"id": 1, "username": "cyber_ninja"}]

@patch('app.get_db_connection')
def test_post_user_success(mock_get_db, client):
    """Перевірка успішного POST /api/users"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    response = client.post('/api/users', json={
        "username": "newuser", 
        "email": "test@example.com", 
        "age": 25
    })
    assert response.status_code == 201
    assert response.json['user']['username'] == 'newuser'

def test_post_user_missing_username(client):
    """Перевірка валідації: відсутній username"""
    response = client.post('/api/users', json={"name": "Test User", "age": 25})
    assert response.status_code == 400
    assert "error" in response.json

def test_post_user_invalid_age(client):
    """Перевірка валідації: вік менше 18"""
    response = client.post('/api/users', json={"username": "test", "age": 12})
    assert response.status_code == 400
    assert "error" in response.json

def test_post_user_invalid_email(client):
    """Перевірка валідації: неправильний формат email"""
    response = client.post('/api/users', json={"username": "test", "email": "not-an-email"})
    assert response.status_code == 400
    assert "error" in response.json

@patch('app.get_db_connection')
def test_put_user(mock_get_db, client):
    """Перевірка успішного PUT /api/users/<id>"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1] # Користувач існує
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    response = client.put('/api/users/1', json={"username": "updated_user", "email": "new@example.com", "age": 30})
    assert response.status_code == 200

@patch('app.get_db_connection')
def test_delete_user(mock_get_db, client):
    """Перевірка успішного DELETE /api/users/<id>"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1] # Користувач існує
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    response = client.delete('/api/users/1')
    assert response.status_code == 200
