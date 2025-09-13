#!/usr/bin/env python3
"""
Demo completo del sistema VisitaSegura integrado
Muestra el sistema completo con login, navegación y todas las vistas
"""

import sys
import os

# Agregar el directorio core al path para las importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Configurar el estilo de la aplicación
    app.setStyle('Fusion')
    
    # Configurar fuente por defecto
    font = QFont("Arial", 9)
    app.setFont(font)
    
    # Crear la ventana principal
    window = MainWindow()
    window.show()
    
    # Mostrar mensaje de bienvenida
    QMessageBox.information(
        window, 
        "🎉 ¡Bienvenido a VisitaSegura!", 
        """
        <h3>🚀 Sistema Completo de Gestión de Visitantes</h3>
        <p>¡Bienvenido al sistema integrado con todas las funcionalidades!</p>
        
        <p><strong>🎯 Funcionalidades disponibles:</strong></p>
        <ul>
            <li>📋 <strong>Registro de Visitas</strong> - Sistema en desarrollo</li>
            <li>👥 <strong>Gestión de Visitantes</strong> - CRUD completo con interfaz intuitiva</li>
            <li>🏢 <strong>Gestión de Zonas</strong> - Administración de sectores</li>
            <li>📊 <strong>Reportes y Estadísticas</strong> - Análisis del sistema</li>
            <li>🔐 <strong>Acceso Administrativo</strong> - Login seguro</li>
        </ul>
        
        <p><strong>💡 Características del sistema:</strong></p>
        <ul>
            <li>🎨 <strong>Interfaz intuitiva</strong> con iconos y tooltips</li>
            <li>🌙 <strong>Tema claro/oscuro</strong> configurable</li>
            <li>📖 <strong>Sistema de ayuda</strong> integrado</li>
            <li>🔄 <strong>Navegación fluida</strong> entre secciones</li>
            <li>💾 <strong>Persistencia de datos</strong> automática</li>
        </ul>
        
        <p><strong>🎮 Cómo usar:</strong></p>
        <ul>
            <li>Haz clic en cualquier botón para navegar a esa sección</li>
            <li>Usa el botón "🏠 Inicio" para regresar al menú principal</li>
            <li>El botón "🌙 Modo oscuro" cambia el tema de la aplicación</li>
            <li>El botón "🔐 Administración" abre el sistema de login</li>
        </ul>
        """
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
