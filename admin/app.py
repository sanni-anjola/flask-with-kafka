from flask import Flask
from flask_restx import Api
from routes import api as routes_api
from kafka_consumer import start_kafka_consumer

app = Flask(__name__)
api = Api(app, version='1.0', title='Library API', description='A simple Library API')

# Register namespaces
api.add_namespace(routes_api)

if __name__ == "__main__":
    # Start Kafka consumer in background
    start_kafka_consumer()
    
    app.run(host='0.0.0.0', port=5001)
