from kafka import KafkaConsumer
import json
import threading
from datetime import datetime, timedelta
from db import get_db_connection
from util.thread_safe_iterator import ThreadSafeIterator
from config import Config
import logging

logging.basicConfig(level=logging.INFO)

def consume_kafka():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        consumer = KafkaConsumer(
            Config.BOOK_TOPIC or 'book_service_topic',
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS or 'kafka:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=Config.KAFKA_CONSUMER_GROUP or 'admin-consumer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        thread_safe_consumer = ThreadSafeIterator(consumer)

        for message in thread_safe_consumer:
            data = message.value
            process_event(data, cursor, conn)

    except Exception as e:
        print(f"Error consuming Kafka messages: {e}")
    finally:
        cursor.close()
        conn.close()

def process_event(data, cursor, conn):
    if data['event'] == "user_created_events":
        cursor.execute(
            """
            INSERT INTO users (id, email, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            """,
            (data['event_data']['id'], data['event_data']['email'], data['event_data']['first_name'], data['event_data']['last_name'])
        )
        conn.commit()

    if data["event"] == "borrow_events":
        book_id = int(data['event_data']['book_id'])
        user_id = int(data['event_data']['user_id'])
        days = int(data['event_data']['days'])
        
        borrow_date = datetime.now()
        return_date = borrow_date + timedelta(days=int(days))
       
        cursor.execute("INSERT INTO borrow_records (book_id, user_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)", (book_id, user_id, borrow_date, return_date))
        cursor.execute("UPDATE books SET available=%s WHERE id=%s", (False, book_id))

        conn.commit()

def start_kafka_consumer():
    consumer_thread = threading.Thread(target=consume_kafka)
    consumer_thread.daemon = True
    consumer_thread.start()
