#!/usr/bin/env python3
"""
Test script for Kafka integration in HangarStack

This script demonstrates how to use the Kafka producer and consumer
to track events in the HangarStack application.
"""

import time
import json
from kafka_producer import HangarStackProducer
from kafka_consumer import HangarStackConsumer
from kafka_config import TOPICS

def test_producer():
    """Test the Kafka producer by sending sample events"""
    print("Testing Kafka Producer...")
    
    producer = HangarStackProducer()
    
    # Test aircraft view tracking
    print("Sending aircraft view event...")
    producer.send_aircraft_view('F-16', '192.168.1.100', 'Mozilla/5.0')
    
    # Test user activity tracking
    print("Sending user activity event...")
    producer.send_user_activity('page_view', {
        'endpoint': 'aircraft_detail',
        'path': '/aircraft/Lockheed/F-16'
    }, '192.168.1.100')
    
    # Test search query tracking
    print("Sending search query event...")
    producer.send_search_query('F-16', {'manufacturer': 'Lockheed'}, '192.168.1.100')
    
    # Test data update tracking
    print("Sending data update event...")
    producer.send_data_update('aircraft_added', 'F-35', {
        'name': 'F-35 Lightning II',
        'manufacturer': 'Lockheed Martin'
    })
    
    print("All test events sent!")
    producer.close()

def test_consumer(topic_name='aircraft_views'):
    """Test the Kafka consumer by listening to events"""
    print(f"Testing Kafka Consumer for topic: {topic_name}")
    print("Press Ctrl+C to stop...")
    
    topic = TOPICS[topic_name]
    consumer = HangarStackConsumer(topic)
    
    try:
        consumer.consume_messages()
    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        consumer.close()

def main():
    """Main function to run tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_kafka.py producer    # Test producer")
        print("  python test_kafka.py consumer    # Test consumer")
        print("  python test_kafka.py consumer <topic>  # Test specific topic")
        print("\nAvailable topics:")
        for topic_name, topic in TOPICS.items():
            print(f"  {topic_name}: {topic}")
        return
    
    test_type = sys.argv[1]
    
    if test_type == 'producer':
        test_producer()
    elif test_type == 'consumer':
        topic_name = sys.argv[2] if len(sys.argv) > 2 else 'aircraft_views'
        if topic_name not in TOPICS:
            print(f"Unknown topic: {topic_name}")
            return
        test_consumer(topic_name)
    else:
        print(f"Unknown test type: {test_type}")

if __name__ == "__main__":
    main() 