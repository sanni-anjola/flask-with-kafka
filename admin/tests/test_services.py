from services import add_book, remove_book, list_users
from unittest.mock import patch


def test_add_book(mock_db_connection, mock_kafka_producer):
    # Mock input data
    book_data = {'title': 'New Book', 'author': 'Author', 'publisher': 'Publisher', 'category': 'Category'}

    # Mock what the DB should return
    mock_db_connection.fetchone.return_value = {
        'id': 1, 'title': 'New Book', 'author': 'Author', 'publisher': 'Publisher', 'category': 'Category'
    }

    # Call the service function
    new_book = add_book(book_data)

    # Ensure DB interaction and Kafka event sending
    mock_db_connection.execute.assert_called_once()
    mock_kafka_producer.assert_called_once_with('admin_service_topic', {'event': 'book_added_events', 'event_data': new_book})

    # Assert the book returned is correct
    assert new_book['title'] == 'New Book'


def test_remove_book(mock_db_connection, mock_kafka_producer):
    # Mock data and DB responses
    book_id = 1

    # Mock what the DB should return
    mock_db_connection.fetchone.return_value = {'id': 1, 'title': 'Old Book', 'author': 'Author'}

    # Call the service
    deleted_book = remove_book(book_id)

    # Ensure DB interaction and Kafka event sending
    mock_db_connection.execute.assert_called_once_with(
        "DELETE FROM books WHERE id = %s RETURNING id, title, author", (book_id,)
    )
    mock_kafka_producer.assert_called_once_with('admin_service_topic', {'event': 'book_deleted_events', 'book_id': book_id})

    # Check that the book was correctly removed
    assert deleted_book['title'] == 'Old Book'


def test_list_users(mock_db_connection):
    # Mock the database response
    mock_db_connection.fetchall.return_value = [
        {'id': 1, 'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    ]

    # Call the service function
    users = list_users()

    # Ensure DB interaction
    mock_db_connection.execute.assert_called_once_with("SELECT * FROM users")

    # Check that the users returned match the mock data
    assert len(users) == 1
    assert users[0]['email'] == 'test@example.com'
