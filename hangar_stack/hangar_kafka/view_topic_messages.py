#!/usr/bin/env python3
"""
Simple Kafka Topic Message Viewer

This script allows you to view messages on any Kafka topic with nice formatting.
"""

import json
import sys
import time
from datetime import datetime
from hangar_stack.hangar_kafka.kafka_consumer import HangarStackConsumer
from hangar_stack.hangar_kafka.kafka_config import TOPICS

def format_message(message):
    """Format a Kafka message for display"""
    try:
        # Try to parse as JSON
        data = json.loads(message.value) if isinstance(message.value, str) else message.value
        
        # Format based on event type
        event_type = data.get('event_type', 'unknown')
        
        if event_type == 'aircraft_view':
            return f"🛩️  Aircraft View: {data.get('aircraft_designation', 'Unknown')} | IP: {data.get('user_ip', 'Unknown')} | Time: {data.get('timestamp', 'Unknown')}"
        elif event_type == 'user_activity':
            return f"👤 User Activity: {data.get('activity_type', 'Unknown')} | IP: {data.get('user_ip', 'Unknown')} | Time: {data.get('timestamp', 'Unknown')}"
        elif event_type == 'search_query':
            return f"🔍 Search Query: '{data.get('query', 'Unknown')}' | IP: {data.get('user_ip', 'Unknown')} | Time: {data.get('timestamp', 'Unknown')}"
        elif event_type == 'data_update':
            return f"📝 Data Update: {data.get('update_type', 'Unknown')} | Entity: {data.get('entity_id', 'Unknown')} | Time: {data.get('timestamp', 'Unknown')}"
        else:
            return f"📨 {event_type}: {json.dumps(data, indent=2)}"
            
    except Exception as e:
        return f"📨 Raw Message: {message.value} (Error parsing: {e})"

def view_topic_messages(topic_name, timeout=60, max_messages=None):
    """View messages on a specific topic"""
    if topic_name not in TOPICS:
        print(f"❌ Error: Unknown topic '{topic_name}'")
        print("Available topics:")
        for name, topic in TOPICS.items():
            print(f"  {name}: {topic}")
        return
    
    topic = TOPICS[topic_name]
    print(f"🔍 Viewing messages on topic: {topic}")
    print(f"⏱️  Timeout: {timeout} seconds")
    if max_messages:
        print(f"📊 Max messages: {max_messages}")
    print("=" * 80)
    
    try:
        consumer = HangarStackConsumer(topic, group_id='viewer_group')
        
        start_time = time.time()
        message_count = 0
        
        print("📡 Listening for messages... (Press Ctrl+C to stop)")
        print()
        
        while time.time() - start_time < timeout:
            messages = consumer.consumer.poll(timeout_ms=1000)
            
            for tp, message_list in messages.items():
                for message in message_list:
                    message_count += 1
                    print(f"📨 Message #{message_count}:")
                    print(f"   Partition: {message.partition}")
                    print(f"   Offset: {message.offset}")
                    print(f"   Key: {message.key}")
                    print(f"   Content: {format_message(message)}")
                    print("-" * 80)
                    
                    if max_messages and message_count >= max_messages:
                        print(f"✅ Reached maximum messages ({max_messages})")
                        consumer.close()
                        return
        
        if message_count == 0:
            print("⚠️  No messages found on this topic.")
            print("💡 Try visiting some aircraft pages in the web app to generate messages!")
        else:
            print(f"✅ Viewed {message_count} messages")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            consumer.close()
        except:
            pass

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python view_topic_messages.py <topic_name> [timeout_seconds] [max_messages]")
        print("\nAvailable topics:")
        for topic_name, topic in TOPICS.items():
            print(f"  {topic_name}: {topic}")
        print("\nExamples:")
        print("  python view_topic_messages.py aircraft_views")
        print("  python view_topic_messages.py aircraft_views 30")
        print("  python view_topic_messages.py aircraft_views 60 10")
        sys.exit(1)
    
    topic_name = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    max_messages = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    view_topic_messages(topic_name, timeout, max_messages)

if __name__ == "__main__":
    main() 