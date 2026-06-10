"""
Downloads SOLUS100 soil property rasters from the public Google Cloud Storage
bucket. Filters the bucket listing by file-name pattern (e.g. 'dboven_') and
saves matching GeoTIFFs to a local directory.
"""

import os
import requests
from bs4 import BeautifulSoup

url = 'https://storage.googleapis.com/solus100pub'

save_dir = 'path/to/solus-data'
os.makedirs(save_dir, exist_ok=True)

response = requests.get(url)
soup = BeautifulSoup(response.content, "xml")

patterns = ["dboven_"]

for pattern in patterns:
    for file in soup.find_all('Contents'):
        file_name = file.find("Key").text
        print(f"Found file: {file_name}")
        if any(file_name.startswith(pattern) and file_name.endswith("_p.tif") for pattern in patterns):
            file_url = f"{url}/{file_name}"
            # Download and save the file
            file_response = requests.get(file_url)
            with open(os.path.join(save_dir, file_name), "wb") as file:
                file.write(file_response.content)
            print(f"Downloaded {file_name}")
