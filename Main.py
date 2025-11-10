# main.py
import os
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from core.main_window import MainWindow
from database import connect_db, check_connection

if __name__ == "__main__":
    # Inicializar la aplicación Qt antes de cualquier diálogo
    app = QApplication(sys.argv)

    # Intentar conexión inicial
    if connect_db():
        check_connection()
    else:
        respuesta = QMessageBox.question(
            None,
            "Conexión a la base de datos",
            "⚠️ No se encontró la base de datos.\n\n¿Desea abrir igualmente la aplicación en modo offline?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if respuesta == QMessageBox.No:
            QMessageBox.information(
                None,
                "Aplicación cerrada",
                "La aplicación se cerrará porque no se estableció conexión con la base de datos.",
            )
            sys.exit(1)

        # Activar modo offline para el resto de la aplicación
        os.environ["VISITASEGURA_OFFLINE"] = "1"
        QMessageBox.information(
            None,
            "Modo offline",
            "La aplicación se iniciará en modo offline.\nAlgunas funciones pueden estar limitadas.",
        )

    # Iniciar la ventana principal
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
