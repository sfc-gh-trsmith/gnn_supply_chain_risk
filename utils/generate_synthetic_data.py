#!/usr/bin/env python3
"""
generate_synthetic_data.py - Generate synthetic supply chain data for GNN training

This script generates four related datasets that simulate a realistic supply chain
for an Electric Vehicle (EV) battery module, following the DRD specification.

Datasets generated:
1. vendors.csv - Vendor Master (50 suppliers with geographic distribution)
2. materials.csv - Material Master (26 parts in hierarchy: 1 FIN, 5 SEMI, 20 RAW)
3. purchase_orders.csv - Purchase Orders (100+ supplier-to-part relationships)
4. trade_data.csv - External Trade Data with HIDDEN BOTTLENECK pattern

The "Vulcan Materials Refiner" pattern:
    A single Tier-2 supplier (Vulcan Materials Refiner) supplies 60% of the
    battery manufacturers' lithium needs, creating a hidden single point of
    failure that the GNN should discover.

Usage:
    python utils/generate_synthetic_data.py
    python utils/generate_synthetic_data.py --output-dir data/synthetic
"""

import argparse
import csv
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


# =============================================================================
# Configuration
# =============================================================================

RANDOM_SEED = 42
OUTPUT_DIR = Path("data/synthetic")

# Geographic distribution: 40% Asia, 30% North America, 30% Europe/SA
# Uses ISO 3166-1 alpha-3 codes for Plotly Choropleth compatibility
REGIONS = {
    "CHN": {"name": "China", "weight": 0.15, "cities": ["Shanghai", "Shenzhen", "Beijing", "Guangzhou"]},
    "KOR": {"name": "South Korea", "weight": 0.15, "cities": ["Seoul", "Busan", "Ulsan", "Daegu"]},
    "JPN": {"name": "Japan", "weight": 0.10, "cities": ["Tokyo", "Osaka", "Nagoya", "Yokohama"]},
    "USA": {"name": "United States", "weight": 0.20, "cities": ["Charlotte", "Detroit", "Houston", "Phoenix"]},
    "MEX": {"name": "Mexico", "weight": 0.10, "cities": ["Monterrey", "Mexico City", "Guadalajara", "Tijuana"]},
    "DEU": {"name": "Germany", "weight": 0.10, "cities": ["Munich", "Stuttgart", "Frankfurt", "Berlin"]},
    "CHL": {"name": "Chile", "weight": 0.10, "cities": ["Santiago", "Antofagasta", "Valparaiso", "Concepcion"]},
    "AUS": {"name": "Australia", "weight": 0.05, "cities": ["Perth", "Sydney", "Melbourne", "Brisbane"]},
    "COD": {"name": "DR Congo", "weight": 0.05, "cities": ["Lubumbashi", "Kolwezi", "Kinshasa", "Likasi"]},
}

# Region risk scores (for seeding the REGIONS table)
# Uses ISO 3166-1 alpha-3 codes
REGION_RISKS = {
    "CHN": {"base": 0.3, "geopolitical": 0.5, "natural": 0.2, "infrastructure": 0.7},
    "KOR": {"base": 0.2, "geopolitical": 0.3, "natural": 0.3, "infrastructure": 0.9},
    "JPN": {"base": 0.2, "geopolitical": 0.1, "natural": 0.5, "infrastructure": 0.95},
    "USA": {"base": 0.1, "geopolitical": 0.1, "natural": 0.2, "infrastructure": 0.9},
    "MEX": {"base": 0.3, "geopolitical": 0.2, "natural": 0.3, "infrastructure": 0.6},
    "DEU": {"base": 0.1, "geopolitical": 0.1, "natural": 0.1, "infrastructure": 0.95},
    "CHL": {"base": 0.4, "geopolitical": 0.2, "natural": 0.6, "infrastructure": 0.7},  # High earthquake risk
    "AUS": {"base": 0.2, "geopolitical": 0.1, "natural": 0.3, "infrastructure": 0.85},
    "COD": {"base": 0.7, "geopolitical": 0.8, "natural": 0.3, "infrastructure": 0.3},  # High risk
}

# HS Codes for trade data
HS_CODES = {
    "2836.91": "Lithium Carbonate",
    "2825.20": "Lithium Hydroxide",
    "8106.00": "Cobalt and Cobalt Products",
    "7408.11": "Copper Wire",
    "7409.11": "Copper Plates",
    "8507.60": "Lithium-ion Batteries",
    "8541.40": "Semiconductor Devices",
    "3904.10": "PVC Compounds",
    "7601.10": "Aluminum Unwrought",
}


