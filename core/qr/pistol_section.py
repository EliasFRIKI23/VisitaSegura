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

        self._build_ui()
        self._setup_connections()

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

        main_frame = QFrame()
        main_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border: 3px solid #003A70;
                border-radius: 12px;
                padding: 40px;
            }
            """
        )
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🔫 Modo Pistola QR")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #003A70; padding: 20px;")
        main_layout.addWidget(title)

        icon = QLabel("📡")
        icon.setFont(QFont("Arial", 80))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("padding: 30px;")
        main_layout.addWidget(icon)

        instructions = QLabel(
            "<b>Instrucciones:</b><br><br>"
            "1. Haga clic en el campo de entrada<br>"
            "2. Apunte la pistola QR al código<br>"
            "3. Presione el gatillo<br>"
            "4. El sistema detectará automáticamente el QR"
        )
        instructions.setFont(QFont("Arial", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet(
            """
            color: #495057;
            background-color: #e3f2fd;
            padding: 25px;
            border-radius: 10px;
            border: 2px solid #90caf9;
            """
        )
        main_layout.addWidget(instructions)

        input_frame = QFrame()
        input_frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 3px solid #28a745;
                border-radius: 10px;
                padding: 20px;
            }
            """
        )
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(15)

        input_label = QLabel("📥 Esperando escaneo...")
        input_label.setFont(QFont("Arial", 16, QFont.Bold))
        input_label.setAlignment(Qt.AlignCenter)
        input_label.setStyleSheet("color: #28a745; padding: 10px;")
        input_layout.addWidget(input_label)

        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText(
            "Haga clic aquí y escanee con la pistola QR..."
        )
        self.scanner_input.setFont(QFont("Arial", 14))
        self.scanner_input.setMinimumHeight(60)
        self.scanner_input.setAlignment(Qt.AlignCenter)
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
        input_layout.addWidget(self.scanner_input)

        self.process_btn = QPushButton("✅ Procesar QR Manualmente")
        self.process_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.process_btn.setMinimumHeight(50)
        self.process_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:pressed { background-color: #004085; }
            """
        )
        input_layout.addWidget(self.process_btn)

        main_layout.addWidget(input_frame)
        main_layout.addStretch()

        layout.addWidget(main_frame)

    # ------------------------------------------------------------------
    # Conexión de señales
    # ------------------------------------------------------------------

    def _setup_connections(self) -> None:
        self.scanner_input.returnPressed.connect(self.process_input)
        self.scanner_input.textChanged.connect(self._on_text_changed)
        self.process_btn.clicked.connect(self.process_input)

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
        if self._notification_label:
            self._notification_label.deleteLater()
            self._notification_label = None


