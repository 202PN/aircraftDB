# Confluent Cloud Setup Guide for HangarStack

## Quick Start

### Prerequisites
- Confluent Cloud account (free tier available)
- Python 3.8 or higher
- Internet connection

### Step 1: Create Confluent Cloud Account
1. Go to [Confluent Cloud](https://www.confluent.io/confluent-cloud/)
2. Click "Start Free" or "Sign Up"
3. Complete the registration process
4. Verify your email address

### Step 2: Run Automated Setup
```bash
# Run the automated setup script
python hangar_kafka/confluent_setup.py
```

This script will:
- Install Confluent 
- Login to your Confluent Cloud account
- Create environment and cluster
- Generate API keys
- Create Kafka topics
- Generate `.env` file
- Test the connection

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Test Integration
```bash
# Run comprehensive integration tests
python hangar_kafka/test_confluent.py
```

Expected output:
```
Confluent Cloud Integration Test
==================================================
Testing Confluent Cloud Connection...
✅ Using Confluent Cloud configuration

📤 Testing Producer...
✅ All test events sent successfully!

🔗 Testing Consumer Connection...
✅ Consumer connected successfully!

📥 Testing Consumer...
✅ Consumer test successful! Received X messages.

🔄 Testing End-to-End Message Flow...
✅ End-to-end test successful!

🎉 All tests passed! Confluent Cloud integration is working correctly.
```

### Step 5: Run Application
```bash
python3 -m hangar_stack.app
```

## Manual Setup (Alternative)

If you prefer to set up Confluent Cloud manually:

### 1. Install Confluent CLI

**macOS:**
```bash
brew install confluentinc/tap/cli
```

**Linux:**
```bash
curl -L --http1.1 https://cnfl.io/cli | sh -s -- -b /usr/local/bin
```

**Windows:**
Download from [Confluent CLI Installation](https://docs.confluent.io/confluent-cli/current/install.html)

### 2. Login to Confluent Cloud
```bash
confluent login
```

### 3. Create Environment
```bash
confluent environment create hangarstack
confluent environment use hangarstack
```

### 4. Create Cluster
```bash
confluent kafka cluster create hangarstack-cluster \
  --cloud aws \
  --region us-west-2 \
  --type basic
```

### 5. Create API Key
```bash
# Get cluster ID
confluent kafka cluster list

# Create API key (replace CLUSTER_ID with actual ID)
confluent api-key create --resource CLUSTER_ID
```

### 6. Create Topics
```bash
# Get cluster ID
confluent kafka cluster list

# Create topics (replace CLUSTER_ID with actual ID)
confluent kafka topic create hangarstack.aircraft.views --cluster CLUSTER_ID
confluent kafka topic create hangarstack.user.activity --cluster CLUSTER_ID
confluent kafka topic create hangarstack.data.updates --cluster CLUSTER_ID
confluent kafka topic create hangarstack.search.queries --cluster CLUSTER_ID
confluent kafka topic create hangarstack.system.events --cluster CLUSTER_ID
```

### 7. Create .env File
Create a `.env` file in your project root:
```env
# Confluent Cloud Configuration
KAFKA_BOOTSTRAP_SERVERS=your-cluster-endpoint:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_USERNAME=your-api-key
KAFKA_PASSWORD=your-api-secret

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=true
```

## Configuration Details

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `KAFKA_BOOTSTRAP_SERVERS` | Confluent Cloud cluster endpoint | `pkc-12345.us-west-2.aws.confluent.cloud:9092` |
| `KAFKA_SECURITY_PROTOCOL` | Security protocol | `SASL_SSL` |
| `KAFKA_SASL_MECHANISM` | SASL mechanism | `PLAIN` |
| `KAFKA_USERNAME` | API key | `ABC123DEF456` |
| `KAFKA_PASSWORD` | API secret | `xyz789abc012` |

### Kafka Topics
The application uses these topics:
- `hangarstack.aircraft.views` - Aircraft page view events
- `hangarstack.user.activity` - User activity tracking
- `hangarstack.data.updates` - Data modification events
- `hangarstack.search.queries` - Search query events
- `hangarstack.system.events` - System-level events

## Testing

### Comprehensive Integration Test
```bash
python hangar_kafka/test_confluent.py
```

This test covers:
- Connection verification
- Producer functionality
- Consumer connectivity
- Message consumption
- End-to-end message flow

### Individual Component Tests
```bash
# Test producer only
python hangar_kafka/test_kafka.py producer

# Test consumer only
python hangar_kafka/test_kafka.py consumer aircraft_views
```

### Monitor in Confluent Cloud Console
1. Go to [Confluent Cloud Console](https://confluent.cloud/)
2. Navigate to your cluster
3. Go to "Topics" to see message activity
4. Go to "Monitoring" to see cluster metrics
5. Check "Data Flow" for real-time message visualization

## Troubleshooting

### Common Issues

#### 1. Connection Refused
**Error:** `Connection refused`
**Solution:** 
- Check your bootstrap servers in `.env` file
- Verify API credentials are correct
- Ensure Confluent Cloud cluster is running

#### 2. Authentication Failed
**Error:** `Authentication failed`
**Solution:** 
- Verify your API key and secret in `.env` file
- Check that credentials match Confluent Cloud console
- Ensure API key has proper permissions

#### 3. Topic Not Found
**Error:** `Topic not found`
**Solution:** 
- Ensure topics are created in Confluent Cloud
- Check topic names match exactly
- Verify cluster ID is correct

#### 4. SSL Certificate Issues
**Error:** `SSL certificate verify failed`
**Solution:** 
- Check your SSL configuration
- Verify Confluent Cloud endpoint is correct
- Ensure system has updated CA certificates

#### 5. Consumer Hanging/Timeout
**Error:** Consumer appears to hang or timeout
**Solution:**
- This was fixed in the latest test script
- Use `python hangar_kafka/test_confluent.py` for proper timeout handling
- Check that topics have messages to consume

### Debug Commands
```bash
# Check Confluent CLI version
confluent version

# List environments
confluent environment list

# List clusters
confluent kafka cluster list

# List topics
confluent kafka topic list

# Describe cluster
confluent kafka cluster describe CLUSTER_ID

# Check API keys
confluent api-key list

# Test connection with CLI
confluent kafka cluster describe CLUSTER_ID
```

### Log Analysis
The test script provides detailed logging:
```bash
# Run with verbose logging
python hangar_kafka/test_confluent.py 2>&1 | tee test_output.log

# Check for specific errors
grep -i error test_output.log
grep -i failed test_output.log
```

## Production Deployment

### Environment Variables (Production)
```env
# Confluent Cloud Configuration
KAFKA_BOOTSTRAP_SERVERS=your-production-cluster:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_USERNAME=your-production-api-key
KAFKA_PASSWORD=your-production-api-secret

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=false
```

### Performance Optimization
- Connection Pooling: Configure appropriate connection limits
- Batch Processing: Optimize producer batch sizes
- Consumer Groups: Use multiple consumer instances for load balancing
- Monitoring: Set up alerts for cluster health and performance

### Security Best Practices
- API Key Rotation: Regularly rotate API keys
- Network Security: Use VPC peering for enhanced security
- Access Control: Implement proper RBAC policies
- Audit Logging: Enable comprehensive audit trails

## Monitoring and Analytics

### Confluent Cloud Metrics
- Cluster Health: Monitor broker status and performance
- Topic Metrics: Track message throughput and lag
- Consumer Groups: Monitor consumer health and performance
- Network: Track connection and bandwidth usage

### Application Metrics
- Event Volume: Track events per second
- Latency: Monitor end-to-end message processing time
- Error Rates: Track failed message deliveries
- Consumer Lag: Monitor message processing delays

## Success Indicators

### Integration Success
- All test cases pass: `python hangar_kafka/test_confluent.py`
- Messages flow end-to-end without errors
- Consumer receives messages within expected timeframes
- No connection timeouts or authentication failures

### Performance Benchmarks
- Event Throughput: 1000+ events per second
- Latency: Sub-100ms event processing
- Reliability: 99.9% uptime
- Scalability: Automatic scaling based on demand

## Maintenance

### Regular Tasks
- Health Checks: Run `python hangar_kafka/test_confluent.py` weekly
- API Key Rotation: Rotate keys every 90 days
- Topic Monitoring: Check topic growth and cleanup old data
- Performance Review: Monitor metrics and optimize as needed

### Updates and Upgrades
- Confluent CLI: Keep CLI updated to latest version
- Dependencies: Update Python packages regularly
- Configuration: Review and update settings as needed

## Additional Resources

- [Confluent Cloud Documentation](https://docs.confluent.io/cloud/current/overview.html)
- [Kafka Python Client Documentation](https://kafka-python.readthedocs.io/)
- [Confluent Cloud Pricing](https://www.confluent.io/confluent-cloud/pricing/)
- [Community Support](https://community.confluent.io/)

## Where to Learn More

- [README (Project Tour & Learning Path)](README.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Deployment & Operations Guide](DEPLOYMENT_OPERATIONS_GUIDE.md)
- [Application Summary](APPLICATION_SUMMARY.md)

## Related Documentation

- [Confluent Cloud Setup Guide](CONFLUENT_SETUP_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Deployment & Operations Guide](DEPLOYMENT_OPERATIONS_GUIDE.md)
- [Application Summary](APPLICATION_SUMMARY.md)

---