# =============================================================================
# Data Generation Functions
# =============================================================================

def generate_vendors(num_vendors: int = 50) -> List[Dict]:
    """Generate vendor master data with realistic company names and geographic distribution."""
    
    # Realistic company name patterns by region and specialty
    company_templates = {
        "battery": [
            "Samsung SDI Co.", "LG Energy Solution", "CATL", "BYD Battery",
            "Panasonic Energy", "SK On", "AESC", "CALB", "EVE Energy",
            "Gotion High-Tech", "Farasis Energy", "Svolt Energy"
        ],
        "lithium": [
            "Albemarle Corp", "SQM Mining", "Livent Corp", "Ganfeng Lithium",
            "Tianqi Lithium", "Pilbara Minerals", "Allkem Ltd", "Sigma Lithium"
        ],
        "cobalt": [
            "Glencore Cobalt", "Umicore SA", "Freeport Cobalt", "Chemaf SPRL",
            "ERG Africa", "Katanga Mining"
        ],
        "copper": [
            "Codelco", "Freeport-McMoRan", "BHP Copper", "Southern Copper",
            "Antofagasta PLC", "First Quantum"
        ],
        "electronics": [
            "Texas Instruments", "Infineon Technologies", "NXP Semiconductors",
            "STMicroelectronics", "Renesas Electronics", "ON Semiconductor"
        ],
        "materials": [
            "BASF Materials", "Umicore Materials", "Sumitomo Chemical",
            "Mitsubishi Chemical", "3M Advanced Materials", "DuPont Electronics"
        ],
        "generic": [
            "Alpha Industries", "Beta Components", "Gamma Manufacturing",
            "Delta Materials", "Epsilon Tech", "Zeta Precision", "Theta Systems"
        ]
    }
    
    vendors = []
    used_names = set()
    
    # Select regions based on weights
    region_codes = list(REGIONS.keys())
    region_weights = [REGIONS[r]["weight"] for r in region_codes]
    
    for i in range(num_vendors):
        vendor_id = f"V{10001 + i}"
        
        # Select region based on weights
        region = random.choices(region_codes, weights=region_weights, k=1)[0]
        city = random.choice(REGIONS[region]["cities"])
        
        # Select company name based on region specialty
        if region in ["CHL", "AUS"] and random.random() < 0.6:
            category = "lithium"
        elif region == "COD" and random.random() < 0.7:
            category = "cobalt"
        elif region in ["KOR", "CHN", "JPN"] and random.random() < 0.4:
            category = "battery"
        elif region in ["USA", "DEU"] and random.random() < 0.3:
            category = "electronics"
        else:
            category = random.choice(["materials", "generic", "copper"])
        
        # Get unique name
        available_names = [n for n in company_templates.get(category, company_templates["generic"]) 
                          if n not in used_names]
        if not available_names:
            # Generate a unique name
            name = f"{category.title()} Corp {i+1}"
        else:
            name = random.choice(available_names)
        used_names.add(name)
        
        # Generate phone number
        phone_prefixes = {
            "CHN": "+86", "KOR": "+82", "JPN": "+81", "USA": "+1",
            "MEX": "+52", "DEU": "+49", "CHL": "+56", "AUS": "+61", "COD": "+243"
        }
        phone = f"{phone_prefixes[region]}-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        
        # Financial health score (0.3 to 0.95)
        financial_health = round(random.uniform(0.3, 0.95), 2)
        
        vendors.append({
            "VENDOR_ID": vendor_id,
            "NAME": name,
            "COUNTRY_CODE": region,
            "CITY": city,
            "PHONE": phone,
            "TIER": 1,
            "FINANCIAL_HEALTH_SCORE": financial_health
        })
    
    return vendors


