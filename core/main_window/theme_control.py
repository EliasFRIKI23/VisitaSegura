from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from .dependencies import DUOC_PRIMARY, DUOC_SECONDARY


class ThemeMixin:
    """Lógica relacionada con la aplicación de temas."""

    def apply_theme(self) -> None:
        if self.dark_mode:
            palette = QPalette()
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
            palette = QApplication.style().standardPalette()
            palette.setColor(QPalette.Highlight, QColor(DUOC_PRIMARY))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            self.theme_action.setText("🌙 Modo oscuro")

        QApplication.instance().setPalette(palette)

    def toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self.navigation_manager.set_theme(self.dark_mode)

    def on_theme_changed(self, dark_mode: bool) -> None:
        self.dark_mode = dark_mode
        self.apply_theme()

        usuarios_view = self.navigation_manager.get_view("usuarios")
        if usuarios_view:
            usuarios_view.set_theme(dark_mode)

        reportes_view = self.navigation_manager.get_view("reportes")
        if reportes_view:
            reportes_view.update_auth_manager(self.auth_manager)

