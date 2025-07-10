import json
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.tree import Tree
from rich.progress import track
from datetime import datetime
import webbrowser

def load_database(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        return json.load(f)

def format_weight(weight_dict: Dict) -> str:
    if not weight_dict:
        return "N/A"
    pounds = weight_dict.get('pounds', 'N/A')
    kg = weight_dict.get('kilograms', 'N/A')
    return f"{pounds:,} lbs ({kg:,} kg)"

def format_speed(speed_dict: Dict) -> str:
    if not speed_dict:
        return "N/A"
    if isinstance(speed_dict, dict):
        parts = []
        if 'mach' in speed_dict:
            parts.append(f"Mach {speed_dict['mach']}")
        if 'knots' in speed_dict:
            parts.append(f"{speed_dict['knots']} knots")
        if 'mph' in speed_dict:
            parts.append(f"{speed_dict['mph']} mph")
        if 'kmh' in speed_dict or 'km_h' in speed_dict:
            kmh = speed_dict.get('kmh', speed_dict.get('km_h', 'N/A'))
            parts.append(f"{kmh} km/h")
        return " / ".join(parts)
    return str(speed_dict)

def format_range(range_data):
    if not range_data:
        return "N/A"
    if isinstance(range_data, dict):
        nm = range_data.get('nautical_miles', 'N/A')
        km = range_data.get('kilometers', 'N/A')
        if isinstance(nm, (int, float)) and isinstance(km, (int, float)):
            return f"{int(nm):,} nm ({int(km):,} km)"
        return f"{nm} nm ({km} km)"
    return str(range_data)

def format_ceiling(ceiling):
    if not ceiling:
        return "N/A"
    if isinstance(ceiling, dict):
        ft = ceiling.get('feet', 'N/A')
        m = ceiling.get('meters', 'N/A')
        if isinstance(ft, (int, float)) and isinstance(m, (int, float)):
            return f"{int(ft):,} ft ({int(m):,} m)"
        return f"{ft} ft ({m} m)"
    return str(ceiling)

def format_dimensions(dim_dict: Dict) -> str:
    if not dim_dict:
        return "N/A"
    ft = dim_dict.get('feet', 'N/A')
    m = dim_dict.get('meters', 'N/A')
    if isinstance(ft, dict):  # Handle special cases like F-14's variable sweep wing
        return f"{ft.get('swept', 'N/A')}/{ft.get('unswept', 'N/A')} ft"
    return f"{ft} ft ({m} m)"

def create_timeline_view(aircraft_list: List[Dict]) -> Table:
    timeline = Table(show_header=True, header_style="bold magenta")
    timeline.add_column("Year")
    timeline.add_column("Aircraft")
    timeline.add_column("Status")
    
    for aircraft in sorted(aircraft_list, key=lambda x: x.get('introduction_year', 9999)):
        year = str(aircraft.get('introduction_year', 'N/A'))
        designation = f"{aircraft['designation']} {aircraft.get('name', '')}"
        status = aircraft.get('status', 'N/A')
        status_style = {
            'Active': 'green',
            'Retired': 'red',
            'Development': 'yellow',
            'Development/Testing': 'yellow'
        }.get(status, 'white')
        
        timeline.add_row(
            year,
            designation,
            Text(status, style=status_style)
        )
    
    return timeline

def display_aircraft_details(console: Console, aircraft: Dict):
    specs = aircraft.get('specifications', {})
    dimensions = specs.get('dimensions', {})
    weights = specs.get('weights', {})
    performance = specs.get('performance', {})
    
    # Create main info table
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="bold cyan")
    info_table.add_column("Value")
    
    info_table.add_row("Designation", aircraft.get('designation', 'N/A'))
    info_table.add_row("Name", aircraft.get('name', 'N/A'))
    info_table.add_row("Status", aircraft.get('status', 'N/A'))
    info_table.add_row("Introduction Year", str(aircraft.get('introduction_year', 'N/A')))
    
    # Dimensions
    info_table.add_row("", "")  # Spacing
    info_table.add_row("[bold]Dimensions[/bold]", "")
    info_table.add_row("Length", format_dimensions(dimensions.get('length', {})))
    info_table.add_row("Wingspan", format_dimensions(dimensions.get('wingspan', {})))
    info_table.add_row("Height", format_dimensions(dimensions.get('height', {})))
    
    # Weights
    info_table.add_row("", "")  # Spacing
    info_table.add_row("[bold]Weights[/bold]", "")
    info_table.add_row("Empty Weight", format_weight(weights.get('empty', {})))
    max_takeoff = weights.get('max_takeoff', weights.get('maximum_takeoff', {}))
    info_table.add_row("Max Takeoff Weight", format_weight(max_takeoff))
    
    # Performance
    info_table.add_row("", "")  # Spacing
    info_table.add_row("[bold]Performance[/bold]", "")
    info_table.add_row("Maximum Speed", format_speed(performance.get('max_speed', {})))
    if 'cruise_speed' in performance:
        info_table.add_row("Cruise Speed", format_speed(performance.get('cruise_speed', {})))
    info_table.add_row("Range", format_range(performance.get('range', {})))
    info_table.add_row("Service Ceiling", format_ceiling(performance.get('service_ceiling', {})))
    
    # Powerplant
    powerplant = specs.get('powerplant', {})
    if powerplant:
        info_table.add_row("", "")  # Spacing
        info_table.add_row("[bold]Powerplant[/bold]", "")
        engines = powerplant.get('engines', [])
        if engines:
            if isinstance(engines, list):
                for idx, engine in enumerate(engines):
                    info_table.add_row(
                        "Engine" if idx == 0 else "",
                        f"{engine.get('count', 1)}× {engine.get('type', 'N/A')}"
                    )
                    if 'power' in engine:
                        power = engine['power']
                        info_table.add_row(
                            "Power per Engine" if idx == 0 else "",
                            f"{power.get('horsepower', 'N/A')} hp ({power.get('kilowatts', 'N/A')} kW)"
                        )
                    elif 'thrust_per_engine' in engine:
                        thrust = engine['thrust_per_engine']
                        info_table.add_row(
                            "Thrust per Engine" if idx == 0 else "",
                            f"{thrust.get('pounds', 'N/A')} lbf ({thrust.get('kilonewtons', 'N/A')} kN)"
                        )
            else:
                info_table.add_row("Engine", str(engines))
    
    # Armament if present
    armament = aircraft.get('armament', {})
    if armament:
        info_table.add_row("", "")  # Spacing
        info_table.add_row("[bold]Armament[/bold]", "")
        if 'hardpoints' in armament:
            info_table.add_row("Hardpoints", str(armament['hardpoints']))
        if 'max_payload' in armament:
            info_table.add_row("Maximum Payload", format_weight(armament['max_payload']))
        if 'weapons' in armament:
            for idx, weapon in enumerate(armament['weapons']):
                info_table.add_row("Weapons" if idx == 0 else "", weapon)
    
    # Source information
    source = aircraft.get('source', {})
    if source:
        info_table.add_row("", "")  # Spacing
        info_table.add_row("[bold]Source Information[/bold]", "")
        if isinstance(source, dict):
            info_table.add_row("Source", source.get('name', 'N/A'))
            if 'url' in source:
                info_table.add_row("Source URL", source.get('url', 'N/A'))
        else:
            info_table.add_row("Source", str(source))
    
    # Description
    if 'description' in aircraft:
        info_table.add_row("", "")  # Spacing
        info_table.add_row("[bold]Description[/bold]", "")
        info_table.add_row("", aircraft['description'])
    
    # Display variants if any
    variants = aircraft.get('variants', [])
    if variants:
        info_table.add_row("", "")  # Spacing
        info_table.add_row("[bold]Variants[/bold]", "")
        for variant in variants:
            if isinstance(variant, dict):
                designation = variant.get('designation', 'N/A')
                name = variant.get('name', '')
                desc = variant.get('description', '')
                info_table.add_row(
                    designation,
                    f"{name}{': ' + desc if desc else ''}"
                )
            else:
                info_table.add_row("", str(variant))
    
    # Create a panel with the table
    title = Text(f"{aircraft.get('designation', 'Unknown')} {aircraft.get('name', '')}", style="bold magenta")
    panel = Panel(info_table, title=title, border_style="blue")
    console.print(panel)
    console.print()

    # Display source URL and offer to open in browser (after showing details)
    source = aircraft.get('source', {})
    if source and isinstance(source, dict) and 'url' in source:
        source_url = source.get('url')
        console.print(f"[bold cyan]Source URL:[/bold cyan] {source_url}")
        open_now = input("Open source page in default browser? (y/n): ")
        if open_now.lower() == 'y':
            try:
                webbrowser.open(source_url)
            except Exception as e:
                console.print(f"[red]Could not open URL: {e}[/red]")
    else:
        console.print("[bold magenta]No source URL available for this aircraft.[/bold magenta]")

