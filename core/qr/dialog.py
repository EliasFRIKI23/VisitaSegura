from __future__ import annotations

import json
from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .camera_section import CameraScannerSection
from .pistol_section import PistolScannerSection
from .utils import detect_qr_type, get_name_from_registry, parse_carnet_data


class QRScannerDialog(QDialog):
    """
    Diálogo principal para la lectura de códigos QR mediante cámara o pistola.
    """

    def __init__(self, parent=None, auth_manager=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.current_carnet_data: Optional[Dict[str, str]] = None

        self.setWindowTitle("📱 Escáner de QR - VisitaSegura")
        self.setModal(True)
        self.resize(1400, 900)
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowCloseButtonHint
        )

        self._build_ui()
        self._setup_connections()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.dialog_layout = QVBoxLayout(self)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)

        self._build_method_selector()
        self._build_header()

        self.camera_section = CameraScannerSection(self)
        self.camera_section.set_register_button_visible(False)

        self.pistol_section = PistolScannerSection(self)
        self.pistol_section.setVisible(False)

        self.content_layout.addWidget(self.camera_section, 1)
        self.content_layout.addWidget(self.pistol_section, 1)

        scroll_area.setWidget(content_widget)
        self.dialog_layout.addWidget(scroll_area)

    def _build_method_selector(self) -> None:
        method_frame = QWidget()
        method_frame.setStyleSheet(
            """
            QWidget {
                background-color: #fff3cd;
                border: 3px solid #ffc107;
                border-radius: 12px;
                padding: 15px;
            }
            """
        )
        layout = QHBoxLayout(method_frame)

        method_label = QLabel("⚙️ Método de Escaneo:")
        method_label.setFont(QFont("Arial", 14, QFont.Bold))
        method_label.setStyleSheet("color: #856404;")

        self.method_group = QButtonGroup(self)
        self.camera_radio = QRadioButton("📷 Cámara")
        self.scanner_radio = QRadioButton("🔫 Pistola QR")

        radio_style = """
            QRadioButton {
                color: #495057;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 15px;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
            QRadioButton::indicator:unchecked {
                background-color: white;
                border: 2px solid #ced4da;
                border-radius: 10px;
            }
            QRadioButton::indicator:checked {
                background-color: #007bff;
                border: 2px solid #0056b3;
                border-radius: 10px;
            }
        """

        self.camera_radio.setStyleSheet(radio_style)
        self.scanner_radio.setStyleSheet(radio_style)

        self.method_group.addButton(self.camera_radio, 0)
        self.method_group.addButton(self.scanner_radio, 1)
        self.camera_radio.setChecked(True)

        layout.addWidget(method_label)
        layout.addWidget(self.camera_radio)
        layout.addWidget(self.scanner_radio)
        layout.addStretch()

        self.content_layout.addWidget(method_frame)

    def _build_header(self) -> None:
        header_frame = QWidget()
        header_frame.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #003A70, stop:1 #0056b3);
                border-radius: 10px;
                padding: 20px;
            }
            """
        )
        header_layout = QHBoxLayout(header_frame)

        left_header = QVBoxLayout()
        title = QLabel("📱 Escáner de Códigos QR")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        subtitle = QLabel("Apunta la cámara hacia un código QR para escanearlo")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #e3f2fd;")

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        header_layout.addLayout(left_header)
        header_layout.addStretch()

        guide_label = QLabel(
            "💡 <b>Instrucciones:</b><br>"
            "• Mantén distancia menor a 15cm<br>"
            "• QR dentro del área verde<br>"
            "• Buena iluminación"
        )
        guide_label.setFont(QFont("Arial", 11))
        guide_label.setStyleSheet(
            "color: white; background-color: rgba(255,255,255,0.2); "
            "padding: 15px; border-radius: 8px;"
        )

        header_layout.addWidget(guide_label)
        self.content_layout.addWidget(header_frame)

    def _setup_connections(self) -> None:
        self.camera_radio.toggled.connect(self._on_method_changed)
        self.camera_section.qr_detected.connect(self.on_qr_detected)
        self.camera_section.register_btn.clicked.connect(self.on_register_clicked)
        self.camera_section.close_btn.clicked.connect(self.close)

        self.pistol_section.qr_detected.connect(self.on_qr_detected)

    # ------------------------------------------------------------------
    # Gestión del método de escaneo
    # ------------------------------------------------------------------

    def _on_method_changed(self, _checked: bool) -> None:
        if self.camera_radio.isChecked():
            self.camera_section.setVisible(True)
            self.pistol_section.setVisible(False)
            self.pistol_section.clear()
            self.pistol_section.scanner_input_timer.stop()
        else:
            self.camera_section.stop_camera()
            self.camera_section.setVisible(False)
            self.camera_section.clear_info()

            self.pistol_section.setVisible(True)
            self.pistol_section.clear()
            self.pistol_section.focus_input()

    # ------------------------------------------------------------------
    # Utilidades de autenticación
    # ------------------------------------------------------------------

    def get_auth_manager(self):
        if self.auth_manager:
            return self.auth_manager

        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "auth_manager"):
                return parent.auth_manager
            parent = parent.parent()

        try:
            from core.auth_manager import AuthManager

            return AuthManager()
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Procesamiento de QR
    # ------------------------------------------------------------------

    def on_qr_detected(self, qr_data: str) -> None:
        if qr_data.startswith("ERROR:"):
            QMessageBox.critical(self, "Error", qr_data)
            return

        qr_type = detect_qr_type(qr_data)

        if qr_type == "visitor":
            self.show_visitor_info_from_qr(qr_data)
        elif qr_type == "carnet":
            self.show_carnet_info(qr_data)
        else:
            self.show_generic_qr_info(qr_data)

    # ------------------------------------------------------------------
    # Manejo de QR tipo carnet
    # ------------------------------------------------------------------

    def show_carnet_info(self, qr_data: str) -> None:
        parsed_data = parse_carnet_data(qr_data)
        self.current_carnet_data = parsed_data

        info_text = "<b>🆔 Carnet Detectado:</b><br><br>"

        self.camera_section.clear_info_actions()
        self.camera_section.set_register_button_visible(False)

        if parsed_data.get("rut"):
            info_text += (
                f"<b>RUT:</b> <font color='#28a745' size='4'>{parsed_data['rut']}</font><br><br>"
                "<i>✅ RUT extraído automáticamente del carnet.</i><br>"
                "<i>💡 Presione 'Iniciar Registro' para obtener el nombre completo.</i><br>"
            )
            self.camera_section.set_register_button_visible(True)
            self.camera_section.set_register_button_text("📝 Iniciar Registro")
        else:
            info_text += (
                f"<b>Contenido:</b> {qr_data[:100]}...<br><br>"
                "<i>No se pudo extraer el RUT automáticamente.</i><br>"
            )

        self.camera_section.set_info_content(info_text)

    def on_register_clicked(self) -> None:
        if self.current_carnet_data and self.current_carnet_data.get("rut"):
            self.open_registration_with_carnet_data(self.current_carnet_data)
        else:
            self.open_manual_registration()

    def open_registration_with_carnet_data(self, parsed_data: Dict[str, str]) -> None:
        try:
            from core.visitor_form import VisitorFormDialog

            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)

            if parsed_data.get("rut"):
                form_dialog.rut_input.setText(parsed_data["rut"])

            nombre_obtenido = ""
            if parsed_data.get("rut"):
                QMessageBox.information(
                    self,
                    "🔍 Consultando API",
                    f"Obteniendo nombre para RUT {parsed_data['rut']}...\n\nPor favor espere un momento.",
                )
                nombre_obtenido = get_name_from_registry(parsed_data["rut"])
                if nombre_obtenido not in [
                    "Nombre no disponible - Ingrese manualmente",
                    "RUT no encontrado - Ingrese manualmente",
                    "Error en consulta - Ingrese manualmente",
                    "Timeout en consulta - Ingrese manualmente",
                    "Error de conexión - Ingrese manualmente",
                    "API no disponible - Ingrese manualmente",
                ]:
                    form_dialog.nombre_input.setText(nombre_obtenido)

            message = f"El RUT {parsed_data.get('rut', 'N/A')} ha sido extraído automáticamente del carnet.\n\n"
            if nombre_obtenido and nombre_obtenido not in [
                "Nombre no disponible - Ingrese manualmente",
                "RUT no encontrado - Ingrese manualmente",
                "Error en consulta - Ingrese manualmente",
                "Timeout en consulta - Ingrese manualmente",
                "Error de conexión - Ingrese manualmente",
                "API no disponible - Ingrese manualmente",
            ]:
                message += f"El nombre {nombre_obtenido} ha sido obtenido automáticamente.\n\n"
            else:
                message += (
                    "No se pudo obtener el nombre automáticamente. Por favor, ingrese el nombre completo manualmente.\n\n"
                )
            message += (
                "Complete los campos restantes:\n• Acompañante\n• Sector\n\nY confirme el registro."
            )

            QMessageBox.information(self, "📋 Datos Pre-rellenados", message)

            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitors import VisitorManager

                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self,
                            "✅ Éxito",
                            f"Visitante {visitor.nombre_completo} registrado correctamente",
                        )
                        self.camera_section.clear_info()
                        self.camera_section.set_register_button_visible(False)
                    else:
                        QMessageBox.warning(
                            self,
                            "⚠️ Advertencia",
                            "El visitante ya existe en el sistema",
                        )
        except Exception as exc:
            QMessageBox.critical(self, "❌ Error", f"Error al abrir registro:\n{str(exc)}")

    def open_manual_registration(self) -> None:
        try:
            from core.visitor_form import VisitorFormDialog

            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)

            QMessageBox.information(
                self,
                "📝 Registro Manual",
                "Se abrirá el formulario de registro manual.\n\n"
                "Por favor, complete todos los campos:\n"
                "• RUT\n"
                "• Nombre completo\n"
                "• Acompañante\n"
                "• Sector\n\n"
                "Y confirme el registro.",
            )

            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitors import VisitorManager

                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self,
                            "✅ Éxito",
                            f"Visitante {visitor.nombre_completo} registrado correctamente",
                        )
                        self.camera_section.clear_info()
                    else:
                        QMessageBox.warning(
                            self,
                            "⚠️ Advertencia",
                            "El visitante ya existe en el sistema",
                        )
        except Exception as exc:
            QMessageBox.critical(self, "❌ Error", f"Error al abrir registro manual:\n{str(exc)}")

    # ------------------------------------------------------------------
    # Manejo de QR de visitante
    # ------------------------------------------------------------------

    def show_visitor_info_from_qr(self, qr_data: str) -> None:
        try:
            visitor_data = json.loads(qr_data)
            if self.is_valid_visitor_qr(visitor_data):
                self.show_visitor_info(visitor_data)
            else:
                self.show_generic_qr_info(qr_data)
        except json.JSONDecodeError:
            self.show_generic_qr_info(qr_data)

    def is_valid_visitor_qr(self, data: Dict) -> bool:
        required_fields = ["rut", "nombre_completo", "acompañante", "sector"]
        return all(field in data for field in required_fields)

    def show_visitor_info(self, visitor_data: Dict) -> None:
        info_text = (
            "<b>👤 Visitante Detectado:</b><br><br>"
            f"<b>Nombre:</b> {visitor_data.get('nombre_completo', 'N/A')}<br>"
            f"<b>RUT:</b> {visitor_data.get('rut', 'N/A')}<br>"
            f"<b>Acompañante:</b> {visitor_data.get('acompañante', 'N/A')}<br>"
            f"<b>Sector:</b> {visitor_data.get('sector', 'N/A')}<br><br>"
            "<i>¿Desea registrar este visitante?</i>"
        )

        self.camera_section.set_info_content(info_text)
        self.camera_section.clear_info_actions()
        self.camera_section.set_register_button_visible(False)

        register_btn = QPushButton("✅ Registrar Visitante")
        register_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0056b3; }
            """
        )
        register_btn.clicked.connect(lambda: self.register_visitor_from_qr(visitor_data))
        self.camera_section.add_info_action(register_btn)

    def register_visitor_from_qr(self, visitor_data: Dict) -> None:
        try:
            from core.visitors import Visitor, VisitorManager

            visitor = Visitor(
                rut=visitor_data["rut"],
                nombre_completo=visitor_data["nombre_completo"],
                acompañante=visitor_data["acompañante"],
                sector=visitor_data["sector"],
            )

            manager = VisitorManager()
            if manager.add_visitor(visitor):
                QMessageBox.information(
                    self,
                    "✅ Éxito",
                    f"Visitante {visitor.nombre_completo} registrado correctamente",
                )
                self.camera_section.clear_info()
            else:
                QMessageBox.warning(
                    self,
                    "⚠️ Advertencia",
                    "El visitante ya existe en el sistema",
                )
        except Exception as exc:
            QMessageBox.critical(
                self, "❌ Error", f"Error al registrar visitante:\n{str(exc)}"
            )

    # ------------------------------------------------------------------
    # Manejo de QR genérico
    # ------------------------------------------------------------------

    def show_generic_qr_info(self, qr_data: str) -> None:
        self.camera_section.set_register_button_visible(False)
        self.camera_section.clear_info_actions()
        self.camera_section.set_info_content(f"<b>Contenido del QR:</b><br>{qr_data}")

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        self.camera_section.cleanup()
        self.pistol_section.scanner_input_timer.stop()
        super().closeEvent(event)


__all__ = ["QRScannerDialog"]

