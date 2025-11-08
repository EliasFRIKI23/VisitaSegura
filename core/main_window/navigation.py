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
    QToolBar,
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


class NavigationMixin:
    """Encapsula la configuración de vistas y acciones de navegación."""

    def setup_toolbar(self) -> None:
        toolbar = QToolBar("Navegación")
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)

        self.home_action = QAction("🏠 Inicio", self)
        self.home_action.triggered.connect(self.go_to_main)
        self.home_action.setVisible(False)
        toolbar.addAction(self.home_action)

        toolbar.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self.theme_action = QAction("🌙 Modo oscuro", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)

    # ------------------------------------------------------------------
    # Configuración de vistas
    # ------------------------------------------------------------------

    def setup_views(self) -> None:
        main_view = self.create_main_view()
        self.navigation_manager.register_view("main", main_view)

        visitas_view = VisitasView(self, self.auth_manager)
        self.navigation_manager.register_view("visitas", visitas_view)

        visitor_view = VisitorListWidget(self, self.auth_manager)
        self.navigation_manager.register_view("visitantes", visitor_view)

        zonas_view = ZonasView(self)
        self.navigation_manager.register_view("zonas", zonas_view)

        reportes_view = ReportesView(self, self.auth_manager)
        self.navigation_manager.register_view("reportes", reportes_view)

        usuarios_view = UsuariosView(self, self.auth_manager)
        self.navigation_manager.register_view("usuarios", usuarios_view)

        self.navigation_manager.navigate_to("main")

    def create_main_view(self) -> QWidget:
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title_label = QLabel("VisitaSegura")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("Sistema de Gestión de Visitas Para La sede de San Bernardo")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("Logo Duoc UC")
            logo_font = QFont()
            logo_font.setPointSize(14)
            logo_font.setBold(True)
            logo_label.setFont(logo_font)

        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        spacer1 = QWidget()
        spacer1.setFixedHeight(30)
        layout.addWidget(spacer1)

        buttons_frame = QFrame()
        buttons_layout = QGridLayout(buttons_frame)
        buttons_layout.setSpacing(20)
        self.create_main_buttons(buttons_layout)
        layout.addWidget(buttons_frame, alignment=Qt.AlignCenter)

        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(spacer2)

        self.btn_open_login = QPushButton("🔐 Administración")
        self.btn_open_login.clicked.connect(self.open_login)
        self.btn_open_login.setMinimumSize(200, 50)
        self.btn_open_login.setMaximumHeight(50)
        self.btn_open_login.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_open_login.setStyleSheet(get_standard_button_style("#6c757d"))
        layout.addWidget(self.btn_open_login, alignment=Qt.AlignCenter)

        return main_widget

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

        self.btn_visitas = QPushButton("📋 Registrar Visitas")
        self.btn_visitas.clicked.connect(self.open_visitas)
        self.btn_visitas.setMinimumSize(btn_width, btn_height)
        self.btn_visitas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_visitas.setStyleSheet(self.get_button_style(DUOC_PRIMARY, font_size))
        layout.addWidget(self.btn_visitas, 0, 0)

        self.btn_visitantes = QPushButton("👥 Visitantes Actuales")
        self.btn_visitantes.clicked.connect(self.open_visitantes)
        self.btn_visitantes.setMinimumSize(btn_width, btn_height)
        self.btn_visitantes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_visitantes.setStyleSheet(self.get_button_style(DUOC_SECONDARY, font_size))
        layout.addWidget(self.btn_visitantes, 0, 1)

        self.btn_zonas = QPushButton("🏢 Zonas")
        self.btn_zonas.clicked.connect(self.open_zonas)
        self.btn_zonas.setMinimumSize(btn_width, btn_height)
        self.btn_zonas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_zonas.setStyleSheet(self.get_button_style(DUOC_SECONDARY, font_size))
        layout.addWidget(self.btn_zonas, 1, 0)

        self.btn_reportes = QPushButton("📊 Reportes")
        self.btn_reportes.clicked.connect(self.open_reportes)
        self.btn_reportes.setMinimumSize(btn_width, btn_height)
        self.btn_reportes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_reportes.setStyleSheet(self.get_button_style(DUOC_PRIMARY, font_size))
        layout.addWidget(self.btn_reportes, 1, 1)

        self.btn_usuarios = QPushButton("👥 Usuarios")
        self.btn_usuarios.clicked.connect(self.open_usuarios)
        self.btn_usuarios.setMinimumSize(btn_width, btn_height)
        self.btn_usuarios.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_usuarios.setStyleSheet(self.get_button_style("#6f42c1", font_size))
        self.btn_usuarios.setVisible(False)
        layout.addWidget(self.btn_usuarios, 2, 0, 1, 2)

    def get_button_style(self, color: str, font_size: int = 16) -> str:
        base_style = get_standard_button_style(color)
        return base_style.replace("font-size: 14px;", f"font-size: {font_size}px;")

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

    def go_to_main(self) -> None:
        self.navigation_manager.navigate_to("main")

    def on_view_changed(self, view_name: str) -> None:
        self.current_view = view_name
        self.home_action.setVisible(view_name != "main")

        titles = {
            "main": "VisitaSegura - Menú Principal",
            "visitas": "VisitaSegura - Registro de Visitas",
            "visitantes": "VisitaSegura - Gestión de Visitantes",
            "zonas": "VisitaSegura - Gestión de Zonas",
            "reportes": "VisitaSegura - Reportes y Estadísticas",
            "usuarios": "VisitaSegura - Gestión de Usuarios",
        }
        self.setWindowTitle(titles.get(view_name, "VisitaSegura"))

