from PyQt6.QtCore import QThread, pyqtSignal
import os
import requests

def human_readable_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:3.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:3.1f} PB"

class DOWNLOAD_WORKER(QThread):
    progress_update = pyqtSignal(int)  
    progress_size = pyqtSignal(int, int) 
    finished = pyqtSignal(str) 
    error = pyqtSignal(str)

    def __init__(self, file_url, save_path, file_name):
        super().__init__()
        self.file_url = file_url
        self.save_path = save_path
        self.file_name = file_name
        self.is_canceled = False 

    def run(self):
        try:
            if not self.file_url:
                raise ValueError("Invalid file URL.")

            if not self.file_name:
                raise ValueError("Invalid file name.")

            if "myl4d2addons/" in self.file_name:
                self.file_name = self.file_name.replace("myl4d2addons/", "")

            file_path = os.path.join(self.save_path, self.file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            response = requests.get(self.file_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            downloaded_size = 0
            self.progress_size.emit(downloaded_size, total_size)

            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.is_canceled:
                        self.error.emit("Download canceled by user.")
                        return

                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        percentage = int((downloaded_size / total_size) * 100)
                        self.progress_update.emit(percentage)
                        self.progress_size.emit(downloaded_size, total_size)

            self.finished.emit(f"File downloaded successfully: {file_path}")

        except Exception as e:
            self.error.emit(f"An error occurred during download: {str(e)}")

    def cancel(self):
        self.is_canceled = True 