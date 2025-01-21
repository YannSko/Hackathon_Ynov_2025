import psycopg2

# Configuration de la base de données
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

# Liste des tables à vérifier
TABLES = [
    "Role",
    "Profil",
    "Transport",
    "Aliment",
    "Chauffage",
    "TransportEmission",
    "AlimentationEmission",
    "ChauffageEmission",
    "BEGES",
    "Defi",
    "ProgressionDefi"
]

# Connexion à la base de données
def connect_to_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

# Fonction pour compter les lignes dans chaque table
def count_rows_in_tables():
    """Count the number of rows in each table."""
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        print("Nombre de lignes par table dans la base de données :")
        for table in TABLES:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cursor.fetchone()[0]
            print(f"- {table} : {row_count} lignes")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Lancer le script
if __name__ == "__main__":
    count_rows_in_tables()
