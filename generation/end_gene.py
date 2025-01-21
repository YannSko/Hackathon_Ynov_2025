import psycopg2
import random
import datetime

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "ClashOfRse",
    "user": "your_username",
    "password": "your_password",
}

# Seasonality mapping for aliments
SEASONAL_ALIMENTS = {
    "winter": ["Soupes", "Ragoût"],
    "summer": ["Salades", "Glaces"],
    "autumn": ["Ragoût"],
    "spring": ["Légumes", "Fruits"]
}

# Helper functions
def random_date(start_date, end_date):
    """Generate a random date between two dates."""
    delta = end_date - start_date
    return start_date + datetime.timedelta(days=random.randint(0, delta.days))

def daterange(start_date, end_date):
    """Generate a range of dates between two dates."""
    for n in range((end_date - start_date).days + 1):
        yield start_date + datetime.timedelta(days=n)

def connect_to_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

# Populate all tables
def populate_database():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Fetch external data
        print("Fetching external data...")
        cursor.execute("SELECT RoleId FROM Role")
        role_ids = [row[0] for row in cursor.fetchall()]
        if not role_ids:
            raise ValueError("No roles found in the database.")

        cursor.execute("SELECT AlimentId, Nom FROM Aliment")
        aliments = cursor.fetchall()  # [(id, name), ...]
        if not aliments:
            raise ValueError("No aliments found in the database.")

        cursor.execute("SELECT TransportId FROM Transport")
        transport_ids = [row[0] for row in cursor.fetchall()]
        if not transport_ids:
            raise ValueError("No transports found in the database.")

        cursor.execute("SELECT ChauffageId FROM Chauffage")
        chauffage_ids = [row[0] for row in cursor.fetchall()]
        if not chauffage_ids:
            raise ValueError("No heating types found in the database.")

        # Insert profiles
        print("Inserting profiles...")
        for profile_id in range(1, 101):  # Generate 100 profiles
            role_id = random.choice(role_ids)
            cursor.execute(
                """
                INSERT INTO Profil (ProfilId, RoleId, Nom, Prenom, DateDeNaissance, Email, Entreprise, Image, DistanceTravailMaison)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    profile_id,
                    role_id,
                    f"User_{profile_id}",
                    f"Prenom_{profile_id}",
                    random_date(datetime.date(1970, 1, 1), datetime.date(2000, 12, 31)),
                    f"user{profile_id}@example.com",
                    f"Entreprise_{random.randint(1, 10)}",
                    None,
                    random.uniform(1, 50),
                )
            )

        # Insert BEGES records
        print("Inserting BEGES records...")
        for beges_id in range(1, 201):  # Generate 200 BEGES records
            profile_id = random.randint(1, 100)  # Reference profiles
            start_date = random_date(datetime.date(2023, 1, 1), datetime.date(2024, 1, 1))
            end_date = start_date + datetime.timedelta(days=30)
            cursor.execute(
                """
                INSERT INTO BEGES (BEGESId, ProfilId, DateDebut, DateFin, CO2Total, GlobalRank)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    beges_id,
                    profile_id,
                    start_date,
                    end_date,
                    random.uniform(100, 1000),  # Random total CO2
                    0  # Placeholder for GlobalRank
                )
            )

            # Insert emissions for each day in BEGES range
            for single_date in daterange(start_date, end_date):
                # Transport emissions
                for transport_id in random.sample(transport_ids, random.randint(1, 3)):
                    cursor.execute(
                        """
                        INSERT INTO TransportEmission (TransportId, BEGESId, CO2EmisTransport, DateDebut, DateFin, Rank)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            transport_id,
                            beges_id,
                            random.uniform(1, 50),  # Example CO2 emissions
                            single_date,
                            single_date,
                            random.randint(1, 5),
                        )
                    )

                # Alimentation emissions (respect seasonality)
                season = "winter" if single_date.month in [12, 1, 2] else \
                         "summer" if single_date.month in [6, 7, 8] else \
                         "autumn" if single_date.month in [9, 10, 11] else "spring"
                for aliment_id, aliment_name in random.sample(aliments, random.randint(1, 3)):
                    if aliment_name in SEASONAL_ALIMENTS.get(season, [a[1] for a in aliments]):
                        cursor.execute(
                            """
                            INSERT INTO AlimentationEmission (AlimentId, BEGESId, CO2EmisAlimentation, DateDebut, DateFin, Rank)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (
                                aliment_id,
                                beges_id,
                                random.uniform(1, 20),  # Example CO2 emissions
                                single_date,
                                single_date,
                                random.randint(1, 5),
                            )
                        )

                # Chauffage emissions
                chauffage_id = random.choice(chauffage_ids)
                cursor.execute(
                    """
                    INSERT INTO ChauffageEmission (ChauffageId, BEGESId, CO2EmisChauffage, DateDebut, DateFin, Rank)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        chauffage_id,
                        beges_id,
                        random.uniform(1, 30),  # Example CO2 emissions
                        single_date,
                        single_date,
                        random.randint(1, 5),
                    )
                )

            # Calculate GlobalRank for BEGES
            cursor.execute(
                """
                SELECT AVG(Rank) FROM (
                    SELECT Rank FROM AlimentationEmission WHERE BEGESId = %s
                    UNION ALL
                    SELECT Rank FROM TransportEmission WHERE BEGESId = %s
                    UNION ALL
                    SELECT Rank FROM ChauffageEmission WHERE BEGESId = %s
                ) ranks
                """,
                (beges_id, beges_id, beges_id)
            )
            global_rank = cursor.fetchone()[0] or 0  # Default to 0 if no ranks are present

            # Update GlobalRank in BEGES
            cursor.execute(
                "UPDATE BEGES SET GlobalRank = %s WHERE BEGESId = %s",
                (global_rank, beges_id)
            )

        # Commit all changes
        connection.commit()
        print("Database populated successfully!")

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
    populate_database()