def generate_materials() -> Tuple[List[Dict], List[Dict]]:
    """Generate material master data with EV battery hierarchy."""
    
    materials = []
    bom = []
    
    # Finished Goods (1)
    finished = [
        {"id": "M-1000", "desc": "EV Battery Pack 85kWh", "group": "FIN", "unit": "PC", "crit": 1.0}
    ]
    
    # Semi-finished (5)
    semi_finished = [
        {"id": "M-2001", "desc": "Battery Module 400V", "group": "SEMI", "unit": "PC", "crit": 0.95},
        {"id": "M-2002", "desc": "Battery Management System", "group": "SEMI", "unit": "PC", "crit": 0.9},
        {"id": "M-2003", "desc": "Thermal Management Assembly", "group": "SEMI", "unit": "PC", "crit": 0.85},
        {"id": "M-2004", "desc": "Battery Enclosure Assembly", "group": "SEMI", "unit": "PC", "crit": 0.8},
        {"id": "M-2005", "desc": "High-Voltage Harness", "group": "SEMI", "unit": "PC", "crit": 0.85}
    ]
    
    # Raw Materials (20)
    raw_materials = [
        # Lithium compounds (critical)
        {"id": "M-3001", "desc": "Lithium Hydroxide Grade A", "group": "RAW", "unit": "KG", "crit": 0.95},
        {"id": "M-3002", "desc": "Lithium Carbonate Battery Grade", "group": "RAW", "unit": "KG", "crit": 0.95},
        # Cathode materials
        {"id": "M-3003", "desc": "Cobalt Oxide Powder", "group": "RAW", "unit": "KG", "crit": 0.9},
        {"id": "M-3004", "desc": "Nickel Sulfate Battery Grade", "group": "RAW", "unit": "KG", "crit": 0.85},
        {"id": "M-3005", "desc": "Manganese Dioxide", "group": "RAW", "unit": "KG", "crit": 0.75},
        # Anode materials
        {"id": "M-3006", "desc": "Synthetic Graphite Anode", "group": "RAW", "unit": "KG", "crit": 0.85},
        {"id": "M-3007", "desc": "Silicon Anode Additive", "group": "RAW", "unit": "KG", "crit": 0.7},
        # Copper components
        {"id": "M-3008", "desc": "Copper Foil 8 Micron", "group": "RAW", "unit": "KG", "crit": 0.85},
        {"id": "M-3009", "desc": "Copper Busbar 5mm", "group": "RAW", "unit": "KG", "crit": 0.8},
        # Aluminum
        {"id": "M-3010", "desc": "Aluminum Foil 15 Micron", "group": "RAW", "unit": "KG", "crit": 0.8},
        {"id": "M-3011", "desc": "Aluminum Housing Profile", "group": "RAW", "unit": "KG", "crit": 0.7},
        # Electrolyte
        {"id": "M-3012", "desc": "Electrolyte LiPF6 Solution", "group": "RAW", "unit": "L", "crit": 0.9},
        # Separator
        {"id": "M-3013", "desc": "Ceramic Coated Separator", "group": "RAW", "unit": "M2", "crit": 0.9},
        # Electronics
        {"id": "M-3014", "desc": "BMS Controller IC", "group": "RAW", "unit": "PC", "crit": 0.85},
        {"id": "M-3015", "desc": "Cell Monitoring ASIC", "group": "RAW", "unit": "PC", "crit": 0.85},
        {"id": "M-3016", "desc": "Power MOSFET Module", "group": "RAW", "unit": "PC", "crit": 0.8},
        # Thermal
        {"id": "M-3017", "desc": "Thermal Interface Material", "group": "RAW", "unit": "KG", "crit": 0.75},
        {"id": "M-3018", "desc": "Cooling Plate Aluminum", "group": "RAW", "unit": "PC", "crit": 0.7},
        # Wiring
        {"id": "M-3019", "desc": "High-Voltage Cable 35mm2", "group": "RAW", "unit": "M", "crit": 0.8},
        {"id": "M-3020", "desc": "Connector Assembly HV", "group": "RAW", "unit": "PC", "crit": 0.75}
    ]
    
    # Combine all materials
    all_materials = finished + semi_finished + raw_materials
    
    for mat in all_materials:
        materials.append({
            "MATERIAL_ID": mat["id"],
            "DESCRIPTION": mat["desc"],
            "MATERIAL_GROUP": mat["group"],
            "UNIT_OF_MEASURE": mat["unit"],
            "CRITICALITY_SCORE": mat["crit"],
            "INVENTORY_DAYS": random.randint(15, 60)
        })
    
    # Generate BOM relationships
    bom_id = 1
    
    # Finished Good -> Semi-finished
    for semi in semi_finished:
        bom.append({
            "BOM_ID": f"BOM-{bom_id:04d}",
            "PARENT_MATERIAL_ID": "M-1000",
            "CHILD_MATERIAL_ID": semi["id"],
            "QUANTITY_PER_UNIT": random.randint(1, 4)
        })
        bom_id += 1
    
    # Semi-finished -> Raw materials (logical groupings)
    semi_to_raw = {
        "M-2001": ["M-3001", "M-3002", "M-3003", "M-3004", "M-3006", "M-3008", "M-3010", "M-3012", "M-3013"],  # Battery Module
        "M-2002": ["M-3014", "M-3015", "M-3016"],  # BMS
        "M-2003": ["M-3017", "M-3018"],  # Thermal
        "M-2004": ["M-3011"],  # Enclosure
        "M-2005": ["M-3009", "M-3019", "M-3020"]  # Harness
    }
    
    for parent, children in semi_to_raw.items():
        for child in children:
            bom.append({
                "BOM_ID": f"BOM-{bom_id:04d}",
                "PARENT_MATERIAL_ID": parent,
                "CHILD_MATERIAL_ID": child,
                "QUANTITY_PER_UNIT": round(random.uniform(0.5, 10), 2)
            })
            bom_id += 1
    
    return materials, bom


