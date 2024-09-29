import json

def test_add_book_route(client, mock_db_connection, mock_kafka_producer):
    # Mock the database response
    mock_db_connection.fetchone.return_value = {
        'id': 1, 'title': 'New Book', 'author': 'Author', 'publisher': 'Publisher', 'category': 'Category'
    }

    # Input data to be sent to the route
    book_data = {
        'title': 'New Book',
        'author': 'Author',
        'publisher': 'Publisher',
        'category': 'Category'
    }

    # Call the API route
    response = client.post('/books', data=json.dumps(book_data), content_type='application/json')

    # Verify the response and status code
    assert response.status_code == 201
    response_json = response.get_json()
    assert response_json['status'] == 'success'
    assert response_json['data']['title'] == 'New Book'

    # Ensure DB interaction and Kafka event sending occurred
    mock_db_connection.execute.assert_called_once()
    mock_kafka_producer.assert_called_once()


def test_remove_book_route(client, mock_db_connection, mock_kafka_producer):
    # Mock the database response
    mock_db_connection.fetchone.return_value = {'id': 1, 'title': 'Old Book', 'author': 'Author'}

    # Call the API route
    response = client.delete('/books/1')

    # Verify the response and status code
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['data']['title'] == 'Old Book'

    # Ensure DB interaction and Kafka event sending occurred
    mock_db_connection.execute.assert_called_once()
    mock_kafka_producer.assert_called_once()
