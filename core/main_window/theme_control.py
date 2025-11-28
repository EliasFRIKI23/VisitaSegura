from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication
from core.ui.icon_loader import get_icon_for_emoji

from .dependencies import DUOC_PRIMARY, DUOC_SECONDARY, get_standard_button_style
from core.theme import (
    DUOC_BG_LIGHT, DUOC_BG_LIGHT_CARD, DUOC_BG_LIGHT_TOOLBAR, DUOC_BG_LIGHT_SECONDARY,
    DUOC_BG_DARK, DUOC_BG_DARK_CARD, DUOC_BG_DARK_TOOLBAR, DUOC_BG_DARK_SECONDARY,
    DUOC_LOGO_GOLD, DUOC_LOGO_BLUE, DUOC_LOGO_GRAY
)


class ThemeMixin:
    """Lógica relacionada con la aplicación de temas."""

    def apply_theme(self) -> None:
        if self.dark_mode:
            palette = QPalette()
            # Usar un fondo oscuro basado en el azul UC pero más claro para legibilidad
            palette.setColor(QPalette.Window, QColor(0x1a, 0x2f, 0x45))  # Variante más clara de #002138
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(0x15, 0x27, 0x38))  # Base un poco más oscura
            palette.setColor(QPalette.AlternateBase, QColor(0x20, 0x37, 0x4d))  # Alternativo basado en UC
            palette.setColor(QPalette.ToolTipBase, QColor(0x54, 0x65, 0x75))  # Usar el gris del logo
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(0x20, 0x37, 0x4d))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, QColor(0xf8, 0xb3, 0x1c))  # Amarillo DUOC
            palette.setColor(QPalette.Highlight, QColor(0xf8, 0xb3, 0x1c))  # Amarillo DUOC para highlights
            palette.setColor(QPalette.HighlightedText, QColor(0x00, 0x21, 0x38))  # Azul UC oscuro para texto sobre highlight
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
        self.update_theme_toggle()

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
            # Toolbar con fondo más claro que el fondo principal para contraste (como en modo claro)
            style = f"""
                QWidget#ToolbarContainer {{
                    background-color: {DUOC_BG_DARK_TOOLBAR};
                }}
                QLabel#ToolbarTitle {{
                    color: #f8f9fa;
                }}
            """
            toggle_text = "☀️ Modo claro"
        else:
            style = f"""
                QWidget#ToolbarContainer {{
                    background-color: {DUOC_BG_LIGHT_TOOLBAR};
                }}
                QLabel#ToolbarTitle {{
                    color: #1f2933;
                }}
            """
            toggle_text = "🌙 Modo oscuro"

        self.toolbar_header.setStyleSheet(style)
        if hasattr(self, "theme_toggle_button"):
            self.update_theme_toggle()

    def _update_background_theme(self) -> None:
        if not hasattr(self, "background_widget"):
            return

        if self.dark_mode:
            # Fondo oscuro basado en el azul UC (#002138) pero más claro
            self.background_widget.setStyleSheet(f"background-color: {DUOC_BG_DARK};")
        else:
            self.background_widget.setStyleSheet(f"background-color: {DUOC_BG_LIGHT_SECONDARY};")

    def _update_card_theme(self) -> None:
        if not hasattr(self, "central_card"):
            return

        if self.dark_mode:
            # Usar los colores exactos del logo para modo oscuro
            duoc_blue = DUOC_LOGO_BLUE  # Azul UC oscuro
            duoc_gold = DUOC_LOGO_GOLD  # Amarillo DUOC exacto
            duoc_logo_gray = DUOC_LOGO_GRAY  # Gris del logo católica
            card_style = f"""
                QFrame {{
                    background-color: {DUOC_BG_DARK_CARD};
                    border-radius: 28px;
                    border: 1px solid rgba(84, 101, 117, 0.25);
                    padding: 40px 48px;
                }}
            """
            button_bg = DUOC_BG_DARK_SECONDARY
            button_border = "rgba(84, 101, 117, 0.3)"
            text_color = "#f5f7fa"
        else:
            card_style = f"""
                QFrame {{
                    background-color: {DUOC_BG_LIGHT_CARD};
                    border-radius: 28px;
                    border: 1px solid rgba(0, 0, 0, 0.06);
                    padding: 40px 48px;
                }}
            """
            button_bg = DUOC_BG_LIGHT_CARD
            button_border = "rgba(0, 0, 0, 0.08)"
            text_color = "#1f2933"

        self.central_card.setStyleSheet(card_style)

        if hasattr(self, "intro_label"):
            if self.dark_mode:
                # Usar un color más claro y vibrante en modo oscuro
                intro_color = "#f8f9fa"
            else:
                intro_color = "#4a5568"
            self.intro_label.setStyleSheet(f"color: {intro_color}; font-size: 28px; font-weight: bold;")

        if hasattr(self, "card_shadow"):
            if self.dark_mode:
                # Sombra más sutil con tinte azul que complementa el fondo
                self.card_shadow.setColor(QColor(0, 33, 56, 220))  # Sombra basada en el azul UC
                self.card_shadow.setBlurRadius(60)
                self.card_shadow.setOffset(0, 32)
            else:
                self.card_shadow.setColor(QColor(0, 0, 0, 55))
                self.card_shadow.setBlurRadius(45)
                self.card_shadow.setOffset(0, 22)

        if hasattr(self, "quick_access_buttons"):
            # Función auxiliar para oscurecer colores (solo para los botones principales)
            def darken_color(color, factor=0.15):
                color = color.lstrip('#')
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                r = max(0, int(r * (1 - factor)))
                g = max(0, int(g * (1 - factor)))
                b = max(0, int(b * (1 - factor)))
                return f"#{r:02x}{g:02x}{b:02x}"

            def lighten_color(color, factor=0.15):
                color = color.lstrip('#')
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                r = min(255, int(r + (255 - r) * factor))
                g = min(255, int(g + (255 - g) * factor))
                b = min(255, int(b + (255 - b) * factor))
                return f"#{r:02x}{g:02x}{b:02x}"

            def is_dark_color(color) -> bool:
                color = color.lstrip('#')
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                # luminosidad perceptual
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                return luminance < 155
            
            for button in self.quick_access_buttons:
                accent = button.property("accentColor") or DUOC_PRIMARY
                font_size = button.property("fontSize") or 14
                
                if self.dark_mode:
                    # Usar los colores exactos del logo en modo oscuro
                    # Si el accent es el azul UC (#003A70 o similar), usar el azul oscuro del logo
                    # Si el accent es el amarillo DUOC, usar el amarillo exacto del logo
                    if accent == DUOC_PRIMARY or accent == "#003A70":
                        # Para botones azules, usar el azul UC oscuro del logo con texto claro
                        button_bg_color = DUOC_LOGO_BLUE
                        hover_bg = "#003350"
                        text_color_button = DUOC_LOGO_GOLD  # Texto amarillo DUOC sobre fondo azul UC
                    elif accent == DUOC_SECONDARY or "#FF" in accent.upper():
                        # Para botones amarillos, usar el amarillo DUOC exacto del logo
                        button_bg_color = DUOC_LOGO_GOLD
                        hover_bg = "#ffc640"
                        text_color_button = DUOC_LOGO_BLUE  # Texto azul UC oscuro sobre fondo amarillo DUOC
                    else:
                        # Fallback para otros colores
                        button_bg_color = accent
                        hover_bg = lighten_color(accent, 0.1)
                        text_color_button = "#f8fafc"
                    border_color_btn = "transparent"
                else:
                    button_bg_color = accent
                    if is_dark_color(accent):
                        hover_bg = lighten_color(accent, 0.12)
                        text_color_button = "#f8fafc"
                    else:
                        hover_bg = darken_color(accent, 0.12)
                        text_color_button = "#0f172a"
                    border_color_btn = "transparent"
                
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {button_bg_color};
                        border-radius: 18px;
                        border: 1px solid {border_color_btn};
                        padding: 16px 20px;
                        text-align: left;
                        font-size: {font_size}px;
                        font-weight: bold;
                        color: {text_color_button};
                    }}
                    QPushButton:hover {{
                        background-color: {hover_bg};
                        border: 1px solid {darken_color(accent, 0.2) if not self.dark_mode else accent};
                    }}
                    QPushButton:pressed {{
                        background-color: {darken_color(accent, 0.2) if not self.dark_mode else button_bg};
                    }}
                    """
                )

        if hasattr(self, "btn_open_login"):
            if self.dark_mode:
                # Botón con el amarillo DUOC para destacar en modo oscuro
                self.btn_open_login.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {DUOC_LOGO_GOLD};
                        color: {DUOC_LOGO_BLUE};
                        border-radius: 18px;
                        padding: 12px 24px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #ffc640;
                    }}
                    """
                )
            else:
                self.btn_open_login.setStyleSheet(
                    get_standard_button_style(DUOC_PRIMARY).replace("padding: 10px 16px;", "padding: 12px 20px;")
                )

    def update_theme_toggle(self) -> None:
        """Actualiza el botón de toggle de tema con icono y texto"""
        if not hasattr(self, "theme_toggle_button"):
            return
        
        if self.dark_mode:
            text = "Modo claro"
            icon = get_icon_for_emoji("☀️", 18)
        else:
            text = "Modo oscuro"
            icon = get_icon_for_emoji("🌙", 18)
        
        self.theme_toggle_button.setText(text)
        self.theme_toggle_button.setIcon(icon)

