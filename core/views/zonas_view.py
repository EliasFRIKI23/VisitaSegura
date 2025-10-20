from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QMessageBox, QScrollArea, QLineEdit, QComboBox, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QGuiApplication
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from visitor_model import VisitorManager

# Importar colores del tema
try:
    from core.theme import (
        DUOC_PRIMARY, DUOC_SECONDARY, DUOC_SUCCESS, DUOC_DANGER, DUOC_INFO,
        darken_color as duoc_darken, get_standard_button_style
    )
    DUOC_ACCENT = "#307FE2"       # Azul acento
    DUOC_NEUTRAL = "#6C757D"      # Gris neutro
    DUOC_LIGHT = "#F8F9FA"        # Gris claro
    DUOC_DARK = "#212529"         # Gris oscuro
    DUOC_WARNING = "#ffc107"      # Amarillo para advertencia
except Exception:
    DUOC_PRIMARY = "#003A70"      # Azul institucional
    DUOC_SECONDARY = "#FFB800"    # Amarillo institucional
    DUOC_SUCCESS = "#28a745"      # Verde para capacidad baja
    DUOC_DANGER = "#dc3545"       # Rojo para capacidad alta
    DUOC_INFO = "#17a2b8"
    DUOC_ACCENT = "#307FE2"       # Azul acento
    DUOC_NEUTRAL = "#6C757D"      # Gris neutro
    DUOC_LIGHT = "#F8F9FA"        # Gris claro
    DUOC_DARK = "#212529"         # Gris oscuro
    DUOC_WARNING = "#ffc107"      # Amarillo para advertencia
    def duoc_darken(color, factor=0.2):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    def get_standard_button_style(color, text_color=None):
        return f"""
            QPushButton {{
                background-color: {color};
                color: {'#000000' if color in [DUOC_SECONDARY, "#ffc107"] else '#ffffff'};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {duoc_darken(color, 0.1)};
            }}
            QPushButton:disabled {{
                background-color: #6c757d;
                color: #adb5bd;
            }}
        """

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

        # Barra de búsqueda y filtro
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar zona por nombre o descripción…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMaximumWidth(350)
        controls_layout.addWidget(self.search_input)

        controls_layout.addStretch()

        self.zone_filter = QComboBox()
        self.zone_filter.addItems(["Todas", "Financiamiento", "CITT", "Auditorio", "Administración"])
        controls_layout.addWidget(QLabel("Filtro:"))
        controls_layout.addWidget(self.zone_filter)

        main_layout.addLayout(controls_layout)
        
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
        self.zones_grid = zones_grid
        self.zone_cards = {}
        
        # Zona Financiamiento
        fin_zone = self.create_zone_card("💰 Financiamiento", DUOC_SECONDARY, "Gestión de servicios financieros y becas", "Financiamiento")
        zones_grid.addWidget(fin_zone, 0, 0)
        self.zone_cards["Financiamiento"] = fin_zone
        
        # Zona CITT
        citt_zone = self.create_zone_card("🎓 CITT", DUOC_PRIMARY, "Centro de Innovación y Transferencia Tecnológica", "CITT")
        zones_grid.addWidget(citt_zone, 0, 1)
        self.zone_cards["CITT"] = citt_zone
        
        # Zona Auditorio
        aud_zone = self.create_zone_card("🎭 Auditorio", DUOC_ACCENT, "Espacios para eventos y presentaciones", "Auditorio")
        zones_grid.addWidget(aud_zone, 1, 0)
        self.zone_cards["Auditorio"] = aud_zone
        
        # Zona Administración
        admin_zone = self.create_zone_card("👥 Administración", DUOC_NEUTRAL, "Oficinas administrativas y atención al público", "Administración")
        zones_grid.addWidget(admin_zone, 1, 1)
        self.zone_cards["Administración"] = admin_zone
        
        content_layout.addLayout(zones_grid)
        
        # Estado vacío (si filtros ocultan todo)
        self.empty_state = QLabel("\nNo hay zonas que coincidan con tu búsqueda/filtro.\n")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setStyleSheet("color: #6c757d; border: 1px dashed #dee2e6; border-radius: 12px; padding: 18px;")
        self.empty_state.setVisible(False)
        content_layout.addWidget(self.empty_state)
        
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
        back_button.setStyleSheet(get_standard_button_style(DUOC_PRIMARY))
        back_button.clicked.connect(self.go_to_main)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        # Configurar el scroll area
        scroll_area.setWidget(main_widget)
        
        # Layout principal del widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        # Conexiones de controles
        self.search_input.textChanged.connect(self.filter_zones)
        self.zone_filter.currentTextChanged.connect(self.filter_zones)
    
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

        # Barra de progreso de capacidad (0-20)
        progress = QProgressBar()
        progress.setRange(0, 20)
        progress.setValue(0)
        progress.setFormat("%v / %m")
        progress.setAlignment(Qt.AlignCenter)
        progress.setObjectName(f"progress_{zone_name}")
        progress.setStyleSheet("""
            QProgressBar {
                background-color: #f1f3f5;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 2px;
                color: #343a40;
            }
            QProgressBar::chunk {
                background-color: %s;
                border-radius: 6px;
            }
        """ % color)
        layout.addWidget(progress)
        
        # Descripción
        desc_label = QLabel(description)
        desc_font = QFont("Segoe UI", desc_font_size)
        desc_label.setFont(desc_font)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {DUOC_NEUTRAL}; padding: 6px; margin: 4px;")
        layout.addWidget(desc_label)
        
        # Botones de acción rápida
        actions = QHBoxLayout()
        view_btn = QPushButton("👥 Ver visitantes")
        view_btn.setFixedHeight(btn_height)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.darken_color(color, 0.15)};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: {desc_font_size}px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        view_btn.clicked.connect(lambda: self.go_to_visitors_with_filter(zone_name))

        add_btn = QPushButton("➕ Registrar")
        add_btn.setFixedHeight(btn_height)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: {desc_font_size}px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        add_btn.clicked.connect(lambda: self.open_new_visitor_in_zone(zone_name))

        actions.addWidget(view_btn)
        actions.addWidget(add_btn)
        layout.addLayout(actions)
        
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
        # Forzar recarga de datos para asegurar que estén actualizados
        self.visitor_manager.force_reload()
        
        zones = ["Financiamiento", "CITT", "Auditorio", "Administración"]
        
        for zone in zones:
            count_label = self.findChild(QLabel, f"count_{zone}")
            progress = self.findChild(QProgressBar, f"progress_{zone}")
            if count_label:
                current_visitors = self.visitor_manager.get_visitors_by_sector(zone)
                current_count = len([v for v in current_visitors if v.estado == "Dentro"])
                count_label.setText(f"👥 {current_count} visitantes actuales")
                
                # Estilo según número de visitantes 🚦
                if current_count >= 20:  # Alto
                    count_label.setStyleSheet(f"""
                        color: white;
                        background-color: {DUOC_DANGER};
                        border-radius: 12px; 
                        padding: 6px 12px;
                        border: 2px solid {self.darken_color(DUOC_DANGER)};
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

            if progress:
                current_visitors = self.visitor_manager.get_visitors_by_sector(zone)
                current_count = len([v for v in current_visitors if v.estado == "Dentro"])
                progress.setValue(min(current_count, 20))
                # Cambiar color del chunk según umbrales
                if current_count >= 20:
                    chunk_color = DUOC_DANGER
                elif current_count >= 10:
                    chunk_color = DUOC_WARNING
                else:
                    chunk_color = DUOC_SUCCESS
                progress.setStyleSheet("""
                    QProgressBar {
                        background-color: #f1f3f5;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 2px;
                        color: #343a40;
                    }
                    QProgressBar::chunk {
                        background-color: %s;
                        border-radius: 6px;
                    }
                """ % chunk_color)

        # Actualizar visibilidad por filtros/búsqueda (en caso de cambios en tiempo real)
        self.filter_zones()

    def filter_zones(self):
        query = self.search_input.text().strip().lower()
        selected = self.zone_filter.currentText()
        any_visible = False
        for zone_name, card in self.zone_cards.items():
            match_filter = (selected == "Todas") or (zone_name == selected)
            # Buscar en título y descripción dentro del card
            # Usamos objectName para localizar labels hijos si fuese necesario
            title_text = ""  # fallback
            desc_text = ""
            for child in card.findChildren(QLabel):
                if child.text() and (" ") in child.text():
                    # Heurística simple: el primero suele ser el título con emoji
                    if not title_text:
                        title_text = child.text()
                    else:
                        desc_text = child.text()
                        break
            match_query = (query == "") or (query in title_text.lower()) or (query in desc_text.lower())
            visible = match_filter and match_query
            card.setVisible(visible)
            any_visible = any_visible or visible
        self.empty_state.setVisible(not any_visible)
    
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

    def go_to_visitors_with_filter(self, sector: str):
        # Navega a la vista de visitantes y aplica filtro por sector
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'navigation_manager'):
                parent.navigation_manager.navigate_to("visitantes")
                # Obtener el widget de visitantes para aplicar el filtro
                try:
                    visitors_widget = parent.navigation_manager.views.get("visitantes")
                    if hasattr(visitors_widget, 'set_zone_filter'):
                        visitors_widget.set_zone_filter(sector)
                except Exception:
                    pass
                return
            parent = parent.parent()

    def open_new_visitor_in_zone(self, sector: str):
        # Abre el formulario de nuevo visitante con sector preseleccionado
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'navigation_manager'):
                parent.navigation_manager.navigate_to("visitantes")
                try:
                    visitors_widget = parent.navigation_manager.views.get("visitantes")
                    if hasattr(visitors_widget, 'open_new_with_sector'):
                        visitors_widget.open_new_with_sector(sector)
                except Exception:
                    pass
                return
            parent = parent.parent()
