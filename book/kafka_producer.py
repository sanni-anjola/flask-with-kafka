import json
from kafka import KafkaProducer
from config import Config
import time
from kafka.errors import NoBrokersAvailable

def create_kafka_producer(retries=5, delay=5):
    for i in range(retries):
        try:
            producer = KafkaProducer(bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS or 'kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            return producer
        except NoBrokersAvailable:
            if i < retries - 1:
                time.sleep(delay)
                print(f"Retrying Kafka connection... ({i + 1}/{retries})")
            else:
                raise

producer = create_kafka_producer()

def send_event(topic, event):
    producer.send(topic, event)
    producer.flush()