def generate_purchase_orders(vendors: List[Dict], materials: List[Dict], num_orders: int = 120) -> List[Dict]:
    """Generate purchase orders linking vendors to materials."""
    
    orders = []
    
    # Filter materials by type
    raw_materials = [m for m in materials if m["MATERIAL_GROUP"] == "RAW"]
    semi_materials = [m for m in materials if m["MATERIAL_GROUP"] == "SEMI"]
    
    # Material-to-vendor affinity (based on regions and specialties)
    # Lithium materials should come from CHL, AUS, CHN
    # Cobalt from COD, CHN
    # Electronics from USA, JPN, KOR, DEU
    material_region_affinity = {
        "M-3001": ["CHL", "AUS", "CHN"],  # Lithium Hydroxide
        "M-3002": ["CHL", "AUS", "CHN"],  # Lithium Carbonate
        "M-3003": ["COD", "CHN"],  # Cobalt
        "M-3004": ["CHN", "JPN"],  # Nickel
        "M-3006": ["CHN", "JPN"],  # Graphite
        "M-3008": ["CHL", "USA"],  # Copper
        "M-3009": ["CHL", "USA"],  # Copper
        "M-3014": ["USA", "JPN", "KOR", "DEU"],  # BMS IC
        "M-3015": ["USA", "JPN", "KOR", "DEU"],  # ASIC
        "M-3016": ["DEU", "JPN", "USA"],  # MOSFET
    }
    
    base_date = datetime(2023, 1, 1)
    
    for i in range(num_orders):
        po_id = f"PO-{9001 + i}"
        
        # Select material (prefer raw materials for realistic distribution)
        if random.random() < 0.85:
            material = random.choice(raw_materials)
        else:
            material = random.choice(semi_materials)
        
        # Select vendor based on affinity
        preferred_regions = material_region_affinity.get(
            material["MATERIAL_ID"], 
            list(REGIONS.keys())
        )
        
        # Find vendors in preferred regions
        preferred_vendors = [v for v in vendors if v["COUNTRY_CODE"] in preferred_regions]
        if not preferred_vendors:
            preferred_vendors = vendors
        
        vendor = random.choice(preferred_vendors)
        
        # Generate order details
        if material["MATERIAL_GROUP"] == "RAW":
            quantity = random.randint(500, 10000)
            unit_price = round(random.uniform(5, 500), 2)
        else:
            quantity = random.randint(50, 500)
            unit_price = round(random.uniform(500, 5000), 2)
        
        order_date = base_date + timedelta(days=random.randint(0, 365))
        delivery_date = order_date + timedelta(days=random.randint(14, 90))
        
        orders.append({
            "PO_ID": po_id,
            "VENDOR_ID": vendor["VENDOR_ID"],
            "MATERIAL_ID": material["MATERIAL_ID"],
            "QUANTITY": quantity,
            "UNIT_PRICE": unit_price,
            "ORDER_DATE": order_date.strftime("%Y-%m-%d"),
            "DELIVERY_DATE": delivery_date.strftime("%Y-%m-%d"),
            "STATUS": random.choice(["OPEN", "CLOSED", "CLOSED", "CLOSED"])
        })
    
    return orders


