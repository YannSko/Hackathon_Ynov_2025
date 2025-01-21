import psycopg2

# Configuration de la base de données
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

# Emissions fixes pour les transports (kg CO2/km)
TRANSPORT_EMISSIONS = {
    "Avion": 0.14157999999999998,
    "TGV": 0.00293,
    "Intercités": 0.00898,
    "Voiture thermique": 0.21760000000000002,
    "Voiture électrique": 0.10339999999999999,
    "Autocar thermique": 0.029421306270000003,
    "Vélo": 0.00017,
    "Vélo à assistance électrique": 0.010950000000000001,
    "Bus thermique": 0.11320000000000001,
    "Tramway": 0.00428,
    "Métro": 0.0044399999999999995,
    "Scooter ou moto légère thermique": 0.0763,
    "Moto thermique": 0.1913,
    "RER ou Transilien": 0.00978,
    "TER": 0.02769,
    "Bus électrique": 0.0217,
    "Trottinette à assistance électrique": 0.0249,
    "Bus (GNV)": 0.1217,
    "Covoiturage thermique (1 passager)": 0.10880000000000001,
    "Covoiturage thermique (2 passagers)": 0.07253333333333334,
    "Covoiturage thermique (3 passagers)": 0.054400000000000004,
    "Covoiturage thermique (4 passagers)": 0.04352,
    "Covoiturage électrique (1 passager)": 0.051699999999999996,
    "Covoiturage électrique (2 passagers)": 0.034466666666666666,
    "Covoiturage électrique (3 passagers)": 0.025849999999999998,
    "Covoiturage électrique (4 passagers)": 0.020679999999999997,
    "Marche": 0.0,
}

# Connexion à la base de données
def connect_to_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

# Fonction pour insérer les données dans la table Transport
def populate_transport_table():
    """Insert transport emissions data into the Transport table."""
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Insérer les données dans la table Transport
        for transport_id, (transport_name, co2_per_km) in enumerate(TRANSPORT_EMISSIONS.items(), start=1):
            cursor.execute(
                """
                INSERT INTO Transport (TransportId, Nom, CO2parKm)
                VALUES (%s, %s, %s)
                """,
                (transport_id, transport_name, co2_per_km),
            )

        # Valider les changements
        connection.commit()
        print("Les données des transports ont été ajoutées avec succès !")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        if connection:
            connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Lancer le script
if __name__ == "__main__":
    populate_transport_table()
