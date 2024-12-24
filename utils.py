import re 
import tkinter as tk
from tkinter import filedialog

class GENERAL_UTILS:
    def is_api_null(self, api_key: str) -> bool:
        return api_key is None or api_key.strip() == ""
    
    def extract_workshop_id(self, url: str):
        pattern = r"[?&]id=(\d+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    
    def get_ids_from_collection(self, collection_details):
        ids = []
        if collection_details:
            for item in collection_details[0].get('children', []):
                ids.append(item['publishedfileid'])

        return ids
    
    def extract_url_mod_from_dict(self, data) -> str:
        try:
            file_details = data.get('response', {}).get('publishedfiledetails', [])
            if file_details and isinstance(file_details, list):
                file_url = file_details[0].get('file_url', '')
                if file_url:
                    return file_url
                else:
                    raise ValueError("File URL not found in the provided data.")
            else:
                raise ValueError("Invalid or empty file details in the data.")
        except Exception as e:
            print(f"An error occurred while extracting the file URL: {e}")
            return None
        
    def check_url(self,text:str) -> str:
        url = text
        pattern = r'^https://steamcommunity\.com/(sharedfiles|workshop)/filedetails/\?id=\d+$'

        if not url:
            return "The input field is empty."
        elif not re.match(pattern, url):
            return "The URL is invalid or does not match the required pattern."
        else:
            return None
        
    def select_folder(self) -> str:
        root = tk.Tk()
        root.withdraw() 
        folder_path = filedialog.askdirectory(title="Select Folder")
        return folder_path