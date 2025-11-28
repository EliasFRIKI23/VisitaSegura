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
    QFrame,
)
from core.ui.icon_loader import get_icon_for_emoji

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
        self.dark_mode = getattr(parent, "dark_mode", False)

        self.setWindowTitle("Escáner de QR - VisitaSegura")
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
            guide_bg = "rgba(14, 165, 233, 0.12)"
        else:
            main_bg = "#f3f4f6"
            card_bg = "#ffffff"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#0f172a"
            muted_color = "#64748b"
            badge_bg = "rgba(14, 165, 233, 0.14)"
            badge_color = "#0284c7"
            guide_bg = "rgba(14, 165, 233, 0.1)"

        self.main_container.setStyleSheet(f"background-color: {main_bg};")
        self.method_card.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )
        self.header_card.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )

        self.title_label.setStyleSheet(f"color: {text_color};")
        self.subtitle_label.setStyleSheet(f"color: {muted_color}; font-size: 13px;")
        self.guide_label.setStyleSheet(
            f"background-color: {guide_bg}; color: {text_color}; padding: 16px; border-radius: 18px;"
        )
        self.method_label.setStyleSheet(f"color: {text_color};")

        radio_style = (
            f"""
            QRadioButton {{
                color: {text_color};
                font-size: 13px;
                font-weight: 600;
                padding: 6px 12px;
            }}
            QRadioButton::indicator {{ width: 20px; height: 20px; }}
            QRadioButton::indicator:unchecked {{
                background-color: {card_bg};
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {badge_color};
                border: 2px solid {badge_color};
                border-radius: 10px;
            }}
            """
        )
        self.camera_radio.setStyleSheet(radio_style)
        self.scanner_radio.setStyleSheet(radio_style)

        self.setStyleSheet(f"QDialog {{ background-color: {main_bg}; }}")
        self.camera_section.set_theme(self.dark_mode)
        self.pistol_section.set_theme(self.dark_mode)

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.dialog_layout = QVBoxLayout(self)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.main_container = QWidget()
        self.content_layout = QVBoxLayout(self.main_container)
        self.content_layout.setContentsMargins(32, 32, 32, 24)
        self.content_layout.setSpacing(24)

        self.method_card = QFrame()
        self.method_card.setObjectName("qrMethodCard")
        method_layout = QHBoxLayout(self.method_card)
        method_layout.setContentsMargins(24, 24, 24, 24)
        method_layout.setSpacing(16)

        self.method_label = QLabel("Selecciona el método de escaneo")
        self.method_label.setFont(QFont("Segoe UI", 14, QFont.Bold))

        self.method_group = QButtonGroup(self)
        self.camera_radio = QRadioButton("Cámara")
        camera_icon = get_icon_for_emoji("📷", 16)
        if not camera_icon.isNull():
            self.camera_radio.setIcon(camera_icon)
        
        self.scanner_radio = QRadioButton("Pistola QR")
        scanner_icon = get_icon_for_emoji("🔫", 16)
        if not scanner_icon.isNull():
            self.scanner_radio.setIcon(scanner_icon)

        for radio in (self.camera_radio, self.scanner_radio):
            radio.setCursor(Qt.PointingHandCursor)

        self.method_group.addButton(self.camera_radio, 0)
        self.method_group.addButton(self.scanner_radio, 1)
        self.camera_radio.setChecked(True)

        method_layout.addWidget(self.method_label)
        method_layout.addStretch()
        method_layout.addWidget(self.camera_radio)
        method_layout.addWidget(self.scanner_radio)

        self.header_card = QFrame()
        self.header_card.setObjectName("qrHeaderCard")
        header_layout = QHBoxLayout(self.header_card)
        header_layout.setContentsMargins(28, 28, 28, 28)
        header_layout.setSpacing(16)

        header_text = QVBoxLayout()
        self.title_label = QLabel("Escáner de códigos QR")
        self.title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header_text.addWidget(self.title_label)

        self.subtitle_label = QLabel("Apunta la cámara o utiliza la pistola de códigos QR para registrar visitantes.")
        self.subtitle_label.setWordWrap(True)
        header_text.addWidget(self.subtitle_label)

        # Crear layout horizontal para link con icono
        droidcam_layout = QHBoxLayout()
        droidcam_layout.setContentsMargins(0, 0, 0, 0)
        droidcam_layout.setSpacing(6)
        
        droidcam_icon = get_icon_for_emoji("📱", 16)
        if not droidcam_icon.isNull():
            icon_label = QLabel()
            icon_label.setStyleSheet("border: none; background-color: transparent; padding: 0; margin: 0;")
            icon_label.setPixmap(droidcam_icon.pixmap(16, 16))
            droidcam_layout.addWidget(icon_label)
        
        self.droidcam_link = QLabel('<a href="https://droidcam.app">Usa tu teléfono como cámara con DroidCam</a>')
        self.droidcam_link.setOpenExternalLinks(True)
        self.droidcam_link.setAlignment(Qt.AlignLeft)
        self.droidcam_link.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: 600;")
        droidcam_layout.addWidget(self.droidcam_link)
        droidcam_layout.addStretch()
        
        droidcam_container = QWidget()
        droidcam_container.setLayout(droidcam_layout)
        header_text.addWidget(droidcam_container)

        header_layout.addLayout(header_text)
        header_layout.addStretch()

        # Crear layout horizontal para guide con icono
        guide_layout = QHBoxLayout()
        guide_layout.setContentsMargins(0, 0, 0, 0)
        guide_layout.setSpacing(8)
        
        guide_icon = get_icon_for_emoji("💡", 18)
        if not guide_icon.isNull():
            icon_label = QLabel()
            icon_label.setStyleSheet("border: none; background-color: transparent; padding: 0; margin: 0;")
            icon_label.setPixmap(guide_icon.pixmap(18, 18))
            guide_layout.addWidget(icon_label)
        
        self.guide_label = QLabel(
            "Consejos rápidos:\n"
            "• Mantén el QR dentro del recuadro\n"
            "• Comprueba buena iluminación\n"
            "• Para pistola, enfoca el campo de texto"
        )
        self.guide_label.setAlignment(Qt.AlignLeft)
        guide_layout.addWidget(self.guide_label)
        guide_layout.addStretch()
        
        guide_container = QWidget()
        guide_container.setLayout(guide_layout)
        header_layout.addWidget(guide_container)

        self.content_layout.addWidget(self.method_card)
        self.content_layout.addWidget(self.header_card)

        self.camera_section = CameraScannerSection(self)
        self.camera_section.set_register_button_visible(False)

        self.pistol_section = PistolScannerSection(self)
        self.pistol_section.setVisible(False)

        self.content_layout.addWidget(self.camera_section, 1)
        self.content_layout.addWidget(self.pistol_section, 1)

        scroll_area.setWidget(self.main_container)
        self.dialog_layout.addWidget(scroll_area)

    def _setup_connections(self) -> None:
        self.camera_radio.toggled.connect(self._on_method_changed)
        self.camera_section.qr_detected.connect(self.on_qr_detected)
        self.camera_section.register_btn.clicked.connect(self.on_register_clicked)
        self.camera_section.close_btn.clicked.connect(self.close)

        self.pistol_section.qr_detected.connect(self.on_qr_detected)
        self.pistol_section.register_btn.clicked.connect(self.on_register_clicked)

    # ------------------------------------------------------------------
    # Gestión del método de escaneo
    # ------------------------------------------------------------------

    def _on_method_changed(self, _checked: bool) -> None:
        if self.camera_radio.isChecked():
            self.camera_section.setVisible(True)
            self.pistol_section.setVisible(False)
            self.pistol_section.clear()
            self.pistol_section.scanner_input_timer.stop()
            # Limpiar datos de carnet cuando se cambia a cámara
            self.current_carnet_data = None
        else:
            self.camera_section.stop_camera()
            self.camera_section.setVisible(False)
            self.camera_section.clear_info()

            self.pistol_section.setVisible(True)
            self.pistol_section.clear()
            self.pistol_section.focus_input()
            # Limpiar datos de carnet cuando se cambia a pistola para nuevo escaneo
            self.current_carnet_data = None
            self.pistol_section.set_register_button_visible(False)

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

        # Limpiar datos del carnet anterior cuando se detecta un nuevo QR
        # Esto asegura que no se usen datos del escaneo anterior
        self.current_carnet_data = None
        
        qr_type = detect_qr_type(qr_data)

        if qr_type == "visitor":
            self.show_visitor_info_from_qr(qr_data)
        elif qr_type == "carnet":
            self.show_carnet_info(qr_data)
        else:
            self.show_generic_qr_info(qr_data)
        
        # Si es pistola QR y se detectó un carnet, el botón de registro ya se muestra en show_carnet_info

    # ------------------------------------------------------------------
    # Manejo de QR tipo carnet
    # ------------------------------------------------------------------

    def show_carnet_info(self, qr_data: str) -> None:
        # Siempre parsear y actualizar con los nuevos datos del QR escaneado
        parsed_data = parse_carnet_data(qr_data)
        # Limpiar datos anteriores antes de asignar los nuevos
        self.current_carnet_data = None
        self.current_carnet_data = parsed_data

        info_text = "<b>Carnet Detectado:</b><br><br>"

        # Limpiar acciones y ocultar botones de registro
        self.camera_section.clear_info_actions()
        self.camera_section.set_register_button_visible(False)
        self.pistol_section.set_register_button_visible(False)

        if parsed_data.get("rut"):
            info_text += (
                f"<b>RUT:</b> <font color='#28a745' size='4'>{parsed_data['rut']}</font><br><br>"
                "<i>RUT extraído automáticamente del carnet.</i><br>"
                "<i>Presione 'Iniciar Registro' para obtener el nombre completo.</i><br>"
            )
            # Mostrar botón de registro en la sección activa
            if self.camera_radio.isChecked():
                self.camera_section.set_register_button_visible(True)
                self.camera_section.set_register_button_text("Iniciar Registro")
            else:
                self.pistol_section.set_register_button_visible(True)
                self.pistol_section.set_register_button_text("Iniciar Registro")
        else:
            info_text += (
                f"<b>Contenido:</b> {qr_data[:100]}...<br><br>"
                "<i>No se pudo extraer el RUT automáticamente.</i><br>"
            )

        # Mostrar información en la sección activa
        if self.camera_radio.isChecked():
            self.camera_section.set_info_content(info_text)
        else:
            # Para la pistola, mostrar información en un QMessageBox o actualizar la UI
            pass

    def on_register_clicked(self) -> None:
        if self.current_carnet_data and self.current_carnet_data.get("rut"):
            self.open_registration_with_carnet_data(self.current_carnet_data)
        else:
            self.open_manual_registration()

    def open_registration_with_carnet_data(self, parsed_data: Dict[str, str]) -> None:
        try:
            from core.visitor_form import VisitorFormDialog

            auth_manager = self.get_auth_manager()
            # Crear nuevo formulario (siempre limpio)
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager, use_modern_theme=True)
            
            # Asegurarse de que los campos estén limpios antes de establecer los nuevos datos
            form_dialog.rut_input.clear()
            form_dialog.nombre_input.clear()
            form_dialog.acompañante_input.clear()

            if parsed_data.get("rut"):
                # Usar método que evita la normalización automática al establecer el RUT
                form_dialog.set_rut_without_normalization(parsed_data["rut"])

            nombre_obtenido = ""
            if parsed_data.get("rut"):
                try:
                    QMessageBox.information(
                        self,
                        "Consultando API",
                        f"Obteniendo nombre para RUT {parsed_data['rut']}...\n\nPor favor espere un momento.",
                    )
                    nombre_obtenido = get_name_from_registry(parsed_data["rut"])
                    if nombre_obtenido and nombre_obtenido not in [
                        "Nombre no disponible - Ingrese manualmente",
                        "RUT no encontrado - Ingrese manualmente",
                        "Error en consulta - Ingrese manualmente",
                        "Timeout en consulta - Ingrese manualmente",
                        "Error de conexión - Ingrese manualmente",
                        "API no disponible - Ingrese manualmente",
                        "Respuesta vacía de la API - Ingrese manualmente",
                        "Error en respuesta de la API - Ingrese manualmente",
                    ]:
                        form_dialog.nombre_input.setText(nombre_obtenido)
                except Exception as api_error:
                    # Si falla la consulta de la API, continuar sin el nombre
                    print(f"Error al consultar API: {api_error}")
                    nombre_obtenido = "Error en consulta - Ingrese manualmente"

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

            QMessageBox.information(self, "Datos Pre-rellenados", message)

            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitors import VisitorManager

                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Visitante {visitor.nombre_completo} registrado correctamente",
                        )
                        # Limpiar datos del carnet anterior para permitir nuevo escaneo
                        self.current_carnet_data = None
                        self.camera_section.clear_info()
                        self.camera_section.set_register_button_visible(False)
                        self.pistol_section.set_register_button_visible(False)
                        # Limpiar el campo de entrada de la pistola para nuevo escaneo
                        if self.scanner_radio.isChecked():
                            self.pistol_section.clear()
                            self.pistol_section.focus_input()
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "El visitante ya existe en el sistema",
                        )
        except Exception as exc:
            error_msg = str(exc)
            # Mensaje más claro para errores de JSON
            if "Expecting value" in error_msg or "JSON" in error_msg:
                error_msg = "Error al consultar la API para obtener el nombre.\n\nPor favor, ingrese el nombre manualmente en el formulario."
            QMessageBox.critical(self, "Error", f"Error al abrir registro:\n{error_msg}")

    def open_manual_registration(self) -> None:
        try:
            from core.visitor_form import VisitorFormDialog

            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager, use_modern_theme=True)

            QMessageBox.information(
                self,
                "Registro Manual",
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
                            "Éxito",
                            f"Visitante {visitor.nombre_completo} registrado correctamente",
                        )
                        self.camera_section.clear_info()
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "El visitante ya existe en el sistema",
                        )
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Error al abrir registro manual:\n{str(exc)}")

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
            "<b>Visitante Detectado:</b><br><br>"
            f"<b>Nombre:</b> {visitor_data.get('nombre_completo', 'N/A')}<br>"
            f"<b>RUT:</b> {visitor_data.get('rut', 'N/A')}<br>"
            f"<b>Acompañante:</b> {visitor_data.get('acompañante', 'N/A')}<br>"
            f"<b>Sector:</b> {visitor_data.get('sector', 'N/A')}<br><br>"
            "<i>¿Desea registrar este visitante?</i>"
        )

        self.camera_section.set_info_content(info_text)
        self.camera_section.clear_info_actions()
        self.camera_section.set_register_button_visible(False)

        register_btn = QPushButton("Registrar Visitante")
        register_btn.setIcon(get_icon_for_emoji("✅", 18))
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
                    "Éxito",
                    f"Visitante {visitor.nombre_completo} registrado correctamente",
                )
                self.camera_section.clear_info()
            else:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "El visitante ya existe en el sistema",
                )
        except Exception as exc:
            QMessageBox.critical(
                self, "Error", f"Error al registrar visitante:\n{str(exc)}"
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

