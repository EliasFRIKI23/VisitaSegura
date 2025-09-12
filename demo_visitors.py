#!/usr/bin/env python3
"""
Demo del sistema de gestión de visitantes para VisitaSegura
Este archivo demuestra las funcionalidades del CRUD de visitantes con interfaz intuitiva
"""

import sys
import os

# Agregar el directorio core al path para las importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.visitor_list import VisitorListWidget

class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Demo - Sistema de Gestión de Visitantes (Interfaz Intuitiva)")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Banner informativo
        banner = QLabel("""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
        <h2 style="color: #1976d2; margin: 0;">🎉 Sistema de Gestión de Visitantes</h2>
        <p style="color: #424242; margin: 5px 0 0 0; font-size: 14px;">
        <strong>✨ Interfaz Intuitiva con Iconos, Tooltips y Ayuda Integrada</strong><br>
        📖 Haz clic en el botón "?" para ver la guía completa de uso
        </p>
        </div>
        """)
        banner.setAlignment(Qt.AlignCenter)
        banner.setFont(QFont("Arial", 12))
        layout.addWidget(banner)
        
        # Agregar el widget de gestión de visitantes
        self.visitor_widget = VisitorListWidget()
        layout.addWidget(self.visitor_widget)
        
        # Footer informativo
        footer = QLabel("""
        <div style="background-color: #f5f5f5; padding: 10px; border-radius: 6px; text-align: center;">
        <small style="color: #666;">
        💡 <strong>Consejo:</strong> Doble clic en cualquier fila para cambiar el estado del visitante | 
        Clic derecho para ver opciones adicionales | 
        Usa los filtros para encontrar visitantes específicos
        </small>
        </div>
        """)
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Arial", 9))
        layout.addWidget(footer)

def main():
    app = QApplication(sys.argv)
    
    # Configurar el estilo de la aplicación
    app.setStyle('Fusion')
    
    # Configurar fuente por defecto
    font = QFont("Arial", 9)
    app.setFont(font)
    
    window = DemoWindow()
    window.show()
    
    # Mostrar mensaje de bienvenida
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.information(
        window, 
        "🎉 ¡Bienvenido al Sistema!", 
        """
        <h3>🚀 Sistema de Gestión de Visitantes</h3>
        <p>¡Bienvenido al sistema con interfaz intuitiva!</p>
        
        <p><strong>🎯 Funcionalidades principales:</strong></p>
        <ul>
            <li>➕ Registro manual de visitantes</li>
            <li>🔄 Cambio de estado con doble clic</li>
            <li>🔍 Filtros por estado y sector</li>
            <li>📊 Estadísticas en tiempo real</li>
            <li>📖 Ayuda integrada con botón "?"</li>
        </ul>
        
        <p><strong>💡 Consejo:</strong> Haz clic en el botón "?" para ver la guía completa de uso.</p>
        """
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