def generate_trade_data(vendors: List[Dict], num_records: int = 150) -> List[Dict]:
    """
    Generate external trade data with the HIDDEN BOTTLENECK pattern.
    
    The key insight: "Vulcan Materials Refiner" is a hidden Tier-2 supplier
    that supplies 60% of the lithium to multiple Tier-1 battery manufacturers.
    This creates a single point of failure that the GNN should discover.
    """
    
    trade_records = []
    
    # The hidden Tier-2 suppliers (not in our vendor list)
    # Uses ISO 3166-1 alpha-3 codes
    tier2_suppliers = [
        # THE BOTTLENECK - high concentration
        {"name": "Vulcan Materials Refiner", "country": "CHL", "specialty": "lithium", "concentration": 0.60},
        # Other Tier-2 suppliers
        {"name": "Pacific Copper Mining", "country": "CHL", "specialty": "copper", "concentration": 0.25},
        {"name": "Congo Cobalt Mines", "country": "COD", "specialty": "cobalt", "concentration": 0.40},
        {"name": "Jiangxi Graphite Ltd", "country": "CHN", "specialty": "graphite", "concentration": 0.30},
        {"name": "Tokyo Chemical Works", "country": "JPN", "specialty": "electrolyte", "concentration": 0.35},
        {"name": "Bavaria Specialty Metals", "country": "DEU", "specialty": "nickel", "concentration": 0.20},
        {"name": "Queensland Minerals", "country": "AUS", "specialty": "lithium", "concentration": 0.15},
        {"name": "Atacama Mining Corp", "country": "CHL", "specialty": "lithium", "concentration": 0.10},
        {"name": "Shanghai Battery Materials", "country": "CHN", "specialty": "cathode", "concentration": 0.25},
        {"name": "Korean Precision Chemicals", "country": "KOR", "specialty": "separator", "concentration": 0.30},
    ]
    
    # Map specialties to HS codes
    specialty_to_hs = {
        "lithium": ["2836.91", "2825.20"],
        "copper": ["7408.11", "7409.11"],
        "cobalt": ["8106.00"],
        "graphite": ["3801.10"],  # Added for graphite
        "electrolyte": ["2826.19"],  # Added for electrolyte
        "nickel": ["7502.10"],  # Added for nickel
        "cathode": ["8507.90"],  # Battery parts
        "separator": ["3920.10"],  # Plastic films
    }
    
    # Identify battery manufacturers in our vendor list (likely consignees)
    battery_manufacturers = [v for v in vendors if any(
        keyword in v["NAME"].lower() 
        for keyword in ["battery", "energy", "sdi", "lg", "catl", "byd", "panasonic", "sk", "aesc"]
    )]
    
    # If no battery manufacturers found, use random vendors from KOR, JPN, CHN
    if not battery_manufacturers:
        battery_manufacturers = [v for v in vendors if v["COUNTRY_CODE"] in ["KOR", "JPN", "CHN"]][:10]
    
    base_date = datetime(2023, 1, 1)
    bol_id = 88001
    
    for i in range(num_records):
        # Select a Tier-2 supplier
        tier2 = random.choice(tier2_suppliers)
        
        # Select a consignee (our Tier-1 vendors)
        # For the bottleneck (Vulcan), ensure high concentration to battery manufacturers
        if tier2["name"] == "Vulcan Materials Refiner":
            # 60% of lithium shipments go to battery manufacturers
            if random.random() < tier2["concentration"] and battery_manufacturers:
                consignee = random.choice(battery_manufacturers)
            else:
                consignee = random.choice(vendors)
        else:
            # Normal distribution
            if random.random() < tier2["concentration"]:
                # Use specialty matching
                if tier2["specialty"] == "lithium" and battery_manufacturers:
                    consignee = random.choice(battery_manufacturers)
                else:
                    consignee = random.choice(vendors)
            else:
                consignee = random.choice(vendors)
        
        # Select HS code based on specialty
        hs_codes = specialty_to_hs.get(tier2["specialty"], ["8507.60"])
        hs_code = random.choice(hs_codes)
        hs_desc = HS_CODES.get(hs_code, "Industrial Materials")
        
        # Generate shipment details
        ship_date = base_date + timedelta(days=random.randint(0, 365))
        weight_kg = random.randint(5000, 50000)
        value_usd = weight_kg * random.uniform(10, 100)
        
        # Ports based on countries (ISO-3 codes)
        ports = {
            "CHL": "Port of Antofagasta",
            "COD": "Port of Dar es Salaam",
            "CHN": "Port of Shanghai",
            "JPN": "Port of Yokohama",
            "KOR": "Port of Busan",
            "DEU": "Port of Hamburg",
            "AUS": "Port of Fremantle",
            "USA": "Port of Los Angeles",
            "MEX": "Port of Manzanillo"
        }
        
        trade_records.append({
            "BOL_ID": f"BL-{bol_id}",
            "SHIPPER_NAME": tier2["name"],
            "SHIPPER_COUNTRY": tier2["country"],
            "CONSIGNEE_NAME": consignee["NAME"],
            "CONSIGNEE_COUNTRY": consignee["COUNTRY_CODE"],
            "HS_CODE": hs_code,
            "HS_DESCRIPTION": hs_desc,
            "SHIP_DATE": ship_date.strftime("%Y-%m-%d"),
            "WEIGHT_KG": weight_kg,
            "VALUE_USD": round(value_usd, 2),
            "PORT_OF_ORIGIN": ports.get(tier2["country"], "Unknown Port"),
            "PORT_OF_DESTINATION": ports.get(consignee["COUNTRY_CODE"], "Unknown Port")
        })
        
        bol_id += 1
    
    return trade_records


