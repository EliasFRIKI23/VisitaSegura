# main.py
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from core.main_window import MainWindow
from database import connect_db, check_connection

if __name__ == "__main__":
    # Conectar a la base de datos antes de iniciar la app
    if connect_db():
        check_connection()
    else:
        # Si falla, mostramos un aviso y cerramos la app
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error de conexión")
        msg.setText("❌ No se pudo conectar con la base de datos MongoDB.")
        msg.exec()
        sys.exit(1)

    # Iniciar la aplicación Qt
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
