from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.ui.icon_loader import get_icon_for_emoji


class VisitasView(QWidget):
    """Vista para el registro de visitas"""

    def __init__(self, parent=None, auth_manager=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.dark_mode = False
        self.option_cards = []
        self.buttons = []
        self.setup_ui()

    def get_auth_manager(self):
        """Obtiene el AuthManager de la ventana principal"""
        if self.auth_manager:
            return self.auth_manager

        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "auth_manager"):
                return parent.auth_manager
            parent = parent.parent()

        try:
            from ..auth_manager import AuthManager

            return AuthManager()
        except Exception:
            return None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.main_container = QWidget()
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(32, 32, 32, 24)
        container_layout.setSpacing(24)
        layout.addWidget(self.main_container)

        self.header_card = QFrame()
        header_layout = QVBoxLayout(self.header_card)
        header_layout.setContentsMargins(28, 28, 28, 28)
        header_layout.setSpacing(10)

        self.title_label = QLabel("Registro de visitas")
        self.title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(
            "Selecciona cómo quieres registrar a un visitante o consulta los registros actuales."
        )
        self.subtitle_label.setWordWrap(True)
        header_layout.addWidget(self.subtitle_label)

        self.header_badge = QLabel("Accesos rápidos a las herramientas de registro")
        self.header_badge.setAlignment(Qt.AlignLeft)
        self.header_badge.setStyleSheet(
            "padding: 6px 14px; border-radius: 14px; font-size: 12px; font-weight: 600;"
        )
        header_layout.addWidget(self.header_badge)

        container_layout.addWidget(self.header_card)

        self.grid_card = QFrame()
        grid_layout = QGridLayout(self.grid_card)
        grid_layout.setContentsMargins(28, 28, 28, 28)
        grid_layout.setHorizontalSpacing(18)
        grid_layout.setVerticalSpacing(18)

        options = [
            {
                "title": "Escanear código QR",
                "emoji": "📱",
                "description": "Escanea credenciales digitales para registrar visitantes en segundos.",
                "button": "📷 Escanear QR",
                "handler": self.open_qr_scanner,
                "accent": "#0ea5e9",
            },
            {
                "title": "Registro manual",
                "emoji": "✏️",
                "description": "Carga datos manualmente cuando no hay QR disponible o se requiere validación especial.",
                "button": "📝 Registro manual",
                "handler": self.open_manual_registration,
                "accent": "#22c55e",
            },
            {
                "title": "Ver visitantes actuales",
                "emoji": "👥",
                "description": "Consulta quién está dentro del campus y gestiona sus entradas o salidas.",
                "button": "👥 Ver visitantes",
                "handler": self.open_visitors_view,
                "accent": "#6366f1",
            },
        ]

        for index, option in enumerate(options):
            card = self.create_option_card(option)
            row, col = divmod(index, 2)
            grid_layout.addWidget(card, row, col)

        container_layout.addWidget(self.grid_card)

        self.back_button = QPushButton("Volver al menú principal")
        self.back_button.setIcon(get_icon_for_emoji("⬅️", 18))
        self.back_button.setMinimumHeight(46)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.go_to_main)
        container_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.apply_theme()

    def set_theme(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            main_bg = "#0b1220"
            card_bg = "#111827"
            border_color = "rgba(148, 163, 184, 0.18)"
            text_color = "#e2e8f0"
            muted_color = "#94a3b8"
            badge_bg = "rgba(56, 189, 248, 0.18)"
            badge_color = "#38bdf8"
            back_border = "rgba(148, 163, 184, 0.4)"
            back_hover = "rgba(148, 163, 184, 0.18)"
        else:
            main_bg = "#f3f4f6"
            card_bg = "#ffffff"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#0f172a"
            muted_color = "#64748b"
            badge_bg = "rgba(14, 165, 233, 0.14)"
            badge_color = "#0284c7"
            back_border = "rgba(15, 23, 42, 0.25)"
            back_hover = "rgba(15, 23, 42, 0.08)"

        self.main_container.setStyleSheet(f"background-color: {main_bg};")
        self.header_card.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )
        self.grid_card.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )
        self.title_label.setStyleSheet(f"color: {text_color}; font-weight: 700;")
        self.subtitle_label.setStyleSheet(f"color: {muted_color}; font-size: 13px;")
        self.header_badge.setStyleSheet(
            f"padding: 6px 14px; border-radius: 14px; font-size: 12px; font-weight: 600;"
            f"background-color: {badge_bg}; color: {badge_color};"
        )

        for info in self.option_cards:
            frame = info["frame"]
            title = info["title"]
            description = info["description"]
            button = info["button"]
            accent = info["accent"]

            frame.setStyleSheet(
                f"QFrame {{ background-color: {card_bg}; border-radius: 20px; border: 1px solid {border_color}; }}"
            )
            title.setStyleSheet(f"color: {accent}; font-weight: 700;")
            description.setStyleSheet(f"color: {muted_color};")
            button.setStyleSheet(self._accent_button_style(accent))

        self.back_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: 1px solid {back_border};
                border-radius: 14px;
                padding: 0 26px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {back_hover};
            }}
            """
        )

    def _accent_button_style(self, accent: str) -> str:
        darker = self.darken_color(accent, 0.15)
        return (
            f"""
            QPushButton {{
                background-color: {accent};
                color: #ffffff;
                border: none;
                border-radius: 14px;
                padding: 0 22px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {darker};
            }}
            """
        )

    @staticmethod
    def lighten_color(color: str, factor: float = 0.1) -> str:
        color = color.lstrip("#")
        r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def darken_color(color: str, factor: float = 0.2) -> str:
        color = color.lstrip("#")
        r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_option_card(self, option: dict) -> QFrame:
        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(16)

        # Crear layout horizontal para título con icono
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # Agregar icono al título
        icon = get_icon_for_emoji(option['emoji'], 24)
        if not icon.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(24, 24))
            title_layout.addWidget(icon_label)
        
        title = QLabel(option['title'])
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        card_layout.addLayout(title_layout)

        description = QLabel(option["description"])
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(description)

        # Extraer emoji del texto del botón si existe
        button_text = option["button"]
        button_emoji = None
        if " " in button_text:
            parts = button_text.split(" ", 1)
            if len(parts[0]) <= 2:  # Probablemente un emoji
                button_emoji = parts[0]
                button_text = parts[1] if len(parts) > 1 else button_text
        
        button = QPushButton(button_text)
        if button_emoji:
            button_icon = get_icon_for_emoji(button_emoji, 18)
            if not button_icon.isNull():
                button.setIcon(button_icon)
        button.setMinimumHeight(46)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(option["handler"])
        card_layout.addWidget(button)

        self.option_cards.append({
            "frame": card,
            "title": title,
            "description": description,
            "button": button,
            "accent": option["accent"],
        })
        self.buttons.append(button)

        return card

    def open_qr_scanner(self):
        """Abre el escáner de códigos QR"""
        try:
            from ..qr import QRScannerDialog
            scanner_dialog = QRScannerDialog(self, self.auth_manager)
            scanner_dialog.exec()
        except ImportError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"No se pudo cargar el escáner QR:\n{str(e)}")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error al abrir el escáner QR:\n{str(e)}")

    def open_manual_registration(self):
        """Abre el formulario de registro manual"""
        try:
            from ..visitor_form import VisitorFormDialog
            # Obtener el auth_manager de la ventana principal
            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)
            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from ..visitors import VisitorManager
                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Visitante {visitor.nombre_completo} registrado correctamente"
                        )
                    else:
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "El visitante ya existe en el sistema"
                        )
        except ImportError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"No se pudo cargar el formulario:\n{str(e)}")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error al abrir el formulario:\n{str(e)}")

    def open_visitors_view(self):
        """Abre la vista de visitantes actuales"""
        # Buscar la ventana principal que contiene el navigation_manager
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'navigation_manager'):
                parent.navigation_manager.navigate_to("visitantes")
                return
            elif hasattr(parent, 'open_visitantes'):
                parent.open_visitantes()
                return
            parent = parent.parent()

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
