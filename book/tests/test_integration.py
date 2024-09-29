import json
import pytest

@pytest.fixture
def setup_database(mock_db_connection):
    """Set up mock database with test data."""
    # Insert some mock data into the mock DB
    mock_db_connection.execute("INSERT INTO users (email, first_name, last_name) VALUES ('test@example.com', 'Test', 'User')")
    mock_db_connection.execute("INSERT INTO books (id, title, available) VALUES (1, 'Test Book', True)")
    mock_db_connection.commit()

def test_integration_enroll_user(client, setup_database, mock_kafka_producer):
    # Mock the Kafka producer
    mock_kafka_producer.return_value = None
    
    # Test enrolling a new user
    user_data = {
        'email': 'newuser@example.com',
        'first_name': 'New',
        'last_name': 'User'
    }
    response = client.post('/users', data=json.dumps(user_data), content_type='application/json')
    
    assert response.status_code == 201
    response_json = response.get_json()
    assert response_json['status'] == 'success'
    assert response_json['data']['email'] == 'newuser@example.com'

    # Check that Kafka producer was called
    mock_kafka_producer.assert_called_once()

def test_integration_borrow_book(client, setup_database, mock_kafka_producer):
    # Borrow a book
    borrow_data = {'user_id': 1, 'days': 7}
    response = client.post('/borrow/1', data=json.dumps(borrow_data), content_type='application/json')
    
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Book borrowed successfully'

    # Check that Kafka producer was called for the borrow event
    mock_kafka_producer.assert_called_once()
