from kafka import KafkaConsumer
import json
from db import get_db_connection
from util.thread_safe_iterator import ThreadSafeIterator
from config import Config

def consume_kafka():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        consumer = KafkaConsumer(
            Config.ADMIN_TOPIC or 'admin_service_topic',
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS or 'kafka:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=Config.KAFKA_CONSUMER_GROUP or 'book-consumer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        return

    thread_safe_consumer = ThreadSafeIterator(consumer)

    for message in thread_safe_consumer:
        data = message.value
        process_event(data, cursor, conn)

    cursor.close()
    conn.close()

def process_event(data, cursor, conn):
    if data['event'] == "book_added_events":
        cursor.execute(
            """
            INSERT INTO books (id, title, author, publisher, category)
            VALUES (%s, %s, %s, %s, %s)
            """, 
            (data['event_data']['id'], data['event_data']['title'], data['event_data']['author'], data['event_data']['publisher'], data['event_data']['category'])
        )
        conn.commit()

    elif data['event'] == "book_deleted_events":
        cursor.execute(
            """
            DELETE FROM books WHERE id = %s
            """, 
            (data['book_id'],)
        )
        conn.commit()

def start_kafka_consumer():
    import threading
    consumer_thread = threading.Thread(target=consume_kafka)
    consumer_thread.daemon = True
    consumer_thread.start()
