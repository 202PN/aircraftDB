#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import jsonschema
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.prompt import Prompt
from rich.progress import track
import pandas as pd

class AircraftViewer:
    def __init__(self, database_path: Path, schema_path: Path):
        self.console = Console()
        self.database_path = database_path
        self.schema_path = schema_path
        self.data = self._load_database()
        self.schema = self._load_schema()
        self._validate_database()

    def _load_database(self) -> dict:
        """Load the aircraft database from JSON file."""
        try:
            with open(self.database_path) as f:
                return json.load(f)
        except Exception as e:
            self.console.print(f"[red]Error loading database: {e}[/red]")
            sys.exit(1)

    def _load_schema(self) -> dict:
        """Load the JSON schema for validation."""
        try:
            with open(self.schema_path) as f:
                return json.load(f)
        except Exception as e:
            self.console.print(f"[red]Error loading schema: {e}[/red]")
            sys.exit(1)

    def _validate_database(self):
        """Validate the database against the schema."""
        try:
            jsonschema.validate(instance=self.data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            self.console.print(f"[red]Database validation error: {e}[/red]")
            sys.exit(1)

    def list_manufacturers(self):
        """Display a list of all manufacturers in the database."""
        table = Table(title="Aircraft Manufacturers")
        table.add_column("Manufacturer", style="cyan")
        table.add_column("Number of Aircraft", justify="right", style="green")
        table.add_column("Active Aircraft", justify="right", style="blue")
        table.add_column("Last Updated", justify="right", style="yellow")
        
        for manufacturer in self.data["manufacturers"]:
            aircraft_list = self.data["manufacturers"][manufacturer]["aircraft"]
            total_count = len(aircraft_list)
            active_count = sum(1 for a in aircraft_list if a.get("status") == "Active")
            last_verified = max(a["last_verified"] for a in aircraft_list)
            
            table.add_row(
                manufacturer,
                str(total_count),
                str(active_count),
                last_verified
            )
        
        self.console.print(table)

    def show_aircraft_by_manufacturer(self, manufacturer: str):
        """Display all aircraft for a specific manufacturer."""
        if manufacturer not in self.data["manufacturers"]:
            self.console.print(f"[red]Manufacturer '{manufacturer}' not found[/red]")
            return

        table = Table(title=f"Aircraft by {manufacturer}")
        table.add_column("Designation", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Variants", style="blue")
        table.add_column("Introduction", style="magenta")
        table.add_column("Max Speed", style="red")
        
        aircraft_list = self.data["manufacturers"][manufacturer]["aircraft"]
        for aircraft in aircraft_list:
            variants = len(aircraft.get("variants", []))
            status = aircraft.get("status", "N/A")
            intro_year = str(aircraft.get("introduction_year", "N/A"))
            max_speed = f"M{aircraft['specifications']['performance']['max_speed']['mach']}"
            
            table.add_row(
                aircraft["designation"],
                aircraft["name"],
                status,
                str(variants),
                intro_year,
                max_speed
            )
        
        self.console.print(table)

    def show_aircraft_details(self, manufacturer: str, designation: str):
        """Display detailed information about a specific aircraft."""
        if manufacturer not in self.data["manufacturers"]:
            self.console.print(f"[red]Manufacturer '{manufacturer}' not found[/red]")
            return

        aircraft_list = self.data["manufacturers"][manufacturer]["aircraft"]
        aircraft = next((a for a in aircraft_list if a["designation"] == designation), None)
        
        if not aircraft:
            self.console.print(f"[red]Aircraft '{designation}' not found[/red]")
            return

        # Create a tree structure for the aircraft details
        tree = Tree(f"[bold cyan]{aircraft['designation']} - {aircraft['name']}[/bold cyan]")
        
        # Basic Information
        info = tree.add("[yellow]Basic Information[/yellow]")
        info.add(f"Status: {aircraft.get('status', 'N/A')}")
        info.add(f"Introduction Year: {aircraft.get('introduction_year', 'N/A')}")
        
        # Specifications
        specs = tree.add("[yellow]Specifications[/yellow]")
        
        # Dimensions
        dims = specs.add("Dimensions")
        for dim, values in aircraft["specifications"]["dimensions"].items():
            dims.add(f"{dim.title()}: {values['feet']:.2f} ft / {values['meters']:.2f} m")
        
        # Weights
        weights = specs.add("Weights")
        for weight, values in aircraft["specifications"]["weights"].items():
            weights.add(f"{weight.replace('_', ' ').title()}: {values['pounds']:,} lbs / {values['kilograms']:,} kg")
        
        # Performance
        perf = specs.add("Performance")
        perf_specs = aircraft["specifications"]["performance"]
        perf.add(f"Max Speed: {perf_specs['max_speed']['knots']} knots (Mach {perf_specs['max_speed']['mach']:.2f})")
        perf.add(f"Range: {perf_specs['range']['nautical_miles']:,} nm / {perf_specs['range']['kilometers']:,} km")
        perf.add(f"Service Ceiling: {perf_specs['service_ceiling']['feet']:,} ft / {perf_specs['service_ceiling']['meters']:,} m")
        
        # Source information
        source = tree.add("[yellow]Source Information[/yellow]")
        source.add(f"Type: {aircraft['source']['type']}")
        source.add(f"Name: {aircraft['source']['name']}")
        source.add(f"URL: {aircraft['source']['url']}")
        source.add(f"Last Verified: {aircraft['last_verified']}")
        
        # Variants
        if "variants" in aircraft and aircraft["variants"]:
            variants = tree.add("[yellow]Variants[/yellow]")
            for variant in aircraft["variants"]:
                var_node = variants.add(f"[bold blue]{variant['designation']} - {variant['name']}[/bold blue]")
                if variant["differences"]:
                    diff_node = var_node.add("Differences from base model")
                    self._add_differences(diff_node, variant["differences"])
        
        self.console.print(tree)

    def _add_differences(self, node, differences, prefix=""):
        """Recursively add differences to the tree node."""
        for key, value in differences.items():
            if isinstance(value, dict):
                sub_node = node.add(f"{prefix}{key}:")
                self._add_differences(sub_node, value, "")
            else:
                node.add(f"{prefix}{key}: {value}")

    def export_to_csv(self, output_path: str):
        """Export the database to CSV format."""
        records = []
        for manufacturer, data in self.data["manufacturers"].items():
            for aircraft in data["aircraft"]:
                record = {
                    "Manufacturer": manufacturer,
                    "Designation": aircraft["designation"],
                    "Name": aircraft["name"],
                    "Status": aircraft.get("status", "N/A"),
                    "Introduction Year": aircraft.get("introduction_year", "N/A"),
                    "Length (ft)": aircraft["specifications"]["dimensions"]["length"]["feet"],
                    "Wingspan (ft)": aircraft["specifications"]["dimensions"]["wingspan"]["feet"],
                    "Height (ft)": aircraft["specifications"]["dimensions"]["height"]["feet"],
                    "Empty Weight (lbs)": aircraft["specifications"]["weights"]["empty"]["pounds"],
                    "Max Takeoff Weight (lbs)": aircraft["specifications"]["weights"]["max_takeoff"]["pounds"],
                    "Max Speed (knots)": aircraft["specifications"]["performance"]["max_speed"]["knots"],
                    "Max Speed (Mach)": aircraft["specifications"]["performance"]["max_speed"]["mach"],
                    "Range (nm)": aircraft["specifications"]["performance"]["range"]["nautical_miles"],
                    "Service Ceiling (ft)": aircraft["specifications"]["performance"]["service_ceiling"]["feet"],
                    "Number of Variants": len(aircraft.get("variants", [])),
                    "Source Type": aircraft["source"]["type"],
                    "Last Verified": aircraft["last_verified"]
                }
                records.append(record)
        
        df = pd.DataFrame(records)
        df.to_csv(output_path, index=False)
        self.console.print(f"[green]Database exported to {output_path}[/green]")

    def search_aircraft(self, query: str):
        """Search for aircraft by designation, name, or specifications."""
        matches = []
        query = query.lower()
        query_words = query.split()
        
        for manufacturer, data in self.data["manufacturers"].items():
            for aircraft in data["aircraft"]:
                score = 0
                designation = aircraft["designation"].lower()
                name = aircraft["name"].lower()
                
                # Exact matches get highest score
                if query == designation or query == name:
                    score = 100
                # Starts with gets high score
                elif designation.startswith(query) or name.startswith(query):
                    score = 75
                # Contains gets medium score
                elif query in designation or query in name:
                    score = 50
                
                # Word matching
                for word in query_words:
                    # Match against designation and name
                    if word in designation or word in name:
                        score += 15
                    
                    # Match against specifications
                    specs = aircraft["specifications"]
                    
                    # Speed matching
                    if "mach" in word and specs["performance"]["max_speed"]["mach"] > 1.0:
                        score += 10
                    elif "supersonic" in word and specs["performance"]["max_speed"]["mach"] > 1.0:
                        score += 10
                    elif "subsonic" in word and specs["performance"]["max_speed"]["mach"] < 1.0:
                        score += 10
                    
                    # Size matching
                    if ("large" in word or "heavy" in word) and specs["weights"]["max_takeoff"]["pounds"] > 100000:
                        score += 10
                    elif ("small" in word or "light" in word) and specs["weights"]["max_takeoff"]["pounds"] < 50000:
                        score += 10
                    
                    # Status matching
                    if word == aircraft.get("status", "").lower():
                        score += 20
                    
                    # Year matching
                    if word.isdigit() and str(aircraft.get("introduction_year", "")) == word:
                        score += 25
                
                if score > 0:
                    matches.append({
                        "manufacturer": manufacturer,
                        "aircraft": aircraft,
                        "score": score
                    })
        
        # Sort by score
        matches.sort(key=lambda x: (-x["score"], x["aircraft"]["designation"]))
        
        if not matches:
            self.console.print(f"[red]No matches found for '{query}'[/red]")
            return None
        
        # Display results in a table with more details
        table = Table(title=f"Search Results for '{query}'")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Score", style="magenta", justify="right")
        table.add_column("Manufacturer", style="green")
        table.add_column("Designation", style="yellow")
        table.add_column("Name", style="blue")
        table.add_column("Status", style="red")
        table.add_column("Year", style="cyan", justify="right")
        table.add_column("Max Speed", style="green", justify="right")
        
        for i, match in enumerate(matches, 1):
            aircraft = match["aircraft"]
            max_speed = f"M{aircraft['specifications']['performance']['max_speed']['mach']:.1f}"
            table.add_row(
                str(i),
                str(match["score"]),
                match["manufacturer"],
                aircraft["designation"],
                aircraft["name"],
                aircraft.get("status", "N/A"),
                str(aircraft.get("introduction_year", "N/A")),
                max_speed
            )
        
        self.console.print(table)
        
        # If there are matches, let user select one
        if matches:
            choice = Prompt.ask(
                "Select aircraft number to view details (or press Enter to cancel)",
                default=""
            )
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                selected = matches[int(choice) - 1]
                self.show_aircraft_details(
                    selected["manufacturer"],
                    selected["aircraft"]["designation"]
                )
            return matches
        return None

    def select_manufacturer(self):
        """Display a menu to select a manufacturer."""
        manufacturers = list(self.data["manufacturers"].keys())
        
        table = Table(title="Select Manufacturer")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Manufacturer", style="green")
        table.add_column("Aircraft Count", style="yellow", justify="right")
        
        for i, manufacturer in enumerate(manufacturers, 1):
            count = len(self.data["manufacturers"][manufacturer]["aircraft"])
            table.add_row(str(i), manufacturer, str(count))
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "Select manufacturer number",
            choices=[str(i) for i in range(1, len(manufacturers) + 1)]
        )
        return manufacturers[int(choice) - 1]

    def select_aircraft(self, manufacturer: str):
        """Display a menu to select an aircraft from a manufacturer."""
        aircraft_list = self.data["manufacturers"][manufacturer]["aircraft"]
        
        table = Table(title=f"Select {manufacturer} Aircraft")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Designation", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Status", style="blue")
        
        for i, aircraft in enumerate(aircraft_list, 1):
            table.add_row(
                str(i),
                aircraft["designation"],
                aircraft["name"],
                aircraft.get("status", "N/A")
            )
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "Select aircraft number",
            choices=[str(i) for i in range(1, len(aircraft_list) + 1)]
        )
        return aircraft_list[int(choice) - 1]["designation"]

    def show_database_stats(self):
        """Display database statistics."""
        total_aircraft = sum(len(m["aircraft"]) for m in self.data["manufacturers"].values())
        total_variants = sum(
            sum(len(a.get("variants", [])) for a in m["aircraft"])
            for m in self.data["manufacturers"].values()
        )
        active_aircraft = sum(
            sum(1 for a in m["aircraft"] if a.get("status") == "Active")
            for m in self.data["manufacturers"].values()
        )
        
        stats = Table(title="Database Statistics")
        stats.add_column("Metric", style="cyan")
        stats.add_column("Value", justify="right", style="green")
        
        stats.add_row("Total Manufacturers", str(len(self.data["manufacturers"])))
        stats.add_row("Total Aircraft", str(total_aircraft))
        stats.add_row("Total Variants", str(total_variants))
        stats.add_row("Active Aircraft", str(active_aircraft))
        stats.add_row("Database Version", self.data["database_version"])
        stats.add_row("Last Updated", self.data["last_updated"])
        
        self.console.print(stats)

