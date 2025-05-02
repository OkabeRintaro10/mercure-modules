import os
import sys
import json
from pathlib import Path
import pydicom
from pydicom.uid import generate_uid


def anonymize_image(file, in_folder, out_folder, series_uid, settings):
    """
    Anonymizes the information of the patient such as name, date of birth etc.
    args:
        file: Name of the file
        in_folder: Location of the mercure file input directory
        out_folder: Location of the mercure file after processing
        series_uid: UID for the dcm file series
        settings: additional settings for the processing of the image
    """
    dcm_file_in = Path(in_folder) / file
    out_filename = series_uid + "#" + file.split("#", 1)[1]
    dcm_file_out = Path(out_folder) / out_filename

    # Load the dicom file
    ds = pydicom.dcmread(dcm_file_in)
    ds.SeriesInstanceUID = series_uid
    # Set a UID for this slice (every slice needs to have a unique instance UID)
    ds.SOPInstanceUID = generate_uid()
    # Add an offset to the series number (to avoid collosion in PACS if sending back into the same study)
    ds.SeriesNumber = ds.SeriesNumber + settings["series_offset"]
    # Update the series description to indicate which the modified DICOM series is
    ds.SeriesDescription = "Anonymized(" + ds.SeriesDescription + ")"
    ds.PatientName = "Anonymized"
    ds.save_as(dcm_file_out)


def main(args=sys.argv[1:]):
    print("I am the anonymizer module")
    if len(sys.argv) < 3:
        print("Error: missing arguments!")
        print("Usage: anonymizer [input-folder] [output-folder]")
        sys.exit(1)
    in_folder = sys.argv[1]
    out_folder = sys.argv[2]
    if not Path(in_folder).exists() or not Path(out_folder).exists():
        print("IN/OUT paths do not exist")
        sys.exit(1)

    # Load the task.json file, which contains the settings for the processing module
    # try:
    #    with open(Path(in_folder) / "task.json", "r") as json_file:
    #        task = json.load(json_file)
    # except Exception:
    #    print("Error: Task file task.json not found")
    #    sys.exit(1)
    settings = {"series_offset": 1000}

    series = {}
    for entry in os.scandir(in_folder):
        if entry.name.endswith(".dcm") and not entry.is_dir():
            # Get the Series UID from the file name
            seriesString = entry.name.split("#", 1)[0]
            # If this is the first image of the series, create new file list for the series
            if seriesString not in series.keys():
                series[seriesString] = []
            # Add the current file to the file list
            series[seriesString].append(entry.name)

    # Now loop over all series found
    for item in series:
        # Create a new series UID, which will be used for the modified DICOM series (to avoid
        # collision with the original series)
        series_uid = generate_uid()
        # Now loop over all slices of the current series and call the processing function
        for image_filename in series[item]:
            anonymize_image(image_filename, in_folder, out_folder, series_uid, settings)


if __name__ == "__main__":
    main()