def generate_regions() -> List[Dict]:
    """Generate region risk data."""
    regions = []
    for code, risks in REGION_RISKS.items():
        regions.append({
            "REGION_CODE": code,
            "REGION_NAME": REGIONS[code]["name"],
            "BASE_RISK_SCORE": risks["base"],
            "GEOPOLITICAL_RISK": risks["geopolitical"],
            "NATURAL_DISASTER_RISK": risks["natural"],
            "INFRASTRUCTURE_SCORE": risks["infrastructure"]
        })
    return regions


# =============================================================================
# File Output Functions
# =============================================================================

def write_csv(data: List[Dict], filepath: Path, fieldnames: List[str] = None):
    """Write data to CSV file."""
    if not data:
        print(f"[WARN] No data to write to {filepath}")
        return
    
    if fieldnames is None:
        fieldnames = list(data[0].keys())
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"[OK] Generated {filepath} ({len(data)} records)")


def main():
    """Main entry point for data generation."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic supply chain data for GNN training"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Output directory for CSV files (default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=RANDOM_SEED,
        help=f"Random seed for reproducibility (default: {RANDOM_SEED})"
    )
    parser.add_argument(
        "--num-vendors",
        type=int,
        default=50,
        help="Number of vendors to generate (default: 50)"
    )
    parser.add_argument(
        "--num-orders",
        type=int,
        default=120,
        help="Number of purchase orders to generate (default: 120)"
    )
    parser.add_argument(
        "--num-trade-records",
        type=int,
        default=150,
        help="Number of trade records to generate (default: 150)"
    )
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(args.seed)
    
    print("=" * 60)
    print("GNN Supply Chain Risk - Synthetic Data Generator")
    print("=" * 60)
    print(f"Output directory: {args.output_dir}")
    print(f"Random seed: {args.seed}")
    print()
    
    # Generate data
    print("Generating vendors...")
    vendors = generate_vendors(args.num_vendors)
    
    print("Generating materials and BOM...")
    materials, bom = generate_materials()
    
    print("Generating purchase orders...")
    purchase_orders = generate_purchase_orders(vendors, materials, args.num_orders)
    
    print("Generating trade data with hidden bottleneck...")
    trade_data = generate_trade_data(vendors, args.num_trade_records)
    
    print("Generating region risk data...")
    regions = generate_regions()
    
    print()
    print("Writing CSV files...")
    
    # Write files
    write_csv(vendors, args.output_dir / "vendors.csv")
    write_csv(materials, args.output_dir / "materials.csv")
    write_csv(bom, args.output_dir / "bill_of_materials.csv")
    write_csv(purchase_orders, args.output_dir / "purchase_orders.csv")
    write_csv(trade_data, args.output_dir / "trade_data.csv")
    write_csv(regions, args.output_dir / "regions.csv")
    
    print()
    print("=" * 60)
    print("Data generation complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Vendors: {len(vendors)}")
    print(f"  - Materials: {len(materials)}")
    print(f"  - BOM relationships: {len(bom)}")
    print(f"  - Purchase orders: {len(purchase_orders)}")
    print(f"  - Trade records: {len(trade_data)}")
    print(f"  - Regions: {len(regions)}")
    print()
    print("Hidden bottleneck pattern:")
    vulcan_count = sum(1 for t in trade_data if t["SHIPPER_NAME"] == "Vulcan Materials Refiner")
    print(f"  - 'Vulcan Materials Refiner' appears in {vulcan_count} trade records")
    print(f"  - This represents ~{vulcan_count * 100 // len(trade_data)}% of trade activity")
    print()
    print("Next steps:")
    print("  1. Upload data to Snowflake: snow sql -c demo -f sql/01_setup.sql")
    print("  2. Load CSV files into tables via DATA_STAGE")


if __name__ == "__main__":
    main()

