import os
from dotenv import load_dotenv

load_dotenv()

# Confluent Cloud Configuration
KAFKA_CONFIG = {
    'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'client_id': 'hangarstack',
    'security_protocol': os.getenv('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT'),
    'sasl_mechanism': os.getenv('KAFKA_SASL_MECHANISM', 'PLAIN'),
    'sasl_username': os.getenv('KAFKA_USERNAME', ''),
    'sasl_password': os.getenv('KAFKA_PASSWORD', ''),
    'ssl_cafile': os.getenv('KAFKA_SSL_CA_FILE', None),
    'ssl_check_hostname': True,
    'ssl_verify_cert': True,
}

# Confluent Cloud specific settings
if KAFKA_CONFIG['security_protocol'] == 'SASL_SSL':
    # Additional settings for Confluent Cloud
    KAFKA_CONFIG.update({
        'session_timeout_ms': 45000,
        'heartbeat_interval_ms': 3000,
        'max_poll_interval_ms': 300000,
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
        'auto_commit_interval_ms': 5000,
    })

# Topic names
TOPICS = {
    'aircraft_views': 'hangarstack.aircraft.views',
    'user_activity': 'hangarstack.user.activity',
    'data_updates': 'hangarstack.data.updates',
    'search_queries': 'hangarstack.search.queries',
    'system_events': 'hangarstack.system.events'
}

# Environment detection
def is_confluent_cloud():
    """Check if using Confluent Cloud"""
    return KAFKA_CONFIG['security_protocol'] == 'SASL_SSL'

def get_connection_info():
    """Get connection information for debugging"""
    if is_confluent_cloud():
        return {
            'type': 'Confluent Cloud',
            'bootstrap_servers': KAFKA_CONFIG['bootstrap_servers'],
            'security_protocol': KAFKA_CONFIG['security_protocol'],
            'username': KAFKA_CONFIG['sasl_username'][:8] + '...' if KAFKA_CONFIG['sasl_username'] else 'Not set'
        }
    else:
        return {
            'type': 'Local Kafka',
            'bootstrap_servers': KAFKA_CONFIG['bootstrap_servers'],
            'security_protocol': KAFKA_CONFIG['security_protocol']
        } 