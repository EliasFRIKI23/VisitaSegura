import sys
from PySide6.QtCore import Qt, QSettings
from core.visitor_list import VisitorListWidget
from PySide6.QtGui import QAction, QPalette, QColor, QGuiApplication, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,

    QVBoxLayout, QListWidget, QTextEdit,
    QSplitter, QSizePolicy, QToolBar,
    QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPalette, QColor, QGuiApplication

from core.login_window import LoginWindow
from core.visitor_list import VisitorListWidget



try:
    from core.login_window import LoginWindow
except ImportError:
    from login_window import LoginWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Nombre de la ventana
        self.setWindowTitle("VisitaSegura")
        # Estado inicial del tema
        self.dark_mode = False

        # === Tamaño inicial relativo y centrado (robusto) ===
        available = QGuiApplication.primaryScreen().availableGeometry()
        w = int(available.width() * 0.8)
        h = int(available.height() * 0.8)
        self.resize(w, h)
        # Centrar ventana
        self.move(available.center() - self.rect().center())

        # Tamaño mínimo razonable
        self.setMinimumSize(900, 560)

        # === Contenido con layouts y splitter (adaptativo) ===
        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)


        # === Barra de herramientas con botón de tema ===
        toolbar = QToolBar("Opciones")
        self.addToolBar(toolbar)
        toolbar.setMovable(False)   # evita que se arrastre
        toolbar.setFloatable(False) # evita que se desacople 

        # == Damos espacio ===
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self.theme_action = QAction("🌙 Modo oscuro", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)
        
        # === Widget apilado para las diferentes páginas ===
        self.stacked_widget = QStackedWidget()
        
        # Página de visitantes
        self.visitor_widget = VisitorListWidget()
        self.stacked_widget.addWidget(self.visitor_widget)
        
        # Páginas placeholder para otras secciones
        self.create_placeholder_pages()
        
        # Splitter para que ambas columnas se adapten
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.stacked_widget)
        splitter.setStretchFactor(0, 1)  # sidebar
        splitter.setStretchFactor(1, 3)  # contenido
        splitter.setSizes([int(w * 0.25), int(w * 0.75)])


        # === Contenido principal con distribución de botones ===
        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(20)

        # Título principal
        title_label = QLabel("VisitaSegura")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Sistema de Gestión de Visitas Para La sede de San Bernardo")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(subtitle_label)

        # Logo de Duoc
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            # Redimensionar el logo manteniendo la proporción
            scaled_pixmap = logo_pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # Si no se puede cargar la imagen, mostrar texto alternativo
            logo_label.setText("Logo Duoc UC")
            logo_font = QFont()
            logo_font.setPointSize(14)
            logo_font.setBold(True)
            logo_label.setFont(logo_font)
        
        logo_label.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(logo_label)

        # Espaciador
        spacer1 = QWidget()
        spacer1.setFixedHeight(30)
        root_layout.addWidget(spacer1)

        # Grid de botones principales
        buttons_frame = QFrame()
        buttons_layout = QGridLayout(buttons_frame)
        buttons_layout.setSpacing(20)

        # Crear botones para las diferentes secciones
        self.create_main_buttons(buttons_layout)

        root_layout.addWidget(buttons_frame, alignment=Qt.AlignCenter)

        # Espaciador final
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        root_layout.addWidget(spacer2)

        # Botón de login en la parte inferior
        self.btn_open_login = QPushButton("🔐 Administración")
        self.btn_open_login.clicked.connect(self.open_login)
        print("✅ Botón de administración configurado y conectado")
        self.btn_open_login.setFixedSize(200, 50)
        self.btn_open_login.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        root_layout.addWidget(self.btn_open_login, alignment=Qt.AlignCenter)

        root_layout.addWidget(splitter)
        self.setCentralWidget(central)
        

        # Aplicar tema inicial
        self.apply_theme()

    def create_main_buttons(self, layout):
        """Crea los botones principales para las diferentes secciones"""
        # Botón de Visitas
        self.btn_visitas = QPushButton("📋 Registrar Visitas")
        self.btn_visitas.clicked.connect(self.open_visitas)
        self.btn_visitas.setFixedSize(184, 122)  # Aumentado en ~2%
        self.btn_visitas.setStyleSheet(self.get_button_style("#007bff"))
        layout.addWidget(self.btn_visitas, 0, 0)

        # Botón de Visitantes
        self.btn_visitantes = QPushButton("👥 Visitantes Actuales")
        self.btn_visitantes.clicked.connect(self.open_visitantes)
        self.btn_visitantes.setFixedSize(184, 122)  # Aumentado en ~2%
        self.btn_visitantes.setStyleSheet(self.get_button_style("#28a745"))
        layout.addWidget(self.btn_visitantes, 0, 1)

        # Botón de Zonas
        self.btn_zonas = QPushButton("🏢 Zonas")
        self.btn_zonas.clicked.connect(self.open_zonas)
        self.btn_zonas.setFixedSize(184, 122)  # Aumentado en ~2%
        self.btn_zonas.setStyleSheet(self.get_button_style("#ffc107"))
        layout.addWidget(self.btn_zonas, 1, 0)

        # Botón de Reportes
        self.btn_reportes = QPushButton("📊 Reportes")
        self.btn_reportes.clicked.connect(self.open_reportes)
        self.btn_reportes.setFixedSize(184, 122)  # Aumentado en ~2%
        self.btn_reportes.setStyleSheet(self.get_button_style("#dc3545"))
        layout.addWidget(self.btn_reportes, 1, 1)

    def get_button_style(self, color):
        """Retorna el estilo CSS para los botones principales"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """

    def darken_color(self, color, factor=0.2):
        """Oscurece un color hexadecimal"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def open_visitas(self):
        """Abre la sección de visitas"""
        print("Abriendo sección de Visitas")
        # Aquí puedes agregar la lógica para abrir la ventana de visitas
        # Por ejemplo: self.visitas_window = VisitasWindow()

    def open_visitantes(self):
        """Abre la sección de visitantes"""
        print("Abriendo sección de Visitantes")
        # Aquí puedes agregar la lógica para abrir la ventana de visitantes

    def open_zonas(self):
        """Abre la sección de zonas"""
        print("Abriendo sección de Zonas")
        # Aquí puedes agregar la lógica para abrir la ventana de zonas

    def open_reportes(self):
        """Abre la sección de reportes"""
        print("Abriendo sección de Reportes")
        # Aquí puedes agregar la lógica para abrir la ventana de reportes


    def open_login(self):
        login = LoginWindow()
        if login.exec():
            print("Login aceptado")

    
    def toggle_theme(self):
        """Cambia entre tema claro y oscuro."""
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            palette = QPalette()
            # === Colores modo oscuro ===
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.theme_action.setText("☀️ Modo claro")
        else:
            # Restaurar tema claro (default del estilo actual)
            palette = QApplication.style().standardPalette()
            self.theme_action.setText("🌙 Modo oscuro")

        QApplication.instance().setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
