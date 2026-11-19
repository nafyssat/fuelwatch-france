
import os
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

import boto3
import requests

from botocore.client import Config
from botocore.exceptions import ClientError


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

FUEL_SOURCE_URL = (
    "https://donnees.roulez-eco.fr/opendata/instantane"
)

ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("R2_BUCKET_NAME")


def validate_configuration():
    """Vérifie que les variables d'environnement sont présentes."""

    required_variables = {
        "R2_ACCOUNT_ID": ACCOUNT_ID,
        "R2_ACCESS_KEY_ID": ACCESS_KEY_ID,
        "R2_SECRET_ACCESS_KEY": SECRET_ACCESS_KEY,
        "R2_BUCKET_NAME": BUCKET_NAME,
    }

    missing = [
        name
        for name, value in required_variables.items()
        if not value
    ]

    if missing:
        raise ValueError(
            f"Variables d'environnement manquantes : {missing}"
        )


# --------------------------------------------------
# CONNEXION CLOUDflare R2
# --------------------------------------------------

def get_r2_client():
    """Construit et retourne un client S3 compatible avec R2."""

    return boto3.client(
        service_name="s3",
        endpoint_url=(
            f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"
        ),
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


# --------------------------------------------------
# TELECHARGEMENT DU ZIP
# --------------------------------------------------

def download_fuel_data(local_file_path):
    """Télécharge l'archive ZIP depuis la source officielle."""

    try:
        with requests.get(
            FUEL_SOURCE_URL,
            stream=True,
            timeout=(10, 120),
        ) as response:

            response.raise_for_status()

            with open(local_file_path, "wb") as file:
                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        file.write(chunk)

        if os.path.getsize(local_file_path) == 0:
            raise ValueError("L'archive téléchargée est vide.")

        print("Téléchargement terminé.")

    except requests.RequestException as error:
        raise RuntimeError(
            f"Erreur pendant le téléchargement : {error}"
        ) from error


# --------------------------------------------------
# UPLOAD VERS R2
# --------------------------------------------------

def upload_to_r2(local_file_path, object_name):
    """Envoie le fichier local dans le bucket R2."""

    client = get_r2_client()

    try:
        client.upload_file(
            local_file_path,
            BUCKET_NAME,
            object_name,
            ExtraArgs={
                "ContentType": "application/zip"
            },
        )

        print(f"Archive envoyée dans R2 : {object_name}")

    except ClientError as error:
        raise RuntimeError(
            f"Erreur pendant l'upload R2 : {error}"
        ) from error


# --------------------------------------------------
# ORCHESTRATION : DOWNLOAD + UPLOAD + CLEANUP
# --------------------------------------------------

def ingest_fuel_data():
    """Orchestre le téléchargement et le stockage Bronze."""

    validate_configuration()

    now = datetime.now(ZoneInfo("Europe/Paris"))

    object_name = (
        f"bronze/{now:%Y/%m/%d}/prix-carburants.zip"
    )

    temporary_file = None

    try:
        # Création d'un fichier temporaire
        with tempfile.NamedTemporaryFile(
            suffix=".zip",
            delete=False,
        ) as temp_file:
            temporary_file = temp_file.name

        # Téléchargement
        download_fuel_data(temporary_file)

        # Upload vers Cloudflare R2
        upload_to_r2(
            temporary_file,
            object_name,
        )

        print("Ingestion Bronze terminée avec succès.")

    finally:
        # Suppression du fichier temporaire
        if temporary_file and os.path.exists(temporary_file):
            os.remove(temporary_file)
            print("Fichier temporaire supprimé.")


