import json
import requests
import os

base_url = "http://localhost:8042/"
temp_dir = "/tmp"


def get_instances() -> json:
    print(base_url + "instances")
    response = requests.get(base_url + "instances")
    return response.json()


def download_instance():
    for instance in get_instances():
        file_path = os.path.join(temp_dir, f"{instance}.dcm")
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(
                    requests.get(base_url + "instances/" + instance + "/file").content
                )
            print(f"Downloaded instance {instance} to {file_path}")


if __name__ == "__main__":
    instances = get_instances()
    for instance in instances:
        instance_content = download_instance(instance)
