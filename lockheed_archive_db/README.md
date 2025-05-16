# Aircraft Database Viewer

This project consists of a comprehensive aircraft database in JSON format and a Python display script that provides a user-friendly interface to view the data.

## Project Structure

```
.
├── data/
│   └── aircraft_database.json    # Aircraft database file
├── src/
│   └── display_aircraft.py       # Display script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Aircraft Classifications

The database includes various types of military aircraft:

### Fighters/Combat Aircraft
- F-22A Raptor (Air Superiority)
- F-35 Lightning II (Multi-role)
- F/A-18 Hornet/Super Hornet (Multi-role)
- F-15E Strike Eagle (Strike Fighter)
- F-5 Freedom Fighter/Tiger II (Light Fighter)
- F-14 Tomcat (Fleet Defense)
- F-104 Starfighter (Interceptor)

### Bombers
- B-2A Spirit (Stealth Strategic)
- B-21 Raider (Stealth Strategic)
- B-52H Stratofortress (Strategic)
- B-17G Flying Fortress (Heavy)
- B-29 Superfortress (Heavy)

### Reconnaissance/Surveillance
- SR-71A Blackbird (Strategic Reconnaissance)
- U-2S Dragon Lady (High-altitude Reconnaissance)
- RQ-4 Global Hawk (UAV ISR)
- E-2D Advanced Hawkeye (Airborne Early Warning)

### Attack/Ground Support
- A-10C Thunderbolt II (Close Air Support)
- A-6E Intruder (All-weather Attack)
- F-117 Nighthawk (Stealth Attack)

### Transport/Tanker
- C-5M Super Galaxy (Strategic Transport)
- C-130J-30 Super Hercules (Tactical Transport)
- C-2A(R) Greyhound (Carrier Onboard Delivery)

### Electronic Warfare
- EA-6B Prowler (Electronic Warfare)

### Unmanned Systems
- MQ-8 Fire Scout (Unmanned Helicopter)
- X-47B UCAS-D (Unmanned Combat Air System)
- RQ-4 Global Hawk (High-altitude UAV)

### Maritime Patrol
- P-2 Neptune (Maritime Patrol)
- P-3 Orion (Maritime Patrol)
- P-38 Lightning (Fighter/Reconnaissance)

### Commercial
- L-1011 TriStar (Commercial Airliner)

## Database Structure (aircraft_database.json)

The database is organized hierarchically:

- `database_version`: Version of the database
- `last_updated`: Timestamp of the last update
- `manufacturers`: Object containing aircraft manufacturers
  - Each manufacturer contains an array of `aircraft`
  - Each aircraft entry includes:
    - Basic information (designation, name, introduction year, status)
    - Specifications (dimensions, weights, performance)
    - Source information and verification date
    - Variants (if applicable)
    - Description
    - Additional details (armament, powerplant, etc. where applicable)

## Display Script (display_aircraft.py)

The display script provides a terminal-based interface with the following features:

### Main Functions

- `load_database()`: Loads and parses the JSON database
- `display_manufacturer_summary()`: Shows statistics for each manufacturer
- `create_timeline_view()`: Creates a chronological timeline of aircraft
- `display_aircraft_details()`: Shows detailed information for each aircraft

### Formatting Functions

- `format_weight()`: Formats weight values in pounds and kilograms
- `format_speed()`: Formats speed values in various units (Mach, knots, mph, km/h)
- `format_range()`: Formats range values in nautical miles and kilometers
- `format_ceiling()`: Formats service ceiling in feet and meters
- `format_dimensions()`: Formats dimensions in feet and meters

### User Interface Features

- Manufacturer selection menu
- Paginated display by manufacturer
- Color-coded status indicators
- Organized display of:
  - Manufacturer summaries
  - Aircraft timelines
  - Detailed specifications
  - Source information
  - Variants and descriptions

## Requirements

The `requirements.txt` file lists the Python packages needed to run this program:

- `rich`: Makes the text look nice in the terminal with colors and formatting
- `pandas`: Helps handle and organize data efficiently
- `requests`: Allows the program to fetch data from the internet
- `jsonschema`: Helps validate JSON data structure
- `PyYAML`: Handles YAML file format
- `pytest`: Used for testing the code

To install these packages, run:
```bash
pip install -r requirements.txt
```

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the display script:
```bash
python src/display_aircraft.py
```

3. Use the interactive menu to:
   - Select a manufacturer to view
   - Navigate through aircraft information
   - Press Enter to return to manufacturer selection
   - Enter 'Q' to quit

## Data Policy

- All specifications are from verified sources
- Sources include:
  - Official military documentation
  - Manufacturer specifications
  - National museums and archives
  - Government factsheets 