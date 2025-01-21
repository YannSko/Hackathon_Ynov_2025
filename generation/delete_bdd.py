import psycopg2

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

# List of tables in dependency order (child tables first, parent tables last)
TABLES_TO_DELETE = [
    "ProgressionDefi",
    "Defi",
    "ChauffageEmission",
    "TransportEmission",
    "AlimentationEmission",
    "BEGES",
    "Profil",
    "Transport",
    "Aliment",
    "Chauffage",
    "Role"
]

def connect_to_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

def delete_all_data():
    """Delete all data from the database tables."""
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Disable foreign key constraints temporarily
        cursor.execute("SET session_replication_role = 'replica';")
        print("Foreign key constraints disabled.")

        # Delete data from all tables
        for table in TABLES_TO_DELETE:
            cursor.execute(f"DELETE FROM {table};")
            print(f"Data deleted from table: {table}")

        # Re-enable foreign key constraints
        cursor.execute("SET session_replication_role = 'origin';")
        print("Foreign key constraints re-enabled.")

        # Commit the changes
        connection.commit()
        print("All data deleted successfully!")

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
    delete_all_data()
