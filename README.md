# Hackathon Ynov 2025

Bienvenue dans le projet **Hackathon Ynov 2025**, une solution innovante pour mesurer et optimiser l'empreinte environnementale à travers des indices personnalisés liés à la consommation alimentaire, le chauffage, et les transports.
Elle calcule les mesures rse et classe les collaborateurs d'une entreprise

## Table des matières

- [Contexte](#contexte)
- [Fonctionnalités](#fonctionnalités)
- [Architecture du projet](#architecture-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API et Endpoints](#api-et-endpoints)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Contexte

Ce projet a été développé dans le cadre du Hackathon Ynov 2025. L'objectif principal est de fournir une solution clé en main permettant de :

- Calculer des indices environnementaux personnalisés.
- Intégrer des données issues de multiples APIs pour fournir des recommandations précises + Clustering des Users + Prevision des besoins
- Exploiter des données via une base relationnelle.

## Fonctionnalités

1. **Calcul des indices environnementaux**
   - Émissions liées à l'alimentation.
   - Empreinte carbone des systèmes de chauffage.
   - Émissions des modes de transport.

2. **Recommandations basées sur les données**
   - Proposition d'alternatives optimisées, recommandantions en fonction du cluster et prevision en fonction de la demande

3. **Déploiement Cloud**
   - Fonctionnalités intégrées dans une Azure Function pour une exécution scalable. 2 azures fonctions l'un pour l'un pipeline de la data requete api, trigger en fonction de la demande client, et le second permet de clusteriser les clients.

4. **Support de l'intégration avec des bases de données**
   - Génération,Stockage et gestion des résultats dans des tables dédiée, set up dans les bases de données

## Architecture du projet

```
Hackathon_Ynov_2025/
├── data/               # Datasets Agribalyse + bdd données & de chaque tables
├── scripts/            # Scripts principaux pour requetees les api et creer des indicateurs de consommations en fonctio de  lasource
│   ├── api/            # Gestion des appels API (alimentation, chauffage, transport)
│   ├── index_calculations.py
│   ├── main_pipeline.py
├── tests/              # Tests unitaires
├── azure_functions/    # Déploiement des fonctions Azure
├── README.md           # Documentation du projet
|── models/   avec son notebook pour set up l'installation,  developpe les modèles et le raisonnement des différents éléments


## Installation

### Prérequis

- **Python 3.8+** + le requirements.txt
- **PostgreSQL** pour la base de données relationnelle.
- **Azure CLI** pour gérer le déploiement cloud.

### Étapes d'installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/YannSko/Hackathon_Ynov_2025.git
   cd Hackathon_Ynov_2025
   ```

2. Créez un environnement virtuel et activez-le :
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez les variables d'environnement pour la base de données et les APIs :
   ```bash
   export DB_HOST="<votre_hôte>"
   export DB_USER="<votre_utilisateur>"
   export DB_PASSWORD="<votre_mot_de_passe>"
   export DB_NAME="<nom_base_de_données>"
   ```

5. Exécutez les migrations SQL (si nécessaire).

6. Lancez le projet en local :
   ```bash
   func start
   ```

## Utilisation

1. Accédez à l'interface (via Postman ou une interface front-end connectée à l'Azure Function).
2. Fournissez les paramètres requis (e.g., alimentation, chauffage, transport).
3. Consultez les résultats détaillés sous format JSON ou dans la base de données associée.

## API et Endpoints

| Endpoint                  | Méthode | Description                                   |
|---------------------------|---------|-----------------------------------------------|
| `/api/calculate_indices`  | POST    | Calculer les indices environnementaux        |
| `/api/recommendations`    | GET     | Récupérer des alternatives optimisées        |

### Exemple de requête

```json
{
  "product_name": "pomme de terre",
  "weight_kg": 1,
  "m2": 50,
  "heating_id": 3,
  "season": "winter",
  "distance": 100,
  "transport_id": 4
}
```

### Réponse attendue

```json
{
  "indices": {
    "Food": {"User Index": 85, "Rank": 2},
    "Heating": {"User Index": 90, "Rank": 1},
    "Transport": {"User Index": 60, "Rank": 3},
    "Global Rank": 2
  }
}
```

## Contribuer

Les contributions sont les bienvenues !

1. Forkez ce dépôt.
2. Créez une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma_fonctionnalité
   ```
3. Faites vos modifications et validez-les.
4. Soumettez une pull request.

## Licence

Ce projet est sous licence MIT. Veuillez consulter le fichier `LICENSE` pour plus d'informations.
