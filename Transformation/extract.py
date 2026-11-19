
import xml.etree.ElementTree as ET

from datetime import datetime, timezone


def extract_prices(xml_file, snapshot_date, ingested_at):
    """
    Extrait les prix des carburants depuis le XML.

    Args:
        xml_file: fichier XML à parcourir.
        snapshot_date: date de collecte du snapshot.
        ingested_at: timestamp d'ingestion.

    Returns:
        Liste de dictionnaires contenant les prix extraits.
    """
    pass


def extract_stations(xml_file, snapshot_date):
    """
    Extrait les informations des stations-service.
    """
    pass


def extract_services(xml_file, snapshot_date):
    """
    Extrait les services proposés par les stations.
    """
    pass


def extract_opening_hours(xml_file, snapshot_date):
    """
    Extrait les horaires d'ouverture des stations.
    """
    pass
