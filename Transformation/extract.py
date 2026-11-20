
import xml.etree.ElementTree as ET

from datetime import datetime



# --------------------------------------------------
# FONCTIONS UTILITAIRES
# --------------------------------------------------

def _parse_xml(xml_file):
    """Charge le fichier XML et retourne sa racine."""
    tree = ET.parse(xml_file)
    return tree.getroot()


def _parse_coordinate(value):
    """
    Convertit les coordonnées du XML en degrés décimaux.

    Hypothèse actuelle : les coordonnées sont multipliées
    par 100 000. Cette règle devra être validée.
    """
    if not value:
        return None

    try:
        return float(value) / 100000
    except (ValueError, TypeError):
        return None


def _parse_price_date(value):
    """Convertit la date de mise à jour du prix."""
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _parse_time(value):
    """Convertit une heure XML comme 08.30 en 08:30."""
    if not value:
        return None

    return value.replace(".", ":")


# --------------------------------------------------
# 1. EXTRACTION DES PRIX
# --------------------------------------------------

def extract_prices(xml_file, snapshot_date, ingested_at):
    """
    Extrait les prix des carburants depuis le XML.

    Une ligne représente un prix pour une station,
    un carburant et un snapshot.
    """

    root = _parse_xml(xml_file)

    prices = []

    for station in root.findall(".//pdv"):

        station_id = station.get("id")

        for price in station.findall("prix"):

            price_value = price.get("valeur")

            try:
                price_value = float(price_value)
            except (ValueError, TypeError):
                price_value = None

            price_data = {
                "station_id": station_id,
                "fuel_id": price.get("id"),
                "fuel_type": price.get("nom"),
                "price_eur_l": price_value,
                "price_updated_at": _parse_price_date(
                    price.get("maj")
                ),
                "snapshot_date": snapshot_date,
                "ingested_at": ingested_at
            }

            prices.append(price_data)

    return prices


# --------------------------------------------------
# 2. EXTRACTION DES STATIONS
# --------------------------------------------------

def extract_stations(xml_file, snapshot_date):
    """
    Extrait les informations des stations-service.

    Une ligne représente une station pour un snapshot.
    """

    root = _parse_xml(xml_file)

    stations = []

    for station in root.findall(".//pdv"):

        station_data = {
            "station_id": station.get("id"),
            "address": station.findtext("adresse"),
            "city": station.findtext("ville"),
            "postal_code": station.get("cp"),
            "latitude": _parse_coordinate(
                station.get("latitude")
            ),
            "longitude": _parse_coordinate(
                station.get("longitude")
            ),
            "population_type": station.get("pop"),
            "snapshot_date": snapshot_date
        }

        stations.append(station_data)

    return stations


# --------------------------------------------------
# 3. EXTRACTION DES SERVICES
# --------------------------------------------------

def extract_services(xml_file, snapshot_date):
    """
    Extrait les services proposés par les stations.

    Une ligne représente un service pour une station
    et un snapshot.
    """

    root = _parse_xml(xml_file)

    services = []

    for station in root.findall(".//pdv"):

        station_id = station.get("id")

        for service in station.findall("services/service"):

            service_name = (service.text or "").strip()

            if not service_name:
                continue

            service_data = {
                "station_id": station_id,
                "service_name": service_name,
                "snapshot_date": snapshot_date
            }

            services.append(service_data)

    return services


# --------------------------------------------------
# 4. EXTRACTION DES HORAIRES
# --------------------------------------------------

def extract_opening_hours(xml_file, snapshot_date):
    """
    Extrait les horaires d'ouverture des stations.

    Une ligne représente une plage horaire pour un jour,
    une station et un snapshot.
    """

    root = _parse_xml(xml_file)

    opening_hours = []

    for station in root.findall(".//pdv"):

        station_id = station.get("id")

        horaires = station.find("horaires")

        # Certaines stations ne renseignent pas leurs horaires.
        if horaires is None:
            continue

        automate_24_24 = horaires.get("automate-24-24")

        for day in horaires.findall("jour"):

            closed_value = day.get("ferme")

            if closed_value == "1":
                is_closed = True
            elif closed_value == "":
                is_closed = False
            else:
                is_closed = None

            time_slots = day.findall("horaire")

            # Un jour peut ne pas avoir de plage horaire.
            if not time_slots:
                time_slots = [None]

            for time_slot in time_slots:

                if time_slot is None:
                    opening_time = None
                    closing_time = None
                else:
                    opening_time = _parse_time(
                        time_slot.get("ouverture")
                    )
                    closing_time = _parse_time(
                        time_slot.get("fermeture")
                    )

                day_data = {
                    "station_id": station_id,
                    "day_id": day.get("id"),
                    "day_name": day.get("nom"),
                    "is_closed": is_closed,
                    "opening_time": opening_time,
                    "closing_time": closing_time,
                    "automate_24_24": automate_24_24,
                    "snapshot_date": snapshot_date
                }

                opening_hours.append(day_data)

    return opening_hours
