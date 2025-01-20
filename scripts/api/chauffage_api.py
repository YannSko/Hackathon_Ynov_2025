import requests
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

class HeatingFootprintModel:
    """
    A model to handle CO2 emissions for heating systems with seasonal adjustments and alternative suggestions.
    """
    HEATING_OPTIONS = {
        1: "Chauffage au gaz",
        2: "Chauffage au fioul",
        3: "Chauffage électrique",
        4: "Chauffage avec une pompe à chaleur",
        5: "Chauffage avec un poêle à granulés",
        6: "Chauffage avec un poêle à bois",
        7: "Chauffage via un réseau de chaleur",
    }

    SEASONAL_MULTIPLIERS = {
        "winter": 1.0,  # Full usage
        "summer": 0.1,  # Minimal usage
        "year": 0.5,  # Average yearly usage
    }

    def __init__(self):
        self.api_url = "https://impactco2.fr/api/v1/chauffage"

    def get_heating_emissions(self, m2, heating_id, season="year", language="fr"):
        """
        Fetch CO2 emissions data for heating from the API and adjust for seasonality.

        :param m2: Surface area in square meters
        :param heating_id: Heating system ID
        :param season: Season (e.g., 'winter', 'summer', or 'year')
        :param language: Language for response data
        :return: Adjusted emissions data
        """
        params = {
            "m2": m2,
            "chauffages": heating_id,
            "language": language,
        }

        try:
            response = requests.get(self.api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    emissions = data["data"]
                    multiplier = self.SEASONAL_MULTIPLIERS.get(season, 1.0)
                    for item in emissions:
                        item["adjusted_ecv"] = item["ecv"] * multiplier
                    return emissions
                else:
                    logging.warning("No emissions data available for the heating query.")
            else:
                logging.error(f"Failed to fetch heating data. HTTP Status: {response.status_code}")
        except Exception as e:
            logging.error(f"An error occurred while fetching heating data: {e}")
        return None

    def suggest_alternative_heatings(self, m2, current_heating_id, season="year"):
        """
        Suggest alternative heating systems with lower CO2 emissions.

        :param m2: Surface area in square meters
        :param current_heating_id: Current heating system ID
        :param season: Season (e.g., 'winter', 'summer', or 'year')
        :return: List of alternative heating options
        """
        heating_ids = ",".join(map(str, self.HEATING_OPTIONS.keys()))
        all_emissions = self.get_heating_emissions(m2, heating_ids, season=season)
        if not all_emissions:
            logging.warning("Could not retrieve emissions data to suggest alternatives.")
            return None

        current_heating_name = self.HEATING_OPTIONS[current_heating_id]
        current_emissions = next(
            (x for x in all_emissions if x["name"] == current_heating_name), None
        )
        if not current_emissions:
            logging.warning(f"Could not find emissions data for heating ID {current_heating_id}.")
            return None

        print(f"\nCurrent Heating System: {current_heating_name} ({season})")
        print(f"- Emissions: {current_emissions['adjusted_ecv']} kg CO2e for {m2} m² (adjusted for {season})")

        all_emissions_sorted = sorted(all_emissions, key=lambda x: x["adjusted_ecv"])
        alternatives = [item for item in all_emissions_sorted if item["adjusted_ecv"] < current_emissions["adjusted_ecv"]]
        return alternatives[:3]

# Expose functions for external use
def calculate_emissions(m2, heating_id, season):
    model = HeatingFootprintModel()
    return model.get_heating_emissions(m2, heating_id, season)

def suggest_alternatives(m2, heating_id, season):
    model = HeatingFootprintModel()
    return model.suggest_alternative_heatings(m2, heating_id, season)

# Main function to call dynamically
if __name__ == "__main__":
    model = HeatingFootprintModel()
    logging.info("Heating CO2 Footprint Calculator")

    while True:
        logging.info("Choose an option:")
        logging.info("1. Calculate heating emissions")
        logging.info("2. Suggest alternative heating systems")
        logging.info("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            try:
                m2 = float(input("Enter the surface area in square meters: ").strip())
                heating_id = int(input("Enter the heating type ID: ").strip())
                season = input("Enter the season (winter, summer, or year): ").strip().lower()
                emissions = calculate_emissions(m2, heating_id, season)
                if emissions:
                    print(f"\nHeating emissions data for {m2} m² using {model.HEATING_OPTIONS[heating_id]} ({season}):")
                    for item in emissions:
                        print(f"- {item['name']}: {item['adjusted_ecv']} kg CO2e (adjusted for {season})")
            except ValueError:
                logging.error("Invalid input for surface area or heating ID. Please enter valid numbers.")
        elif choice == "2":
            try:
                m2 = float(input("Enter the surface area in square meters: ").strip())
                heating_id = int(input("Enter the heating type ID: ").strip())
                season = input("Enter the season (winter, summer, or year): ").strip().lower()
                alternatives = suggest_alternatives(m2, heating_id, season)
                if alternatives:
                    print("\nSuggested alternative heating systems with lower CO2 emissions:")
                    for alt in alternatives:
                        print(f"- {alt['name']}: {alt['adjusted_ecv']} kg CO2e (adjusted for {season})")
            except ValueError:
                logging.error("Invalid input for surface area or heating ID. Please enter valid numbers.")
        elif choice == "3":
            logging.info("Exiting the program. Goodbye!")
            break
        else:
            logging.error("Invalid choice. Please select 1, 2, or 3.")
