from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PistolScannerSection(QWidget):
    """
    Sección encargada de gestionar el ingreso mediante pistola lectora de QR.
    """

    qr_detected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scanner_auto_process_delay = 300
        self._notification_label: QLabel | None = None
        self.dark_mode = getattr(parent, "dark_mode", False)

        self._build_ui()
        self._setup_connections()
        self.apply_theme()

        self.scanner_input_timer = QTimer(self)
        self.scanner_input_timer.setSingleShot(True)
        self.scanner_input_timer.timeout.connect(self._auto_process_input)

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.main_frame = QFrame()
        main_layout = QVBoxLayout(self.main_frame)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("🔫 Modo Pistola QR")
        self.title_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.icon_label = QLabel("📡")
        self.icon_label.setFont(QFont("Arial", 80))
        self.icon_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.icon_label)

        self.instructions_label = QLabel(
            "<b>Instrucciones:</b><br><br>"
            "1. Haga clic en el campo de entrada<br>"
            "2. Apunte la pistola QR al código<br>"
            "3. Presione el gatillo<br>"
            "4. El sistema detectará automáticamente el QR"
        )
        self.instructions_label.setFont(QFont("Arial", 14))
        self.instructions_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.instructions_label)

        self.input_frame = QFrame()
        input_layout = QVBoxLayout(self.input_frame)
        input_layout.setSpacing(15)

        self.input_label = QLabel("📥 Esperando escaneo...")
        self.input_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.input_label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.input_label)

        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText(
            "Haga clic aquí y escanee con la pistola QR..."
        )
        self.scanner_input.setFont(QFont("Arial", 14))
        self.scanner_input.setMinimumHeight(60)
        self.scanner_input.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.scanner_input)

        self.process_btn = QPushButton("✅ Procesar QR Manualmente")
        self.process_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.process_btn.setMinimumHeight(50)
        input_layout.addWidget(self.process_btn)

        self.register_btn = QPushButton("📝 Iniciar Registro")
        self.register_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.register_btn.setMinimumHeight(50)
        self.register_btn.setVisible(False)  # Oculto por defecto, se muestra cuando hay RUT detectado
        input_layout.addWidget(self.register_btn)

        main_layout.addWidget(self.input_frame)
        main_layout.addStretch()

        layout.addWidget(self.main_frame)

    # ------------------------------------------------------------------
    # Conexión de señales
    # ------------------------------------------------------------------

    def _setup_connections(self) -> None:
        self.scanner_input.returnPressed.connect(self.process_input)
        self.scanner_input.textChanged.connect(self._on_text_changed)
        self.process_btn.clicked.connect(self.process_input)
        # El botón de registro se conectará desde el diálogo padre

    # ------------------------------------------------------------------
    # Lógica de procesamiento
    # ------------------------------------------------------------------

    def _on_text_changed(self, text: str) -> None:
        if text.strip():
            self.scanner_input_timer.stop()
            self.scanner_input_timer.start(self.scanner_auto_process_delay)

    def _auto_process_input(self) -> None:
        qr_data = self.scanner_input.text().strip()
        if qr_data and len(qr_data) >= 10:
            self.process_input()

    def process_input(self) -> None:
        qr_data = self.scanner_input.text().strip()
        if not qr_data:
            QMessageBox.warning(
                self,
                "⚠️ Campo Vacío",
                "Por favor, escanee un código QR con la pistola.",
            )
            return

        self.scanner_input.clear()
        self._show_success_feedback()
        self.qr_detected.emit(qr_data)
        QTimer.singleShot(100, self.focus_input)

    # ------------------------------------------------------------------
    # Feedback visual
    # ------------------------------------------------------------------

    def _show_success_feedback(self) -> None:
        self.scanner_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #d4edda;
                color: #155724;
                border: 3px solid #28a745;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
            }
            """
        )

        if self._notification_label:
            self._notification_label.deleteLater()
            self._notification_label = None

        notification = QLabel("✅ QR Escaneado Exitosamente", self)
        notification.setStyleSheet(
            """
            QLabel {
                background-color: #28a745;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            """
        )
        notification.setAlignment(Qt.AlignCenter)
        notification.setGeometry(
            int(self.width() / 2 - 150),
            int(self.height() - 100),
            300,
            50,
        )
        notification.show()
        self._notification_label = notification

        QTimer.singleShot(2000, notification.deleteLater)
        QTimer.singleShot(500, self._reset_input_style)

    def _reset_input_style(self) -> None:
        self.scanner_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 2px solid #ced4da;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #28a745;
                background-color: white;
            }
            """
        )

    # ------------------------------------------------------------------
    # Utilidades públicas
    # ------------------------------------------------------------------

    def focus_input(self) -> None:
        self.scanner_input.setFocus()

    def clear(self) -> None:
        self.scanner_input.clear()
        self._reset_input_style()
        self.set_register_button_visible(False)
        if self._notification_label:
            self._notification_label.deleteLater()
            self._notification_label = None
    
    def set_register_button_visible(self, visible: bool) -> None:
        """Muestra u oculta el botón de registro"""
        self.register_btn.setVisible(visible)
    
    def set_register_button_text(self, text: str) -> None:
        """Establece el texto del botón de registro"""
        self.register_btn.setText(text)

    def set_theme(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            card_bg = "#111827"
            main_bg = "#0b1220"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#e2e8f0"
            muted_color = "#94a3b8"
            accent = "#38bdf8"
            info_bg = "rgba(56, 189, 248, 0.12)"
            input_bg = "#0f172a"
            input_border = "rgba(148, 163, 184, 0.35)"
            button_bg = "#38bdf8"
        else:
            card_bg = "#ffffff"
            main_bg = "#f3f4f6"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#0f172a"
            muted_color = "#64748b"
            accent = "#0ea5e9"
            info_bg = "rgba(14, 165, 233, 0.14)"
            input_bg = "#ffffff"
            input_border = "rgba(148, 163, 184, 0.3)"
            button_bg = "#0f172a"

        self.setStyleSheet(f"QWidget {{ background-color: {main_bg}; }}")
        self.main_frame.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; padding: 40px; }}"
        )
        self.title_label.setStyleSheet(f"color: {accent}; padding: 20px;")
        self.icon_label.setStyleSheet("padding: 30px;")
        self.instructions_label.setStyleSheet(
            f"color: {muted_color}; background-color: {info_bg}; padding: 25px; border-radius: 16px;"
        )
        self.input_frame.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 18px; padding: 24px; }}"
        )
        self.input_label.setStyleSheet(f"color: {accent}; padding: 10px;")
        self.scanner_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {input_border};
                border-radius: 12px;
                padding: 15px;
                font-size: 16px;
            }}
            QLineEdit:focus {{ border: 1px solid {accent}; }}
            """
        )
        self.process_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {button_bg};
                color: #ffffff;
                border: none;
                border-radius: 14px;
                padding: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self._darken_color(button_bg, 0.15)}; }}
            """
        )
        self.register_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {accent};
                color: #ffffff;
                border: none;
                border-radius: 14px;
                padding: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self._darken_color(accent, 0.15)}; }}
            """
        )

    @staticmethod
    def _darken_color(color: str, factor: float = 0.2) -> str:
        color = color.lstrip("#")
        r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"


