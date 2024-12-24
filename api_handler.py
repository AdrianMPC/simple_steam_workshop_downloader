import requests
import os
from dotenv import load_dotenv 
from PyQt6.QtWidgets import QMessageBox
import sys

import utils

class API_HANDLER:
    api_key: str = None
    api_url: str = 'https://api.steampowered.com/IPublishedFileService/GetDetails/v1/'
    api_collection_url = 'https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/'

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")

        if utils.GENERAL_UTILS().is_api_null(self.api_key):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("STEAM API key Error")
            msg_box.setText("Failed obtaining the API KEY")
            msg_box.setInformativeText("Please put it in a .env file as API_KEY")
            msg_box.exec()
            sys.exit(1)

    def fetch_collection_details(self, collection_id: str):
        params = {
            'key': self.api_key,
            'collectioncount': 1,
            'publishedfileids[0]': collection_id
        }
        response = requests.post(self.api_collection_url, data=params)
        response.raise_for_status()
        return response.json()

    def fetch_workshop_details(self, item_id: str):
        params = {
            'key': self.api_key,
            'publishedfileids[0]': item_id
        }
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        return response.json()