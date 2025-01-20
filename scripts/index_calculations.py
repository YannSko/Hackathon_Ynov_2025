import math
from scripts.api.food_api import FoodFootprintModel
from scripts.api.chauffage_api import HeatingFootprintModel
from scripts.api.trajet_api import (
    calculate_transport_emissions,
    suggest_transport_alternatives,
    get_transport_options,
)


class EnvironmentalIndexCalculator:
    # Thresholds for optimized values
    OPTIMAL_FOOD_CARBON_PER_PERSON = 2.5  # kg CO₂e per day for food
    OPTIMAL_HEATING_EMISSIONS = {
        "winter": 150,  # kg CO₂e for 50 m²
        "summer": 10,   # kg CO₂e for 50 m²
        "year": 80,     # kg CO₂e for 50 m²
    }
    OPTIMAL_TRANSPORT_PER_KM = 0.02  # kg CO₂e per km for sustainable transport

    def __init__(self, food_model: FoodFootprintModel, heating_model: HeatingFootprintModel):
        self.food_model = food_model
        self.heating_model = heating_model

    def determine_rank(self, user_index: float) -> int:
        """Determine the rank based on the user's index."""
        if user_index >= 80:
            return 1
        elif user_index >= 60:
            return 2
        elif user_index >= 40:
            return 3
        elif user_index >= 20:
            return 4
        else:
            return 5

    def calculate_global_rank(self, ranks: list[int]) -> int:
        """Calculate the global rank based on the average of individual ranks."""
        valid_ranks = [rank for rank in ranks if rank is not None]
        if valid_ranks:
            global_rank = round(sum(valid_ranks) / len(valid_ranks))  # Rounded to nearest integer
            return global_rank
        return None

    def calculate_user_food_index(self, product_name: str, weight_kg: float) -> dict:
        """Calculate the food index for the user based on their food consumption."""
        result = self.food_model.search_in_open_food_facts(product_name, weight_kg)
        if result["carbon_footprint"] is not None:
            user_footprint = result["carbon_footprint"]
            optimized_footprint = self.OPTIMAL_FOOD_CARBON_PER_PERSON
            user_index = min((optimized_footprint / user_footprint) * 100, 100)
            rank = self.determine_rank(user_index)
            return {
                "User Index": user_index,
                "Rank": rank,
                "User Emissions": user_footprint,
                "Optimized Emissions": optimized_footprint,
            }
        return None

    def calculate_user_heating_index(self, m2: float, heating_id: int, season: str) -> dict:
        """Calculate the heating index for the user based on their heating system."""
        emissions = self.heating_model.get_heating_emissions(m2, heating_id, season=season)
        if emissions:
            base_optimized_emissions = self.OPTIMAL_HEATING_EMISSIONS[season]
            optimized_emissions = base_optimized_emissions * (m2 / 50)  # Scale for area
            adjusted_emissions = emissions[0]["adjusted_ecv"]
            user_index = min((optimized_emissions / adjusted_emissions) * 100, 100)
            rank = self.determine_rank(user_index)
            return {
                "User Index": user_index,
                "Rank": rank,
                "User Emissions": adjusted_emissions,
                "Optimized Emissions": optimized_emissions,
            }
        return None

    def calculate_user_transport_index(self, distance: float, transport_id: int) -> dict:
        """Calculate the transport index for the user."""
        emissions = calculate_transport_emissions(distance, transport_id)
        if emissions:
            user_emissions = emissions[0]["value"]
            optimized_emissions = distance * self.OPTIMAL_TRANSPORT_PER_KM
            user_index = min((optimized_emissions / user_emissions) * 100, 100)
            rank = self.determine_rank(user_index)
            return {
                "User Index": user_index,
                "Rank": rank,
                "User Emissions": user_emissions,
                "Optimized Emissions": optimized_emissions,
            }
        return None

    def calculate_optimized_transport_index(self, distance: float) -> dict:
        """Suggest the most optimized transport mode for the distance."""
        transport_options = get_transport_options()
        best_alternatives = {}

        for transport_id, transport_name in transport_options.items():
            emissions = calculate_transport_emissions(distance, transport_id)
            if emissions:
                total_emissions = emissions[0]["value"]
                best_alternatives[transport_name] = total_emissions

        if not best_alternatives:
            return None

        optimized_transport = min(best_alternatives, key=best_alternatives.get)
        optimized_emissions = best_alternatives[optimized_transport]
        optimized_index = min((self.OPTIMAL_TRANSPORT_PER_KM * distance / optimized_emissions) * 100, 100)

        return {
            "Optimized Transport": optimized_transport,
            "Optimized Emissions": optimized_emissions,
            "Optimized Index": optimized_index,
        }

    def calculate_indices(self, product_name: str, weight_kg: float, m2: float, heating_id: int,
                          season: str, distance: float, transport_id: int) -> dict:
        """Calculate all indices and ranks."""
        food_index = self.calculate_user_food_index(product_name, weight_kg)
        heating_index = self.calculate_user_heating_index(m2, heating_id, season)
        transport_index = self.calculate_user_transport_index(distance, transport_id)

        # Collect ranks for global rank calculation
        ranks = [
            food_index["Rank"] if food_index else None,
            heating_index["Rank"] if heating_index else None,
            transport_index["Rank"] if transport_index else None,
        ]
        global_rank = self.calculate_global_rank(ranks)

        return {
            "Food": food_index,
            "Heating": heating_index,
            "Transport": transport_index,
            "Global Rank": global_rank,
        }


