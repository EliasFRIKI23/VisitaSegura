from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit, QHeaderView, QMessageBox,
    QMenu, QAbstractItemView, QFrame, QSplitter, QGroupBox,
    QDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QAction, QIcon, QColor, QPixmap
try:
    from .theme import (
        DUOC_PRIMARY, DUOC_SECONDARY, DUOC_SUCCESS, DUOC_DANGER, DUOC_INFO,
        DUOC_GRAY, DUOC_GRAY_DARK,
        darken_color as duoc_darken, get_standard_button_style,
        normalize_rut, format_rut_display, get_current_user
    )
    from core.ui import configure_modern_table, apply_modern_table_theme
except Exception:
    DUOC_PRIMARY = "#003A70"
    DUOC_SECONDARY = "#FFB81C"
    DUOC_SUCCESS = "#28a745"
    DUOC_DANGER = "#dc3545"
    DUOC_INFO = "#17a2b8"

    def duoc_darken(color, factor=0.2):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_standard_button_style(color, text_color=None):
        resolved_color = text_color or ('#000000' if color in [DUOC_SECONDARY, "#ffc107"] else '#ffffff')
        return f"""
            QPushButton {{
                background-color: {color};
                color: {resolved_color};
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

    def normalize_rut(rut_input):
        """Fallback si no se puede importar la función"""
        return rut_input

    def format_rut_display(rut):
        """Fallback si no se puede importar la función"""
        return rut

    def get_current_user():
        """Fallback si no se puede importar la función"""
        return "Sistema"

    def configure_modern_table(table, **kwargs):  # type: ignore
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)

    def apply_modern_table_theme(table, dark_mode=False):  # type: ignore
        base_bg = "#0f172a" if dark_mode else "#ffffff"
        base_fg = "#e2e8f0" if dark_mode else "#1f2937"
        table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {base_bg};
                color: {base_fg};
                border: none;
            }}
            """
        )
from datetime import datetime
from .visitors import VisitorManager
from .visitor_form import VisitorFormDialog, QuickVisitorForm
from .help_dialog import HelpDialog

