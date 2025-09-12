import sys
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

        # Barra lateral para mejor navegación
        self.sidebar = QListWidget()
        self.sidebar.addItems(["Visitas", "Visitantes", "Zonas", "Reportes"])
        self.sidebar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.sidebar.currentRowChanged.connect(self.change_page)

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

        root_layout.addWidget(splitter)
        self.setCentralWidget(central)
        
        # Establecer la página inicial
        self.sidebar.setCurrentRow(1)  # Visitantes

    def create_placeholder_pages(self):
        """Crea páginas placeholder para las secciones no implementadas"""
        # Página de Visitas
        visits_page = QTextEdit()
        visits_page.setPlaceholderText("Módulo de Visitas - En desarrollo...")
        visits_page.setReadOnly(True)
        self.stacked_widget.addWidget(visits_page)
        
        # Página de Zonas
        zones_page = QTextEdit()
        zones_page.setPlaceholderText("Módulo de Zonas - En desarrollo...")
        zones_page.setReadOnly(True)
        self.stacked_widget.addWidget(zones_page)
        
        # Página de Reportes
        reports_page = QTextEdit()
        reports_page.setPlaceholderText("Módulo de Reportes - En desarrollo...")
        reports_page.setReadOnly(True)
        self.stacked_widget.addWidget(reports_page)
    
    def change_page(self, index):
        """Cambia la página mostrada según la selección del sidebar"""
        if index >= 0 and index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)

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
