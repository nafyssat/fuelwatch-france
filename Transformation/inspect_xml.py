
import os
import boto3
import zipfile
import xml.etree.ElementTree as ET

from io import BytesIO
from dotenv import load_dotenv


# 1. Charger la configuration
load_dotenv()

account_id = os.getenv("R2_ACCOUNT_ID")
access_key = os.getenv("R2_ACCESS_KEY_ID")
secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
bucket_name = os.getenv("R2_BUCKET_NAME")

if not all([account_id, access_key, secret_key, bucket_name]):
    raise ValueError("Configuration R2 incomplète. Vérifie ton fichier .env.")


# 2. Créer le client R2
s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="auto",
)


# 3. Télécharger l'archive depuis R2 en mémoire
object_name = "bronze/2026/11/19/prix-carburants.zip"

print("Téléchargement de l'archive depuis R2...")

response = s3.get_object(
    Bucket=bucket_name,
    Key=object_name
)

zip_data = BytesIO(response["Body"].read())

print("Archive téléchargée.")


# 4. Examiner le contenu du ZIP
with zipfile.ZipFile(zip_data) as archive:

    files = archive.namelist()

    print("\nFichiers présents dans l'archive :")
    for file in files:
        print("-", file)

    xml_files = [
        file for file in files
        if file.lower().endswith(".xml")
    ]

    if not xml_files:
        raise ValueError("Aucun fichier XML trouvé dans l'archive.")

    xml_file = xml_files[0]

    print(f"\nInspection du fichier XML : {xml_file}")

    # 5. Lire la structure du XML
    with archive.open(xml_file) as xml:

        depth = 0
        records_found = 0

        for event, element in ET.iterparse(xml, events=("start", "end")):

            if event == "start":
                depth += 1

                if depth == 1:
                    print("\nÉlément racine :", element.tag)
                    print("Attributs :", element.attrib)

                elif depth == 2 and records_found < 2:
                    print(f"\nExemple d'enregistrement : {element.tag}")
                    print("Attributs :", element.attrib)

            else:
                if depth == 2 and records_found < 2:
                    print("Sous-éléments :")

                    for child in element:
                        print(
                            f"  - {child.tag} | "
                            f"Attributs : {child.attrib} | "
                            f"Valeur : {child.text}"
                        )

                    records_found += 1
                    element.clear()

                depth -= 1

            if records_found >= 2:
                break

print("\nInspection terminée.")
