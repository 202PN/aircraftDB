#!/usr/bin/env python3
"""
Kafka Consumer Runner for HangarStack

This script runs the Kafka consumer to process events from various topics.
Useful for development and testing Kafka integration.
"""

import sys
import logging
from hangar_stack.hangar_kafka.kafka_consumer import HangarStackConsumer
from hangar_stack.hangar_kafka.kafka_config import TOPICS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to run Kafka consumer"""
    if len(sys.argv) < 2:
        print("Usage: python run_kafka_consumer.py <topic_name>")
        print("Available topics:")
        for topic_name, topic in TOPICS.items():
            print(f"  {topic_name}: {topic}")
        sys.exit(1)
    
    topic_name = sys.argv[1]
    
    if topic_name not in TOPICS:
        print(f"Error: Unknown topic '{topic_name}'")
        print("Available topics:")
        for topic_name, topic in TOPICS.items():
            print(f"  {topic_name}: {topic}")
        sys.exit(1)
    
    topic = TOPICS[topic_name]
    print(f"Starting consumer for topic: {topic}")
    
    try:
        consumer = HangarStackConsumer(topic)
        consumer.consume_messages()
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    except Exception as e:
        print(f"Error running consumer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 