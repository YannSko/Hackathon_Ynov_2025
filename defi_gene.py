import psycopg2
import random

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

def populate_defis_and_progressions():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Fetch existing profile IDs
        cursor.execute("SELECT ProfilId FROM Profil")
        profile_ids = [row[0] for row in cursor.fetchall()]
        if not profile_ids:
            raise ValueError("No profiles found in the database.")

        # Insert Defis (Challenges)
        print("Inserting challenges...")
        for defi_id in range(1, 51):  # Generate 50 challenges
            cursor.execute(
                """
                INSERT INTO Defi (DefiId, Nom, Description, Objectif)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    defi_id,
                    f"Defi_{defi_id}",
                    f"Description for challenge {defi_id}",
                    random.randint(10, 100),  # Random objective
                )
            )

        # Insert ProgressionDefi (Challenge Progression)
        print("Inserting challenge progressions...")
        for profile_id in profile_ids:  # Assign progress to all profiles
            for defi_id in random.sample(range(1, 51), random.randint(5, 15)):  # Assign random challenges
                cursor.execute(
                    """
                    INSERT INTO ProgressionDefi (ProfilId, DefiId, Score)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        profile_id,
                        defi_id,
                        random.randint(0, 100),  # Random score for each challenge
                    )
                )

        # Commit changes
        connection.commit()
        print("Challenges and progressions added successfully!")

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
    populate_defis_and_progressions()
