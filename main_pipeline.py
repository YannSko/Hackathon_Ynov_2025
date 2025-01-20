from scripts.api.food_api import FoodFootprintModel
from scripts.api.chauffage_api import HeatingFootprintModel
from scripts.api.trajet_api import (
    calculate_transport_emissions,
    suggest_transport_alternatives,
    get_transport_options,
)
from scripts.index_calculations import EnvironmentalIndexCalculator

# Food footprint model usage
# Define datasets
datasets = {
    "par_etape": "./data/agribalyse-31-detail-par-etape.csv",
    "par_ingredient": "./data/agribalyse-31-detail-par-ingredient.csv",
    "synthese": "./data/agribalyse-31-synthese.csv"
}

# Initialize the food model
food_model = FoodFootprintModel(datasets)

# Food query example
product_name = "pomme de terre"
weight_kg = 0.5

result = food_model.search_in_open_food_facts(product_name, weight_kg)
if result["carbon_footprint"] is not None:
    print(f"Final Result: {result['product_name']} - {result['carbon_footprint']:.2f} kg CO₂e")
else:
    print(f"No carbon footprint data available for '{product_name}'.")

# Heating footprint model usage
# Initialize the heating model
heating_model = HeatingFootprintModel()

# Heating query example
m2 = 50  # Surface area in square meters
heating_id = 3  # Example: Chauffage électrique
season = "winter"  # Winter season

# Get emissions data
heating_emissions = heating_model.get_heating_emissions(m2, heating_id, season=season)
if heating_emissions:
    print(f"\nHeating emissions data for {m2} m² using {heating_model.HEATING_OPTIONS[heating_id]} ({season}):")
    for item in heating_emissions:
        print(f"- {item['name']}: {item['adjusted_ecv']} kg CO₂e (adjusted for {season})")

# Suggest alternative heating systems
alternatives = heating_model.suggest_alternative_heatings(m2, heating_id, season=season)
if alternatives:
    print("\nSuggested alternative heating systems with lower CO₂ emissions:")
    for alt in alternatives:
        print(f"- {alt['name']}: {alt['adjusted_ecv']} kg CO₂e (adjusted for {season})")

# Query example
distance = 50  # Distance in kilometers
transport_id = 4  # Example: Voiture thermique

# Get transport emissions
transport_emissions = calculate_transport_emissions(distance, transport_id)
if transport_emissions:
    print(f"\nTransport emissions data for {distance} km using {get_transport_options()[transport_id]}:")
    for item in transport_emissions:
        print(f"- {item['name']}: {item['value']} kg CO₂e")

# Suggest alternative transport methods
transport_alternatives = suggest_transport_alternatives(distance, transport_id)
if transport_alternatives:
    print("\nSuggested alternative transport options with lower CO₂ emissions:")
    for alt in transport_alternatives:
        print(f"- {alt['name']}: {alt['value']} kg CO₂e")

# === Environmental Indices ===
# Initialize the Environmental Index Calculator
calculator = EnvironmentalIndexCalculator(food_model, heating_model)

# Calculate all indices and global rank
results = calculator.calculate_indices(
    product_name=product_name,
    weight_kg=weight_kg,
    m2=m2,
    heating_id=heating_id,
    season=season,
    distance=distance,
    transport_id=transport_id
)

# Display results
print("\n=== Environmental Indices ===")
for category, data in results.items():
    if category == "Global Rank":
        # Handle Global Rank as a single value
        print(f"\n{category}: {data}")
    else:
        # Handle other categories as dictionaries
        print(f"\n{category}:")
        for key, value in data.items():
            print(f"- {key}: {value}")