class VisitorListWidget(QWidget):
    """Widget principal para la gestión de visitantes"""
    
    # Señales
    visitor_updated = Signal()
    
    def __init__(self, parent=None, auth_manager=None):
        super().__init__(parent)
        self.visitor_manager = VisitorManager()
        self.auth_manager = auth_manager  # Guardar referencia al AuthManager
        self.dark_mode = False
        
        # Configurar tamaño mínimo para mejor visualización de la tabla
        self.setMinimumSize(1200, 600)  # Ancho mínimo de 1200px para acomodar todas las columnas
        
        self.setup_ui()
        self.setup_connections()
        self.refresh_list()
        
        # Timer para actualizar la lista cada 30 segundos
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_list)
        self.refresh_timer.start(30000)  # 30 segundos
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.main_container = QFrame()
        self.main_container.setObjectName("visitorsMainContainer")
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(32, 32, 32, 24)
        container_layout.setSpacing(24)
        outer_layout.addWidget(self.main_container)

        # Encabezado principal
        self.header_card = QFrame()
        self.header_card.setObjectName("visitorsHeaderCard")
        header_layout = QHBoxLayout(self.header_card)
        header_layout.setContentsMargins(28, 28, 28, 28)
        header_layout.setSpacing(18)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(8)

        self.title_label = QLabel("Gestión de Visitantes")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_text_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(
            "Supervisa el flujo de visitantes en tiempo real, aplica filtros rápidos y gestiona registros en segundos."
        )
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("color: #64748b; font-size: 13px;")
        header_text_layout.addWidget(self.subtitle_label)

        self.header_badge = QLabel("Actualización automática cada 30 segundos")
        self.header_badge.setAlignment(Qt.AlignLeft)
        self.header_badge.setStyleSheet(
            f"padding: 6px 14px; border-radius: 14px; font-size: 12px;"
            f"background-color: rgba(0, 58, 112, 0.12); color: {DUOC_PRIMARY}; font-weight: 600;"
        )
        header_text_layout.addWidget(self.header_badge)

        header_layout.addLayout(header_text_layout, stretch=1)

        container_layout.addWidget(self.header_card)

        # Controles superiores
        self.controls_card = QFrame()
        self.controls_card.setObjectName("visitorsControlsCard")
        controls_layout = QHBoxLayout(self.controls_card)
        controls_layout.setContentsMargins(24, 20, 24, 20)
        controls_layout.setSpacing(16)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por RUT, nombre, acompañante o sector…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedHeight(44)
        self.search_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid rgba(148, 163, 184, 0.4);
                border-radius: 14px;
                padding: 0 16px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0ea5e9;
            }
            """
        )
        controls_layout.addWidget(self.search_input, stretch=2)

        self.filter_label = QLabel("Filtro:")
        controls_layout.addWidget(self.filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Todos", "Dentro", "Fuera", "Financiamiento", "CITT", "Auditorio", "Administración"
        ])
        self.filter_combo.setFixedHeight(44)
        self.filter_combo.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid rgba(148, 163, 184, 0.4);
                border-radius: 14px;
                padding: 0 14px;
                font-size: 13px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.3);
                padding: 4px;
            }
            """
        )
        controls_layout.addWidget(self.filter_combo)

        controls_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setMinimumHeight(44)
        self.refresh_btn.setToolTip("Actualizar la lista de visitantes")
        self.refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {DUOC_PRIMARY};
                color: #ffffff;
                border-radius: 14px;
                padding: 0 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {duoc_darken(DUOC_PRIMARY, 0.1)};
            }}
            """
        )
        controls_layout.addWidget(self.refresh_btn)

        container_layout.addWidget(self.controls_card)

        # Contenido principal con splitter
        self.content_splitter = QSplitter(Qt.Horizontal)
        self.content_splitter.setObjectName("visitorsSplitter")
        container_layout.addWidget(self.content_splitter, 1)

        # Panel izquierdo (tabla y acciones)
        left_panel = QFrame()
        left_panel.setObjectName("visitorsLeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(18)

        self.actions_card = QFrame()
        self.actions_card.setObjectName("visitorsActionsCard")
        actions_layout = QHBoxLayout(self.actions_card)
        actions_layout.setContentsMargins(24, 24, 24, 24)
        actions_layout.setSpacing(16)

        self.add_btn = QPushButton("➕ Nuevo visitante")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setMinimumHeight(46)
        self.add_btn.setToolTip("Registrar un nuevo visitante en el sistema")
        self.add_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #22c55e;
                color: #0f172a;
                border-radius: 14px;
                padding: 12px 22px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4ade80;
            }
            """
        )
        actions_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Editar")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setMinimumHeight(46)
        self.edit_btn.setToolTip("Editar la información del visitante seleccionado")
        self.edit_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {DUOC_PRIMARY};
                color: #ffffff;
                border-radius: 14px;
                padding: 12px 22px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {duoc_darken(DUOC_PRIMARY, 0.1)};
            }}
            QPushButton:disabled {{
                background-color: rgba(148, 163, 184, 0.25);
                color: rgba(148, 163, 184, 0.9);
            }}
            """
        )
        actions_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ Eliminar")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setMinimumHeight(46)
        self.delete_btn.setToolTip("Eliminar el visitante seleccionado (acción irreversible)")
        self.delete_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ef4444;
                color: #f8fafc;
                border-radius: 14px;
                padding: 12px 22px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f87171;
            }
            QPushButton:disabled {
                background-color: rgba(148, 163, 184, 0.25);
                color: rgba(148, 163, 184, 0.9);
            }
            """
        )
        actions_layout.addWidget(self.delete_btn)

        actions_layout.addStretch()
        left_layout.addWidget(self.actions_card)

        self.visitor_table = QTableWidget()
        self.visitor_table.setColumnCount(8)
        self.visitor_table.setHorizontalHeaderLabels([
            "🆔 ID", "📄 RUT", "👤 Nombre", "🤝 Acompañante", "🏢 Sector", "📍 Estado", "⏰ Ingreso", "👨‍💼 Registrado por"
        ])

        configure_modern_table(self.visitor_table)
        apply_modern_table_theme(self.visitor_table)
        self.visitor_table.setContextMenuPolicy(Qt.CustomContextMenu)

        header = self.visitor_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setMinimumSectionSize(80)
        header.setDefaultSectionSize(120)

        left_layout.addWidget(self.visitor_table)

        self.empty_state = QLabel(
            "\nNo hay visitantes para mostrar.\n\nUsa \"Nuevo visitante\" o ajusta filtros/búsqueda."
        )
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setStyleSheet(
            "color: #64748b; border: 1px dashed rgba(148, 163, 184, 0.45);"
            "border-radius: 18px; padding: 20px; background-color: rgba(148, 163, 184, 0.08);"
        )
        self.empty_state.setVisible(False)
        left_layout.addWidget(self.empty_state)

        self.content_splitter.addWidget(left_panel)

        # Panel derecho (formulario rápido y estadísticas)
        self.sidebar_card = QFrame()
        self.sidebar_card.setObjectName("visitorsSidebarCard")
        sidebar_layout = QVBoxLayout(self.sidebar_card)
        sidebar_layout.setContentsMargins(24, 24, 24, 24)
        sidebar_layout.setSpacing(20)

        self.sidebar_title = QLabel("Registro rápido")
        self.sidebar_title.setAlignment(Qt.AlignLeft)
        sidebar_layout.addWidget(self.sidebar_title)

        self.quick_section = QFrame()
        self.quick_section.setObjectName("visitorsQuickSection")
        quick_section_layout = QVBoxLayout(self.quick_section)
        quick_section_layout.setContentsMargins(0, 0, 0, 0)
        quick_section_layout.setSpacing(0)

        self.quick_form = QuickVisitorForm(self, self.auth_manager)
        quick_section_layout.addWidget(self.quick_form)

        self.stats_card = QFrame()
        self.stats_card.setObjectName("visitorsStatsCard")
        stats_layout = QVBoxLayout(self.stats_card)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(12)

        self.stats_title = QLabel("📊 Resumen en vivo")
        self.stats_title.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.stats_title)

        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setToolTip("Estadísticas actualizadas en tiempo real")
        stats_layout.addWidget(self.stats_label)

        sidebar_layout.addWidget(self.quick_section)
        sidebar_layout.addStretch()

        self.stats_card = None
        self.stats_title = None
        self.stats_label = None

        self.content_splitter.addWidget(self.sidebar_card)
        self.content_splitter.setSizes([820, 320])

        # Botón de regreso
        self.back_button = QPushButton("⬅️ Volver al menú principal")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setMinimumHeight(46)
        self.back_button.clicked.connect(self.go_to_main)
        container_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.apply_theme()

    def set_theme(self, dark_mode: bool):
        """Actualiza el tema visual del módulo"""
        self.dark_mode = dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            main_bg = "#0b1220"
            card_bg = "#111827"
            sidebar_bg = DUOC_GRAY_DARK  # Gris institucional oscuro para tarjetas secundarias
            border_color = "rgba(148, 163, 184, 0.18)"
            text_color = "#e2e8f0"
            muted_color = DUOC_GRAY  # Gris institucional para texto secundario
            badge_bg = "rgba(56, 189, 248, 0.18)"
            badge_color = "#38bdf8"
            input_bg = "#0f172a"
            input_border = "rgba(148, 163, 184, 0.4)"
            input_text = "#f1f5f9"
            button_border = "rgba(148, 163, 184, 0.35)"
            empty_bg = "rgba(148, 163, 184, 0.12)"
            empty_border = "rgba(148, 163, 184, 0.25)"
            refresh_bg = DUOC_PRIMARY
            refresh_fg = "#ffffff"
            refresh_hover = duoc_darken(DUOC_PRIMARY, 0.1)
            back_border = "rgba(148, 163, 184, 0.4)"
            back_hover = "rgba(148, 163, 184, 0.18)"
        else:
            main_bg = "#f3f4f6"
            card_bg = "#ffffff"
            sidebar_bg = "#f8f9fa"  # Gris claro institucional para tarjetas secundarias
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#0f172a"
            muted_color = DUOC_GRAY  # Gris institucional para texto secundario
            badge_bg = "rgba(14, 165, 233, 0.12)"
            badge_color = "#0284c7"
            input_bg = "#ffffff"
            input_border = "rgba(148, 163, 184, 0.35)"
            input_text = "#1f2937"
            button_border = "rgba(148, 163, 184, 0.25)"
            empty_bg = "rgba(148, 163, 184, 0.08)"
            empty_border = "rgba(148, 163, 184, 0.35)"
            refresh_bg = DUOC_PRIMARY
            refresh_fg = "#ffffff"
            refresh_hover = duoc_darken(DUOC_PRIMARY, 0.1)
            back_border = "rgba(15, 23, 42, 0.25)"
            back_hover = "rgba(15, 23, 42, 0.08)"

        self.main_container.setStyleSheet(
            f"""
            QFrame#visitorsMainContainer {{
                background-color: {main_bg};
            }}
            QFrame#visitorsHeaderCard,
            QFrame#visitorsControlsCard,
            QFrame#visitorsActionsCard,
            QFrame#visitorsSidebarCard,
            QFrame#visitorsStatsCard {{
                background-color: {card_bg};
                border-radius: 24px;
                border: 1px solid {border_color};
            }}
            QFrame#visitorsQuickSection {{
                border: none;
            }}
            QFrame#visitorsActionsCard {{
                border-radius: 20px;
            }}
            QFrame#visitorsSidebarCard {{
                border-radius: 24px;
            }}
            QSplitter#visitorsSplitter::handle {{
                background-color: transparent;
            }}
            """
        )

        self.title_label.setStyleSheet(f"color: {text_color};")
        self.subtitle_label.setStyleSheet(f"color: {muted_color}; font-size: 13px;")
        self.header_badge.setStyleSheet(
            f"padding: 6px 14px; border-radius: 14px; font-size: 12px;"
            f"background-color: {badge_bg}; color: {badge_color}; font-weight: 600;"
        )

        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {input_bg};
                border: 1px solid {input_border};
                border-radius: 14px;
                padding: 0 16px;
                font-size: 13px;
                color: {input_text};
            }}
            QLineEdit:focus {{
                border-color: {DUOC_PRIMARY};
            }}
            """
        )

        filter_style = (
            f"""
            QComboBox {{
                background-color: {input_bg};
                border: 1px solid {input_border};
                border-radius: 14px;
                padding: 0 14px;
                font-size: 13px;
                min-width: 200px;
                color: {input_text};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {card_bg};
                border-radius: 12px;
                border: 1px solid {border_color};
                padding: 4px;
                color: {text_color};
            }}
            """
        )
        self.filter_combo.setStyleSheet(filter_style)
        self.filter_label.setStyleSheet(f"font-weight: 600; color: {muted_color};")

        self.refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {refresh_bg};
                color: {refresh_fg};
                border-radius: 14px;
                padding: 0 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {refresh_hover};
            }}
            """
        )

        self.add_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #22c55e;
                color: #0f172a;
                border-radius: 14px;
                padding: 12px 22px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4ade80;
            }
            """
        )
        self.edit_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {DUOC_PRIMARY};
                color: #ffffff;
                border-radius: 14px;
                padding: 12px 22px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {duoc_darken(DUOC_PRIMARY, 0.1)};
            }}
            QPushButton:disabled {{
                background-color: rgba(148, 163, 184, 0.25);
                color: rgba(148, 163, 184, 0.9);
            }}
            """
        )
        self.delete_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ef4444;
                color: #f8fafc;
                border-radius: 14px;
                padding: 12px 22px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f87171;
            }
            QPushButton:disabled {
                background-color: rgba(148, 163, 184, 0.25);
                color: rgba(148, 163, 184, 0.9);
            }
            """
        )

        self.sidebar_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {text_color};")
        if self.stats_title:
            self.stats_title.setStyleSheet(f"font-weight: 600; color: {text_color};")
        if self.stats_card:
            self.stats_card.setStyleSheet(
                f"background-color: {sidebar_bg}; border-radius: 20px; border: 1px solid {border_color};"
            )
        if self.stats_label:
            self.stats_label.setStyleSheet(f"color: {text_color}; font-size: 13px;")

        self.empty_state.setStyleSheet(
            f"color: {muted_color}; border: 1px dashed {empty_border};"
            f"border-radius: 18px; padding: 20px; background-color: {empty_bg};"
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

        if hasattr(self.quick_form, "apply_theme"):
            self.quick_form.apply_theme(self.dark_mode)

        apply_modern_table_theme(self.visitor_table, self.dark_mode)

    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.add_btn.clicked.connect(self.add_visitor)
        self.edit_btn.clicked.connect(self.edit_visitor)
        self.delete_btn.clicked.connect(self.delete_visitor)
        self.refresh_btn.clicked.connect(self.refresh_list)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        self.search_input.textChanged.connect(self.apply_filter)
        
        self.visitor_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.visitor_table.itemDoubleClicked.connect(self.toggle_visitor_status)
        self.visitor_table.customContextMenuRequested.connect(self.show_context_menu)
    
    # === Métodos públicos para integración con otras vistas ===
    def set_zone_filter(self, sector: str):
        """Aplica un filtro directo por sector desde otras vistas."""
        if sector in ["Financiamiento", "CITT", "Auditorio", "Administración"]:
            self.filter_combo.setCurrentText(sector)
        else:
            self.filter_combo.setCurrentText("Todos")
        if hasattr(self, 'search_input'):
            self.search_input.clear()
        self.refresh_list()

    def open_new_with_sector(self, sector: str):
        """Abre el formulario de nuevo visitante con el sector preseleccionado."""
        dialog = VisitorFormDialog(self, auth_manager=self.auth_manager)
        try:
            idx = dialog.sector_combo.findText(sector)
            if idx >= 0:
                dialog.sector_combo.setCurrentIndex(idx)
        except Exception:
            pass
        if dialog.exec() == QDialog.Accepted:
            visitor = dialog.get_visitor()
            if self.visitor_manager.add_visitor(visitor):
                self.refresh_list()
                QMessageBox.information(self, "✅ Éxito", f"👤 Visitante registrado en {sector}")
            else:
                QMessageBox.warning(self, "⚠️ Error", "🔍 Ya existe un visitante con ese RUT en el sistema")

    def add_visitor(self):
        """Abre el formulario para agregar un nuevo visitante"""
        dialog = VisitorFormDialog(self, auth_manager=self.auth_manager)
        if dialog.exec() == QDialog.Accepted:
            visitor = dialog.get_visitor()
            if self.visitor_manager.add_visitor(visitor):
                self.refresh_list()
                QMessageBox.information(self, "✅ Éxito", "👤 Visitante registrado correctamente en el sistema")
            else:
                QMessageBox.warning(self, "⚠️ Error", "🔍 Ya existe un visitante con ese RUT en el sistema")
    
    def edit_visitor(self):
        """Edita el visitante seleccionado"""
        current_row = self.visitor_table.currentRow()
        if current_row < 0:
            return
        
        visitor_id = self.visitor_table.item(current_row, 0).text()
        visitor = self.visitor_manager.get_visitor_by_id(visitor_id)
        
        if visitor:
            dialog = VisitorFormDialog(self, visitor, auth_manager=self.auth_manager)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_list()
                QMessageBox.information(self, "✅ Éxito", "✏️ Información del visitante actualizada correctamente")
    
    def delete_visitor(self):
        """Elimina el visitante seleccionado"""
        current_row = self.visitor_table.currentRow()
        if current_row < 0:
            return
        
        visitor_id = self.visitor_table.item(current_row, 0).text()
        visitor = self.visitor_manager.get_visitor_by_id(visitor_id)
        
        if visitor:
            reply = QMessageBox.question(
                self, "🗑️ Confirmar Eliminación",
                f"⚠️ ¿Está seguro de que desea eliminar al visitante:\n\n👤 {visitor.nombre_completo}\n🆔 {visitor.rut}\n\n❌ Esta acción no se puede deshacer",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.visitor_manager.delete_visitor(visitor_id):
                    self.refresh_list()
                    QMessageBox.information(self, "✅ Éxito", "🗑️ Visitante eliminado correctamente del sistema")
                else:
                    QMessageBox.critical(self, "❌ Error", "🚫 No se pudo eliminar el visitante del sistema")
    
    def toggle_visitor_status(self, item):
        """Cambia el estado del visitante (doble clic)"""
        row = item.row()
        visitor_id = self.visitor_table.item(row, 0).text()
        
        # Prevenir cambios si ya está fuera
        visitor = self.visitor_manager.get_visitor_by_id(visitor_id)
        if visitor and visitor.estado == "Fuera":
            QMessageBox.information(
                self,
                "🔒 Cambio no permitido",
                f"🚫 El visitante <b>{visitor.nombre_completo}</b> ya está <b>Fuera</b> y su estado no puede modificarse."
            )
            return

        if self.visitor_manager.toggle_visitor_status(visitor_id):
            self.refresh_list()
            
            visitor = self.visitor_manager.get_visitor_by_id(visitor_id)
            if visitor:
                if visitor.estado == "Dentro":
                    status_text = "entró"
                    icon = "🟢"
                else:
                    status_text = "salió"
                    icon = "🔴"
                
                QMessageBox.information(
                    self, "🔄 Estado Actualizado",
                    f"{icon} <b>{visitor.nombre_completo}</b> {status_text} del establecimiento\n\n📍 Estado actual: <b>{visitor.estado}</b>"
                )
    
    def show_context_menu(self, position):
        """Muestra el menú contextual"""
        if self.visitor_table.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        menu.setTitle("🎯 Acciones")
        
        toggle_action = QAction("🔄 Cambiar Estado", self)
        toggle_action.setToolTip("Cambiar entre 'Dentro' y 'Fuera'")
        toggle_action.triggered.connect(lambda: self.toggle_visitor_status(
            self.visitor_table.itemAt(position)
        ))
        menu.addAction(toggle_action)
        
        edit_action = QAction("✏️ Editar Información", self)
        edit_action.setToolTip("Modificar datos del visitante")
        edit_action.triggered.connect(self.edit_visitor)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("🗑️ Eliminar Visitante", self)
        delete_action.setToolTip("Eliminar permanentemente del sistema")
        delete_action.triggered.connect(self.delete_visitor)
        menu.addAction(delete_action)
        
        menu.exec(self.visitor_table.mapToGlobal(position))
    
    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        has_selection = self.visitor_table.currentRow() >= 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def apply_filter(self, filter_text):
        """Aplica filtros a la lista"""
        self.refresh_list()
    
    def show_help(self):
        """Muestra el diálogo de ayuda"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()
    
    def go_to_main(self):
        """Regresa al menú principal"""
        # Buscar la ventana principal que contiene el navigation_manager
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'navigation_manager'):
                parent.navigation_manager.navigate_to("main")
                return
            elif hasattr(parent, 'go_to_main'):
                parent.go_to_main()
                return
            parent = parent.parent()
    
    def refresh_list(self):
        """Actualiza la lista de visitantes"""
        # Forzar recarga de datos para asegurar que estén actualizados
        self.visitor_manager.force_reload()
        visitors = self.visitor_manager.get_all_visitors()
        
        # Aplicar filtros
        filter_text = self.filter_combo.currentText()
        if filter_text != "Todos":
            if filter_text in ["Dentro", "Fuera"]:
                visitors = [v for v in visitors if v.estado == filter_text]
            else:
                visitors = [v for v in visitors if v.sector == filter_text]

        # Aplicar búsqueda
        query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
        if query:
            def match(v):
                return any([
                    query in (v.rut or '').lower(),
                    query in (v.nombre_completo or '').lower(),
                    query in (v.acompañante or '').lower(),
                    query in (v.sector or '').lower(),
                ])
            visitors = [v for v in visitors if match(v)]
        
        # Ordenar por fecha de ingreso (más recientes primero)
        visitors.sort(key=lambda x: x.fecha_ingreso, reverse=True)
        
        # Actualizar tabla
        self.visitor_table.setRowCount(len(visitors))
        
        for row, visitor in enumerate(visitors):
            # ID
            self.visitor_table.setItem(row, 0, QTableWidgetItem(visitor.id))
            
            # RUT - mostrar normalizado
            rut_display = format_rut_display(visitor.rut) if visitor.rut else "N/A"
            self.visitor_table.setItem(row, 1, QTableWidgetItem(rut_display))
            
            # Nombre
            self.visitor_table.setItem(row, 2, QTableWidgetItem(visitor.nombre_completo))
            
            # Acompañante
            self.visitor_table.setItem(row, 3, QTableWidgetItem(visitor.acompañante))
            
            # Sector
            self.visitor_table.setItem(row, 4, QTableWidgetItem(visitor.sector))
            
            # Estado
            estado_item = QTableWidgetItem(visitor.estado)
            if visitor.estado == "Dentro":
                estado_item.setBackground(QColor(144, 238, 144))  # Verde claro
            else:
                estado_item.setBackground(QColor(255, 182, 193))  # Rosa claro
            self.visitor_table.setItem(row, 5, estado_item)
            
            # Fecha de ingreso
            fecha_formatted = datetime.strptime(visitor.fecha_ingreso, "%Y-%m-%d %H:%M:%S")
            fecha_str = fecha_formatted.strftime("%d/%m/%Y %H:%M")
            self.visitor_table.setItem(row, 6, QTableWidgetItem(fecha_str))
            
            # Usuario registrador
            usuario_registrador = visitor.usuario_registrador or "Sistema"
            self.visitor_table.setItem(row, 7, QTableWidgetItem(usuario_registrador))
        
        # Mostrar/ocultar estado vacío
        self.empty_state.setVisible(len(visitors) == 0)

        # Actualizar estadísticas
        if self.stats_label:
            self.update_stats(visitors)
    
    def handle_quick_registration(self):
        """Maneja el registro rápido desde el formulario lateral"""
        if self.quick_form.register_visitor():
            # Actualizar la lista después del registro exitoso
            self.refresh_list()
            QMessageBox.information(
                self, 
                "✅ Éxito", 
                "🚀 Visitante registrado correctamente mediante registro rápido"
            )
    
    def update_stats(self, visitors):
        """Actualiza las estadísticas mostradas"""
        if not self.stats_label:
            return

        total = len(visitors)
        dentro = len([v for v in visitors if v.estado == "Dentro"])
        fuera = total - dentro

        dentro_icon = "🟢" if dentro > 0 else "⚪"
        fuera_icon = "🔴" if fuera > 0 else "⚪"

        stats_text = f"""
        <div style="text-align: center;">
        <b>📊 Resumen de Visitantes</b><br><br>
        👥 <b>Total:</b> {total}<br>
        {dentro_icon} <b>Dentro:</b> {dentro}<br>
        {fuera_icon} <b>Fuera:</b> {fuera}<br><br>
        <small>💡 Actualizado automáticamente</small>
        </div>
        """
        self.stats_label.setText(stats_text)
