# General Import
import os
import sys
import json
from pathlib import Path
import logging

# Importing DICOM specific lib
import pydicom
from pydicom.uid import generate_uid


import mysql.connector
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def store_dicom_data(in_folder):
    try:
        connection = mysql.connector.connect(
            host="172.17.0.2",
            port=3306,
            user="root",
            password="root",
            database="dicom_tag_test",
        )
        cursor = connection.cursor()
        for entry in os.scandir(in_folder):
            if entry.name.endswith(".dcm") and not entry.is_dir():
                ds = pydicom.dcmread(Path(in_folder) / entry.name)
                patient_name = ds.PatientName
                patient_id = ds.PatientID
                series_uid = ds.SeriesInstanceUID
                cursor.execute(
                    "INSERT INTO dicom_data (patient_name, patient_id, series_uid) VALUES (%s, %s, %s)",
                    (str(patient_name), int(patient_id), str(series_uid)),
                )
        connection.commit()
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
    finally:
        if "connection" in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    return


def anonymize_image(file, in_folder, out_folder, series_uid, settings):
    # I/O formating for mercure
    dcm_file_in = Path(in_folder) / file
    logging.info(f"Anonymizing {dcm_file_in}")
    out_filename = series_uid + "#" + file.split("#", 1)[1]
    dcm_file_out = Path(out_folder) / out_filename

    # Anonymize the DICOM file
    ds = pydicom.dcmread(dcm_file_in)
    ds.SeriesInstanceUID = series_uid
    ds.SOPInstanceUID = generate_uid()
    ds.SeriesNumber = ds.SeriesNumber + 1000
    ds.SeriesDescription = "Anonymized(" + ds.SeriesDescription + ")"
    ds.PatientName = "Anonymized"
    ds.PatientBirthDate = "Anonymized"
    ds.save_as(dcm_file_out)


#
def main(args=sys.argv[1:]):
    logging.info("Starting Anonymizer")

    # Checking for conditions regarding the I/O buffer folder
    if len(sys.argv) < 3:
        logging.error("Missing Arguments!")
        logging.info("Usage: Anonymizer [input-folder][output-folder]")
        sys.exit(1)
    in_folder = sys.argv[1]
    out_folder = sys.argv[2]
    if not Path(in_folder).exists() or not Path(out_folder).exists():
        logging.error("I/O paths don't exist")
        sys.exit(1)

    # Loading setting from the task.json file
    try:
        with open(Path(in_folder) / "task.json", "r") as json_file:
            task = json.load(json_file)
    except Exception as e:
        logging.error(f"Error: Task file task.json not found {e}")
        sys.exit(1)

    setting = {"series_offset": 1000}
    if task.get("process", ""):
        setting.update(task["process"].get("settings", {}))

    # Collecting all DICOM series for processing
    series = {}
    for entry in os.scandir(in_folder):
        if entry.name.endswith(".dcm") and not entry.is_dir():
            seriesString = entry.name.split("#", 1)[0]
            if seriesString not in series.keys():
                series[seriesString] = []
            series[seriesString].append(entry.name)

    # Anonymize each series found
    for item in series:
        series_uid = generate_uid()
        for image_filename in series[item]:
            store_dicom_data(in_folder)
            anonymize_image(
                image_filename,
                in_folder,
                out_folder,
                series_uid,
                setting,
            )


if __name__ == "__main__":
    main()
