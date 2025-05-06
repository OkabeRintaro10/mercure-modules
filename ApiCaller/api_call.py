import requests

files = {
    "file": open(
        "/mnt/f/mercure/addons/vagrant/systemd/sampledata/case_1/IM-0001-0001-0001-199.dcm",
        "rb",
    )
}
response = requests.post("10.0.2.2:8001/upload")
print(response.json())
