import psycopg2

# Configuration de la base de données
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

# Emissions fixes pour les chauffages (kg CO2/m²)
CHAUFFAGE_EMISSIONS = {
    1: {"name": "Chauffage au gaz", "co2_per_m": 50},
    2: {"name": "Chauffage au fioul", "co2_per_m": 60},
    3: {"name": "Chauffage électrique", "co2_per_m": 30},
    4: {"name": "Pompe à chaleur", "co2_per_m": 15},
    5: {"name": "Poêle à granulés", "co2_per_m": 10},
    6: {"name": "Poêle à bois", "co2_per_m": 20},
    7: {"name": "Réseau de chaleur", "co2_per_m": 5},
    8: {"name": "Chauffage au charbon", "co2_per_m": 80},
}

# Connexion à la base de données
def connect_to_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

# Fonction pour insérer les données dans la table Chauffage
def populate_chauffage_table():
    """Insert chauffage emissions data into the Chauffage table."""
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Insérer les données dans la table Chauffage
        for chauffage_id, chauffage_data in CHAUFFAGE_EMISSIONS.items():
            cursor.execute(
                """
                INSERT INTO Chauffage (ChauffageId, Nom, CO2parM)
                VALUES (%s, %s, %s)
                """,
                (chauffage_id, chauffage_data["name"], chauffage_data["co2_per_m"]),
            )

        # Valider les changements
        connection.commit()
        print("Les données des chauffages ont été ajoutées avec succès !")

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
    populate_chauffage_table()
