
import os
import boto3
import zipfile
import xml.etree.ElementTree as ET

from io import BytesIO
from dotenv import load_dotenv


def display_tree(element, level=0):
    """Affiche récursivement la structure d'un élément XML."""

    indentation = "  " * level

    print(
        f"{indentation}{element.tag} "
        f"| Attributs : {element.attrib} "
        f"| Texte : {(element.text or '').strip()}"
    )

    for child in element:
        display_tree(child, level + 1)


def inspect_xml():

    # 1. Charger les variables d'environnement
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

    # 3. Télécharger l'archive depuis R2
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

        

        
        # Rechercher des horaires détaillés dans tout le XML
        found = 0

        with archive.open(xml_file) as xml:
            for event, element in ET.iterparse(xml, events=("end",)):

                if element.tag == "pdv":

                    jours = element.findall("./horaires/jour")

                    jours_detailles = [
                        jour for jour in jours if len(jour) > 0
                    ]

                    if jours_detailles:
                        print("\nStation :", element.get("id"))
                        print("Ville :", element.findtext("ville"))

                        for jour in jours_detailles:
                            display_tree(jour)

                        found += 1

                        if found == 3:
                            break

                    element.clear()

        if found == 0:
            print("Aucun horaire détaillé trouvé dans cet échantillon.")


if __name__ == "__main__":
    inspect_xml()
