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
python test_confluent.py

# Run basic Kafka tests
python test_kafka.py producer
python test_kafka.py consumer aircraft_views
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
from kafka_config import get_connection_info
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
from kafka_producer import HangarStackProducer
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
from kafka_producer import HangarStackProducer
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

### Latency Testing
```bash
# Measure end-to-end latency
python test_confluent.py
# Check the timing output in the logs
```

## 🔄 Continuous Testing

### Automated Test Script
Create a test runner script:

```bash
#!/bin/bash
# test_runner.sh

echo "🧪 Running HangarStack Test Suite"
echo "=================================="

# Run Confluent Cloud tests
echo "📊 Testing Confluent Cloud Integration..."
python test_confluent.py

if [ $? -eq 0 ]; then
    echo "✅ Confluent Cloud tests passed"
else
    echo "❌ Confluent Cloud tests failed"
    exit 1
fi

# Run basic Kafka tests
echo "📤 Testing Producer..."
python test_kafka.py producer

echo "📥 Testing Consumer..."
python test_kafka.py consumer aircraft_views

echo "🎉 All tests completed!"
```

### Scheduled Testing
```bash
# Add to crontab for daily testing
0 9 * * * cd /path/to/hangar_stack && ./test_runner.sh >> test_logs.txt 2>&1
```

## 📈 Test Metrics

### Success Criteria
- **Connection Success Rate**: 100%
- **Producer Success Rate**: 100%
- **Consumer Success Rate**: 100%
- **End-to-End Success Rate**: 100%
- **Average Latency**: < 100ms
- **Test Execution Time**: < 60 seconds

### Monitoring
```bash
# Track test results over time
echo "$(date): $(python test_confluent.py 2>&1 | grep -c '✅') tests passed" >> test_history.log

# Generate test report
echo "Test Report - $(date)" > test_report.txt
python test_confluent.py 2>&1 >> test_report.txt
```

## 🛠️ Test Development

### Adding New Tests
1. **Create test function** in appropriate test file
2. **Add assertions** for expected behavior
3. **Include error handling** for edge cases
4. **Document test purpose** and expected results
5. **Add to test suite** for automated execution

### Test Best Practices
- **Isolation**: Each test should be independent
- **Cleanup**: Always clean up resources after tests
- **Timeout**: Include appropriate timeouts
- **Logging**: Provide detailed logging for debugging
- **Documentation**: Document test purpose and expected results

## 📚 Additional Resources

- [Confluent Cloud Testing](https://docs.confluent.io/cloud/current/client-apps/testing.html)
- [Kafka Python Testing](https://kafka-python.readthedocs.io/en/master/testing.html)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## 📚 Where to Learn More

- [README (Project Tour & Learning Path)](README.md)
- [Confluent Cloud Setup Guide](CONFLUENT_SETUP_GUIDE.md)
- [Deployment & Operations Guide](DEPLOYMENT_OPERATIONS_GUIDE.md)
- [Application Summary](APPLICATION_SUMMARY.md)
- [Cleanup Summary](CLEANUP_SUMMARY.md)

---
