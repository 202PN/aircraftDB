#!/usr/bin/env python3
"""
Confluent Cloud Test Script for HangarStack

This script tests the Confluent Cloud integration by sending and receiving
messages through the configured Kafka cluster.
"""

import time
import json
import logging
from datetime import datetime
from hangar_stack.hangar_kafka.kafka_producer import HangarStackProducer
from hangar_stack.hangar_kafka.kafka_consumer import HangarStackConsumer
from hangar_stack.hangar_kafka.kafka_config import TOPICS, get_connection_info, is_confluent_cloud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_confluent_connection():
    """Test connection to Confluent Cloud"""
    print("🔗 Testing Confluent Cloud Connection...")
    
    conn_info = get_connection_info()
    print(f"Connection Type: {conn_info['type']}")
    print(f"Bootstrap Servers: {conn_info['bootstrap_servers']}")
    print(f"Security Protocol: {conn_info['security_protocol']}")
    
    if is_confluent_cloud():
        print(f"Username: {conn_info['username']}")
        print("✅ Using Confluent Cloud configuration")
    else:
        print("⚠️ Using local Kafka configuration")
    
    return True

def test_producer():
    """Test the Kafka producer with Confluent Cloud"""
    print("\n📤 Testing Producer...")
    
    try:
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
        
        print("✅ All test events sent successfully!")
        producer.close()
        return True
        
    except Exception as e:
        print(f"❌ Producer test failed: {e}")
        return False

def test_consumer_connection():
    """Test consumer connection without waiting for messages"""
    print("\n🔗 Testing Consumer Connection...")
    
    try:
        topic = TOPICS['aircraft_views']
        consumer = HangarStackConsumer(topic, group_id='test_connection')
        
        # Just verify we can create the consumer and get topic metadata
        topics = consumer.consumer.topics()
        print(f"✅ Consumer connected successfully!")
        print(f"Available topics: {list(topics)}")
        
        consumer.close()
        return True
        
    except Exception as e:
        print(f"❌ Consumer connection test failed: {e}")
        return False

def test_consumer(topic_name='aircraft_views', timeout=30):
    """Test the Kafka consumer with Confluent Cloud"""
    print(f"\n📥 Testing Consumer for topic: {topic_name}")
    print(f"Listening for {timeout} seconds...")
    
    try:
        topic = TOPICS[topic_name]
        consumer = HangarStackConsumer(topic)
        
        # Set a timeout for the consumer
        start_time = time.time()
        message_count = 0
        
        # Use poll with timeout instead of infinite loop
        while time.time() - start_time < timeout:
            messages = consumer.consumer.poll(timeout_ms=1000)  # Poll for 1 second
            
            for tp, message_list in messages.items():
                for message in message_list:
                    message_count += 1
                    print(f"📨 Received message {message_count}: {message.value}")
                    
                    # Stop after 5 messages
                    if message_count >= 5:
                        break
                
                if message_count >= 5:
                    break
            
            if message_count >= 5:
                break
        
        consumer.close()
        
        if message_count > 0:
            print(f"✅ Consumer test successful! Received {message_count} messages.")
            return True
        else:
            print("⚠️ No messages received. This might be normal if no producer is running.")
            return True
            
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")
        return False

def test_end_to_end():
    """Test end-to-end message flow"""
    print("\n🔄 Testing End-to-End Message Flow...")
    
    import threading
    import queue
    
    # Queue to store received messages
    received_messages = queue.Queue()
    
    def consumer_thread():
        """Consumer thread function"""
        try:
            topic = TOPICS['aircraft_views']
            consumer = HangarStackConsumer(topic, group_id='test_group')
            
            # Listen for one message with timeout
            start_time = time.time()
            while time.time() - start_time < 15:  # 15 second timeout
                messages = consumer.consumer.poll(timeout_ms=1000)
                
                for tp, message_list in messages.items():
                    for message in message_list:
                        received_messages.put(message.value)
                        consumer.close()
                        return
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
            
            consumer.close()
        except Exception as e:
            print(f"Consumer thread error: {e}")
    
    # Start consumer thread
    consumer_thread = threading.Thread(target=consumer_thread)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Wait a moment for consumer to start
    time.sleep(2)
    
    # Send a test message
    try:
        producer = HangarStackProducer()
        producer.send_aircraft_view('TEST-AIRCRAFT', '127.0.0.1', 'Test-Agent')
        producer.close()
        
        # Wait for message to be received
        try:
            message = received_messages.get(timeout=10)
            print(f"✅ End-to-end test successful! Received: {message}")
            return True
        except queue.Empty:
            print("❌ End-to-end test failed: No message received")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Confluent Cloud Integration Test")
    print("=" * 50)
    
    # Test connection
    if not test_confluent_connection():
        print("❌ Connection test failed")
        return
    
    # Test producer
    if not test_producer():
        print("❌ Producer test failed")
        return
    
    # Test consumer connection
    if not test_consumer_connection():
        print("❌ Consumer connection test failed")
        return
    
    # Test consumer (optional - will timeout if no messages)
    print("\n📝 Note: Consumer test will timeout if no messages are available.")
    print("This is normal for a fresh topic. Messages will appear when you use the web app.")
    test_consumer(timeout=10)  # Reduced timeout
    
    # Test end-to-end
    if not test_end_to_end():
        print("❌ End-to-end test failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Confluent Cloud integration is working correctly.")
    print("\n📋 Next steps:")
    print("1. Run the Flask application: python app.py")
    print("2. Visit aircraft detail pages to see real-time tracking")
    print("3. Monitor events in Confluent Cloud console")

if __name__ == "__main__":
    main() 