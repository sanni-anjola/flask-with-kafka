import pytest
from app import app as flask_app
from db import get_db_connection
from kafka_producer import send_event
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    # Return the Flask app
    return flask_app

@pytest.fixture
def client(app):
    # Create a test client
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def mock_db_connection():
    """Mock the database connection for unit tests."""
    with patch('db.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        conn = mock_conn.return_value
        conn.cursor.return_value = mock_cursor
        yield mock_cursor
        patch.stopall()

@pytest.fixture(scope='function')
def mock_kafka_producer():
    """Mock Kafka producer to avoid sending real messages during tests."""
    with patch('kafka_producer.send_event') as mock_producer:
        yield mock_producer
