import logging
import azure.functions as func
import json
from sqlalchemy import create_engine
from scripts.api.food_api import FoodFootprintModel
from scripts.api.chauffage_api import HeatingFootprintModel
from scripts.api.trajet_api import calculate_transport_emissions, get_transport_options
from scripts.index_calculations import EnvironmentalIndexCalculator

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

def get_database_connection():
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    return create_engine(db_url)

# Initialize API models
datasets = {
    "par_etape": "./data/agribalyse-31-detail-par-etape.csv",
    "par_ingredient": "./data/agribalyse-31-detail-par-ingredient.csv",
    "synthese": "./data/agribalyse-31-synthese.csv"
}
food_model = FoodFootprintModel(datasets)
heating_model = HeatingFootprintModel()
calculator = EnvironmentalIndexCalculator(food_model, heating_model)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function triggered to process environmental indices.')

    try:
        # Extract inputs from request
        product_name = req.params.get("product_name")
        weight_kg = req.params.get("weight_kg")
        m2 = req.params.get("m2")
        heating_id = req.params.get("heating_id")
        season = req.params.get("season")
        distance = req.params.get("distance")
        transport_id = req.params.get("transport_id")

        # Check for missing fields
        missing_fields = []
        if not product_name:
            missing_fields.append("product_name")
        if not weight_kg:
            missing_fields.append("weight_kg")
        if not m2:
            missing_fields.append("m2")
        if not heating_id:
            missing_fields.append("heating_id")
        if not season:
            missing_fields.append("season")
        if not distance:
            missing_fields.append("distance")
        if not transport_id:
            missing_fields.append("transport_id")

        if missing_fields:
            return func.HttpResponse(
                json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"}),
                status_code=400,
                mimetype="application/json"
            )

        # Convert fields to appropriate types
        weight_kg = float(weight_kg)
        m2 = float(m2)
        heating_id = int(heating_id)
        distance = float(distance)
        transport_id = int(transport_id)

        # Calculate indices
        indices = calculator.calculate_indices(product_name, weight_kg, m2, heating_id, season, distance, transport_id)

        # Save indices to database
        engine = get_database_connection()
        with engine.connect() as connection:
            for category, data in indices.items():
                if category != "Global Rank":
                    table_name = category.lower()
                    record = {
                        "user_index": data.get("User Index"),
                        "rank": data.get("Rank"),
                        "user_emissions": data.get("User Emissions"),
                        "optimized_emissions": data.get("Optimized Emissions")
                    }
                    connection.execute(f"INSERT INTO {table_name} (user_index, rank, user_emissions, optimized_emissions) VALUES (%(user_index)s, %(rank)s, %(user_emissions)s, %(optimized_emissions)s)", record)

        # Return response
        response = {
            "indices": indices
        }
        return func.HttpResponse(json.dumps(response, indent=4), mimetype="application/json")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")
