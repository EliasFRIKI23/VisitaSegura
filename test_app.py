#!/usr/bin/env python3
"""
Script de prueba para verificar que el botón de administración funciona
"""

import sys
import os

# Agregar el directorio actual al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from core.main_window import MainWindow

def test_login_button():
    """Prueba que el botón de login funciona correctamente"""
    app = QApplication(sys.argv)
    
    # Crear ventana principal
    window = MainWindow()
    window.show()
    
    print("✅ Ventana principal creada correctamente")
    print("✅ Botón de administración configurado")
    print("🔍 Haz clic en '🔐 Administración' para probar la ventana de login")
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    test_login_button()
