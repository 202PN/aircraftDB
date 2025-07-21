#!/usr/bin/env python3
"""
Test Flask Kafka Integration

This script tests if the Flask app's Kafka producer is working correctly.
"""

import requests
import time
from hangar_stack.hangar_kafka.kafka_consumer import HangarStackConsumer
from hangar_stack.hangar_kafka.kafka_config import TOPICS

def test_flask_aircraft_view():
    """Test if Flask app sends aircraft view events"""
    print("🧪 Testing Flask Aircraft View Tracking...")
    
    # Start consumer to listen for messages
    topic = TOPICS['aircraft_views']
    consumer = HangarStackConsumer(topic, group_id='test_flask_group')
    
    print("📡 Consumer started, listening for messages...")
    
    # Send a request to the Flask app
    print("🌐 Sending request to Flask app...")
    response = requests.get("http://localhost:5000/aircraft/Lockheed%20Martin/F-35")
    
    if response.status_code == 200:
        print("✅ Flask app responded successfully")
    else:
        print(f"❌ Flask app error: {response.status_code}")
        return False
    
    # Wait a moment for the message to be sent
    print("⏳ Waiting for Kafka message...")
    time.sleep(2)
    
    # Check for messages
    messages = consumer.consumer.poll(timeout_ms=3000)
    
    if messages:
        print("🎉 Message received from Flask app!")
        for tp, message_list in messages.items():
            for message in message_list:
                print(f"📨 Message: {message.value}")
        consumer.close()
        return True
    else:
        print("❌ No message received from Flask app")
        consumer.close()
        return False

def test_direct_kafka():
    """Test direct Kafka producer"""
    print("\n🧪 Testing Direct Kafka Producer...")
    
    from hangar_stack.hangar_kafka.kafka_producer import HangarStackProducer
    
    producer = HangarStackProducer()
    producer.send_aircraft_view('TEST-DIRECT', '127.0.0.1', 'Test-Agent')
    producer.close()
    
    print("✅ Direct producer test completed")

if __name__ == "__main__":
    test_direct_kafka()
    test_flask_aircraft_view() 