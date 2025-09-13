from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

class VisitasView(QWidget):
    """Vista para el registro de visitas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header con título y logo
        header_layout = QHBoxLayout()
        
        # Título
        title_layout = QVBoxLayout()
        title = QLabel("📋 Registro de Visitas")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        
        subtitle = QLabel("Sistema de registro y gestión de visitas")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignLeft)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        
        # Logo Duoc
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🏢 Duoc UC")
            logo_font = QFont("Arial", 12, QFont.Bold)
            logo_label.setFont(logo_font)
        
        logo_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(logo_label)
        
        main_layout.addLayout(header_layout)
        
        # Contenido principal
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.StyledPanel)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)
        
        # Mensaje de bienvenida
        welcome_label = QLabel("""
        <div style="text-align: center; padding: 40px;">
        <h2 style="color: #007bff;">🚧 Módulo en Desarrollo</h2>
        <p style="font-size: 16px; color: #6c757d; margin: 20px 0;">
        El sistema de registro de visitas está siendo desarrollado.<br>
        Próximamente podrás registrar y gestionar todas las visitas al establecimiento.
        </p>
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #1976d2; margin: 0 0 10px 0;">🎯 Funcionalidades Planificadas:</h3>
        <ul style="text-align: left; color: #424242;">
        <li>📝 Registro rápido de visitas</li>
        <li>🔍 Búsqueda y filtrado de visitas</li>
        <li>📊 Estadísticas de visitas</li>
        <li>📅 Historial de visitas</li>
        <li>🔔 Notificaciones automáticas</li>
        </ul>
        </div>
        </div>
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(welcome_label)
        
        main_layout.addWidget(content_frame)
        main_layout.addStretch()
        
        # Botón de regreso
        back_button = QPushButton("⬅️ Volver al Menú Principal")
        back_button.setFixedSize(200, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
