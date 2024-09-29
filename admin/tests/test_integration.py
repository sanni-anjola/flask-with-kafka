import json
import pytest

@pytest.fixture
def setup_database(mock_db_connection):
    """Set up mock database with test data."""
    mock_db_connection.execute("INSERT INTO users (id, email, first_name, last_name) VALUES (1, 'test@example.com', 'Test', 'User')")
    mock_db_connection.execute("INSERT INTO books (id, title, available) VALUES (1, 'Test Book', True)")
    mock_db_connection.commit()

def test_integration_add_book(client, setup_database, mock_kafka_producer):
    # Test adding a book
    book_data = {
        'title': 'New Book',
        'author': 'Author',
        'publisher': 'Publisher',
        'category': 'Category'
    }
    response = client.post('/books', data=json.dumps(book_data), content_type='application/json')

    assert response.status_code == 201
    response_json = response.get_json()
    assert response_json['data']['title'] == 'New Book'

    # Check that Kafka producer was called
    mock_kafka_producer.assert_called_once()


def test_integration_remove_book(client, setup_database, mock_kafka_producer):
    # Test removing a book
    response = client.delete('/books/1')

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['data']['title'] == 'Test Book'

    # Check that Kafka producer was called
    mock_kafka_producer.assert_called_once()

