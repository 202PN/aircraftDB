import json
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
from hangar_stack.hangar_kafka.kafka_config import KAFKA_CONFIG, TOPICS, is_confluent_cloud, get_connection_info

class HangarStackProducer:
    def __init__(self):
        # Configure producer based on environment
        producer_config = {
            'bootstrap_servers': KAFKA_CONFIG['bootstrap_servers'],
            'client_id': KAFKA_CONFIG['client_id'],
            'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
            'key_serializer': lambda k: k.encode('utf-8') if k else None,
        }
        
        # Add Confluent Cloud specific configuration
        if is_confluent_cloud():
            producer_config.update({
                'security_protocol': KAFKA_CONFIG['security_protocol'],
                'sasl_mechanism': KAFKA_CONFIG['sasl_mechanism'],
                'sasl_plain_username': KAFKA_CONFIG['sasl_username'],
                'sasl_plain_password': KAFKA_CONFIG['sasl_password'],
            })
            
            if KAFKA_CONFIG['ssl_cafile']:
                producer_config['ssl_cafile'] = KAFKA_CONFIG['ssl_cafile']
        
        self.producer = KafkaProducer(**producer_config)
        self.logger = logging.getLogger(__name__)
        
        # Log connection info
        conn_info = get_connection_info()
        self.logger.info(f"Producer initialized for {conn_info['type']}")
        self.logger.info(f"Bootstrap servers: {conn_info['bootstrap_servers']}")

    def send_aircraft_view(self, aircraft_designation, user_ip, user_agent):
        """Track aircraft page views"""
        event = {
            'event_type': 'aircraft_view',
            'aircraft_designation': aircraft_designation,
            'user_ip': user_ip,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._send_message(TOPICS['aircraft_views'], event, aircraft_designation)

    def send_user_activity(self, activity_type, details, user_ip):
        """Track user activities"""
        event = {
            'event_type': 'user_activity',
            'activity_type': activity_type,
            'details': details,
            'user_ip': user_ip,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._send_message(TOPICS['user_activity'], event, activity_type)

    def send_data_update(self, update_type, entity_id, changes):
        """Track data updates"""
        event = {
            'event_type': 'data_update',
            'update_type': update_type,
            'entity_id': entity_id,
            'changes': changes,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._send_message(TOPICS['data_updates'], event, update_type)

    def send_search_query(self, query, filters, user_ip):
        """Track search queries"""
        event = {
            'event_type': 'search_query',
            'query': query,
            'filters': filters,
            'user_ip': user_ip,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._send_message(TOPICS['search_queries'], event, query)

    def _send_message(self, topic, message, key=None):
        """Send message to Kafka topic"""
        try:
            future = self.producer.send(topic, value=message, key=key)
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            self.producer.flush()
        except Exception as e:
            self.logger.error(f"Failed to send message to {topic}: {e}")

    def _on_send_success(self, record_metadata):
        self.logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition}")

    def _on_send_error(self, excp):
        self.logger.error(f"Failed to send message: {excp}")

    def close(self):
        self.producer.close() 