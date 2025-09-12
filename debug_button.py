#!/usr/bin/env python3
"""
Script simple para probar el botón de administración
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Prueba las importaciones"""
    try:
        from core.main_window import MainWindow
        print("✅ Importación de MainWindow exitosa")
        
        from core.login_window import LoginWindow
        print("✅ Importación de LoginWindow exitosa")
        
        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_button_creation():
    """Prueba la creación del botón"""
    try:
        from PySide6.QtWidgets import QApplication
        from core.main_window import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        
        # Verificar que el botón existe
        if hasattr(window, 'btn_open_login'):
            print("✅ Botón btn_open_login existe")
            print(f"✅ Texto del botón: {window.btn_open_login.text()}")
            return True
        else:
            print("❌ Botón btn_open_login no existe")
            return False
            
    except Exception as e:
        print(f"❌ Error al crear ventana: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Probando funcionalidad del botón de administración...")
    
    if test_imports():
        if test_button_creation():
            print("✅ Todas las pruebas pasaron correctamente")
        else:
            print("❌ Error en la creación del botón")
    else:
        print("❌ Error en las importaciones")
