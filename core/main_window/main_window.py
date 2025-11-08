from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QSizePolicy
from PySide6.QtCore import QSettings
from PySide6.QtGui import QGuiApplication

from .auth import AuthMixin
from .dependencies import AuthManager, NavigationManager
from .navigation import NavigationMixin
from .theme_control import ThemeMixin


class MainWindow(QMainWindow, NavigationMixin, AuthMixin, ThemeMixin):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VisitaSegura")
        self.settings = QSettings("VisitaSegura", "Settings")
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)

        self.navigation_manager = NavigationManager(self)
        self.auth_manager = AuthManager()
        self.current_view = "main"

        self._configure_initial_geometry()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setup_toolbar()

        self.stacked_widget = QStackedWidget()
        self.navigation_manager.set_stacked_widget(self.stacked_widget)

        self.setup_views()

        self.navigation_manager.view_changed.connect(self.on_view_changed)
        self.navigation_manager.theme_changed.connect(self.on_theme_changed)

        self.setCentralWidget(self.stacked_widget)
        self.apply_theme()

    # ------------------------------------------------------------------
    # Configuración inicial
    # ------------------------------------------------------------------

    def _configure_initial_geometry(self) -> None:
        available = QGuiApplication.primaryScreen().availableGeometry()

        if available.width() >= 1920:
            w = int(available.width() * 0.95)
            h = int(available.height() * 0.95)
            min_w, min_h = 1400, 900
        elif available.width() >= 1366:
            w = int(available.width() * 0.95)
            h = int(available.height() * 0.95)
            min_w, min_h = 1200, 800
        else:
            w = int(available.width() * 0.95)
            h = int(available.height() * 0.95)
            min_w, min_h = 1000, 700

        self.resize(w, h)
        self.setMinimumSize(min_w, min_h)
        self.move(available.center() - self.rect().center())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

