import psycopg2
import random

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

# Role data
ROLES = [
    {"name": "Admin"},
    {"name": "User"},
    {"name": "Manager"},
    {"name": "Employé"},
]

# Aliments data with massekg
ALIMENTS = [
    {"name": "Viande", "co2_per_100g": 25, "massekg": random.uniform(0.5, 5)},
    {"name": "Légumes", "co2_per_100g": 5, "massekg": random.uniform(0.5, 5)},
    {"name": "Fruits", "co2_per_100g": 7, "massekg": random.uniform(0.5, 5)},
    {"name": "Produits laitiers", "co2_per_100g": 12, "massekg": random.uniform(0.5, 5)},
    {"name": "Céréales", "co2_per_100g": 10, "massekg": random.uniform(0.5, 5)},
    {"name": "Poisson", "co2_per_100g": 22, "massekg": random.uniform(0.5, 5)},
    {"name": "Produits transformés", "co2_per_100g": 15, "massekg": random.uniform(0.5, 5)},
    {"name": "Boissons sucrées", "co2_per_100g": 8, "massekg": random.uniform(0.5, 5)},
    {"name": "Soupes", "co2_per_100g": 7, "massekg": random.uniform(0.5, 3)},
    {"name": "Salades", "co2_per_100g": 3, "massekg": random.uniform(0.5, 2)},
    {"name": "Ragoût", "co2_per_100g": 15, "massekg": random.uniform(0.5, 4)},
    {"name": "Glaces", "co2_per_100g": 8, "massekg": random.uniform(0.5, 1)},
]

# Connect to the database
def connect_to_db():
    return psycopg2.connect(**DB_CONFIG)

# Populate roles and aliments
def populate_roles_and_aliments():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Insert roles
        print("Inserting roles...")
        for role_id, role in enumerate(ROLES, start=1):
            cursor.execute(
                """
                INSERT INTO Role (RoleId, Nom)
                VALUES (%s, %s)
                ON CONFLICT (RoleId) DO NOTHING
                """,
                (role_id, role["name"]),
            )

        # Insert aliments
        print("Inserting aliments...")
        for aliment_id, aliment in enumerate(ALIMENTS, start=1):
            cursor.execute(
                """
                INSERT INTO Aliment (AlimentId, Nom, CO2par100g, MasseKG)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (AlimentId) DO NOTHING
                """,
                (aliment_id, aliment["name"], aliment["co2_per_100g"], aliment["massekg"]),
            )

        # Commit the changes
        connection.commit()
        print("Roles and aliments added successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        if connection:
            connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Main execution
if __name__ == "__main__":
    populate_roles_and_aliments()
