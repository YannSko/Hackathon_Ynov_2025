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

SEASONAL_ALIMENTS = {
    "winter": ["Soupes", "Ragoût"],
    "summer": ["Salades", "Glaces"],
    "autumn": ["Ragoût"],
    "spring": ["Légumes", "Fruits"]
}

def connect_to_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

def seasonal_modifier(season, base_value):
    """Adjust values based on the season."""
    modifiers = {
        "winter": 1.2,  # 20% increase for heating and transport in winter
        "summer": 0.8,  # 20% decrease for heating in summer
        "autumn": 1.0,  # Neutral for autumn
        "spring": 0.9   # Slight decrease in spring
    }
    return base_value * modifiers[season]

def generate_emissions(cursor, beges_id, profil_id, start_date, end_date, season, transport_ids, aliments, chauffage_ids):
    """
    Generate and insert emissions data for transport, alimentation, and heating.
    """
    for single_date in daterange(start_date, end_date):
        # Transport emissions
        for transport_id in random.sample(transport_ids, random.randint(1, 3)):
            co2_emis = seasonal_modifier(season, random.uniform(5, 50))  # Adjusted emissions
            cursor.execute(
                """
                INSERT INTO TransportEmission (TransportId, BEGESId, CO2EmisTransport, DateDebut, DateFin, Rank)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    transport_id,
                    beges_id,
                    co2_emis,
                    single_date,
                    single_date,
                    random.randint(1, 5),
                )
            )

        # Alimentation emissions (respect seasonality)
        for aliment_id, aliment_name in random.sample(aliments, random.randint(1, 3)):
            if aliment_name in SEASONAL_ALIMENTS.get(season, [a[1] for a in aliments]):
                co2_emis = seasonal_modifier(season, random.uniform(1, 20))
                cursor.execute(
                    """
                    INSERT INTO AlimentationEmission (AlimentId, BEGESId, CO2EmisAlimentation, DateDebut, DateFin, Rank)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        aliment_id,
                        beges_id,
                        co2_emis,
                        single_date,
                        single_date,
                        random.randint(1, 5),
                    )
                )

        # Heating emissions
        chauffage_id = random.choice(chauffage_ids)
        co2_emis = seasonal_modifier(season, random.uniform(10, 40))
        cursor.execute(
            """
            INSERT INTO ChauffageEmission (ChauffageId, BEGESId, CO2EmisChauffage, DateDebut, DateFin, Rank)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                chauffage_id,
                beges_id,
                co2_emis,
                single_date,
                single_date,
                random.randint(1, 5),
            )
        )

def add_monthly_beges():
    """
    Add monthly BEGES records for each profile and update influencing tables.
    """
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Fetch existing profiles and external data
        print("Fetching profiles and external data...")
        cursor.execute("SELECT ProfilId FROM Profil")
        profiles = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT AlimentId, Nom FROM Aliment")
        aliments = cursor.fetchall()  # [(id, name), ...]

        cursor.execute("SELECT TransportId FROM Transport")
        transport_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT ChauffageId FROM Chauffage")
        chauffage_ids = [row[0] for row in cursor.fetchall()]

        if not profiles or not aliments or not transport_ids or not chauffage_ids:
            raise ValueError("Ensure all necessary external data (profiles, aliments, transports, chauffages) is populated.")

        # Insert monthly BEGES records and related emissions
        print("Adding monthly BEGES records...")
        cursor.execute("SELECT MAX(BEGESId) FROM BEGES")
        result = cursor.fetchone()
        current_beges_id = result[0] if result and result[0] else 0

        for profil_id in profiles:
            # Generate 12 months of BEGES records starting from Jan 2023
            for month_offset in range(12):
                start_date = datetime.date(2023, 1, 1) + datetime.timedelta(days=month_offset * 30)
                end_date = start_date + datetime.timedelta(days=29)  # Approx. 1 month
                season = (
                    "winter" if start_date.month in [12, 1, 2] else
                    "spring" if start_date.month in [3, 4, 5] else
                    "summer" if start_date.month in [6, 7, 8] else "autumn"
                )

                current_beges_id += 1
                total_co2 = random.uniform(500, 2000)
                cursor.execute(
                    """
                    INSERT INTO BEGES (BEGESId, ProfilId, DateDebut, DateFin, CO2Total, GlobalRank)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        current_beges_id,
                        profil_id,
                        start_date,
                        end_date,
                        total_co2,
                        0,  # GlobalRank will be calculated later
                    )
                )

                # Generate emissions for the month
                generate_emissions(cursor, current_beges_id, profil_id, start_date, end_date, season, transport_ids, aliments, chauffage_ids)

                # Calculate GlobalRank for the BEGES
                cursor.execute(
                    """
                    SELECT AVG(Rank) FROM (
                        SELECT Rank FROM TransportEmission WHERE BEGESId = %s
                        UNION ALL
                        SELECT Rank FROM AlimentationEmission WHERE BEGESId = %s
                        UNION ALL
                        SELECT Rank FROM ChauffageEmission WHERE BEGESId = %s
                    ) AS CombinedRanks
                    """,
                    (current_beges_id, current_beges_id, current_beges_id)
                )
                global_rank = cursor.fetchone()[0]
                cursor.execute("UPDATE BEGES SET GlobalRank = %s WHERE BEGESId = %s", (global_rank, current_beges_id))

        # Commit changes
        connection.commit()
        print("Monthly BEGES records and emissions added successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        if connection:
            connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def daterange(start_date, end_date):
    """Generate a range of dates between two dates."""
    for n in range((end_date - start_date).days + 1):
        yield start_date + datetime.timedelta(days=n)

if __name__ == "__main__":
    add_monthly_beges()
