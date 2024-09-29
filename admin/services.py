from db import get_db_connection
from kafka_producer import send_event
from util.helpers import dict_fetchone, dict_fetchall, convert_dates
from config import Config

def add_book(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO books (title, author, publisher, category)
        VALUES (%s, %s, %s, %s)
        RETURNING id, title, author, publisher, category
        """,
        (data['title'], data['author'], data['publisher'], data['category'])
    )
    new_book = convert_dates(dict_fetchone(cursor))
    conn.commit()

    # Publish book added event
    send_event(Config.ADMIN_TOPIC, {'event': 'book_added_events', 'event_data': new_book})
    
    cursor.close()
    conn.close()

    return new_book

def remove_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM books
        WHERE id = %s
        RETURNING id, title, author
        """, (book_id,)
    )
    deleted_book = dict_fetchone(cursor)
    conn.commit()
    
    if deleted_book:
        send_event(Config.ADMIN_TOPIC, {'event': 'book_deleted_events', 'book_id': book_id})

    cursor.close()
    conn.close()
    
    return deleted_book

def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = convert_dates(dict_fetchall(cursor))
    return users


# def list_borrowings():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM borrow_records")
#     borrow_records = convert_dates(dict_fetchall(cursor))
#     return borrow_records

def list_borrowings():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT br.id, br.borrow_date, br.return_date,
           u.id as user_id, u.first_name as first_name, u.last_name as last_name, u.email as user_email,
           b.id as book_id, b.title as book_title, b.author as book_author
    FROM borrow_records br
    JOIN users u ON br.user_id = u.id
    JOIN books b ON br.book_id = b.id
    """
    cursor.execute(query)
    borrow_records = convert_dates(dict_fetchall(cursor))
    transformed_records = [
        {
            "id": item["id"],
            "borrow_date": item["borrow_date"],
            "return_date": item["return_date"],
            "user": {
                "id": item["user_id"],
                "name": f"{item['first_name']} {item['last_name']}",
                "email": item["user_email"]
            },
            "book": {
                "id": item["book_id"],
                "title": item["book_title"],
                "author": item["book_author"]
            }
        } for item in borrow_records
    ]
    return transformed_records


def list_unavailable_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE available=%s", (False,))
    books = convert_dates(dict_fetchall(cursor))
    return books
