#!/usr/bin/env python3

import json
import sys
from pathlib import Path

def load_database():
    db_path = Path(__file__).parent.parent / 'data' / 'aircraft_database.json'
    with open(db_path) as f:
        return json.load(f)

def display_aircraft(aircraft):
    print("\n" + "="*80)
    print(f"{aircraft['designation']} {aircraft['name']}")
    print(f"Type: {aircraft['type']}")
    print(f"Service Entry: {aircraft['service_entry']}")
    
    print("\nSpecifications:")
    specs = aircraft['specifications']
    
    print("\nDimensions:")
    for key, value in specs['dimensions'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\nWeights:")
    for key, value in specs['weights'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\nPerformance:")
    for key, value in specs['performance'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nSource: {aircraft['source']}")

def main():
    db = load_database()
    
    print("\nAircraft Database Viewer")
    print("="*80)
    
    for manufacturer_id, manufacturer_data in db['manufacturers'].items():
        print(f"\n{manufacturer_data['name']} Aircraft:")
        print("-"*40)
        
        for aircraft in manufacturer_data['aircraft']:
            display_aircraft(aircraft)

if __name__ == "__main__":
    main() 