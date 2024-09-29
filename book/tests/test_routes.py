import json

def test_enroll_user_route(client, mock_db_connection, mock_kafka_producer):
    # Mock the database response
    mock_db_connection.fetchone.return_value = {
        'id': 1, 'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'
    }

    # Input data to be sent to the route
    user_data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }

    # Call the API route
    response = client.post('/users', data=json.dumps(user_data), content_type='application/json')

    # Verify the response and status code
    assert response.status_code == 201
    response_json = response.get_json()
    assert response_json['status'] == 'success'
    assert response_json['data']['email'] == 'test@example.com'

    # Ensure DB interaction and Kafka event sending occurred
    mock_db_connection.execute.assert_called_once()
    mock_kafka_producer.assert_called_once()

def test_list_books_route(client, mock_db_connection):
    # Mock the database response
    mock_db_connection.fetchall.return_value = [
        {'id': 1, 'title': 'Book 1', 'author': 'Author 1', 'available': True}
    ]

    # Call the API route
    response = client.get('/books?publisher=OReilly&category=Technology')

    # Verify the response and status code
    assert response.status_code == 200
    books = response.get_json()
    assert len(books) == 1
    assert books[0]['title'] == 'Book 1'
