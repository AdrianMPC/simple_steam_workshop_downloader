from io import BytesIO
import os
from tqdm import tqdm
import requests
import api_handler
import utils
from PyQt6.QtGui import QPixmap

from pathlib import Path

class API_UI_CONNECTOR:
    def __init__(self):
        try:
            self.api_obj = api_handler.API_HANDLER()
            self.utils_obj = utils.GENERAL_UTILS()
            self.save_path = os.path.join(Path.home(), "Downloads")
            self.workshop_item = None
        except Exception as e:
            print(f"Something went wrong: {e}")

    def get_collection_details(self, item_url: str) -> list:
        try:
            collection_id = self.utils_obj.extract_workshop_id(item_url)
            if not collection_id:
                raise ValueError("Invalid URL or collection ID not found.")

            data = self.api_obj.fetch_collection_details(collection_id)
            return self.process_collection_details(data)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def process_collection_details(self, data: dict) -> list:
        collection_details = data.get('response', {}).get('collectiondetails', [])

        if collection_details:
            children = collection_details[0].get('children', [])
            if children:
                return self.utils_obj.get_ids_from_collection(collection_details)
            return [collection_details[0]['publishedfileid']]
        else:
            raise ValueError("No collection details found.")

    def get_workshop_details(self, item_id: str) -> dict:
        try:
            data = self.api_obj.fetch_workshop_details(item_id)
            return self.process_workshop_details(data)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def process_workshop_details(self, data: dict) -> dict:
        item_details = data.get('response', {}).get('publishedfiledetails', [])
        if item_details:
            self.workshop_item = item_details[0]
            return self.workshop_item
        else:
            raise ValueError("Workshop item not found.")

    def download_workshop_file(self, file_url: str):
        try:
            if not file_url:
                raise ValueError("Invalid file URL.")

            if not self.workshop_item:
                raise ValueError("Workshop item details not loaded. Please call `get_workshop_details` first.")

            filename = self.workshop_item.get('filename', 'downloaded_file') 

            if "myl4d2addons/" in filename:
                filename = filename.replace("myl4d2addons/", "")

            file_path = os.path.join(self.save_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            print(f"Downloading from URL: {file_url}")
            response = requests.get(file_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(file_path, "wb") as file, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=filename
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))

            print(f"File downloaded successfully: {file_path}")
        except Exception as e:
            print(f"An error occurred during download: {e}")

    def load_image(self, url: str) -> QPixmap:
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data.read())
            return pixmap
        except requests.RequestException:
            return None