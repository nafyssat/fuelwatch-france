
import json
import logging
from io import BytesIO

import pyarrow as pa
import pyarrow.parquet as pq


logger = logging.getLogger(__name__)


# --------------------------------------------------
# 1. CONVERSION D'UNE LISTE EN TABLE PARQUET
# --------------------------------------------------

def list_to_parquet(records):
    """
    Convertit une liste de dictionnaires Python
    en fichier Parquet conservé en mémoire.
    """
    table = pa.Table.from_pylist(records)

    buffer = BytesIO()
    pq.write_table(table, buffer)

    return buffer.getvalue()


# --------------------------------------------------
# 2. CHARGEMENT D'UN FICHIER PARQUET DANS R2
# --------------------------------------------------

def upload_parquet_to_r2(s3_client, bucket_name, data, object_name):
    """
    Envoie un fichier Parquet vers Cloudflare R2
    sans le sauvegarder sur le disque local.
    """
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=data,
        ContentType="application/vnd.apache.parquet"
    )

    logger.info("Fichier envoyé dans R2 : %s", object_name)


# --------------------------------------------------
# 3. CRÉATION DU MANIFESTE JSON
# --------------------------------------------------

def upload_manifest_to_r2(
    s3_client,
    bucket_name,
    manifest,
    object_name
):
    """
    Envoie le manifeste JSON dans R2.
    """
    manifest_data = json.dumps(
        manifest,
        indent=4,
        ensure_ascii=False
    ).encode("utf-8")

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=manifest_data,
        ContentType="application/json"
    )

    logger.info("Manifeste envoyé dans R2 : %s", object_name)


# --------------------------------------------------
# 4. CHARGEMENT DES QUATRE TABLES SILVER
# --------------------------------------------------

def load_silver_data(
    s3_client,
    bucket_name,
    prices,
    stations,
    services,
    opening_hours,
    snapshot_date
):
    """
    Convertit les quatre extractions en Parquet,
    les envoie dans R2 et publie un manifeste.
    """

    snapshot = snapshot_date.strftime("%Y-%m-%d")

    datasets = {
        "prices": prices,
        "stations": stations,
        "services": services,
        "opening_hours": opening_hours
    }

    # Suivi individuel de chaque table
    table_status = {}

    for name, records in datasets.items():

        if not records:
            table_status[name] = {
                "status": "failed",
                "error": "Aucune donnée disponible"
            }
            logger.error("Aucune donnée pour %s", name)
            continue

        try:
            # Conversion en Parquet
            parquet_data = list_to_parquet(records)

            # Nom de l'objet dans R2
            object_name = (
                f"silver/{name}/snapshot_date={snapshot}/data.parquet"
            )
            
            # Upload dans R2
            upload_parquet_to_r2(
                s3_client,
                bucket_name,
                parquet_data,
                object_name
            )

            table_status[name] = {
                "status": "success",
                "object": object_name,
                "row_count": len(records)
            }

        except Exception as error:
            table_status[name] = {
                "status": "failed",
                "error": str(error)
            }

            logger.exception("Échec du chargement de %s", name)

    # --------------------------------------------------
    # 5. CONSTRUCTION DU MANIFESTE
    # --------------------------------------------------

    all_success = all(
        table["status"] == "success"
        for table in table_status.values()
    )

    manifest = {
        "snapshot_date": snapshot,
        "status": "completed" if all_success else "failed",
        "tables": table_status
    }

    manifest_object = (
        f"silver/manifests/snapshot_date={snapshot}/manifest.json"
    )

    # Publication du manifeste
    try:
        upload_manifest_to_r2(
            s3_client,
            bucket_name,
            manifest,
            manifest_object
        )
    except Exception:
        logger.exception("Impossible de publier le manifeste")
        raise

    # Le pipeline doit échouer si au moins une table a échoué
    if not all_success:
        raise RuntimeError(
            f"Snapshot {snapshot} incomplet. "
            f"Consulter le manifeste : {manifest_object}"
        )

    logger.info("Snapshot %s chargé avec succès", snapshot)

    return manifest
