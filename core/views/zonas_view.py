from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QMessageBox,
    QScrollArea,
    QLineEdit,
    QComboBox,
    QProgressBar,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QGuiApplication
from core.ui.icon_loader import get_icon_for_emoji
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.visitors import VisitorManager
from string import Template

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
        self.dark_mode = False
        self.zone_cards = {}
        self.progress_template = ""
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.main_container = QWidget()
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(32, 32, 32, 24)
        container_layout.setSpacing(24)

        self.header_card = QFrame()
        header_layout = QVBoxLayout(self.header_card)
        header_layout.setContentsMargins(28, 28, 28, 28)
        header_layout.setSpacing(10)

        self.title_label = QLabel("Gestión de Zonas")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(
            "Monitorea la ocupación y accede rápidamente a cada sector del campus."
        )
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("font-size: 13px;")
        header_layout.addWidget(self.subtitle_label)

        self.header_badge = QLabel("Actualización automática cada 5 segundos")
        self.header_badge.setAlignment(Qt.AlignLeft)
        self.header_badge.setStyleSheet(
            "padding: 6px 14px; border-radius: 14px; font-size: 12px; font-weight: 600;"
        )
        header_layout.addWidget(self.header_badge)

        container_layout.addWidget(self.header_card)

        self.controls_card = QFrame()
        controls_layout = QHBoxLayout(self.controls_card)
        controls_layout.setContentsMargins(24, 20, 24, 20)
        controls_layout.setSpacing(16)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar zona por nombre o descripción…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(44)
        controls_layout.addWidget(self.search_input, stretch=2)

        self.filter_label = QLabel("Filtro")
        controls_layout.addWidget(self.filter_label)

        self.zone_filter = QComboBox()
        self.zone_filter.addItems(["Todas", "Financiamiento", "CITT", "Auditorio", "Administración"])
        self.zone_filter.setMinimumHeight(44)
        controls_layout.addWidget(self.zone_filter)

        controls_layout.addStretch()

        container_layout.addWidget(self.controls_card)

        self.grid_card = QFrame()
        grid_layout = QVBoxLayout(self.grid_card)
        grid_layout.setContentsMargins(28, 28, 28, 28)
        grid_layout.setSpacing(20)

        # Crear layout horizontal para título con icono
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # Agregar icono al título
        title_icon = get_icon_for_emoji("📍", 20)
        if not title_icon.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(title_icon.pixmap(20, 20))
            title_layout.addWidget(icon_label)
        
        self.zones_title = QLabel("Zonas disponibles")
        self.zones_title.setAlignment(Qt.AlignLeft)
        self.zones_title.setStyleSheet("font-size: 18px; font-weight: 700;")
        title_layout.addWidget(self.zones_title)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        grid_layout.addWidget(title_container)

        self.zones_grid = QGridLayout()
        self.zones_grid.setSpacing(18)
        grid_layout.addLayout(self.zones_grid)

        self.empty_state = QLabel("\nNo hay zonas que coincidan con tu búsqueda/filtro.\n")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setVisible(False)
        grid_layout.addWidget(self.empty_state)

        container_layout.addWidget(self.grid_card)

        self.back_button = QPushButton("Volver al menú principal")
        self.back_button.setIcon(get_icon_for_emoji("⬅️", 18))
        self.back_button.setMinimumHeight(46)
        container_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        scroll_area.setWidget(self.main_container)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        self.search_input.textChanged.connect(self.filter_zones)
        self.zone_filter.currentTextChanged.connect(self.filter_zones)

        self.back_button.clicked.connect(self.go_to_main)

        self.zone_cards = {}
        zones = [
            ("Financiamiento", "💰", DUOC_SECONDARY, "Gestión de servicios financieros y becas"),
            ("CITT", "🎓", DUOC_PRIMARY, "Centro de Innovación y Transferencia Tecnológica"),
            ("Auditorio", "🎭", DUOC_ACCENT, "Espacios para eventos y presentaciones"),
            ("Administración", "👥", DUOC_NEUTRAL, "Oficinas administrativas y atención al público"),
        ]

        for index, (name, emoji, color, description) in enumerate(zones):
            card_info = self.create_zone_card(name, emoji, color, description)
            row, col = divmod(index, 2)
            self.zones_grid.addWidget(card_info["frame"], row, col)
            self.zone_cards[name] = card_info

        self.apply_theme()

    def set_theme(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self.apply_theme()
        self.update_zone_counts()

    def apply_theme(self):
        if self.dark_mode:
            main_bg = "#0b1220"
            card_bg = "#111827"
            inner_card_bg = "#111827"
            border_color = "rgba(148, 163, 184, 0.18)"
            text_color = "#e2e8f0"
            muted_color = "#94a3b8"
            badge_bg = "rgba(56, 189, 248, 0.18)"
            badge_color = "#38bdf8"
            input_bg = "#0f172a"
            input_border = "rgba(148, 163, 184, 0.35)"
            input_text = "#f8fafc"
            back_border = "rgba(148, 163, 184, 0.4)"
            back_hover = "rgba(148, 163, 184, 0.18)"
            progress_bg = "rgba(148, 163, 184, 0.14)"
            progress_text = "#e2e8f0"
        else:
            main_bg = "#f3f4f6"
            card_bg = "#ffffff"
            inner_card_bg = "#ffffff"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#0f172a"
            muted_color = "#64748b"
            badge_bg = "rgba(14, 165, 233, 0.14)"
            badge_color = "#0284c7"
            input_bg = "#ffffff"
            input_border = "rgba(148, 163, 184, 0.3)"
            input_text = "#1f2937"
            back_border = "rgba(15, 23, 42, 0.25)"
            back_hover = "rgba(15, 23, 42, 0.08)"
            progress_bg = "rgba(148, 163, 184, 0.18)"
            progress_text = "#0f172a"

        self.progress_template = Template(
            """
            QProgressBar {
                background-color: $bg_color;
                border: 1px solid $border_color;
                border-radius: 10px;
                padding: 4px;
                color: $text_color;
            }
            QProgressBar::chunk {
                background-color: $chunk_color;
                border-radius: 8px;
            }
            """
        )
        self.progress_base_colors = {
            "bg_color": progress_bg,
            "border_color": border_color,
            "text_color": progress_text,
        }

        self.count_palette = {
            "low": (DUOC_SUCCESS, "#0f172a" if not self.dark_mode else "#0f172a"),
            "medium": (DUOC_SECONDARY, "#0f172a"),
            "high": (DUOC_DANGER, "#0f172a"),
        }
        if self.dark_mode:
            self.count_palette["medium"] = (DUOC_SECONDARY, "#0f172a")
            self.count_palette["low"] = (DUOC_SUCCESS, "#0f172a")
            self.count_palette["high"] = (DUOC_DANGER, "#f8fafc")
        else:
            self.count_palette["high"] = (DUOC_DANGER, "#ffffff")

        self.main_container.setStyleSheet(
            f"""
            QWidget {{
                background-color: {main_bg};
            }}
            QFrame#visitorsQuickSection {{ border: none; }}
            """
        )

        self.header_card.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )
        self.controls_card.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )
        self.grid_card.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )

        self.title_label.setStyleSheet(f"color: {text_color}; font-size: 24px; font-weight: 700;")
        self.subtitle_label.setStyleSheet(f"color: {muted_color}; font-size: 13px;")
        self.header_badge.setStyleSheet(
            f"padding: 6px 14px; border-radius: 14px; font-size: 12px; font-weight: 600;"
            f"background-color: rgba(0, 58, 112, 0.12); color: {DUOC_PRIMARY};"
        )

        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {input_border};
                border-radius: 14px;
                padding: 0 16px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {DUOC_PRIMARY};
            }}
            """
        )
        self.filter_label.setStyleSheet(f"font-weight: 600; color: {muted_color};")
        self.zone_filter.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {input_border};
                border-radius: 14px;
                padding: 0 14px;
                min-width: 180px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {card_bg};
                border-radius: 12px;
                border: 1px solid {border_color};
                padding: 4px;
                color: {text_color};
            }}
            """
        )

        self.zones_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {text_color};")
        self.empty_state.setStyleSheet(
            f"color: {muted_color}; border: 1px dashed {border_color};"
            f"border-radius: 18px; padding: 20px; background-color: rgba(148, 163, 184, 0.08);"
        )

        self.back_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 184, 28, 0.1);
                color: {DUOC_SECONDARY};
                border: 2px solid {DUOC_SECONDARY};
                border-radius: 14px;
                padding: 0 26px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {DUOC_SECONDARY};
                color: #000000;
            }}
            """
        )

        for info in self.zone_cards.values():
            accent = info["accent"]
            frame = info["frame"]
            frame.setStyleSheet(
                f"QFrame {{ background-color: {inner_card_bg}; border-radius: 20px; border: 1px solid {border_color}; }}"
            )
            info["title"].setStyleSheet(f"color: {accent}; font-weight: 700;")
            # Actualizar estilos del contador con colores institucionales
            count_number = info.get("count_number")
            if count_number:
                count_number.setStyleSheet("""
                    color: #ffffff;
                    background-color: transparent;
                    padding: 0px;
                    margin: 0px;
                """)
            count_label = info.get("count_label")
            if count_label:
                count_label.setStyleSheet("""
                    color: rgba(255,255,255,0.85);
                    background-color: transparent;
                    padding: 0px;
                    margin: 0px;
                    font-weight: 600;
                """)
            info["description"].setStyleSheet(f"color: {muted_color};")
            info["view_btn"].setStyleSheet(self._ghost_button_style(accent))
            info["add_btn"].setStyleSheet(self._accent_button_style(accent))

    def _ghost_button_style(self, accent: str) -> str:
        tint = self.lighten_color(accent, 0.45)
        return (
            f"""
            QPushButton {{
                background-color: {tint};
                color: #0f172a;
                border: none;
                border-radius: 14px;
                padding: 10px 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(accent, 0.1)};
                color: #ffffff;
            }}
            """
        )

    def _accent_button_style(self, accent: str) -> str:
        darker = self.darken_color(accent, 0.15)
        return (
            f"""
            QPushButton {{
                background-color: {accent};
                color: #ffffff;
                border: none;
                border-radius: 14px;
                padding: 10px 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {darker};
            }}
            """
        )

    def _style_count_label(self, label: QLabel, level: str):
        bg_color, fg_color = self.count_palette.get(level, (DUOC_SUCCESS, "#0f172a"))
        label.setStyleSheet(
            f"background-color: {bg_color}; color: {fg_color};"
            "font-weight: 600; padding: 8px 12px; border-radius: 12px;"
        )

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

    def create_zone_card(self, zone_name, emoji, color, description):
        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        # Crear layout horizontal para título con icono
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # Agregar icono al título
        icon_obj = get_icon_for_emoji(emoji, 20)
        if not icon_obj.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(icon_obj.pixmap(20, 20))
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(zone_name)
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        card_layout.addLayout(title_layout)

        # Contenedor del contador con diseño elegante usando colores institucionales
        count_container = QFrame()
        count_container.setObjectName("CountContainer")
        count_container.setStyleSheet(f"""
            QFrame#CountContainer {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {DUOC_PRIMARY},
                    stop:1 rgba(0, 58, 112, 0.8));
                border-radius: 12px;
                padding: 14px 18px;
                border: 2px solid rgba(0, 58, 112, 0.35);
            }}
        """)
        
        count_layout = QHBoxLayout(count_container)
        count_layout.setContentsMargins(0, 0, 0, 0)
        count_layout.setSpacing(14)
        
        # Icono con fondo circular usando color secundario
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {DUOC_SECONDARY};
                border-radius: 20px;
            }}
        """)
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        count_icon = get_icon_for_emoji("👥", 22)
        if not count_icon.isNull():
            count_icon_label = QLabel()
            count_icon_label.setPixmap(count_icon.pixmap(22, 22))
            count_icon_label.setStyleSheet("background-color: transparent;")
            icon_layout.addWidget(count_icon_label)
        
        count_layout.addWidget(icon_container)
        
        # Layout vertical para número y texto
        count_text_layout = QVBoxLayout()
        count_text_layout.setContentsMargins(0, 0, 0, 0)
        count_text_layout.setSpacing(3)
        
        # Número destacado con color institucional
        count_number = QLabel("0")
        count_number.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        count_number.setFont(QFont("Segoe UI", 36, QFont.Bold))
        count_number.setStyleSheet("""
            color: #ffffff;
            background-color: transparent;
            padding: 0px;
            margin: 0px;
        """)
        count_text_layout.addWidget(count_number)
        
        # Texto descriptivo con color secundario
        count_label = QLabel("visitantes actuales")
        count_label.setAlignment(Qt.AlignLeft)
        count_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        count_label.setStyleSheet("""
            color: rgba(255,255,255,0.85);
            background-color: transparent;
            padding: 0px;
            margin: 0px;
        """)
        count_text_layout.addWidget(count_label)
        
        count_layout.addLayout(count_text_layout)
        count_layout.addStretch()
        
        card_layout.addWidget(count_container)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(desc_label)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        view_btn = QPushButton("Ver visitantes")
        view_btn.setIcon(get_icon_for_emoji("👥", 16))
        view_btn.setMinimumHeight(42)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(lambda: self.go_to_visitors_with_filter(zone_name))

        add_btn = QPushButton("Registrar")
        add_btn.setIcon(get_icon_for_emoji("➕", 16))
        add_btn.setMinimumHeight(42)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(lambda: self.open_new_visitor_in_zone(zone_name))

        actions_layout.addWidget(view_btn)
        actions_layout.addWidget(add_btn)
        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)

        return {
            "frame": card,
            "accent": color,
            "title": title_label,
            "count": count_container,  # Devolver el widget contenedor en lugar del label
            "count_number": count_number,  # Referencia al número destacado
            "count_label": count_label,  # Guardar también la referencia al label para actualizar
            "description": desc_label,
            "view_btn": view_btn,
            "add_btn": add_btn,
        }

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

        for zone_name, info in self.zone_cards.items():
            # Obtener el número destacado y el label del contador
            count_number = info.get("count_number", None)
            count_label = info.get("count_label", None)
            if not count_number or not count_label:
                # Fallback: intentar obtener desde el widget contenedor (QFrame)
                count_widget = info.get("count")
                if count_widget and hasattr(count_widget, 'layout'):
                    count_layout = count_widget.layout()
                    if count_layout and count_layout.count() > 1:
                        # El segundo item es el layout vertical con número y texto (índice 1)
                        text_layout_item = count_layout.itemAt(1)
                        if text_layout_item and text_layout_item.layout():
                            text_layout = text_layout_item.layout()
                            # El número está en el primer item del layout vertical (índice 0)
                            if text_layout.count() > 0 and not count_number:
                                count_number = text_layout.itemAt(0).widget()
                            # El label está en el segundo item del layout vertical (índice 1)
                            if text_layout.count() > 1 and not count_label:
                                count_label = text_layout.itemAt(1).widget()
            
            current_visitors = self.visitor_manager.get_visitors_by_sector(zone_name)
            current_count = len([v for v in current_visitors if v.estado == "Dentro"])
            
            if count_number:
                count_number.setText(str(current_count))
            if count_label:
                count_label.setText("visitantes actuales")

        # Actualizar visibilidad por filtros/búsqueda (en caso de cambios en tiempo real)
        self.filter_zones()

    def filter_zones(self):
        query = self.search_input.text().strip().lower()
        selected = self.zone_filter.currentText()
        any_visible = False
        for zone_name, info in self.zone_cards.items():
            frame = info["frame"]
            title_text = info["title"].text().lower()
            desc_text = info["description"].text().lower()
            match_filter = (selected == "Todas") or (zone_name == selected)
            match_query = (query == "") or (query in title_text) or (query in desc_text)
            visible = match_filter and match_query
            frame.setVisible(visible)
            any_visible = any_visible or visible
        self.empty_state.setVisible(not any_visible)

    def manage_zone(self, zone_name):
        current_visitors = self.visitor_manager.get_visitors_by_sector(zone_name)
        current_count = len([v for v in current_visitors if v.estado == "Dentro"])

        QMessageBox.information(
            self,
            f"Gestión de {zone_name}",
            f"Zona: {zone_name}\n"
            f"Visitantes actuales: {current_count}\n\n"
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
