from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QGuiApplication, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QMessageBox,
)

from .dependencies import (
    DUOC_PRIMARY,
    DUOC_SECONDARY,
    DUOC_DANGER,
    DUOC_INFO,
    DUOC_SUCCESS,
    VisitorListWidget,
    VisitasView,
    ZonasView,
    ReportesView,
    UsuariosView,
    get_standard_button_style,
)


def heading_font(size: int = 20, bold: bool = True) -> QFont:
    font = QFont()
    font.setPointSize(size)
    font.setBold(bold)
    return font


def body_font(size: int = 13) -> QFont:
    font = QFont()
    font.setPointSize(size)
    return font


class NavigationMixin:
    """Encapsula la configuración de vistas y acciones de navegación."""

    def setup_toolbar(self) -> None:
        self.toolbar_header = QWidget()
        self.toolbar_header.setObjectName("ToolbarContainer")
        header_layout = QHBoxLayout(self.toolbar_header)
        header_layout.setContentsMargins(24, 12, 24, 12)
        header_layout.setSpacing(16)

        title_group = QWidget()
        title_layout = QHBoxLayout(title_group)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)

        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            resized = logo_pixmap.scaled(110, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(resized)
        else:
            logo_label.setText("Duoc UC")
            logo_label.setFont(heading_font(16))

        title_label = QLabel("VisitaSegura")
        title_label.setObjectName("ToolbarTitle")
        title_label.setFont(heading_font(18))

        title_layout.addWidget(logo_label)
        title_layout.addWidget(title_label)
        header_layout.addWidget(title_group)

        header_layout.addStretch()

        self.home_button = QPushButton("🏠 Inicio")
        self.home_button.setCursor(Qt.PointingHandCursor)
        self.home_button.setFixedHeight(32)
        self.home_button.setVisible(False)
        self.home_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(0, 0, 0, 0.04);
                border: none;
                border-radius: 10px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.12);
            }
            """
        )
        self.home_button.clicked.connect(self.go_to_main)
        header_layout.addWidget(self.home_button)

        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.setCursor(Qt.PointingHandCursor)
        self.theme_toggle_button.setFixedHeight(32)
        self.theme_toggle_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(0, 58, 112, 0.08);
                border: 1px solid rgba(0, 58, 112, 0.16);
                border-radius: 10px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 58, 112, 0.16);
            }
            """
        )
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        self.theme_toggle_button.setText("☀️ Modo claro" if getattr(self, "dark_mode", False) else "🌙 Modo oscuro")
        header_layout.addWidget(self.theme_toggle_button)

        self.setMenuWidget(self.toolbar_header)

    # ------------------------------------------------------------------
    # Configuración de vistas
    # ------------------------------------------------------------------

    def setup_views(self) -> None:
        main_view = self.create_main_view()
        self.navigation_manager.register_view("main", main_view)

        visitas_view = VisitasView(self, self.auth_manager)
        if hasattr(visitas_view, "set_theme"):
            visitas_view.set_theme(self.dark_mode)
        self.navigation_manager.register_view("visitas", visitas_view)

        visitor_view = VisitorListWidget(self, self.auth_manager)
        if hasattr(visitor_view, "set_theme"):
            visitor_view.set_theme(self.dark_mode)
        self.navigation_manager.register_view("visitantes", visitor_view)

        zonas_view = ZonasView(self)
        if hasattr(zonas_view, "set_theme"):
            zonas_view.set_theme(self.dark_mode)
        self.navigation_manager.register_view("zonas", zonas_view)

        reportes_view = ReportesView(self, self.auth_manager)
        self.navigation_manager.register_view("reportes", reportes_view)

        usuarios_view = UsuariosView(self, self.auth_manager)
        self.navigation_manager.register_view("usuarios", usuarios_view)

        self.navigation_manager.navigate_to("main")

    def create_main_view(self) -> QWidget:
        background = QWidget()
        self.background_widget = background
        outer_layout = QVBoxLayout(background)
        outer_layout.setContentsMargins(0, 20, 0, 20)
        outer_layout.setSpacing(0)

        outer_layout.addStretch(1)

        card = QFrame()
        self.central_card = card
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(24)
        card_layout.setAlignment(Qt.AlignCenter)

        intro_label = QLabel("Selecciona un módulo para continuar")
        intro_label.setFont(body_font(14))
        intro_label.setAlignment(Qt.AlignCenter)
        self.intro_label = intro_label
        card_layout.addWidget(intro_label)

        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(20)
        self.create_main_buttons(buttons_layout)
        card_layout.addLayout(buttons_layout)

        self.btn_open_login = QPushButton("🔐 Administración")
        self.btn_open_login.clicked.connect(self.open_login)
        self.btn_open_login.setMinimumHeight(46)
        self.btn_open_login.setMinimumWidth(260)
        self.btn_open_login.setCursor(Qt.PointingHandCursor)
        card_layout.addWidget(self.btn_open_login, alignment=Qt.AlignCenter)

        outer_layout.addWidget(card, alignment=Qt.AlignCenter)
        outer_layout.addStretch(2)

        self._update_background_theme()
        self._update_card_theme()
        return background

    def create_main_buttons(self, layout: QGridLayout) -> None:
        available = QGuiApplication.primaryScreen().availableGeometry()

        if available.width() >= 1920:
            btn_width, btn_height = 220, 140
            font_size = 16
        elif available.width() >= 1366:
            btn_width, btn_height = 184, 122
            font_size = 14
        else:
            btn_width, btn_height = 150, 100
            font_size = 12

        self.quick_access_buttons = []

        def add_button(
            row: int,
            col: int,
            title: str,
            description: str,
            icon: str,
            accent: str,
            callback,
            col_span: int = 1,
        ) -> QPushButton:
            button = QPushButton(f"{icon} {title}\n{description}")
            button.clicked.connect(callback)
            button.setMinimumSize(btn_width, btn_height)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setCursor(Qt.PointingHandCursor)
            button.setProperty("accentColor", accent)
            button.setProperty("fontSize", font_size)
            layout.addWidget(button, row, col, 1, col_span)
            self.quick_access_buttons.append(button)
            return button

        # Colores institucionales suaves de DUOC UC para los botones principales
        def get_soft_duoc_color(base_color, factor=0.85):
            """Crea una versión suave de un color mezclándolo con blanco"""
            base_color = base_color.lstrip('#')
            r, g, b = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))
            r = min(255, int(r + (255 - r) * (1 - factor)))
            g = min(255, int(g + (255 - g) * (1 - factor)))
            b = min(255, int(b + (255 - b) * (1 - factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
        
        # Colores suaves con buen contraste y agradables a la vista
        soft_blue = get_soft_duoc_color(DUOC_PRIMARY, 0.82)  # Azul institucional suave
        soft_yellow = get_soft_duoc_color(DUOC_SECONDARY, 0.88)  # Amarillo institucional suave
        soft_blue_alt = get_soft_duoc_color(DUOC_PRIMARY, 0.78)  # Azul alternativo más claro
        soft_yellow_alt = get_soft_duoc_color(DUOC_SECONDARY, 0.85)  # Amarillo alternativo

        self.btn_visitas = add_button(
            0,
            0,
            "Registrar Visitas",
            "Controla ingresos y salidas",
            "📋",
            soft_blue,
            self.open_visitas,
        )

        self.btn_visitantes = add_button(
            0,
            1,
            "Visitantes Actuales",
            "Revisa quién está en la sede",
            "👥",
            soft_yellow,
            self.open_visitantes,
        )

        self.btn_zonas = add_button(
            1,
            0,
            "Zonas",
            "Administra espacios y aforos",
            "🏢",
            soft_blue_alt,
            self.open_zonas,
        )

        self.btn_reportes = add_button(
            1,
            1,
            "Reportes",
            "Genera estadísticas y reportes",
            "📊",
            soft_yellow_alt,
            self.open_reportes,
        )

        self.btn_manual = add_button(
            2,
            0,
            "Manual de Usuario",
            "Consulta la guía de uso del sistema",
            "📖",
            soft_blue,
            self.open_manual,
        )

        self.btn_usuarios = add_button(
            2,
            1,
            "Usuarios",
            "Gestiona cuentas y permisos",
            "🛡️",
            soft_blue,
            self.open_usuarios,
        )
        self.btn_usuarios.setVisible(False)

        self._update_card_theme()

    # ------------------------------------------------------------------
    # Navegación entre vistas
    # ------------------------------------------------------------------

    def open_visitas(self) -> None:
        if not self.check_authentication():
            return
        self.navigation_manager.navigate_to("visitas")

    def open_visitantes(self) -> None:
        if not self.check_authentication():
            return
        self.navigation_manager.navigate_to("visitantes")

    def open_zonas(self) -> None:
        if not self.check_authentication():
            return
        self.navigation_manager.navigate_to("zonas")

    def open_reportes(self) -> None:
        if not self.check_authentication():
            return
        self.navigation_manager.navigate_to("reportes")

    def open_usuarios(self) -> None:
        if not self.check_authentication():
            return
        if not self.auth_manager.is_admin():
            QMessageBox.warning(
                self,
                "Acceso Denegado",
                "Solo los administradores pueden gestionar usuarios.",
            )
            return

        self.navigation_manager.navigate_to("usuarios")

    def open_manual(self) -> None:
        """Abre el manual de usuario"""
        try:
            from core.help_dialog import HelpDialog
            help_dialog = HelpDialog(self)
            help_dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el manual de usuario:\n{str(e)}"
            )

    def go_to_main(self) -> None:
        self.navigation_manager.navigate_to("main")

    def on_view_changed(self, view_name: str) -> None:
        self.current_view = view_name
        if hasattr(self, "home_button"):
            self.home_button.setVisible(view_name != "main")

        titles = {
            "main": "VisitaSegura - Menú Principal",
            "visitas": "VisitaSegura - Registro de Visitas",
            "visitantes": "VisitaSegura - Gestión de Visitantes",
            "zonas": "VisitaSegura - Gestión de Zonas",
            "reportes": "VisitaSegura - Reportes y Estadísticas",
            "usuarios": "VisitaSegura - Gestión de Usuarios",
        }
        self.setWindowTitle(titles.get(view_name, "VisitaSegura"))

