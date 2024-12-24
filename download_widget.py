from PyQt6.QtWidgets import QWidget, QLabel, QProgressBar, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

class DOWNLOAD_WIDGET(QWidget):
    cancel_requested = pyqtSignal(str) 

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.label_filename = QLabel(self.filename)
        layout.addWidget(self.label_filename)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.label_size = QLabel("0 / 0")
        layout.addWidget(self.label_size)

        self.button_cancel = QPushButton("X")
        self.button_cancel.clicked.connect(self.handle_cancel)
        layout.addWidget(self.button_cancel)

        self.setLayout(layout)

    def handle_cancel(self):
        self.cancel_requested.emit(self.filename)

    def update_progress(self, progress, downloaded, total):
        self.progress_bar.setValue(progress)
        self.label_size.setText(f"{downloaded} / {total}")
