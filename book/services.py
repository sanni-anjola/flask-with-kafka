from db import get_db_connection
from kafka_producer import send_event
from util.helpers import dict_fetchone, dict_fetchall
from config import Config

def enroll_user(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (email, first_name, last_name)
        VALUES (%s, %s, %s)
        RETURNING id, email, first_name, last_name
        """, (data['email'], data['first_name'], data['last_name'])
    )
    new_user = dict_fetchone(cursor)
    conn.commit()
    
    # Publish the event to Kafka
    send_event(Config.BOOK_TOPIC, {'event': 'user_created_events', 'event_data': new_user})

    cursor.close()
    conn.close()

    return new_user

def get_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
    
    book = dict_fetchone(cursor)
    
    cursor.close()
    conn.close()
    
    return book


def list_books(publisher=None, category=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    base_query = "SELECT * FROM books WHERE available=%s"
    params = [True]
    
    if category:
        base_query += " AND LOWER(category)=LOWER(%s)"
        params.append(category)
    
    if publisher:
        base_query += " AND LOWER(publisher)=LOWER(%s)"
        params.append(publisher)
    
    cursor.execute(base_query, tuple(params))
    books = dict_fetchall(cursor)
    
    cursor.close()
    conn.close()
    
    return books


def borrow_book(book_id, user_id, days):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
    book = dict_fetchone(cursor)

    if not book['available']:
        return {'message': 'Book not available'}, 400

    cursor.execute("UPDATE books SET available=%s WHERE id=%s", (False, book_id))
    conn.commit()

    # Send Kafka event
    event_data = {
        'book_id': book_id,
        'user_id': user_id,
        'days': days
    }
    send_event(Config.BOOK_TOPIC, {'event': 'borrow_events', 'event_data': event_data})

    cursor.close()
    conn.close()

    return {'message': 'Book borrowed successfully'}, 200
