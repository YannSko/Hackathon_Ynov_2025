from scripts.api.food_api import FoodFootprintModel

# Define datasets
datasets = {
    "par_etape": "./data/agribalyse-31-detail-par-etape.csv",
    "par_ingredient": "./data/agribalyse-31-detail-par-ingredient.csv",
    "synthese": "./data/agribalyse-31-synthese.csv"
}

# Initialize the model
model = FoodFootprintModel(datasets)

# Query example
product_name = "pomme de terre"
weight_kg = 0.5

result = model.search_in_open_food_facts(product_name, weight_kg)
if result["carbon_footprint"] is not None:
    print(f"Final Result: {result['product_name']} - {result['carbon_footprint']:.2f} kg CO₂e")
else:
    print(f"No carbon footprint data available for '{product_name}'.")
