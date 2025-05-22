import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Error crítico", f"Ocurrió un error inesperado:\n{str(e)}")