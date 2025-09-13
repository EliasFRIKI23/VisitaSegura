from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

class ZonasView(QWidget):
    """Vista para la gestión de zonas"""
    
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
        title = QLabel("🏢 Gestión de Zonas")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        
        subtitle = QLabel("Administración de zonas y sectores del establecimiento")
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
        
        # Zonas disponibles
        zones_title = QLabel("📍 Zonas Disponibles")
        zones_title.setFont(QFont("Arial", 16, QFont.Bold))
        zones_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(zones_title)
        
        # Grid de zonas
        zones_grid = QGridLayout()
        zones_grid.setSpacing(15)
        
        # Zona Financiamiento
        fin_zone = self.create_zone_card("💰 Financiamiento", "#28a745", "Gestión de servicios financieros y becas")
        zones_grid.addWidget(fin_zone, 0, 0)
        
        # Zona CITT
        citt_zone = self.create_zone_card("🎓 CITT", "#007bff", "Centro de Innovación y Transferencia Tecnológica")
        zones_grid.addWidget(citt_zone, 0, 1)
        
        # Zona Auditorio
        aud_zone = self.create_zone_card("🎭 Auditorio", "#ffc107", "Espacios para eventos y presentaciones")
        zones_grid.addWidget(aud_zone, 1, 0)
        
        # Zona Administración
        admin_zone = self.create_zone_card("👥 Administración", "#dc3545", "Oficinas administrativas y atención al público")
        zones_grid.addWidget(admin_zone, 1, 1)
        
        content_layout.addLayout(zones_grid)
        
        # Mensaje de desarrollo
        dev_label = QLabel("""
        <div style="text-align: center; padding: 20px; background-color: #fff3cd; border-radius: 8px;">
        <h3 style="color: #856404; margin: 0 0 10px 0;">🚧 Módulo en Desarrollo</h3>
        <p style="color: #856404; margin: 0;">
        La gestión avanzada de zonas estará disponible próximamente.
        </p>
        </div>
        """)
        content_layout.addWidget(dev_label)
        
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
        back_button.clicked.connect(self.go_to_main)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
    
    def go_to_main(self):
        """Regresa al menú principal"""
        if hasattr(self.parent(), 'navigation_manager'):
            self.parent().navigation_manager.navigate_to("main")
        elif hasattr(self.parent(), 'go_to_main'):
            self.parent().go_to_main()
    
    def create_zone_card(self, title, color, description):
        """Crea una tarjeta para una zona"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 12px;
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Título de la zona
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(desc_label)
        
        # Botón de gestión
        manage_btn = QPushButton("🔧 Gestionar")
        manage_btn.setFixedHeight(35)
        manage_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        layout.addWidget(manage_btn)
        
        return card
    
    def lighten_color(self, color, factor=0.1):
        """Aclara un color hexadecimal"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, color, factor=0.2):
        """Oscurece un color hexadecimal"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
