import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from hangar_stack.hangar_kafka.kafka_config import KAFKA_CONFIG, TOPICS, is_confluent_cloud, get_connection_info

class HangarStackConsumer:
    def __init__(self, topic, group_id='hangarstack_group'):
        # Configure consumer based on environment
        consumer_config = {
            'bootstrap_servers': KAFKA_CONFIG['bootstrap_servers'],
            'group_id': group_id,
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': True,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8'))
        }
        
        # Add Confluent Cloud specific configuration
        if is_confluent_cloud():
            consumer_config.update({
                'security_protocol': KAFKA_CONFIG['security_protocol'],
                'sasl_mechanism': KAFKA_CONFIG['sasl_mechanism'],
                'sasl_plain_username': KAFKA_CONFIG['sasl_username'],
                'sasl_plain_password': KAFKA_CONFIG['sasl_password'],
                'session_timeout_ms': KAFKA_CONFIG.get('session_timeout_ms', 45000),
                'heartbeat_interval_ms': KAFKA_CONFIG.get('heartbeat_interval_ms', 3000),
                'max_poll_interval_ms': KAFKA_CONFIG.get('max_poll_interval_ms', 300000),
                'auto_commit_interval_ms': KAFKA_CONFIG.get('auto_commit_interval_ms', 5000),
            })
            
            if KAFKA_CONFIG['ssl_cafile']:
                consumer_config['ssl_cafile'] = KAFKA_CONFIG['ssl_cafile']
        
        self.consumer = KafkaConsumer(topic, **consumer_config)
        self.logger = logging.getLogger(__name__)
        
        # Log connection info
        conn_info = get_connection_info()
        self.logger.info(f"Consumer initialized for {conn_info['type']}")
        self.logger.info(f"Bootstrap servers: {conn_info['bootstrap_servers']}")
        self.logger.info(f"Topic: {topic}, Group ID: {group_id}")

    def consume_messages(self):
        """Consume messages from Kafka topic"""
        try:
            for message in self.consumer:
                self.process_message(message)
        except KeyboardInterrupt:
            self.logger.info("Stopping consumer...")
        finally:
            self.consumer.close()

    def process_message(self, message):
        """Process individual message"""
        try:
            event = message.value
            event_type = event.get('event_type')
            
            if event_type == 'aircraft_view':
                self.handle_aircraft_view(event)
            elif event_type == 'user_activity':
                self.handle_user_activity(event)
            elif event_type == 'data_update':
                self.handle_data_update(event)
            elif event_type == 'search_query':
                self.handle_search_query(event)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def handle_aircraft_view(self, event):
        """Handle aircraft view events"""
        # Update view counters in cache/database
        aircraft_designation = event['aircraft_designation']
        self.logger.info(f"Aircraft viewed: {aircraft_designation}")
        
        # Here you could update Redis cache, database, or send to analytics
        # Example: update_view_count(aircraft_designation)

    def handle_user_activity(self, event):
        """Handle user activity events"""
        activity_type = event['activity_type']
        self.logger.info(f"User activity: {activity_type}")
        
        # Here you could track user sessions, behavior patterns, etc.
        # Example: update_user_analytics(event)

    def handle_data_update(self, event):
        """Handle data update events"""
        update_type = event['update_type']
        self.logger.info(f"Data updated: {update_type}")
        
        # Here you could invalidate caches, notify other services, etc.
        # Example: invalidate_cache(event['entity_id'])

    def handle_search_query(self, event):
        """Handle search query events"""
        query = event['query']
        self.logger.info(f"Search query: {query}")
        
        # Here you could update search analytics, improve search results, etc.
        # Example: update_search_analytics(query, event['filters'])

    def close(self):
        self.consumer.close() 