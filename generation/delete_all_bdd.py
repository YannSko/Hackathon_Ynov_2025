import psycopg2

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

def connect_to_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

def drop_all_tables():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Disable foreign key constraints temporarily
        cursor.execute("SET session_replication_role = 'replica';")

        # Fetch all table names
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()

        # Drop each table
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")

        # Re-enable foreign key constraints
        cursor.execute("SET session_replication_role = 'origin';")

        connection.commit()
        print("All tables dropped successfully!")

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
    drop_all_tables()
