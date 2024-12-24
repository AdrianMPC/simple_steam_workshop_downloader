import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import QProcess

class TERMINAL_WIDGET(QWidget):
    def __init__(self):
            super().__init__()

            self.terminal = QTextEdit(self)
            self.terminal.setReadOnly(True)
            layout = QVBoxLayout(self)
            layout.addWidget(self.terminal)
            
            layout.setContentsMargins(0, 0, 0, 0)  
            layout.setSpacing(0)  

            self.old_stdout = sys.stdout 
            sys.stdout = self 

    def write(self, message: str):
        self.terminal.append(message)  
        self.scroll_to_bottom() 

    def flush(self):
        QApplication.processEvents()

    def reset_stdout(self):
        sys.stdout = self.old_stdout 

    def append_message(self, message: str):
        self.terminal.append(message)  
        self.scroll_to_bottom() 
    
    def scroll_to_bottom(self):
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum()) 

    def clear(self):
        self.terminal.clear()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TERMINAL_WIDGET()
    window.show()
    sys.exit(app.exec())