import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QScrollArea, QTableView, QVBoxLayout, QWidget, 
    QPushButton, QLineEdit, QLabel, QMessageBox, QRadioButton, 
    QHeaderView
)
from PyQt6 import uic
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import Qt, QSize
import api_ui_connector
import utils
import download_thread
import download_widget


class MAIN_WINDOW(QMainWindow):
    img_size: int = 128

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "resources_ui", "main_workshop.ui"), self)
        self.setWindowTitle("Workshop Downloader")

        self.label = self.findChild(QLabel, "label")
        self.LE_workshop_link = self.findChild(QLineEdit, "LE_workshop_link")
        self.LE_location_editor = self.findChild(QLineEdit, "LE_location_editor")
        self.B_explore = self.findChild(QPushButton, "B_explore")
        self.mod_table = self.findChild(QTableView, "mod_table")
        self.B_search_mod = self.findChild(QPushButton, "B_search_mod")
        self.R_images = self.findChild(QRadioButton, "R_images")

        self.area_download = self.findChild(QScrollArea, "area_download")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.area_download.setWidget(self.scroll_widget)
        self.area_download.setWidgetResizable(True)

        self.B_explore.clicked.connect(self.explore_button_clicked)
        self.B_search_mod.clicked.connect(self.search_button_clicked)

        self.setup_table()

        self.api_ui_connector = api_ui_connector.API_UI_CONNECTOR()
        self.utils_obj = utils.GENERAL_UTILS()
        self.R_images.setChecked(True)

        self.active_downloads = {}

    def setup_table(self):
        model = QStandardItemModel(0, 5)
        headers = ["Mod Image", "Title", "Game name", "Size", "Download"]
        model.setHorizontalHeaderLabels(headers)
        self.mod_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mod_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.mod_table.setIconSize(QSize(self.img_size, self.img_size))
        self.mod_table.setModel(model)

    def clear_table(self):
        model = self.mod_table.model()
        model.removeRows(0, model.rowCount())

    def explore_button_clicked(self):
        folder_path: str = self.utils_obj.select_folder()
        
        while folder_path is None or folder_path == "":
            response = QMessageBox.warning(self, "File validation", "Please select a folder!", 
                                           QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel)
            if response == QMessageBox.StandardButton.Cancel:
                return
            folder_path: str = self.utils_obj.select_folder()

        self.change_text_location(folder_path)

    def change_text_location(self, text: str):
        self.LE_location_editor.setText(text)

    def search_button_clicked(self):
        text: str = self.LE_workshop_link.text()

        msg = self.utils_obj.check_url(text)

        if msg is not None:
            QMessageBox.warning(self, "Validation Error", msg)
            return
        else:
            list_data: list = self.api_ui_connector.get_collection_details(text)
            self.update_table(list_data)

    def update_table(self, list_data: list):
        self.clear_table()
        for wh_id in list_data:
            data: str = self.api_ui_connector.get_workshop_details(wh_id)
            model = self.mod_table.model()

            if not data or not isinstance(data, dict):
                continue

            row = []
            if self.R_images.isChecked():
                image_item = QStandardItem()
                pixmap = self.api_ui_connector.load_image(data.get('preview_url'))
                if pixmap:
                    scaled_pixmap = pixmap.scaled(
                        self.img_size, self.img_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    icon = QIcon(scaled_pixmap)
                    image_item.setIcon(icon)
                image_item.setEditable(False)
            else:
                image_item = QStandardItem('*')
                image_item.setEditable(False)
            row.append(image_item)

            title_item = QStandardItem(data.get('title', 'Unknown Title'))
            title_item.setEditable(False)
            row.append(title_item)

            game_name_item = QStandardItem(data.get('app_name', 'Unknown Game'))
            game_name_item.setEditable(False)
            row.append(game_name_item)

            size_in_mb = f"{int(data.get('file_size', 0)) / (1024 ** 2):.2f} MB"
            size_item = QStandardItem(size_in_mb)
            size_item.setEditable(False)
            row.append(size_item)

            placeholder_item = QStandardItem()
            placeholder_item.setEditable(False)
            row.append(placeholder_item)

            model.appendRow(row)

            download_button = QPushButton("Download")
            download_button.setEnabled(data.get('file_url') is not None or data.get('file_url') != "")
            download_button.clicked.connect(
                lambda _, url=data.get('file_url'), filename=data.get('filename', 'generic_file.vpk'), button=download_button: 
                self.handle_download(url, filename, button)
            )
            self.mod_table.setIndexWidget(
                model.index(model.rowCount() - 1, 4), download_button
            )

    def handle_download(self, url: str, filename: str, button: QPushButton):
        if url:
            button.setEnabled(False)
            button.setText("Downloading...")

            download_widgets = download_widget.DOWNLOAD_WIDGET(filename)
            self.scroll_layout.addWidget(download_widgets)
            download_widgets.show()

            download_widgets.cancel_requested.connect(
                lambda fname: self.cancel_download(fname, button) 
            )

            self.download_worker = download_thread.DOWNLOAD_WORKER(
                url, self.LE_location_editor.text(), filename
            )
            self.download_worker.progress_size.connect(
                lambda downloaded, total_size: download_widgets.update_progress(
                    int((downloaded / total_size) * 100),
                    download_thread.human_readable_size(downloaded),
                    download_thread.human_readable_size(total_size)
                )
            )
            self.download_worker.finished.connect(
                lambda message: self.download_completed(filename, download_widgets, button)  
            )
            self.download_worker.error.connect(
                lambda error_message: self.download_error(error_message, filename, download_widgets, button) 
            )

            self.active_downloads[filename] = self.download_worker
            self.download_worker.start()
        else:
            QMessageBox.critical(self, "Download Error", "No valid file URL provided.")

    def cancel_download(self, filename, button: QPushButton):
        if filename in self.active_downloads:
            self.active_downloads[filename].cancel()
            del self.active_downloads[filename]
            button.setEnabled(True)
            button.setText("Download")

    def download_completed(self, filename, download_widgets, button: QPushButton):
        QMessageBox.information(self, "Download Complete", f"{filename} completed.")
        self.scroll_layout.removeWidget(download_widgets)
        download_widgets.deleteLater()
        button.setEnabled(True)
        button.setText("Download")

    def download_error(self, error_message, filename, download_widgets, button: QPushButton):
        QMessageBox.critical(self, "Download Error", f"{filename} error: {error_message}")
        self.scroll_layout.removeWidget(download_widgets)
        download_widgets.deleteLater()
        button.setEnabled(True)
        button.setText("Download")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MAIN_WINDOW()
    window.show()
    sys.exit(app.exec())
