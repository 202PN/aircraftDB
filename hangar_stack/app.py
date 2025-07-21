from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from datetime import datetime
import logging
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Kafka producer (optional - will be None if Kafka is not available)
kafka_producer = None
try:
    from hangar_stack.hangar_kafka.kafka_producer import HangarStackProducer
    kafka_producer = HangarStackProducer()
    logger.info("Kafka producer initialized successfully")
except ImportError as e:
    logger.warning(f"Kafka dependencies not installed. Running without Kafka integration. Details: {e}")
except Exception as e:
    logger.warning(f"Failed to initialize Kafka producer: {e}. Running without Kafka integration.")

# Load the aircraft database
def load_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'data', 'aircraft_database.json')
    with open(db_path, 'r') as f:
        return json.load(f)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def home():
    """Home page showing database info and manufacturer list"""
    db = load_database()
    manufacturers = list(db.get('manufacturers', {}).keys())
    return render_template('home.html', 
                         manufacturers=manufacturers,
                         db_version=db.get('database_version'),
                         last_updated=db.get('last_updated'))

@app.route('/manufacturer/<manufacturer_name>')
def manufacturer(manufacturer_name):
    """Show aircraft list for a specific manufacturer"""
    db = load_database()
    manufacturers = db.get('manufacturers', {})
    if manufacturer_name not in manufacturers:
        return "Manufacturer not found", 404
    aircraft_list = manufacturers[manufacturer_name].get('aircraft', [])
    # Sort by introduction year
    sorted_aircraft = sorted(aircraft_list, key=lambda x: x.get('introduction_year', 9999))
    # Calculate summary stats
    active = sum(1 for a in aircraft_list if a.get('status') == 'Active')
    retired = sum(1 for a in aircraft_list if a.get('status') == 'Retired')
    development = sum(1 for a in aircraft_list if 'Development' in str(a.get('status', '')))
    return render_template('manufacturer.html',
                         manufacturer=manufacturer_name,
                         aircraft=sorted_aircraft,
                         total=len(aircraft_list),
                         active=active,
                         retired=retired,
                         development=development)

@app.route('/api/aircraft/<manufacturer_name>')
def aircraft_api(manufacturer_name):
    """API endpoint to get aircraft data as JSON"""
    db = load_database()
    manufacturers = db.get('manufacturers', {})
    if manufacturer_name not in manufacturers:
        return jsonify({'error': 'Manufacturer not found'}), 404
    aircraft_list = manufacturers[manufacturer_name].get('aircraft', [])
    sorted_aircraft = sorted(aircraft_list, key=lambda x: x.get('introduction_year', 9999))
    return jsonify({
        'manufacturer': manufacturer_name,
        'aircraft': sorted_aircraft
    })

@app.route('/aircraft/<manufacturer_name>/<path:designation>')
def aircraft_detail(manufacturer_name, designation):
    """Show detailed information for a specific aircraft"""
    # Track aircraft view with Kafka if available
    if kafka_producer:
        try:
            kafka_producer.send_aircraft_view(
                designation,
                request.remote_addr,
                request.headers.get('User-Agent', '')
            )
        except Exception as e:
            logger.error(f"Failed to track aircraft view: {e}")
    
    db = load_database()
    manufacturers = db.get('manufacturers', {})
    if manufacturer_name not in manufacturers:
        return "Manufacturer not found", 404
    # Find the specific aircraft
    aircraft = None
    for a in manufacturers[manufacturer_name].get('aircraft', []):
        if a.get('designation') == designation:
            aircraft = a
            break
    if not aircraft:
        return "Aircraft not found", 404
    return render_template('aircraft_detail.html',
                         aircraft=aircraft,
                         manufacturer=manufacturer_name)

# Add API endpoint for tracking aircraft views
@app.route('/api/aircraft/<path:designation>/view', methods=['POST'])
def track_aircraft_view(designation):
    """API endpoint for tracking aircraft views"""
    if kafka_producer:
        try:
            kafka_producer.send_aircraft_view(
                designation,
                request.remote_addr,
                request.headers.get('User-Agent', '')
            )
            return jsonify({'status': 'success', 'message': 'View tracked'})
        except Exception as e:
            logger.error(f"Failed to track aircraft view: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'success', 'message': 'Kafka not available'})

# Cleanup on app shutdown
import atexit

def cleanup():
    if kafka_producer:
        try:
            kafka_producer.close()
            logger.info("Kafka producer closed")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}")

# Register cleanup function to run when the app exits
atexit.register(cleanup)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 