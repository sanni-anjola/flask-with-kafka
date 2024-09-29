from services import enroll_user, list_books, borrow_book
from unittest.mock import patch

def test_enroll_user(mock_db_connection, mock_kafka_producer):
    # Mock input data
    user_data = {'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}

    # Mock what the DB should return
    mock_db_connection.fetchone.return_value = {
        'id': 1, 'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'
    }

    # Call the service function
    new_user = enroll_user(user_data)

    # Ensure DB interaction and Kafka event sending
    mock_db_connection.execute.assert_called_once()
    mock_kafka_producer.assert_called_once_with('book_service_topic', {'event': 'user_created_events', 'event_data': new_user})

    # Assert the user returned is correct
    assert new_user['email'] == 'test@example.com'


def test_borrow_book(mock_db_connection, mock_kafka_producer):
    # Mock data and DB responses
    book_id = 1
    user_id = 2
    days = 7
    mock_db_connection.fetchone.return_value = {'available': True}

    # Call the service
    response, status_code = borrow_book(book_id, user_id, days)

    # Ensure the database and Kafka interactions occurred
    mock_db_connection.execute.assert_called_with("UPDATE books SET available=%s WHERE id=%s", (False, book_id))
    mock_kafka_producer.assert_called_once_with(
        'book_service_topic', {'event': 'borrow_events', 'event_data': {'book_id': book_id, 'user_id': user_id, 'days': days}}
    )

    # Check the service response
    assert status_code == 200
    assert response['message'] == 'Book borrowed successfully'
