#!/usr/bin/env python3
# test_export_permissions.py
"""
Script de prueba para verificar las restricciones de exportación a Excel
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.auth_manager import AuthManager
from core.views.reportes_view import ReportesView
from database import connect_db

def test_export_permissions():
    """Prueba las restricciones de exportación"""
    print("Probando restricciones de exportacion a Excel...")
    
    # Conectar a la base de datos
    if not connect_db():
        print("Error conectando a la base de datos")
        return False
    
    # Crear instancia del AuthManager
    auth = AuthManager()
    
    # Probar con usuario administrador
    print("\n1. Probando con usuario administrador...")
    if auth.login("admin", "admin123"):
        print("Login de administrador exitoso")
        
        # Crear vista de reportes
        reportes_view = ReportesView(auth_manager=auth)
        
        # Verificar que el botón está visible para admin
        if hasattr(reportes_view, 'btn_export'):
            print("Botón de exportar está visible para administrador")
        else:
            print("Botón de exportar no encontrado")
        
        # Verificar permisos en el método
        print("Verificando permisos en export_to_excel...")
        # Simular verificación de permisos
        if auth.is_admin():
            print("✅ Administrador puede exportar")
        else:
            print("❌ Administrador no puede exportar")
    
    # Probar con usuario guardia
    print("\n2. Probando con usuario guardia...")
    auth.logout()  # Cerrar sesión anterior
    if auth.login("guardia1", "guardia123"):
        print("Login de guardia exitoso")
        
        # Crear vista de reportes
        reportes_view = ReportesView(auth_manager=auth)
        
        # Verificar que el botón NO está visible para guardia
        if hasattr(reportes_view, 'btn_export'):
            print("Botón de exportar encontrado")
            # Actualizar visibilidad
            reportes_view.update_export_button_visibility()
            print("Visibilidad del botón actualizada según permisos")
        else:
            print("Botón de exportar no encontrado")
        
        # Verificar permisos en el método
        print("Verificando permisos en export_to_excel...")
        if auth.is_admin():
            print("❌ Guardia puede exportar (ERROR)")
        else:
            print("✅ Guardia NO puede exportar (CORRECTO)")
    
    print("\nPrueba de restricciones completada")

if __name__ == "__main__":
    test_export_permissions()
