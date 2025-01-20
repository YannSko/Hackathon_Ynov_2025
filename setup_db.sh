#!/bin/bash

# Vérifiez que le script est exécuté avec bash
if [ -z "$BASH_VERSION" ]; then
  echo "Ce script doit être exécuté avec bash."
  exit 1
fi

echo ">>> Démarrage du pipeline"

# Étape 1: Lancer Docker Compose
echo ">>> Démarrage de Docker Compose..."
docker-compose up -d
if [ $? -ne 0 ]; then
  echo "Erreur lors du démarrage de Docker Compose."
  exit 1
fi

echo ">>> Docker Compose démarré avec succès."

# Étape 2: Exécuter le script build_db.py
echo ">>> Exécution de build_db.py..."
python build_db.py
if [ $? -ne 0 ]; then
  echo "Erreur lors de l'exécution de build_db.py."
  exit 1
fi

echo ">>> Base de données construite avec succès."

# Étape 3: Exécuter le script food_gene.py
echo ">>> Exécution de food_gene.py..."
python food_gene.py
if [ $? -ne 0 ]; then
  echo "Erreur lors de l'exécution de food_gene.py."
  exit 1
fi

echo ">>> Génération des aliments terminée avec succès."

# Étape 4: Exécuter le script transports_gene.py
echo ">>> Exécution de transports_gene.py..."
python transports_gene.py
if [ $? -ne 0 ]; then
  echo "Erreur lors de l'exécution de transports_gene.py."
  exit 1
fi

echo ">>> Génération des transports terminée avec succès."

# Étape 5: Exécuter le script end_gene.py
echo ">>> Exécution de end_gene.py..."
python end_gene.py
if [ $? -ne 0 ]; then
  echo "Erreur lors de l'exécution de end_gene.py."
  exit 1
fi

echo ">>> Génération finale des données terminée avec succès."

# Étape 6: Vérifier la base de données avec check_database.py
echo ">>> Exécution de check_database.py..."
python check_database.py
if [ $? -ne 0 ]; then
  echo "Erreur lors de l'exécution de check_database.py."
  exit 1
fi

echo ">>> Vérification de la base de données terminée avec succès."

echo ">>> Pipeline exécuté avec succès !"
