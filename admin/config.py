import os

class Config:
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'admin_service_db')
    DB_NAME = os.getenv('DB_NAME', 'admin_service_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'mysecretpassword')
    
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    KAFKA_CONSUMER_GROUP = 'admin-consumer-group'
    BOOK_TOPIC = 'book_service_topic'
    ADMIN_TOPIC = 'admin_service_topic'
