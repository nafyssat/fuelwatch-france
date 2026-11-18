
# FuelWatch France ⛽

## Présentation

**FuelWatch France** est un projet de Data Engineering visant à collecter, historiser, transformer et analyser les prix des carburants en France à partir des données Open Data officielles.


## Problématique métier

Les prix des carburants évoluent régulièrement et varient selon les stations-service et les territoires.

FuelWatch France cherche à répondre à plusieurs questions :

- Quelles sont les stations-service les moins chères ?
- Comment évoluent les prix des carburants dans le temps ?
- Quels départements présentent les prix moyens les plus élevés ?
- Quelles stations ont récemment augmenté ou diminué leurs prix ?
- Quels sont les écarts de prix entre les régions ?

## Source de données

Les données proviennent du portail officiel Open Data des prix des carburants :

- **Portail :** https://www.prix-carburants.gouv.fr/rubrique/opendata/
- **Flux instantané :** https://donnees.roulez-eco.fr/opendata/instantane

Les données sont fournies sous forme d'archives ZIP contenant des fichiers XML.

## Architecture cible

Le projet s'appuiera sur une architecture Data Lake organisée en trois couches :

| Couche | Responsabilité |
|---|---|
| Bronze | Conservation des données brutes |
| Silver | Extraction, nettoyage et normalisation |
| Gold | Agrégations et indicateurs métier |

## Stack technique envisagée

| Technologie | Utilisation |
|---|---|
| Python | Ingestion et traitement des données |
| Requests | Téléchargement des données |
| PostgreSQL | Stockage analytique |
| dbt | Transformations SQL |
| Apache Airflow | Orchestration des pipelines |
| Docker | Conteneurisation |
| Power BI | Visualisation et reporting |
| Git / GitHub | Versionnement du code |

Des extensions pourront être étudiées ultérieurement, notamment Kafka pour l'ingestion événementielle et le streaming.

## Structure du projet

```text
fuelwatch-france/
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── src/
│   └── ingestion/
│
├── logs/
│
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Roadmap

- [ ] Initialisation de l'environnement Python
- [ ] Développement du pipeline d'ingestion
- [ ] Téléchargement et archivage des données brutes
- [ ] Extraction et analyse de la structure XML
- [ ] Construction des couches Bronze, Silver et Gold
- [ ] Mise en place des contrôles de qualité des données
- [ ] Modélisation et stockage dans PostgreSQL
- [ ] Développement des transformations avec dbt
- [ ] Orchestration avec Apache Airflow
- [ ] Création d'un dashboard Power BI
- [ ] Tests, documentation et amélioration du pipeline

## Objectifs techniques

Le projet vise notamment à mettre en œuvre les principes suivants :

- Data Ingestion et ETL / ELT
- Data Lake et architecture Medallion
- Historisation des données
- Idempotence et gestion des doublons
- Data Quality
- Gestion des erreurs et mécanismes de reprise
- Orchestration des workflows
- Modélisation dimensionnelle

## Statut du projet

🚧 **En cours de développement — Phase 1 : Ingestion des données**

---

*FuelWatch France — Un projet pratique de Data Engineering basé sur des données publiques réelles.*
