from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from .dependencies import DUOC_PRIMARY, DUOC_SECONDARY, get_standard_button_style


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
        else:
            palette = QApplication.style().standardPalette()
            palette.setColor(QPalette.Highlight, QColor(DUOC_PRIMARY))
            palette.setColor(QPalette.HighlightedText, Qt.white)

        QApplication.instance().setPalette(palette)
        self._update_toolbar_theme()
        self._update_background_theme()
        self._update_card_theme()

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

        visitor_view = self.navigation_manager.get_view("visitantes")
        if visitor_view and hasattr(visitor_view, "set_theme"):
            visitor_view.set_theme(dark_mode)

        visitas_view = self.navigation_manager.get_view("visitas")
        if visitas_view and hasattr(visitas_view, "set_theme"):
            visitas_view.set_theme(dark_mode)

        zonas_view = self.navigation_manager.get_view("zonas")
        if zonas_view and hasattr(zonas_view, "set_theme"):
            zonas_view.set_theme(dark_mode)

        qr_dialog = getattr(self, "qr_dialog", None)
        if qr_dialog and hasattr(qr_dialog, "set_theme"):
            qr_dialog.set_theme(dark_mode)

        reportes_view = self.navigation_manager.get_view("reportes")
        if reportes_view:
            reportes_view.update_auth_manager(self.auth_manager)
        self._update_toolbar_theme()
        self._update_background_theme()
        self._update_card_theme()

    def _update_toolbar_theme(self) -> None:
        if not hasattr(self, "toolbar_header"):
            return

        if self.dark_mode:
            style = """
                QWidget#ToolbarContainer {
                    background-color: #1e1e1e;
                }
                QLabel#ToolbarTitle {
                    color: #f8f9fa;
                }
            """
            toggle_text = "☀️ Modo claro"
        else:
            style = """
                QWidget#ToolbarContainer {
                    background-color: #ffffff;
                }
                QLabel#ToolbarTitle {
                    color: #1f2933;
                }
            """
            toggle_text = "🌙 Modo oscuro"

        self.toolbar_header.setStyleSheet(style)
        if hasattr(self, "theme_toggle_button"):
            self.theme_toggle_button.setText(toggle_text)

    def _update_background_theme(self) -> None:
        if not hasattr(self, "background_widget"):
            return

        if self.dark_mode:
            self.background_widget.setStyleSheet("background-color: #1e2024;")
        else:
            self.background_widget.setStyleSheet("background-color: #f3f4f7;")

    def _update_card_theme(self) -> None:
        if not hasattr(self, "central_card"):
            return

        if self.dark_mode:
            card_style = """
                QFrame {
                    background-color: #252830;
                    border-radius: 28px;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    padding: 40px 48px;
                }
            """
            button_bg = "#2f3240"
            button_border = "rgba(255, 255, 255, 0.08)"
            text_color = "#f5f7fa"
        else:
            card_style = """
                QFrame {
                    background-color: #ffffff;
                    border-radius: 28px;
                    border: 1px solid rgba(0, 0, 0, 0.06);
                    padding: 40px 48px;
                }
            """
            button_bg = "#ffffff"
            button_border = "rgba(0, 0, 0, 0.08)"
            text_color = "#1f2933"

        self.central_card.setStyleSheet(card_style)

        if hasattr(self, "intro_label"):
            intro_color = "#e2e8f0" if self.dark_mode else "#4a5568"
            self.intro_label.setStyleSheet(f"color: {intro_color}; font-size: 14px;")

        if hasattr(self, "quick_access_buttons"):
            for button in self.quick_access_buttons:
                accent = button.property("accentColor") or DUOC_PRIMARY
                font_size = button.property("fontSize") or 14
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {button_bg};
                        border-radius: 18px;
                        border: 1px solid {button_border};
                        padding: 16px 20px;
                        text-align: left;
                        font-size: {font_size}px;
                        font-weight: 600;
                        color: {text_color};
                    }}
                    QPushButton:hover {{
                        border: 1px solid {accent};
                    }}
                    """
                )

        if hasattr(self, "btn_open_login"):
            if self.dark_mode:
                self.btn_open_login.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {DUOC_PRIMARY};
                        color: #ffffff;
                        border-radius: 18px;
                        padding: 12px 24px;
                        font-size: 14px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(0, 58, 112, 0.8);
                    }}
                    """
                )
            else:
                self.btn_open_login.setStyleSheet(
                    get_standard_button_style(DUOC_PRIMARY).replace("padding: 10px 16px;", "padding: 12px 20px;")
                )

