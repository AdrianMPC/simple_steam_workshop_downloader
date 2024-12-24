import sys
import workshop_ui
from PyQt6.QtWidgets import QApplication


def main():
    try:
        """
        test = 'https://steamcommunity.com/workshop/filedetails/?id=2066337798'
        """

        app = QApplication(sys.argv)
        ui_handler = workshop_ui.MAIN_WINDOW()
        ui_handler.show()
        sys.exit(app.exec())

    except Exception as e:
        print(f"An error occurred in main: {e}")


if __name__ == "__main__":
    main()
