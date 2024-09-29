from flask import Flask, request, jsonify
import psycopg2
import json
from kafka import KafkaProducer, KafkaConsumer
import threading
import logging
from util.thread_safe_iterator import ThreadSafeIterator
from datetime import datetime, timedelta
from util.helpers import dict_fetchall, dict_fetchone

# Configure basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
log = app.logger

# Database connection
def get_db_connection():
    conn = psycopg2.connect(host="book_service_db", database="book_service_db", user="postgres", password="mysecretpassword")
    return conn

# Kafka producer
producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))


def consume_kafka():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        consumer = KafkaConsumer(
            'admin_service_topic',
            bootstrap_servers='kafka:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='book-consumer-group',  # Add a group ID for managing consumer offsets
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))

        )

    except Exception as e:
        log.error(f"Error connecting to Kafka: {e}")
        return

    thread_safe_consumer = ThreadSafeIterator(consumer)

    for message in thread_safe_consumer:
        # Process the message
        data = message.value

        if data['event'] == "book_added_events":
            # Insert the new user and return the newly created user
            cursor.execute(
        """
        INSERT INTO books (id, title, author, publisher, category)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (data['id'], data['title'], data['author'], data['publisher'], data['category'])
    )
 
            conn.commit()

        if data['event'] == 'book_deleted_events':
            cursor.execute(
                """
                DELETE FROM books
                WHERE id = %s
                """,
                (data['book_id'],)
            )

            # Commit the transaction
            conn.commit()


    cursor.close()
    conn.close()


@app.route('/users', methods=['POST'])
def enroll_user():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    
# Insert the new user and return the newly created user
    cursor.execute(
        """
        INSERT INTO users (email, first_name, last_name)
        VALUES (%s, %s, %s)
        RETURNING id, email, first_name, last_name
        """,
        (data['email'], data['first_name'], data['last_name'])
    )

# Fetch the newly created user
    new_user = dict_fetchone(cursor=cursor)    
    conn.commit()

    producer.send('book_service_topic', {'event': 'user_created_events', 'event_data': new_user})

    return jsonify({'status': 'sucess', 'message': 'User enrolled successfully', 'data': new_user}), 201


@app.route('/books', methods=['GET'])
def list_books():

    publisher = request.args.get('publisher')
    category = request.args.get('category')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE available=%s AND category=%s AND publisher=%s", (True, category, publisher))

    
    books = dict_fetchall(cursor=cursor)
    return jsonify(books), 200


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE book_id=%s", book_id)
    book = dict_fetchone(cursor=cursor)
    return jsonify(book), 200


@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    data = request.get_json()
    user_id = data['user_id']
    days = data['days']
    cursor.execute("SELECT * FROM books WHERE id=%s", book_id)
    book = dict_fetchone(cursor=cursor)

    if not book.available:
        return jsonify({'message': 'Book not available'}), 400
    

    cursor.execute("UPDATE books SET available=%s WHERE id=%s", False, book_id)
    event_data = {
        'book_id': book_id,
        'user_id': user_id,
        'days': days
    }

    producer.send('book_service_topic', {'event': 'borrow_events', 'event_data': event_data})

    return jsonify({'message': 'Book borrowed successfully'}), 200



@app.route("/hello", methods=['GET'])
def hello():
    return jsonify({'status': 'success', 'hello': "hello Flasky"}), 200


if __name__ == "__main__":

    # Start the Kafka consumer thread
    consumer_thread = threading.Thread(target=consume_kafka)
    consumer_thread.daemon = True
    consumer_thread.start()

    app.run(host='0.0.0.0', port=5000)
