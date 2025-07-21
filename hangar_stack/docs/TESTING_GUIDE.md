# Testing Guide for HangarStack

This guide covers all testing procedures for the HangarStack application, including unit tests, integration tests, and Confluent Cloud connectivity tests.

## 🧪 Testing Overview

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end functionality testing
3. **Confluent Cloud Tests**: Event streaming integration testing
4. **Performance Tests**: Load and stress testing
5. **UI Tests**: Frontend functionality testing

## 🚀 Quick Test Suite

### Run All Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run comprehensive Confluent Cloud tests
python hangar_kafka/test_confluent.py

# Run basic Kafka tests
python hangar_kafka/test_kafka.py producer
python hangar_kafka/test_kafka.py consumer aircraft_views
```

## 📊 Confluent Cloud Integration Tests

### Comprehensive Integration Test
The main test script `test_confluent.py` performs a complete integration test:

```bash
python test_confluent.py
```

**What it tests:**
- ✅ **Connection Test**: Verifies Confluent Cloud connectivity
- ✅ **Producer Test**: Sends test events to all topics
- ✅ **Consumer Connection Test**: Verifies consumer connectivity
- ✅ **Consumer Test**: Receives and processes messages
- ✅ **End-to-End Test**: Complete message flow validation

**Expected Output:**
```
🚀 Confluent Cloud Integration Test
==================================================
🔗 Testing Confluent Cloud Connection...
Connection Type: Confluent Cloud
Bootstrap Servers: pkc-xxxxx.us-east1.gcp.confluent.cloud:9092
Security Protocol: SASL_SSL
Username: 7NOVAQSU...
✅ Using Confluent Cloud configuration

📤 Testing Producer...
✅ All test events sent successfully!

🔗 Testing Consumer Connection...
✅ Consumer connected successfully!
Available topics: ['hangarstack.user.activity', 'hangarstack.system.events', ...]

📥 Testing Consumer...
📨 Received message 1: {'event_type': 'aircraft_view', ...}
📨 Received message 2: {'event_type': 'aircraft_view', ...}
✅ Consumer test successful! Received 2 messages.

🔄 Testing End-to-End Message Flow...
✅ End-to-end test successful! Received: {'event_type': 'aircraft_view', ...}

🎉 All tests passed! Confluent Cloud integration is working correctly.
```

### Individual Component Tests

#### Producer Test
```bash
python test_kafka.py producer
```

**Tests:**
- Aircraft view event creation
- User activity tracking
- Search query logging
- Data update notifications

#### Consumer Test
```bash
python test_kafka.py consumer aircraft_views
```

**Tests:**
- Message consumption
- Event processing
- Connection stability
- Error handling

## 🔧 Test Configuration

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Confluent Cloud (if not already done)
python confluent_setup.py
```

### Test Environment Variables
```env
# Required for Confluent Cloud tests
KAFKA_BOOTSTRAP_SERVERS=your-cluster-endpoint:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_USERNAME=your-api-key
KAFKA_PASSWORD=your-api-secret
```

## 📋 Test Cases

### 1. Connection Tests

#### Confluent Cloud Connection
```python
def test_confluent_connection():
    """Test connection to Confluent Cloud"""
    conn_info = get_connection_info()
    assert conn_info['type'] == 'Confluent Cloud'
    assert 'confluent.cloud' in conn_info['bootstrap_servers']
```

#### Consumer Connection
```python
def test_consumer_connection():
    """Test consumer connection without waiting for messages"""
    consumer = HangarStackConsumer(topic, group_id='test_connection')
    topics = consumer.consumer.topics()
    assert len(topics) > 0
    consumer.close()
```

### 2. Producer Tests

#### Event Creation
```python
def test_producer():
    """Test the Kafka producer with Confluent Cloud"""
    producer = HangarStackProducer()
    
    # Test aircraft view tracking
    producer.send_aircraft_view('F-16', '192.168.1.100', 'Mozilla/5.0')
    
    # Test user activity tracking
    producer.send_user_activity('page_view', {
        'endpoint': 'aircraft_detail',
        'path': '/aircraft/Lockheed/F-16'
    }, '192.168.1.100')
    
    producer.close()
```

### 3. Consumer Tests

#### Message Consumption
```python
def test_consumer(topic_name='aircraft_views', timeout=30):
    """Test the Kafka consumer with Confluent Cloud"""
    consumer = HangarStackConsumer(topic)
    
    start_time = time.time()
    message_count = 0
    
    while time.time() - start_time < timeout:
        messages = consumer.consumer.poll(timeout_ms=1000)
        
        for tp, message_list in messages.items():
            for message in message_list:
                message_count += 1
                # Process message
                
        if message_count >= 5:
            break
    
    consumer.close()
    return message_count > 0
```

### 4. End-to-End Tests

#### Complete Message Flow
```python
def test_end_to_end():
    """Test end-to-end message flow"""
    # Start consumer thread
    consumer_thread = threading.Thread(target=consumer_thread)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Send test message
    producer = HangarStackProducer()
    producer.send_aircraft_view('TEST-AIRCRAFT', '127.0.0.1', 'Test-Agent')
    producer.close()
    
    # Wait for message to be received
    message = received_messages.get(timeout=10)
    assert message is not None
```

## 🐛 Troubleshooting Tests

### Common Test Failures

#### 1. Connection Timeout
**Error:** `Connection refused` or timeout
**Solution:**
```bash
# Check Confluent Cloud status
confluent kafka cluster list

# Verify credentials
cat .env | grep KAFKA

# Test connection manually
python -c "
from hangar_stack.hangar_kafka.kafka_config import get_connection_info
print(get_connection_info())
"
```

#### 2. Authentication Failed
**Error:** `Authentication failed`
**Solution:**
```bash
# Verify API key
confluent api-key list

# Check credentials in .env
grep -E "KAFKA_USERNAME|KAFKA_PASSWORD" .env

# Regenerate API key if needed
confluent api-key create --resource CLUSTER_ID
```

#### 3. Topic Not Found
**Error:** `Topic not found`
**Solution:**
```bash
# List topics
confluent kafka topic list

# Create missing topics
confluent kafka topic create hangarstack.aircraft.views --cluster CLUSTER_ID
```

#### 4. Consumer Hanging
**Error:** Consumer appears to hang indefinitely
**Solution:**
```bash
# Use the fixed test script
python test_confluent.py

# Check for messages in topic
confluent kafka topic describe hangarstack.aircraft.views --cluster CLUSTER_ID
```

### Debug Commands
```bash
# Run with verbose logging
python test_confluent.py 2>&1 | tee test_output.log

# Check for specific errors
grep -i error test_output.log
grep -i failed test_output.log
grep -i timeout test_output.log

# Test individual components
python -c "
from hangar_stack.hangar_kafka.kafka_producer import HangarStackProducer
producer = HangarStackProducer()
print('Producer created successfully')
producer.close()
"
```

## 📊 Performance Testing

### Load Testing
```bash
# Send high volume of events
python -c "
from hangar_stack.hangar_kafka.kafka_producer import HangarStackProducer
import time

producer = HangarStackProducer()
start_time = time.time()

for i in range(1000):
    producer.send_aircraft_view(f'F-{i}', '192.168.1.100', 'Load-Test')
    
end_time = time.time()
print(f'Sent 1000 events in {end_time - start_time:.2f} seconds')
producer.close()
"
```

## Related Documentation

- [Confluent Cloud Setup Guide](CONFLUENT_SETUP_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Deployment & Operations Guide](DEPLOYMENT_OPERATIONS_GUIDE.md)
- [Application Summary](APPLICATION_SUMMARY.md)