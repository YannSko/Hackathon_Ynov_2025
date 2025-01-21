import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import json

# Database configuration
DB_CONFIG = {
    "host": "localhost",        
    "database": "ClashOfRse",  
    "user": "your_username", 
    "password": "your_password", 
}

def get_database_connection():
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    return create_engine(db_url)

def fetch_data():
    query = """
    SELECT 
        b.BEGESId,
        b.ProfilId,
        b.CO2Total,
        t.CO2EmisTransport AS co2emistransport,
        c.CO2EmisChauffage AS co2emischauffage,
        a.CO2EmisAlimentation AS co2emisalimentation,
        p.DateDeNaissance,
        p.DistanceTravailMaison,
        p.RoleId,
        b.GlobalRank
    FROM BEGES b
    LEFT JOIN TransportEmission t ON b.BEGESId = t.BEGESId
    LEFT JOIN ChauffageEmission c ON b.BEGESId = c.BEGESId
    LEFT JOIN AlimentationEmission a ON b.BEGESId = a.BEGESId
    LEFT JOIN Profil p ON b.ProfilId = p.ProfilId;
    """
    engine = get_database_connection()
    return pd.read_sql_query(query, con=engine)

def preprocess_data(df):
    df['datedenaissance'] = pd.to_datetime(df['datedenaissance'], errors='coerce')
    df['age'] = df['datedenaissance'].apply(lambda x: pd.Timestamp.now().year - x.year if pd.notnull(x) else None)

    numeric_columns = ['co2total', 'co2emistransport', 'co2emischauffage', 'co2emisalimentation', 
                       'distancetravailmaison', 'globalrank', 'age']

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col].fillna(df[col].median(), inplace=True)

    return df, numeric_columns

def find_best_clustering(scaled_data):
    clustering_algorithms = {
        'KMeans': KMeans(n_clusters=3, random_state=42),
        'DBSCAN': DBSCAN(eps=0.5, min_samples=10),
        'Agglomerative': AgglomerativeClustering(n_clusters=3),
        'GMM': GaussianMixture(n_components=3, random_state=42)
    }

    best_algorithm = None
    best_score = -1
    best_labels = None

    for name, algorithm in clustering_algorithms.items():
        if name == 'DBSCAN':
            labels = algorithm.fit_predict(scaled_data)
            if len(set(labels)) <= 1:
                continue
        else:
            labels = algorithm.fit_predict(scaled_data)
        
        score = silhouette_score(scaled_data, labels)
        if score > best_score:
            best_score = score
            best_algorithm = name
            best_labels = labels

    return best_algorithm, best_score, best_labels

def save_clusters_to_db(df, cluster_labels):
    engine = get_database_connection()
    df['Cluster'] = cluster_labels
    df[['begesid', 'Cluster']].to_sql('ClusteringResults', con=engine, if_exists='replace', index=False)
    # Save ProfilId and Cluster as a CSV file
    cluster_csv = df[['profilid', 'Cluster']]
    cluster_csv.to_csv('profilid_clusters.csv', index=False)

def generate_cluster_statistics(df):
    stats = df.groupby('Cluster').mean().to_dict()
    return stats

def main():
    try:
        # Fetch and preprocess data
        raw_data = fetch_data()
        preprocessed_data, numeric_columns = preprocess_data(raw_data)

        # Scale data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(preprocessed_data[numeric_columns])

        # Find best clustering algorithm
        best_algo, best_score, cluster_labels = find_best_clustering(scaled_data)
        print(f"Best algorithm: {best_algo} with silhouette score: {best_score}")

        # Save clusters to DB and CSV
        save_clusters_to_db(preprocessed_data, cluster_labels)

        # Generate statistics
        stats = generate_cluster_statistics(preprocessed_data)

        # Output statistics and CSV path
        return json.dumps({
            "best_algorithm": best_algo,
            "silhouette_score": best_score,
            "cluster_statistics": stats,
            "csv_file": "profilid_clusters.csv"
        }, indent=4)

    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    result = main()
    print(result)