def main():
    console = Console()
    
    # Set up paths
    base_path = Path(__file__).parent.parent
    database_path = base_path / "data" / "aircraft_database.json"
    schema_path = base_path / "data" / "schema.json"
    
    viewer = AircraftViewer(database_path, schema_path)
    
    while True:
        console.print("\n[bold cyan]Aircraft Database Viewer[/bold cyan]")
        console.print("1. List all manufacturers")
        console.print("2. Browse aircraft by manufacturer")
        console.print("3. Quick search aircraft")
        console.print("4. Show database statistics")
        console.print("5. Export database to CSV")
        console.print("6. Exit")
        
        choice = Prompt.ask("\nEnter your choice", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            viewer.list_manufacturers()
        
        elif choice == "2":
            manufacturer = viewer.select_manufacturer()
            if manufacturer:
                designation = viewer.select_aircraft(manufacturer)
                if designation:
                    viewer.show_aircraft_details(manufacturer, designation)
        
        elif choice == "3":
            query = Prompt.ask("Enter search term (aircraft name or designation)")
            viewer.search_aircraft(query)
        
        elif choice == "4":
            viewer.show_database_stats()
        
        elif choice == "5":
            output_path = Prompt.ask("Enter output CSV path")
            viewer.export_to_csv(output_path)
        
        elif choice == "6":
            console.print("[green]Goodbye![/green]")
            break

if __name__ == "__main__":
    main() 