#!/usr/bin/env python3
"""
Script para probar el botón de administración en acción
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from core.main_window import MainWindow

def main():
    """Función principal para probar la aplicación"""
    app = QApplication(sys.argv)
    
    print("🚀 Iniciando aplicación VisitaSegura...")
    
    # Crear ventana principal
    window = MainWindow()
    window.show()
    
    print("✅ Ventana principal abierta")
    print("🔍 Haz clic en el botón '🔐 Administración' para probar la ventana de login")
    print("📝 Los mensajes de debug aparecerán en la consola cuando hagas clic")
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
