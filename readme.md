
# FuelWatch France

## Présentation

**FuelWatch France** est un projet de Data Engineering et d'Analytics Engineering visant à collecter, stocker, transformer et analyser les prix des carburants en France à partir des données ouvertes officielles.

L'objectif est de construire un pipeline de données automatisé reposant sur une architecture Medallion (Bronze, Silver, Gold), afin de produire des indicateurs fiables sur les prix des carburants à l'échelle nationale et départementale.

## Objectifs du projet

- Automatiser la collecte quotidienne des données officielles.
- Construire un Data Lake dans le cloud.
- Conserver les données brutes pour assurer leur traçabilité.
- Transformer les données XML en données structurées et normalisées.
- Produire des tables analytiques adaptées aux besoins métier.
- Mettre en place des contrôles de qualité des données.
- Automatiser l'exécution du pipeline.
- Concevoir un dashboard pour analyser les prix des carburants.

## Source de données

Les données proviennent du portail officiel français des prix des carburants :

- [Portail Open Data des prix des carburants](https://www.prix-carburants.gouv.fr/rubrique/opendata/)
- [Flux instantané](https://donnees.roulez-eco.fr/opendata/instantane)

Le flux instantané fournit une archive ZIP contenant un fichier XML avec les informations des stations-service et les prix des carburants.

La collecte est prévue quotidiennement afin de constituer un historique des prix.

## Architecture technique

Le projet repose sur une architecture Medallion organisée en trois couches :

### Bronze — Données brutes

**Technologies : Python, Requests, Boto3, Cloudflare R2**

Responsabilités :

- Télécharger quotidiennement l'archive ZIP depuis la source officielle.
- Conserver les données brutes sans modification.
- Stocker les archives dans Cloudflare R2.
- Organiser les fichiers par date de collecte.

### Silver — Données nettoyées et structurées

**Technologies : Python, DuckDB, Parquet**

Responsabilités :

- Extraire le fichier XML de l'archive ZIP.
- Parser les informations des stations-service et des carburants.
- Nettoyer et normaliser les données.
- Convertir les types de données.
- Produire des fichiers Parquet structurés.
- Stocker les résultats dans Cloudflare R2.

### Gold — Données analytiques

**Technologies : dbt-duckdb, SQL, Parquet**

Responsabilités :

- Construire des modèles analytiques à partir de la couche Silver.
- Agréger les prix par département et type de carburant.
- Identifier les stations les moins chères.
- Analyser l'évolution des prix dans le temps.
- Ajouter des tests de qualité et documenter les modèles.

## Stack technique

| Domaine | Technologie |
|---|---|
| Langage | Python |
| Collecte des données | Requests |
| Accès au stockage cloud | Boto3 |
| Data Lake | Cloudflare R2 |
| Format de stockage | Parquet |
| Moteur SQL | DuckDB |
| Transformation analytique | dbt-duckdb |
| Infrastructure as Code | Terraform |
| Orchestration | GitHub Actions |
| Versionnement | Git / GitHub |
| Visualisation | Power BI ou Streamlit |

## Organisation du stockage

Un bucket Cloudflare R2 est utilisé pour stocker les différentes couches du Data Lake.

```text
fuelwatch-france-bronze/
│
├── bronze/
│   └── YYYY/MM/DD/
│       └── prix-carburants.zip
│
├── silver/
│   └── prices/
│       └── snapshot_date=YYYY-MM-DD/
│           └── part-000.parquet
│
└── gold/
    ├── department_prices/
    ├── cheapest_stations/
    └── price_evolution/
```

Les répertoires représentent des préfixes d'objets dans R2.

## Modèle de données envisagé

La table principale de la couche Silver sera `silver_prices`.

Son grain sera une observation de prix par station, type de carburant et instantané de collecte.

| Colonne | Description |
|---|---|
| `station_id` | Identifiant de la station-service |
| `postal_code` | Code postal |
| `city` | Ville |
| `latitude` | Latitude de la station |
| `longitude` | Longitude de la station |
| `fuel_id` | Identifiant du carburant |
| `fuel_type` | Type de carburant |
| `price_eur_l` | Prix du carburant en euros par litre |
| `price_updated_at` | Date de mise à jour du prix |
| `snapshot_date` | Date de collecte de l'instantané |
| `ingested_at` | Date et heure d'ingestion |

Ce schéma est provisoire et sera confirmé après l'analyse complète de la structure XML.

## Organisation du projet

```text
FUELWATCH-FRANCE/
│
├── Ingestion/
│   └── storage.py
│
├── Transformation/
│   ├── inspect_xml.py
│   ├── extract.py
│   └── load.py
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── tests/
│   └── dbt_project.yml
│
├── tests/
│   ├── test_ingestion.py
│   └── test_transformation.py
│
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── storage.tf
```

## État d'avancement

### Réalisé

- [x] Création du projet Cloudflare.
- [x] Création du bucket R2 avec Terraform.
- [x] Configuration des accès R2.
- [x] Mise en place de l'environnement Python.
- [x] Développement de l'ingestion des données.
- [x] Téléchargement de l'archive ZIP depuis la source officielle.
- [x] Upload de l'archive dans Cloudflare R2.
- [x] Organisation du stockage Bronze par date.
- [x] Première inspection de la structure XML.

### En cours

- [ ] Analyse complète de la structure XML.
- [ ] Développement du parseur XML.
- [ ] Création de la table Silver.
- [ ] Conversion des données en Parquet.
- [ ] Stockage de la couche Silver dans R2.

### À venir

- [ ] Configuration de DuckDB.
- [ ] Initialisation de dbt-duckdb.
- [ ] Développement des modèles analytiques Gold.
- [ ] Mise en place des tests de qualité des données.
- [ ] Automatisation quotidienne avec GitHub Actions.
- [ ] Développement du dashboard.
- [ ] Documentation complète de l'architecture.

## Choix d'architecture

- **Cloudflare R2** assure le stockage durable des données.
- **DuckDB** est utilisé comme moteur de traitement SQL.
- **Parquet** est utilisé comme format de stockage des données structurées.
- **dbt-duckdb** permet de construire et tester les modèles analytiques.
- **GitHub Actions** assurera l'orchestration quotidienne du pipeline.

Les traitements seront exécutés dans un environnement cloud. Les fichiers locaux éventuels seront temporaires et supprimés après utilisation.

## Limites et considérations

La collecte quotidienne du flux instantané constitue un historique de snapshots quotidiens et non un historique exhaustif de toutes les variations intrajournalières.

La date de mise à jour d'un prix (`price_updated_at`) doit être distinguée de la date de collecte (`snapshot_date`) et de la date d'ingestion (`ingested_at`).

## Auteur

Projet personnel de Data Engineering et Analytics Engineering — FuelWatch France.
