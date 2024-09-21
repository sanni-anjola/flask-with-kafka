from flask import Flask, request, jsonify
import psycopg2
import json
from kafka import KafkaConsumer, KafkaProducer
import logging
import threading
from datetime import datetime, timedelta
from util.thread_safe_iterator import ThreadSafeIterator
from util.helpers import dict_fetchall, dict_fetchone
# Configure basic logging
logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
log = app.logger

# Kafka producer
producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Database connection
def get_db_connection():
    print("Admin db Connecting...")
    conn = psycopg2.connect(host="admin_service_db", database="admin_service_db", user="postgres", password="mysecretpassword")
    print("Admin db Connected")
    return conn



def consume_kafka():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("Connecting to Kafka...")
        consumer = KafkaConsumer(
            'book_service_topic',
            bootstrap_servers='kafka:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='admin-consumer-group',  # Add a group ID for managing consumer offsets
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))

        )
        print("Kafka connected successfully, consuming messages...")

    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        return

    thread_safe_consumer = ThreadSafeIterator(consumer)

    for message in thread_safe_consumer:
        # Process the message
        data = message.value
        log.info(f"Received message: {data}")
        log.info(f"Received message: {data['event_data']}")
        if data['event'] == "user_created_events":
            log.info("User created event running")
            # Insert the new user and return the newly created user
            cursor.execute(
                """
                INSERT INTO users (id, email, first_name, last_name)
                VALUES (%s, %s, %s, %s)
                """,
                (data['event_data']['id'], data['event_data']['email'], data['event_data']['first_name'], data['event_data']['last_name'])
            )
 
            conn.commit()
            log.info("User added")


        if data["event"] == "borrow_events":
            # update book and add to borrow_records
            book_id = data['event_data']['book_id']
            user_id = data['event_data']['user_id']
            days = data['event_data']['days']
            
            borrow_date = datetime.now()
            return_date = borrow_date + timedelta(days=int(days))

            cursor.execute("INSERT INTO borrow_records (book_id, user_id, borrow_date, return_date) VALUES (%s, %s, %s)", (book_id, user_id, borrow_date, return_date))
            
            #  update book
            cursor.commit()


    cursor.close()
    conn.close()
            

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

# Insert the new book and return the newly created book
    cursor.execute(
        """
        INSERT INTO books (title, author, publisher, category)
        VALUES (%s, %s, %s)
        RETURNING id, title, author, publisher, category
        """,
        (data['title'], data['author'], data['publisher'], data['category'])
    )

# Fetch the newly created book
    new_book = dict_fetchone(cursor=cursor)    
    conn.commit()

    producer.send('admin_service_topic', {'event': 'book_added_events', 'event_data': new_book})

    return jsonify({'status': 'sucess', 'message': 'Book added successfully', 'data': new_book}), 201


@app.route('/books/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
    """
    DELETE FROM books
    WHERE id = %s
    RETURNING id, title, author
    """,
    (book_id,)
)

    # Fetch the deleted book
    deleted_book = dict_fetchone(cursor=cursor)

    conn.commit()

    if deleted_book:
        producer.send('admin_service_topic', {'event': 'book_deleted_events', 'book_id': book_id})

        return jsonify({'message': 'Book removed successfully', 'data': deleted_book}), 200

    else:
        return jsonify({'message': 'Book not found'}), 400

@app.route('/users', methods=['GET'])
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    users = dict_fetchall(cursor=cursor)
    return jsonify(users), 200

@app.route('/borrowings', methods=['GET'])
def list_borrowings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM borrow_records")

    borrow_records = dict_fetchall(cursor=cursor)
    return jsonify(borrow_records), 200


@app.route('/books/unavailable', methods=['GET'])
def list_unavailable_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE available=%s", (False,))

    books = dict_fetchall(cursor=cursor)
    return jsonify(books), 200


@app.route('/')
def index():
    log.info("Info: Index page was accessed")
    log.warning("Warning: Something non-critical happened")
    log.error("Error: Something went wrong!")
    return jsonify({'message': 'Kafka consumer is running in the background'})


if __name__ == "__main__":

        # Start the Kafka consumer thread
    consumer_thread = threading.Thread(target=consume_kafka)
    consumer_thread.daemon = True
    consumer_thread.start()

    app.run(host='0.0.0.0', port=5001)
