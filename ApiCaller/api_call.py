import requests
import sys
import logging
from pathlib import Path
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main(args=sys.argv[1:]):
    logging.info("Starting ApiCaller")
    # Checking for conditions regarding the I/O buffer folder
    if len(sys.argv) < 3:
        logging.error("Missing Arguments!")
        logging.info("Usage: ApiCaller [input-folder][output-folder]")
        sys.exit(1)
    in_folder = sys.argv[1]
    out_folder = sys.argv[2]
    if not Path(in_folder).exists() or not Path(out_folder).exists():
        logging.error("I/O paths don't exist")
        sys.exit(1)

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
        for image_filename in series[item]:
            files = {"image": open(os.path.join(in_folder, image_filename), "rb")}
            response = requests.post("http://10.0.2.2:8001/upload", files=files)
            print(response.json())
