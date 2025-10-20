import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QSizePolicy, QToolBar, QPushButton,
    QLabel, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QPalette, QColor, QGuiApplication, QFont, QPixmap

try:
    from core.login_window import LoginDialog
    from core.visitor_list import VisitorListWidget
    from core.views import VisitasView, ZonasView, ReportesView, UsuariosView
    from core.navigation_manager import NavigationManager
    from core.auth_manager import AuthManager
except ImportError:
    from login_window import LoginDialog
    from visitor_list import VisitorListWidget
    from views import VisitasView, ZonasView, ReportesView, UsuariosView
    from navigation_manager import NavigationManager
    from auth_manager import AuthManager

# Tema institucional Duoc UC
try:
    from core.theme import (
        DUOC_PRIMARY, DUOC_SECONDARY, DUOC_SUCCESS, DUOC_DANGER, DUOC_INFO,
        darken_color as duoc_darken, get_standard_button_style
    )
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Nombre de la ventana
        self.setWindowTitle("VisitaSegura")
        
        # Configuración para persistencia
        self.settings = QSettings("VisitaSegura", "Settings")
        
        # Estado inicial del tema (cargar desde configuración)
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)
        
        # Inicializar el sistema de navegación
        self.navigation_manager = NavigationManager(self)
        
        # Inicializar el sistema de autenticación
        self.auth_manager = AuthManager()
        
        self.current_view = "main"  # Vista principal por defecto

        # === Tamaño inicial responsivo y centrado ===
        available = QGuiApplication.primaryScreen().availableGeometry()
        
        # Calcular tamaño responsivo basado en la resolución de pantalla
        if available.width() >= 1920:  # Pantallas grandes (Full HD+)
            w = int(available.width() * 0.95)
            h = int(available.height() * 0.95)
            min_w, min_h = 1400, 900
        elif available.width() >= 1366:  # Pantallas medianas (HD+)
            w = int(available.width() * 0.95)
            h = int(available.height() * 0.95)
            min_w, min_h = 1200, 800
        else:  # Pantallas pequeñas
            w = int(available.width() * 0.95)
            h = int(available.height() * 0.95)
            min_w, min_h = 1000, 700
        
        self.resize(w, h)
        self.setMinimumSize(min_w, min_h)
        
        # Centrar ventana
        self.move(available.center() - self.rect().center())
        
        # Configurar redimensionamiento responsivo
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # === Barra de herramientas con navegación y tema ===
        toolbar = QToolBar("Navegación")
        self.addToolBar(toolbar)
        toolbar.setMovable(False)   # evita que se arrastre
        toolbar.setFloatable(False) # evita que se desacople 

        # Botón de inicio
        self.home_action = QAction("🏠 Inicio", self)
        self.home_action.triggered.connect(self.go_to_main)
        self.home_action.setVisible(False)  # Oculto inicialmente
        toolbar.addAction(self.home_action)

        # Separador
        toolbar.addSeparator()

        # == Damos espacio ===
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Botón de tema
        self.theme_action = QAction("🌙 Modo oscuro", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)

        # === Sistema de navegación con widget apilado ===
        self.stacked_widget = QStackedWidget()
        self.navigation_manager.set_stacked_widget(self.stacked_widget)
        
        # Crear y registrar todas las vistas
        self.setup_views()
        
        # Conectar señales del sistema de navegación
        self.navigation_manager.view_changed.connect(self.on_view_changed)
        self.navigation_manager.theme_changed.connect(self.on_theme_changed)
        
        self.setCentralWidget(self.stacked_widget)
        
        # Aplicar tema inicial
        self.apply_theme()
    
    def setup_views(self):
        """Configura y registra todas las vistas del sistema"""
        # Vista principal (menú de inicio)
        main_view = self.create_main_view()
        self.navigation_manager.register_view("main", main_view)
        
        # Vista de visitas
        visitas_view = VisitasView(self)
        self.navigation_manager.register_view("visitas", visitas_view)
        
        # Vista de visitantes (sistema completo)
        visitor_view = VisitorListWidget(self, self.auth_manager)
        self.navigation_manager.register_view("visitantes", visitor_view)
        
        # Vista de zonas
        zonas_view = ZonasView(self)
        self.navigation_manager.register_view("zonas", zonas_view)
        
        # Vista de reportes
        reportes_view = ReportesView(self, self.auth_manager)
        self.navigation_manager.register_view("reportes", reportes_view)
        
        # Vista de usuarios (solo para administradores)
        usuarios_view = UsuariosView(self, self.auth_manager)
        self.navigation_manager.register_view("usuarios", usuarios_view)
        
        # Establecer la vista principal como inicial
        self.navigation_manager.navigate_to("main")
    
    def create_main_view(self):
        """Crea la vista principal con el menú de inicio"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título principal
        title_label = QLabel("VisitaSegura")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Sistema de Gestión de Visitas Para La sede de San Bernardo")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # Logo de Duoc
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

        # Espaciador
        spacer1 = QWidget()
        spacer1.setFixedHeight(30)
        layout.addWidget(spacer1)

        # Grid de botones principales
        buttons_frame = QFrame()
        buttons_layout = QGridLayout(buttons_frame)
        buttons_layout.setSpacing(20)

        # Crear botones para las diferentes secciones
        self.create_main_buttons(buttons_layout)

        layout.addWidget(buttons_frame, alignment=Qt.AlignCenter)

        # Espaciador final
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(spacer2)

        # Botón de login en la parte inferior
        self.btn_open_login = QPushButton("🔐 Administración")
        self.btn_open_login.clicked.connect(self.open_login)
        self.btn_open_login.setMinimumSize(200, 50)  # Cambié de setFixedSize a setMinimumSize
        self.btn_open_login.setMaximumHeight(50)    # Mantener altura fija
        self.btn_open_login.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Expandir horizontalmente
        self.btn_open_login.setStyleSheet(get_standard_button_style("#6c757d"))
        layout.addWidget(self.btn_open_login, alignment=Qt.AlignCenter)
        
        return main_widget

    def create_main_buttons(self, layout):
        """Crea los botones principales para las diferentes secciones"""
        # Obtener tamaño de pantalla para hacer botones responsivos
        available = QGuiApplication.primaryScreen().availableGeometry()
        
        # Calcular tamaño de botones basado en la resolución
        if available.width() >= 1920:
            btn_width, btn_height = 220, 140
            font_size = 16
        elif available.width() >= 1366:
            btn_width, btn_height = 184, 122
            font_size = 14
        else:
            btn_width, btn_height = 150, 100
            font_size = 12
        
        # Botón de Visitas
        self.btn_visitas = QPushButton("📋 Registrar Visitas")
        self.btn_visitas.clicked.connect(self.open_visitas)
        self.btn_visitas.setMinimumSize(btn_width, btn_height)
        self.btn_visitas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_visitas.setStyleSheet(self.get_button_style(DUOC_PRIMARY, font_size))
        layout.addWidget(self.btn_visitas, 0, 0)

        # Botón de Visitantes
        self.btn_visitantes = QPushButton("👥 Visitantes Actuales")
        self.btn_visitantes.clicked.connect(self.open_visitantes)
        self.btn_visitantes.setMinimumSize(btn_width, btn_height)
        self.btn_visitantes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_visitantes.setStyleSheet(self.get_button_style(DUOC_SECONDARY, font_size))
        layout.addWidget(self.btn_visitantes, 0, 1)

        # Botón de Zonas
        self.btn_zonas = QPushButton("🏢 Zonas")
        self.btn_zonas.clicked.connect(self.open_zonas)
        self.btn_zonas.setMinimumSize(btn_width, btn_height)
        self.btn_zonas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_zonas.setStyleSheet(self.get_button_style(DUOC_SECONDARY, font_size))
        layout.addWidget(self.btn_zonas, 1, 0)

        # Botón de Reportes
        self.btn_reportes = QPushButton("📊 Reportes")
        self.btn_reportes.clicked.connect(self.open_reportes)
        self.btn_reportes.setMinimumSize(btn_width, btn_height)
        self.btn_reportes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_reportes.setStyleSheet(self.get_button_style(DUOC_PRIMARY, font_size))
        layout.addWidget(self.btn_reportes, 1, 1)

        # Botón de Usuarios (solo para administradores)
        self.btn_usuarios = QPushButton("👥 Usuarios")
        self.btn_usuarios.clicked.connect(self.open_usuarios)
        self.btn_usuarios.setMinimumSize(btn_width, btn_height)
        self.btn_usuarios.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_usuarios.setStyleSheet(self.get_button_style("#6f42c1", font_size))  # Color púrpura para diferenciarlo
        self.btn_usuarios.setVisible(False)  # Oculto por defecto
        layout.addWidget(self.btn_usuarios, 2, 0, 1, 2)  # Ocupa ambas columnas

    def get_button_style(self, color, font_size=16):
        """Retorna el estilo CSS para los botones principales"""
        # Usar el sistema estandarizado pero con tamaño de fuente personalizado
        base_style = get_standard_button_style(color)
        # Reemplazar el font-size en el estilo base
        return base_style.replace("font-size: 14px;", f"font-size: {font_size}px;")

    # Ya usamos duoc_darken desde core.theme

    def open_visitas(self):
        """Abre la sección de visitas"""
        if not self.check_authentication():
            return
        print("Abriendo sección de Visitas")
        self.navigation_manager.navigate_to("visitas")

    def open_visitantes(self):
        """Abre la sección de visitantes"""
        if not self.check_authentication():
            return
        print("Abriendo sección de Visitantes")
        self.navigation_manager.navigate_to("visitantes")

    def open_zonas(self):
        """Abre la sección de zonas"""
        if not self.check_authentication():
            return
        print("Abriendo sección de Zonas")
        self.navigation_manager.navigate_to("zonas")

    def open_reportes(self):
        """Abre la sección de reportes"""
        if not self.check_authentication():
            return
        print("Abriendo sección de Reportes")
        self.navigation_manager.navigate_to("reportes")
    
    def open_usuarios(self):
        """Abre la sección de usuarios (solo administradores)"""
        if not self.check_authentication():
            return
        
        # Verificar que sea administrador
        if not self.auth_manager.is_admin():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Acceso Denegado", 
                "Solo los administradores pueden gestionar usuarios."
            )
            return
        
        print("Abriendo sección de Usuarios")
        self.navigation_manager.navigate_to("usuarios")
    
    def go_to_main(self):
        """Regresa al menú principal"""
        self.navigation_manager.navigate_to("main")
    
    def on_view_changed(self, view_name):
        """Maneja el cambio de vista"""
        self.current_view = view_name
        self.home_action.setVisible(view_name != "main")
        
        # Actualizar título de la ventana
        if view_name == "main":
            self.setWindowTitle("VisitaSegura - Menú Principal")
        elif view_name == "visitas":
            self.setWindowTitle("VisitaSegura - Registro de Visitas")
        elif view_name == "visitantes":
            self.setWindowTitle("VisitaSegura - Gestión de Visitantes")
        elif view_name == "zonas":
            self.setWindowTitle("VisitaSegura - Gestión de Zonas")
        elif view_name == "reportes":
            self.setWindowTitle("VisitaSegura - Reportes y Estadísticas")
        elif view_name == "usuarios":
            self.setWindowTitle("VisitaSegura - Gestión de Usuarios")
    
    def on_theme_changed(self, dark_mode):
        """Maneja el cambio de tema"""
        self.dark_mode = dark_mode
        self.apply_theme()
        
        # Aplicar tema a la vista de usuarios si existe
        usuarios_view = self.navigation_manager.get_view("usuarios")
        if usuarios_view:
            usuarios_view.set_theme(dark_mode)
        
        # Aplicar tema a la vista de reportes si existe
        reportes_view = self.navigation_manager.get_view("reportes")
        if reportes_view:
            reportes_view.update_auth_manager(self.auth_manager)

    def check_authentication(self):
        """Verifica si el usuario está autenticado"""
        if self.auth_manager.is_logged_in():
            return True
        
        # Si no está autenticado, mostrar ventana de login
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            "🔐 Autenticación Requerida", 
            "Debe iniciar sesión para acceder a esta función.\n\n¿Desea iniciar sesión ahora?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.open_login()
            return self.auth_manager.is_logged_in()
        
        return False

    def open_login(self):
        print("🔍 Intentando abrir ventana de login...")
        try:
            login = LoginDialog(self.dark_mode)
            print("✅ Ventana de login creada correctamente")
            result = login.exec()
            print(f"🔍 Resultado del login: {result}")
            if result:
                print("✅ Login aceptado")
                # Actualizar el estado de autenticación
                self.auth_manager = login.get_auth_manager()
                self.update_ui_for_authentication()
            else:
                print("❌ Login cancelado")
        except Exception as e:
            print(f"❌ Error al abrir ventana de login: {e}")
            import traceback
            traceback.print_exc()
    
    def update_ui_for_authentication(self):
        """Actualiza la UI según el estado de autenticación"""
        if self.auth_manager.is_logged_in():
            user = self.auth_manager.get_current_user()
            # Cambiar el texto del botón de administración
            self.btn_open_login.setText(f"👤 {user['full_name']} (Cerrar Sesión)")
            self.btn_open_login.clicked.disconnect()
            self.btn_open_login.clicked.connect(self.logout)
            
            # Mostrar/ocultar botón de usuarios según el rol
            self.btn_usuarios.setVisible(self.auth_manager.is_admin())
            
            # Actualizar el AuthManager en la vista de usuarios
            usuarios_view = self.navigation_manager.get_view("usuarios")
            if usuarios_view:
                usuarios_view.update_auth_manager(self.auth_manager)
                usuarios_view.set_theme(self.dark_mode)
            
            # Actualizar el AuthManager en la vista de reportes
            reportes_view = self.navigation_manager.get_view("reportes")
            if reportes_view:
                reportes_view.update_auth_manager(self.auth_manager)
        else:
            self.btn_open_login.setText("🔐 Administración")
            self.btn_open_login.clicked.disconnect()
            self.btn_open_login.clicked.connect(self.open_login)
            
            # Ocultar botón de usuarios cuando no hay sesión
            self.btn_usuarios.setVisible(False)
        
        # Ajustar el tamaño del botón al contenido
        self.btn_open_login.adjustSize()
    
    def logout(self):
        """Cierra la sesión del usuario"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            "🚪 Cerrar Sesión", 
            "¿Está seguro de que desea cerrar la sesión?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.auth_manager.logout()
            self.update_ui_for_authentication()
            QMessageBox.information(
                self, 
                "✅ Sesión Cerrada", 
                "Ha cerrado sesión correctamente."
            )

    def apply_theme(self):
        """Aplica el tema actual (claro u oscuro)"""
        if self.dark_mode:
            palette = QPalette()
            # === Colores modo oscuro ===
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(40, 40, 40))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(DUOC_SECONDARY))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.theme_action.setText("☀️ Modo claro")
        else:
            # Restaurar tema claro (default del estilo actual)
            palette = QApplication.style().standardPalette()
            # Acentos institucionals
            palette.setColor(QPalette.Highlight, QColor(DUOC_PRIMARY))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            self.theme_action.setText("🌙 Modo oscuro")

        QApplication.instance().setPalette(palette)
    
    def toggle_theme(self):
        """Cambia entre tema claro y oscuro."""
        self.dark_mode = not self.dark_mode
        
        # Guardar el estado en configuración
        self.settings.setValue("dark_mode", self.dark_mode)
        
        # Propagar el cambio de tema a través del sistema de navegación
        self.navigation_manager.set_theme(self.dark_mode)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())