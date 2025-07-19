from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Load the aircraft database
def load_database():
    with open('data/aircraft_database.json', 'r') as f:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 