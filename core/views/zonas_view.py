from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QMessageBox, QScrollArea
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QGuiApplication
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from visitor_model import VisitorManager

# Colores institucionales de DuocUC
DUOC_PRIMARY = "#003A70"      # Azul institucional
DUOC_SECONDARY = "#FFB800"    # Amarillo institucional
DUOC_ACCENT = "#307FE2"       # blanco institucional
DUOC_NEUTRAL = "#6C757D"      # Gris neutro
DUOC_LIGHT = "#F8F9FA"        # Gris claro
DUOC_DARK = "#212529"         # Gris oscuro
DUOC_SUCCESS = "#28a745"      # Verde para pocos visitantes
DUOC_WARNING = "#ffc107"      # Amarillo para advertencia

class ZonasView(QWidget):
    """Vista para la gestión de zonas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.visitor_manager = VisitorManager()
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Crear área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget principal que contendrá todo el contenido
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Configuración responsiva de márgenes
        available = QGuiApplication.primaryScreen().availableGeometry()
        if available.width() >= 1920:
            margin = 50
            spacing = 40
        elif available.width() >= 1366:
            margin = 40
            spacing = 35
        else:
            margin = 30
            spacing = 30
            
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(spacing)
        
        # Header con título y logo
        header_layout = QHBoxLayout()
        
        # Título
        title_layout = QVBoxLayout()
        title = QLabel("🏢 Gestión de Zonas")
        
        # Configuración responsiva de fuentes
        if available.width() >= 1920:
            title_font_size = 24
            subtitle_font_size = 16
        elif available.width() >= 1366:
            title_font_size = 20
            subtitle_font_size = 14
        else:
            title_font_size = 18
            subtitle_font_size = 12
            
        title_font = QFont("Segoe UI", title_font_size, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(f"color: {DUOC_PRIMARY}; margin-bottom: 5px;")
        
        subtitle = QLabel("Administración de zonas y sectores del establecimiento")
        subtitle_font = QFont("Segoe UI", subtitle_font_size)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignLeft)
        subtitle.setStyleSheet(f"color: {DUOC_NEUTRAL};")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        
        # Logo Duoc
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            # Escalar logo responsivamente
            if available.width() >= 1920:
                logo_size = (160, 80)
            elif available.width() >= 1366:
                logo_size = (140, 70)
            else:
                logo_size = (120, 60)
            scaled_pixmap = logo_pixmap.scaled(logo_size[0], logo_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🏢 Duoc UC")
            logo_font = QFont("Segoe UI", 14, QFont.Bold)
            logo_label.setFont(logo_font)
            logo_label.setStyleSheet(f"color: {DUOC_PRIMARY};")
        
        logo_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(logo_label)
        
        main_layout.addLayout(header_layout)
        
        # Contenido principal
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.StyledPanel)
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 3px solid {DUOC_PRIMARY};
                border-radius: 20px;
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        
        # Configuración responsiva de márgenes del contenido
        if available.width() >= 1920:
            content_margin = 50
            content_spacing = 30
        elif available.width() >= 1366:
            content_margin = 40
            content_spacing = 25
        else:
            content_margin = 30
            content_spacing = 20
            
        content_layout.setContentsMargins(content_margin, content_margin, content_margin, content_margin)
        content_layout.setSpacing(content_spacing)
        
        # Zonas disponibles
        zones_title = QLabel("📍 Zonas Disponibles")
        zones_title_font = QFont("Segoe UI", 24, QFont.Bold)
        zones_title.setFont(zones_title_font)
        zones_title.setAlignment(Qt.AlignCenter)
        zones_title.setStyleSheet(f"color: {DUOC_PRIMARY}; margin-bottom: 20px; padding: 15px;")
        content_layout.addWidget(zones_title)
        
        # Grid de zonas
        zones_grid = QGridLayout()
        zones_grid.setSpacing(20)
        
        # Zona Financiamiento
        fin_zone = self.create_zone_card("💰 Financiamiento", DUOC_SECONDARY, "Gestión de servicios financieros y becas", "Financiamiento")
        zones_grid.addWidget(fin_zone, 0, 0)
        
        # Zona CITT
        citt_zone = self.create_zone_card("🎓 CITT", DUOC_PRIMARY, "Centro de Innovación y Transferencia Tecnológica", "CITT")
        zones_grid.addWidget(citt_zone, 0, 1)
        
        # Zona Auditorio
        aud_zone = self.create_zone_card("🎭 Auditorio", DUOC_ACCENT, "Espacios para eventos y presentaciones", "Auditorio")
        zones_grid.addWidget(aud_zone, 1, 0)
        
        # Zona Administración
        admin_zone = self.create_zone_card("👥 Administración", DUOC_NEUTRAL, "Oficinas administrativas y atención al público", "Administración")
        zones_grid.addWidget(admin_zone, 1, 1)
        
        content_layout.addLayout(zones_grid)
        
        # Mensaje de desarrollo
        dev_label = QLabel("""
        <div style="text-align: center; padding: 30px; background-color: #fff3cd; border-radius: 15px; border: 3px solid #ffc107;">
        <h3 style="color: #856404; margin: 0 0 15px 0; font-family: 'Segoe UI', sans-serif; font-size: 18px; font-weight: bold;">🚧 Módulo en Desarrollo</h3>
        <p style="color: #856404; margin: 0; font-family: 'Segoe UI', sans-serif; font-size: 16px;">
        La gestión avanzada de zonas estará disponible próximamente.
        </p>
        </div>
        """)
        content_layout.addWidget(dev_label)
        
        main_layout.addWidget(content_frame)
        main_layout.addStretch()
        
        # Botón de regreso
        back_button = QPushButton("⬅️ Volver al Menú Principal")
        
        # Configuración responsiva del botón
        if available.width() >= 1920:
            btn_width, btn_height = 250, 50
            btn_font_size = 16
        elif available.width() >= 1366:
            btn_width, btn_height = 220, 45
            btn_font_size = 14
        else:
            btn_width, btn_height = 200, 40
            btn_font_size = 12
            
        back_button.setFixedSize(btn_width, btn_height)
        back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DUOC_PRIMARY};
                color: white;
                border: 2px solid {self.darken_color(DUOC_PRIMARY)};
                border-radius: 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: {btn_font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(DUOC_PRIMARY)};
                border-color: {DUOC_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(DUOC_PRIMARY, 0.3)};
            }}
        """)
        back_button.clicked.connect(self.go_to_main)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        # Configurar el scroll area
        scroll_area.setWidget(main_widget)
        
        # Layout principal del widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
    
    def go_to_main(self):
        """Regresa al menú principal"""
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'navigation_manager'):
                parent.navigation_manager.navigate_to("main")
                return
            elif hasattr(parent, 'go_to_main'):
                parent.go_to_main()
                return
            parent = parent.parent()
    
    def create_zone_card(self, title, color, description, zone_name):
        """Crea una tarjeta para una zona (compacta y con contador de color)"""
        available = QGuiApplication.primaryScreen().availableGeometry()
        
        if available.width() >= 1920:
            title_font_size = 16
            count_font_size = 14
            desc_font_size = 12
            btn_height = 45
            card_padding = 20
        elif available.width() >= 1366:
            title_font_size = 14
            count_font_size = 12
            desc_font_size = 11
            btn_height = 40
            card_padding = 16
        else:
            title_font_size = 13
            count_font_size = 11
            desc_font_size = 10
            btn_height = 35
            card_padding = 14
            
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 3px solid {color};
                border-radius: 15px;
                padding: {card_padding}px;
                min-height: 180px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", title_font_size, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {color}; margin-bottom: 5px; padding: 5px;")
        layout.addWidget(title_label)
        
        # Contador
        count_label = QLabel("👥 0 visitantes actuales")
        count_font = QFont("Segoe UI", count_font_size, QFont.Bold)
        count_label.setFont(count_font)
        count_label.setAlignment(Qt.AlignCenter)
        count_label.setStyleSheet(f"""
            color: white; 
            background-color: {color};
            border-radius: 12px; 
            padding: 6px 12px;
            border: 2px solid {self.darken_color(color, 0.2)};
            margin: 5px;
        """)
        count_label.setObjectName(f"count_{zone_name}")
        layout.addWidget(count_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_font = QFont("Segoe UI", desc_font_size)
        desc_label.setFont(desc_font)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {DUOC_NEUTRAL}; padding: 6px; margin: 4px;")
        layout.addWidget(desc_label)
        
        # Botón
        manage_btn = QPushButton("🔧 Gestionar")
        manage_btn.setFixedHeight(btn_height)
        manage_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: {desc_font_size}px;
                margin: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """)
        manage_btn.clicked.connect(lambda: self.manage_zone(zone_name))
        layout.addWidget(manage_btn)
        
        return card
    
    def lighten_color(self, color, factor=0.1):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, color, factor=0.2):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_zone_counts)
        self.timer.start(5000)
        self.update_zone_counts()
    
    def update_zone_counts(self):
        zones = ["Financiamiento", "CITT", "Auditorio", "Administración"]
        
        for zone in zones:
            count_label = self.findChild(QLabel, f"count_{zone}")
            if count_label:
                current_visitors = self.visitor_manager.get_visitors_by_sector(zone)
                current_count = len([v for v in current_visitors if v.estado == "Dentro"])
                count_label.setText(f"👥 {current_count} visitantes actuales")
                
                # Estilo según número de visitantes 🚦
                if current_count >= 20:  # Rojo
                    count_label.setStyleSheet(f"""
                        color: white;
                        background-color: {DUOC_ACCENT};
                        border-radius: 12px; 
                        padding: 6px 12px;
                        border: 2px solid {self.darken_color(DUOC_ACCENT)};
                        font-weight: bold;
                        margin: 5px;
                    """)
                elif current_count >= 10:  # Amarillo
                    count_label.setStyleSheet(f"""
                        color: black;
                        background-color: {DUOC_WARNING};
                        border-radius: 12px; 
                        padding: 6px 12px;
                        border: 2px solid {self.darken_color(DUOC_WARNING)};
                        font-weight: bold;
                        margin: 5px;
                    """)
                else:  # Verde
                    count_label.setStyleSheet(f"""
                        color: white;
                        background-color: {DUOC_SUCCESS};
                        border-radius: 12px; 
                        padding: 6px 12px;
                        border: 2px solid {self.darken_color(DUOC_SUCCESS)};
                        font-weight: bold;
                        margin: 5px;
                    """)
    
    def manage_zone(self, zone_name):
        current_visitors = self.visitor_manager.get_visitors_by_sector(zone_name)
        current_count = len([v for v in current_visitors if v.estado == "Dentro"])
        
        if current_count >= 20:
            reply = QMessageBox.question(
                self, 
                "⚠️ Cupo Máximo Alcanzado",
                f"La zona {zone_name} ya tiene {current_count} visitantes (cupo máximo: 20).\n\n"
                f"¿Estás seguro que quieres agregar más visitantes a esta zona?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        QMessageBox.information(
            self,
            f"Gestión de {zone_name}",
            f"Zona: {zone_name}\n"
            f"Visitantes actuales: {current_count}\n"
            f"Cupo máximo: 20\n\n"
            f"Funcionalidad de gestión en desarrollo..."
        )
