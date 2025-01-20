import requests
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


class TransportFootprintModel:
    """
    A model to handle CO2 emissions for transport systems and suggest alternatives based on credible ranges.
    """
    TRANSPORT_OPTIONS = {
        1: "Avion",
        2: "TGV",
        3: "Intercités",
        4: "Voiture thermique",
        5: "Voiture électrique",
        6: "Autocar thermique",
        7: "Vélo",
        8: "Vélo à assistance électrique",
        9: "Bus thermique",
        10: "Tramway",
        11: "Métro",
        12: "Scooter ou moto légère thermique",
        13: "Moto thermique",
        14: "RER ou Transilien",
        15: "TER",
        16: "Bus électrique",
        17: "Trottinette à assistance électrique",
        21: "Bus (GNV)",
        22: "Covoiturage thermique (1 passager)",
        23: "Covoiturage thermique (2 passagers)",
        24: "Covoiturage thermique (3 passagers)",
        25: "Covoiturage thermique (4 passagers)",
        26: "Covoiturage électrique (1 passager)",
        27: "Covoiturage électrique (2 passagers)",
        28: "Covoiturage électrique (3 passagers)",
        29: "Covoiturage électrique (4 passagers)",
        30: "Marche",
    }

    CREDIBLE_RANGES = {
    1: (200, float('inf')),  # Avion
    2: (100, float('inf')),  # TGV
    3: (10, 400),            # Intercités
    4: (5, 1000),            # Voiture thermique
    5: (5, 1000),            # Voiture électrique
    6: (0.1, 500),           # Autocar thermique
    7: (0.1, 20),            # Vélo
    8: (0.1, 50),            # Vélo à assistance électrique
    9: (0.2, 100),           # Bus thermique
    10: (0.5, 30),           # Tramway
    11: (0.1, 50),           # Métro
    12: (0.5, 100),          # Scooter ou moto légère thermique
    13: (0.8, 300),          # Moto thermique
    14: (0.5, 200),          # RER ou Transilien
    15: (0.5, 300),          # TER
    16: (0.1, 100),          # Bus électrique
    17: (0.1, 10),           # Trottinette à assistance électrique
    21: (0.5, 100),          # Bus (GNV)
    22: (5, 1000),           # Covoiturage thermique (1 passager)
    23: (5, 1000),           # Covoiturage thermique (2 passagers)
    24: (5, 1000),           # Covoiturage thermique (3 passagers)
    25: (5, 1000),           # Covoiturage thermique (4 passagers)
    26: (5, 1000),           # Covoiturage électrique (1 passager)
    27: (5, 1000),           # Covoiturage électrique (2 passagers)
    28: (5, 1000),           # Covoiturage électrique (3 passagers)
    29: (5, 1000),           # Covoiturage électrique (4 passagers)
    30: (0.01, 10),          # Marche
}

    def __init__(self):
        self.api_url = "https://impactco2.fr/api/v1/transport"

    def get_transport_emissions(self, km, transport_id, language="fr"):
        """
        Fetch CO2 emissions data for transport from the API.

        :param km: Distance in kilometers
        :param transport_id: Transport system ID
        :param language: Language for response data
        :return: Emissions data
        """
        params = {
            "km": km,
            "transports": transport_id,
            "language": language,
        }

        try:
            response = requests.get(self.api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", None)
            else:
                logging.error(f"Failed to fetch transport data. HTTP Status: {response.status_code}")
        except Exception as e:
            logging.error(f"An error occurred while fetching transport data: {e}")
        return None

    def suggest_alternative_transports(self, km, current_transport_id):
        """
        Suggest alternative transport modes with lower CO2 emissions within credible ranges.

        :param km: Distance in kilometers
        :param current_transport_id: Current transport system ID
        :return: List of alternative transport options
        """
        transport_ids = ",".join(map(str, self.TRANSPORT_OPTIONS.keys()))
        all_emissions = self.get_transport_emissions(km, transport_ids)
        if not all_emissions:
            logging.warning("Could not retrieve emissions data to suggest alternatives.")
            return None

        current_emissions = next(
            (x for x in all_emissions if x["id"] == current_transport_id), None
        )
        if not current_emissions:
            logging.warning(f"Could not find emissions data for transport ID {current_transport_id}.")
            return None

        current_transport_name = self.TRANSPORT_OPTIONS[current_transport_id]
        print(f"\nCurrent Transport System: {current_transport_name}")
        print(f"- Emissions: {current_emissions['value']} kg CO2e for {km} km")

        all_emissions_sorted = sorted(all_emissions, key=lambda x: x["value"])
        alternatives = [
            item for item in all_emissions_sorted
            if item["value"] < current_emissions["value"]
            and self.CREDIBLE_RANGES[item["id"]][0] <= km <= self.CREDIBLE_RANGES[item["id"]][1]
        ]
        return alternatives[:3]
    
    def get_transport_options(self):
        """
        Return the dictionary of transport options.
        """
        return self.TRANSPORT_OPTIONS

# Expose functions for external use
def calculate_transport_emissions(km, transport_id):
    model = TransportFootprintModel()
    return model.get_transport_emissions(km, transport_id)

def suggest_transport_alternatives(km, transport_id):
    model = TransportFootprintModel()
    return model.suggest_alternative_transports(km, transport_id)
def get_transport_options():
    """
    Return the dictionary of transport options.
    """
    model = TransportFootprintModel()
    return model.get_transport_options()