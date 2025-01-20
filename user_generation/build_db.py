import psycopg2
# Script création BDE
# confing connexion bde
DB_HOST = "localhost"
DB_NAME = "ClashOfRse"
DB_USER = "your_username"
DB_PASSWORD = "your_password"

# Requêtes SQL création eds tables
CREATE_TABLES_SQL = [
    """
    CREATE TABLE Role (
        RoleId SERIAL PRIMARY KEY,
        Nom VARCHAR(255) NOT NULL
    );
    """,
    """
    CREATE TABLE Profil (
        ProfilId SERIAL PRIMARY KEY,
        RoleId INT NOT NULL,
        Nom VARCHAR(255) NOT NULL,
        Prenom VARCHAR(255) NOT NULL,
        DateDeNaissance DATE,
        Email VARCHAR(255) UNIQUE NOT NULL,
        Entreprise VARCHAR(255),
        Image VARCHAR(255),
        DistanceTravailMaison FLOAT,
        CONSTRAINT fk_role FOREIGN KEY (RoleId) REFERENCES Role(RoleId) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE Defi (
        DefiId SERIAL PRIMARY KEY,
        Nom VARCHAR(255) NOT NULL,
        Description VARCHAR(500),
        Objectif INT NOT NULL
    );
    """,
    """
    CREATE TABLE ProgressionDefi (
        ProgressionId SERIAL PRIMARY KEY,
        ProfilId INT NOT NULL,
        DefiId INT NOT NULL,
        Score INT NOT NULL,
        CONSTRAINT fk_profil_progression FOREIGN KEY (ProfilId) REFERENCES Profil(ProfilId) ON DELETE CASCADE,
        CONSTRAINT fk_defi_progression FOREIGN KEY (DefiId) REFERENCES Defi(DefiId) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE BEGES (
        BEGESId SERIAL PRIMARY KEY,
        ProfilId INT NOT NULL,
        DateDebut DATE NOT NULL,
        DateFin DATE NOT NULL,
        CO2Total FLOAT NOT NULL,
        CONSTRAINT fk_profil_beges FOREIGN KEY (ProfilId) REFERENCES Profil(ProfilId) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE Transport (
        TransportId SERIAL PRIMARY KEY,
        Nom VARCHAR(255) NOT NULL,
        CO2parKm FLOAT NOT NULL
    );
    """,
    """
    CREATE TABLE TransportEmission (
        TransportEmissionId SERIAL PRIMARY KEY,
        TransportId INT NOT NULL,
        BEGESId INT NOT NULL,
        CO2EmisTransport FLOAT NOT NULL,
        DateDebut DATE NOT NULL,
        DateFin DATE NOT NULL,
        Rank INT,
        CONSTRAINT fk_transport FOREIGN KEY (TransportId) REFERENCES Transport(TransportId) ON DELETE CASCADE,
        CONSTRAINT fk_beges_transport FOREIGN KEY (BEGESId) REFERENCES BEGES(BEGESId) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE Chauffage (
        ChauffageId SERIAL PRIMARY KEY,
        Nom VARCHAR(255) NOT NULL,
        CO2parM FLOAT NOT NULL
    );
    """,
    """
    CREATE TABLE ChauffageEmission (
        ChauffageEmissionId SERIAL PRIMARY KEY,
        ChauffageId INT NOT NULL,
        BEGESId INT NOT NULL,
        CO2EmisChauffage FLOAT NOT NULL,
        DateDebut DATE NOT NULL,
        DateFin DATE NOT NULL,
        Rank INT,
        CONSTRAINT fk_chauffage FOREIGN KEY (ChauffageId) REFERENCES Chauffage(ChauffageId) ON DELETE CASCADE,
        CONSTRAINT fk_beges_chauffage FOREIGN KEY (BEGESId) REFERENCES BEGES(BEGESId) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE Aliment (
        AlimentId SERIAL PRIMARY KEY,
        Nom VARCHAR(255) NOT NULL,
        CO2par100g FLOAT NOT NULL,
        MasseKG FLOAT NOT NULL
    );
    """,
    """
    CREATE TABLE AlimentationEmission (
        AlimentationEmissionId SERIAL PRIMARY KEY,
        AlimentId INT NOT NULL,
        BEGESId INT NOT NULL,
        CO2EmisAlimentation FLOAT NOT NULL,
        DateDebut DATE NOT NULL,
        DateFin DATE NOT NULL,
        Rank INT,
        CONSTRAINT fk_aliment FOREIGN KEY (AlimentId) REFERENCES Aliment(AlimentId) ON DELETE CASCADE,
        CONSTRAINT fk_beges_alimentation FOREIGN KEY (BEGESId) REFERENCES BEGES(BEGESId) ON DELETE CASCADE
    );
    """
]

# Connexion  PostgreSQL + exécution  requêtes
try:
    # Connexion à la base de données
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    # Exéc requêtes SQL
    for sql in CREATE_TABLES_SQL:
        cursor.execute(sql)
        print(f"Table created successfully:\n{sql.strip().split(' ')[2]}")

    # Validation des changements
    connection.commit()
    print("All tables created successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
    if connection:
        connection.rollback()

finally:

    if cursor:
        cursor.close()
    if connection:
        connection.close()
