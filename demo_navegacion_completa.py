#!/usr/bin/env python3
"""
Demo de navegación completa del sistema VisitaSegura
Muestra todas las vistas con botones de regreso funcionando
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
    
    # Mostrar mensaje de bienvenida con información sobre navegación
    QMessageBox.information(
        window, 
        "🎉 ¡Navegación Completa Disponible!", 
        """
        <h3>🚀 Sistema VisitaSegura - Navegación Completa</h3>
        <p>¡Bienvenido al sistema con navegación completa entre todas las vistas!</p>
        
        <p><strong>🎯 Navegación disponible:</strong></p>
        <ul>
            <li>🏠 <strong>Menú Principal</strong> - Vista inicial con botones de navegación</li>
            <li>📋 <strong>Registro de Visitas</strong> - Con botón "⬅️ Volver al Menú Principal"</li>
            <li>👥 <strong>Gestión de Visitantes</strong> - CRUD completo + botón de regreso</li>
            <li>🏢 <strong>Gestión de Zonas</strong> - Con botón "⬅️ Volver al Menú Principal"</li>
            <li>📊 <strong>Reportes y Estadísticas</strong> - Con botón "⬅️ Volver al Menú Principal"</li>
        </ul>
        
        <p><strong>🔄 Cómo navegar:</strong></p>
        <ul>
            <li><strong>Desde el menú:</strong> Haz clic en cualquier botón para ir a esa sección</li>
            <li><strong>Desde cualquier vista:</strong> Usa "⬅️ Volver al Menú Principal"</li>
            <li><strong>Desde la barra:</strong> Usa "🏠 Inicio" (aparece automáticamente)</li>
            <li><strong>Tema:</strong> Botón "🌙 Modo oscuro" en la barra superior</li>
        </ul>
        
        <p><strong>✨ Características de navegación:</strong></p>
        <ul>
            <li>🔄 <strong>Transiciones suaves</strong> entre vistas</li>
            <li>🏠 <strong>Botón inicio</strong> aparece automáticamente</li>
            <li>📱 <strong>Títulos dinámicos</strong> según la sección</li>
            <li>💾 <strong>Estado persistente</strong> de configuración</li>
            <li>🎨 <strong>Tema unificado</strong> en todas las vistas</li>
        </ul>
        
        <p><strong>🎮 Prueba la navegación:</strong></p>
        <ol>
            <li>Haz clic en "👥 Visitantes Actuales" para ver el CRUD completo</li>
            <li>Usa "⬅️ Volver al Menú Principal" para regresar</li>
            <li>Prueba las otras secciones con sus botones de regreso</li>
            <li>Observa cómo aparece el botón "🏠 Inicio" en la barra</li>
        </ol>
        """
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