def display_manufacturer_summary(console: Console, manufacturer: str, aircraft_list: List[Dict]):
    active = sum(1 for a in aircraft_list if a.get('status') == 'Active')
    retired = sum(1 for a in aircraft_list if a.get('status') == 'Retired')
    development = sum(1 for a in aircraft_list if 'Development' in str(a.get('status', '')))
    
    summary = Table.grid(padding=1)
    summary.add_column(style="bold yellow")
    summary.add_column()
    
    summary.add_row("Total Aircraft:", str(len(aircraft_list)))
    summary.add_row("Active:", Text(str(active), style="green"))
    summary.add_row("Retired:", Text(str(retired), style="red"))
    summary.add_row("In Development:", Text(str(development), style="yellow"))
    
    console.print(Panel(summary, title=f"[bold]{manufacturer} Summary[/bold]", border_style="yellow"))
    console.print()

def main():
    console = Console()
    db = load_database('data/aircraft_database.json')
    
    # Display header
    console.print("\n[bold blue]Aircraft Database Viewer[/bold blue]\n")
    console.print(f"Database Version: {db.get('database_version')}")
    console.print(f"Last Updated: {db.get('last_updated')}\n")
    
    manufacturers = db.get('manufacturers', {})
    
    while True:
        # Show manufacturer menu
        console.print("\n[bold yellow]Select a manufacturer to view:[/bold yellow]")
        manufacturer_list = list(manufacturers.keys())
        for idx, manufacturer in enumerate(manufacturer_list, 1):
            console.print(f"{idx}. {manufacturer}")
        console.print("Q. Quit")
        
        choice = input("\nEnter your choice (1-{} or Q): ".format(len(manufacturer_list)))
        
        if choice.upper() == 'Q':
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(manufacturer_list):
                manufacturer = manufacturer_list[idx]
                console.clear()
                console.print("\n[bold blue]Aircraft Database Viewer[/bold blue]\n")
                
                # Display manufacturer header
                console.rule(f"[bold yellow]{manufacturer}[/bold yellow]")
                console.print()
                
                # Get and sort aircraft list
                data = manufacturers[manufacturer]
                aircraft_list = data.get('aircraft', [])
                sorted_aircraft = sorted(aircraft_list, key=lambda x: x.get('introduction_year', 9999))
                
                # Display manufacturer summary
                display_manufacturer_summary(console, manufacturer, sorted_aircraft)
                
                # Display timeline
                console.print(Panel(
                    create_timeline_view(sorted_aircraft),
                    title="[bold]Aircraft Timeline[/bold]",
                    border_style="blue"
                ))
                console.print()
                
                # Aircraft selection loop
                while True:
                    console.print("[bold yellow]Select an aircraft to view details:[/bold yellow]")
                    for aidx, aircraft in enumerate(sorted_aircraft, 1):
                        designation = aircraft.get('designation', 'N/A')
                        name = aircraft.get('name', '')
                        console.print(f"{aidx}. {designation} {name}")
                    console.print("B. Back to manufacturer selection")
                    console.print("Q. Quit")
                    achoice = input(f"\nEnter your choice (1-{len(sorted_aircraft)}, B, or Q): ")
                    if achoice.upper() == 'B':
                        console.clear()
                        break
                    elif achoice.upper() == 'Q':
                        console.clear()
                        return
                    try:
                        aidx = int(achoice) - 1
                        if 0 <= aidx < len(sorted_aircraft):
                            console.clear()
                            display_aircraft_details(console, sorted_aircraft[aidx])
                            input("\nPress Enter to return to aircraft list...")
                            console.clear()
                        else:
                            console.print("[red]Invalid choice. Please try again.[/red]")
                    except ValueError:
                        console.print("[red]Invalid input. Please enter a number, B, or Q.[/red]")
                
                input("\nPress Enter to return to manufacturer selection...")
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number or Q to quit.[/red]")
    
    # Display database metadata at the end
    if 'metadata' in db:
        metadata = db['metadata']
        console.print(Panel(
            "\n".join([
                "[bold]Data Policy:[/bold]",
                "✓ Verification Required" if metadata['data_policy']['verification_required'] else "✗ Verification Not Required",
                "\n[bold]Source Requirements:[/bold]",
                "\n".join(f"• {req}" for req in metadata['data_policy']['source_requirements'])
            ]),
            title="[bold]Database Metadata[/bold]",
            border_style="green"
        ))

if __name__ == "__main__":
    main() 