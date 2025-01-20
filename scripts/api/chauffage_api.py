import requests
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


class HeatingFootprintModel:
    """
    A model to handle CO2 emissions for heating systems.
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

    def __init__(self):
        self.api_url = "https://impactco2.fr/api/v1/chauffage"

    def display_heating_options(self):
        """Display heating options."""
        print("\nHeating Options:")
        for key, value in self.HEATING_OPTIONS.items():
            print(f"{key}: {value}")

    def get_heating_emissions(self, m2, heating_id, language="fr"):
        """
        Fetch CO2 emissions data for heating from the API.

        :param m2: Surface area in square meters
        :param heating_id: Heating system ID
        :param language: Language for response data
        :return: List of heating emissions data
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
                    return data["data"]
                else:
                    logging.warning("No emissions data available for the heating query.")
            else:
                logging.error(f"Failed to fetch heating data. HTTP Status: {response.status_code}")
        except Exception as e:
            logging.error(f"An error occurred while fetching heating data: {e}")
        return None

    def suggest_alternative_heatings(self, m2, current_heating_id):
        """
        Suggest alternative heating systems with lower CO2 emissions.

        :param m2: Surface area in square meters
        :param current_heating_id: Current heating system ID
        :return: List of alternative heating options
        """
        # Fetch emissions data for all heating systems
        heating_ids = ",".join(map(str, self.HEATING_OPTIONS.keys()))
        all_emissions = self.get_heating_emissions(m2, heating_ids)
        if not all_emissions:
            logging.warning("Could not retrieve emissions data to suggest alternatives.")
            return None

        # Get the name of the current heating system
        current_heating_name = self.HEATING_OPTIONS[current_heating_id]

        # Find the current heating system emissions
        current_emissions = next(
            (x for x in all_emissions if x["name"] == current_heating_name), None
        )
        if not current_emissions:
            logging.warning(f"Could not find emissions data for heating ID {current_heating_id}.")
            return None

        # Display the current heating system emissions
        print(f"\nCurrent Heating System: {current_heating_name}")
        print(f"- Emissions: {current_emissions['ecv']} kg CO2e for {m2} m²")

        # Sort by CO2 emissions
        all_emissions_sorted = sorted(all_emissions, key=lambda x: x["ecv"])

        # Find alternatives with lower emissions than the current heating system
        alternatives = [
            item for item in all_emissions_sorted if item["ecv"] < current_emissions["ecv"]
        ]
        return alternatives[:3]  # Return top 3 alternatives


# Example Usage
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
            # Calculate heating emissions
            model.display_heating_options()
            try:
                m2 = float(input("Enter the surface area in square meters: ").strip())
                heating_id = int(input("Enter the heating type ID: ").strip())
                if heating_id not in model.HEATING_OPTIONS:
                    logging.error("Invalid heating ID. Please select from the list.")
                    continue

                emissions_data = model.get_heating_emissions(m2, heating_id)
                if emissions_data:
                    print(f"\nHeating emissions data for {m2} m² using {model.HEATING_OPTIONS[heating_id]}:")
                    for item in emissions_data:
                        print(f"- {item['name']}: {item['ecv']} kg CO2e")
            except ValueError:
                logging.error("Invalid input for surface area or heating ID. Please enter valid numbers.")
        elif choice == "2":
            # Suggest alternative heating systems
            model.display_heating_options()
            try:
                m2 = float(input("Enter the surface area in square meters: ").strip())
                heating_id = int(input("Enter the heating type ID: ").strip())
                if heating_id not in model.HEATING_OPTIONS:
                    logging.error("Invalid heating ID. Please select from the list.")
                    continue

                alternatives = model.suggest_alternative_heatings(m2, heating_id)
                if alternatives:
                    print("\nSuggested alternative heating systems with lower CO2 emissions:")
                    for alt in alternatives:
                        print(f"- {alt['name']}: {alt['ecv']} kg CO2e")
            except ValueError:
                logging.error("Invalid input for surface area or heating ID. Please enter valid numbers.")
        elif choice == "3":
            logging.info("Exiting the program. Goodbye!")
            break
        else:
            logging.error("Invalid choice. Please select 1, 2, or 3.")
