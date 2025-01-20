import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unidecode
import os
import json
from concurrent.futures import ThreadPoolExecutor
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

class FoodFootprintModel:
    def __init__(self, datasets, cache_file="open_food_facts_cache.json"):
        self.datasets = datasets
        self.cache_file = cache_file
        self.column_mappings = {
            "par_etape": "Nom du Produit en Français",
            "par_ingredient": "Nom Français",
            "synthese": "Nom du Produit en Français"
        }
        self.cache = self.load_cache()
        self.agribalyse_data = self.load_datasets()
        self.vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), stop_words="english")
        self.vocabulary = None
        self.precomputed_tfidf = self.precompute_tfidf()

    def load_datasets(self):
        """Load Agribalyse datasets into memory."""
        return {key: pd.read_csv(path) for key, path in self.datasets.items()}

    def load_cache(self):
        """Load cached data from a JSON file."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def save_cache(self):
        """Save the cache to a JSON file."""
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def normalize_text(self, text):
        """Normalize text by removing accents and converting to lowercase."""
        return unidecode.unidecode(text.strip().lower())

    def filter_meaningful_components(self, components):
        """Filter out common stopwords and retain meaningful components."""
        french_stopwords = {"de", "et", "aux", "pour", "avec", "sur", "au"}
        return [component for component in components if component not in french_stopwords]

    def precompute_tfidf(self):
        """Precompute the TF-IDF matrices for all datasets."""
        precomputed_tfidf = {}
        for key, dataset in self.agribalyse_data.items():
            column_name = self.column_mappings[key]
            dataset[column_name] = dataset[column_name].dropna().str.strip().str.lower().apply(unidecode.unidecode)
            
            if self.vocabulary is None:
                # Fit the vectorizer on the first dataset and save the vocabulary
                tfidf_matrix = self.vectorizer.fit_transform(dataset[column_name].tolist())
                self.vocabulary = self.vectorizer.vocabulary_
            else:
                # Use the same vocabulary for other datasets
                temp_vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), stop_words="english", vocabulary=self.vocabulary)
                tfidf_matrix = temp_vectorizer.fit_transform(dataset[column_name].tolist())
            
            precomputed_tfidf[key] = {"matrix": tfidf_matrix, "names": dataset[column_name]}
        return precomputed_tfidf

    def search_in_dataset_with_similarity(self, dataset_key, search_term, weight_kg):
        """Search in a specific Agribalyse dataset using precomputed TF-IDF."""
        column_name = self.column_mappings[dataset_key]
        tfidf_data = self.precomputed_tfidf[dataset_key]
        tfidf_matrix = tfidf_data["matrix"]
        product_names = tfidf_data["names"]

        search_term_vector = self.vectorizer.transform([self.normalize_text(search_term)])
        similarities = cosine_similarity(search_term_vector, tfidf_matrix)[0]

        best_match_index = similarities.argmax()
        best_match_score = similarities[best_match_index]

        if best_match_score > 0.2:
            best_match_product = self.agribalyse_data[dataset_key].iloc[best_match_index]
            product_name = best_match_product[column_name]
            carbon_footprint_per_kg = best_match_product.get("Changement climatique", 0)
            carbon_footprint = carbon_footprint_per_kg * weight_kg
            return {"product_name": product_name, "carbon_footprint": carbon_footprint}

        return None

    def search_in_all_datasets(self, search_term, weight_kg):
        """Search across all Agribalyse datasets."""
        results = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.search_in_dataset_with_similarity, key, search_term, weight_kg) for key in self.agribalyse_data]
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)
        return results

    def search_in_open_food_facts(self, product_name, weight_kg):
        """Search in Open Food Facts and fallback to Agribalyse."""
        # Check cache first
        if product_name in self.cache:
            logging.info(f"Using cached data for '{product_name}'...")
            return self.cache[product_name]

        search_url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": product_name,
            "search_simple": 1,
            "json": 1,
            "page_size": 1,
        }

        try:
            response = requests.get(search_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("products"):
                    product = data["products"][0]
                    product_name = product.get("product_name", "Unknown Product")
                    carbon_footprint_100g = product.get("carbon_footprint_100g", None)

                    if carbon_footprint_100g:
                        carbon_footprint = (float(carbon_footprint_100g) / 100) * weight_kg * 1000
                        result = {"product_name": product_name, "carbon_footprint": carbon_footprint}
                        self.cache[product_name] = result
                        self.save_cache()
                        return result
            logging.info("No products found in Open Food Facts.")
        except requests.exceptions.Timeout:
            logging.warning("Open Food Facts API timeout.")
        except Exception as e:
            logging.error(f"Error occurred: {e}")

        # Fallback to Agribalyse
        logging.info("Switching to Agribalyse datasets...")
        components = self.filter_meaningful_components(product_name.split())
        results = []
        for component in components:
            logging.info(f"Searching for component: {component}...")
            component_results = self.search_in_all_datasets(component, weight_kg)
            results.extend(component_results)

        if results:
            total_footprint = sum(r["carbon_footprint"] for r in results)
            mean_footprint = total_footprint / len(results)
            final_result = {"product_name": product_name, "carbon_footprint": mean_footprint}
            self.cache[product_name] = final_result
            self.save_cache()
            return final_result

        return {"product_name": product_name, "carbon_footprint": None}
