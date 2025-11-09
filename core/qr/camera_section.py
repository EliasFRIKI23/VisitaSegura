from __future__ import annotations

import cv2
import numpy as np
from pyzbar import pyzbar
from typing import List, Optional

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont, QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class CameraScannerThread(QThread):
    """
    Hilo encargado de capturar imágenes desde la cámara y detectar códigos QR.
    """

    qr_detected = Signal(str)
    frame_ready = Signal(np.ndarray)

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self.camera_index = camera_index
        self.capturing = False
        self.cap: Optional[cv2.VideoCapture] = None

    def run(self) -> None:
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        self.cap = None

        for backend in backends:
            try:
                cap = cv2.VideoCapture(self.camera_index, backend)
                if not cap.isOpened():
                    cap.release()
                    continue

                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
                cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
                cap.set(cv2.CAP_PROP_SATURATION, 0.5)
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)

                ret, frame = cap.read()
                if not ret or frame is None:
                    cap.release()
                    continue

                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                if width < 1000:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

                self.cap = cap
                break
            except Exception:
                if cap:
                    cap.release()
                continue

        if not self.cap or not self.cap.isOpened():
            self.qr_detected.emit("ERROR: No se pudo abrir la cámara con ningún backend")
            return

        self.capturing = True
        frame_fail_count = 0

        while self.capturing:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                frame_fail_count += 1
                if frame_fail_count > 10:
                    self.qr_detected.emit("ERROR: Pérdida de conexión con la cámara")
                    break
                self.msleep(100)
                continue

            frame_fail_count = 0
            self.frame_ready.emit(frame)

            try:
                qr_codes = pyzbar.decode(frame)
                if not qr_codes:
                    qr_codes = self.enhanced_qr_detection(frame)

                for qr_code in qr_codes:
                    try:
                        qr_data = qr_code.data.decode("utf-8")
                    except UnicodeDecodeError:
                        try:
                            qr_data = qr_code.data.decode("latin-1")
                        except UnicodeDecodeError:
                            continue

                    if qr_data and qr_data.strip():
                        self.qr_detected.emit(qr_data)
                        break
            except Exception as exc:
                print(f"Error decodificando QR: {exc}")

            self.msleep(33)

        if self.cap:
            self.cap.release()
            self.cap = None

    def stop(self) -> None:
        self.capturing = False
        self.wait()

    # ------------------------------------------------------------------
    # Procesamiento de imagen auxiliar
    # ------------------------------------------------------------------

    def enhanced_qr_detection(self, frame: np.ndarray):
        """
        Aplica múltiples técnicas de procesamiento para mejorar la detección de QR.
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            qr_codes = pyzbar.decode(enhanced)
            if qr_codes:
                return qr_codes

            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            qr_codes = pyzbar.decode(denoised)
            if qr_codes:
                return qr_codes

            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2,
            )
            qr_codes = pyzbar.decode(thresh)
            if qr_codes:
                return qr_codes

            inverted = cv2.bitwise_not(thresh)
            qr_codes = pyzbar.decode(inverted)
            if qr_codes:
                return qr_codes

            _, otsu_thresh = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            qr_codes = pyzbar.decode(otsu_thresh)
            if qr_codes:
                return qr_codes

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            qr_codes = pyzbar.decode(morphed)
            if qr_codes:
                return qr_codes

            height, width = gray.shape
            if height > 480:
                scale_factor = 1.5
                resized = cv2.resize(
                    gray,
                    (int(width * scale_factor), int(height * scale_factor)),
                    interpolation=cv2.INTER_CUBIC,
                )
                qr_codes = pyzbar.decode(resized)
                if qr_codes:
                    return qr_codes

            for scale in [0.8, 1.2, 1.5]:
                if scale == 1.0:
                    continue
                scaled_frame = cv2.resize(
                    gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
                )
                qr_codes = pyzbar.decode(scaled_frame)
                if qr_codes:
                    return qr_codes
        except Exception as exc:
            print(f"Error en detección mejorada: {exc}")

        return []


class CameraScannerSection(QWidget):
    """
    Sección de UI que gestiona la captura por cámara y la visualización del video.
    """

    qr_detected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_index = 0
        self.available_cameras: List[dict] = []
        self.scanner_thread: Optional[CameraScannerThread] = None
        self.current_resolution = "Desconocida"
        self.dark_mode = getattr(parent, "dark_mode", False)

        self._detect_available_cameras()
        self._build_ui()
        self._setup_connections()
        self.apply_theme()

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        left_column = self._build_camera_column()
        right_column = self._build_side_column()

        content_layout.addLayout(left_column, 3)
        content_layout.addLayout(right_column, 1)

        main_layout.addLayout(content_layout, 1)

    def _build_camera_column(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.camera_frame = QFrame()
        cam_layout = QHBoxLayout(self.camera_frame)

        self.camera_label = QLabel("📷 Cámara:")
        self.camera_label.setFont(QFont("Arial", 13, QFont.Bold))

        self.camera_combo = QComboBox()
        self.camera_combo.setFont(QFont("Arial", 12))
        self._populate_camera_combo()

        self.resolution_label = QLabel("Resolución: Desconocida")
        self.resolution_label.setFont(QFont("Arial", 11))

        cam_layout.addWidget(self.camera_label)
        cam_layout.addWidget(self.camera_combo)
        cam_layout.addWidget(self.resolution_label)
        cam_layout.addStretch()

        layout.addWidget(self.camera_frame)

        self.video_frame = QFrame()
        self.video_frame.setMinimumSize(800, 600)
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        video_layout = QVBoxLayout(self.video_frame)
        video_layout.setContentsMargins(0, 0, 0, 0)

        self.video_label = QLabel("Presione 'Iniciar Cámara' para comenzar")
        self.video_label.setAlignment(Qt.AlignCenter)

        video_layout.addWidget(self.video_label)
        layout.addWidget(self.video_frame, 1)

        return layout

    def _build_side_column(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.info_frame = self._create_info_frame()
        self.info_frame.setVisible(False)
        layout.addWidget(self.info_frame)

        controls_frame = self._create_controls_frame()
        layout.addWidget(controls_frame)

        return layout

    def _create_info_frame(self) -> QFrame:
        frame = QFrame()
        frame.setMinimumHeight(200)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        self.info_title = QLabel("📱 QR Detectado")
        self.info_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.info_title.setAlignment(Qt.AlignCenter)

        self.qr_info_label = QLabel()
        self.qr_info_label.setFont(QFont("Arial", 12))
        self.qr_info_label.setWordWrap(True)
        self.qr_info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        layout.addWidget(self.info_title)
        layout.addWidget(self.qr_info_label)

        self._info_actions_widget = QWidget()
        self._info_actions_layout = QVBoxLayout(self._info_actions_widget)
        self._info_actions_layout.setContentsMargins(0, 0, 0, 0)
        self._info_actions_layout.setSpacing(8)
        layout.addWidget(self._info_actions_widget)

        return frame

    def _create_controls_frame(self) -> QFrame:
        frame = QFrame()
        self.controls_frame = frame
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        self.controls_title = QLabel("🎮 Controles")
        self.controls_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.controls_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.controls_title)

        self.start_btn = QPushButton("🎥 Iniciar Cámara")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ Detener Cámara")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(self.stop_btn)

        self.controls_separator_top = QFrame()
        self.controls_separator_top.setFrameShape(QFrame.HLine)
        layout.addWidget(self.controls_separator_top)

        self.register_btn = QPushButton("📝 Iniciar Registro")
        self.register_btn.setMinimumHeight(50)
        self.register_btn.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(self.register_btn)

        layout.addStretch()

        self.controls_separator_bottom = QFrame()
        self.controls_separator_bottom.setFrameShape(QFrame.HLine)
        layout.addWidget(self.controls_separator_bottom)

        self.close_btn = QPushButton("❌ Cerrar")
        self.close_btn.setMinimumHeight(50)
        self.close_btn.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(self.close_btn)

        return frame

    # ------------------------------------------------------------------
    # Conexiones y lógica
    # ------------------------------------------------------------------

    def _setup_connections(self) -> None:
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)

    def _detect_available_cameras(self) -> None:
        self.available_cameras = []
        for index in range(11):
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                continue

            ret, frame = cap.read()
            if ret and frame is not None:
                resolution = (
                    f"{frame.shape[1]}x{frame.shape[0]}" if frame is not None else "Desconocida"
                )
                self.available_cameras.append(
                    {"index": index, "name": f"Cámara {index}", "resolution": resolution}
                )
            cap.release()

        if not self.available_cameras:
            self.available_cameras.append(
                {
                    "index": -1,
                    "name": "No se detectaron cámaras",
                    "resolution": "Verificar conexión",
                }
            )

    def _populate_camera_combo(self) -> None:
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()
        for camera in self.available_cameras:
            if camera["index"] == -1:
                self.camera_combo.addItem(f"❌ {camera['name']}")
            else:
                self.camera_combo.addItem(
                    f"📷 {camera['name']} ({camera['resolution']})"
                )
        self.camera_combo.blockSignals(False)

    def on_camera_changed(self, index: int) -> None:
        if 0 <= index < len(self.available_cameras):
            camera = self.available_cameras[index]
            if camera["index"] != -1:
                self.camera_index = camera["index"]
                self.video_label.setText(f"Cámara seleccionada: {camera['name']}")
            else:
                self.camera_index = 0
                self.video_label.setText("❌ No hay cámaras disponibles")
        else:
            self.camera_index = 0

    def start_camera(self) -> None:
        if not self.available_cameras or self.available_cameras[0]["index"] == -1:
            QMessageBox.warning(
                self,
                "⚠️ Sin Cámaras",
                (
                    "No se detectaron cámaras disponibles.\n\n"
                    "💡 Soluciones:\n"
                    "• Verifica que el celular esté conectado por USB\n"
                    "• Habilita la depuración USB en el celular\n"
                    "• Prueba con una cámara web externa\n"
                    "• Reinicia la aplicación"
                ),
            )
            return

        selected_camera = self.available_cameras[self.camera_combo.currentIndex()]
        if selected_camera["index"] == -1:
            QMessageBox.warning(
                self,
                "⚠️ Cámara No Disponible",
                "La cámara seleccionada no está disponible.",
            )
            return

        try:
            self.scanner_thread = CameraScannerThread(selected_camera["index"])
            self.scanner_thread.qr_detected.connect(self.qr_detected.emit)
            self.scanner_thread.frame_ready.connect(self.update_frame)
            self.scanner_thread.start()

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

            QTimer.singleShot(500, self.update_resolution_display)

            self.video_label.setText(
                f"🎥 Cámara iniciada: {selected_camera['name']}\nApunta hacia un código QR..."
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "❌ Error de Cámara",
                (
                    "No se pudo iniciar la cámara:\n\n"
                    f"{str(exc)}\n\n"
                    "💡 Soluciones:\n"
                    "• Verifica que la cámara no esté siendo usada por otra aplicación\n"
                    "• Prueba con otra cámara\n"
                    "• Reinicia la aplicación"
                ),
            )

    def stop_camera(self) -> None:
        if self.scanner_thread:
            self.scanner_thread.stop()
            self.scanner_thread = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.video_label.setText("Cámara detenida")
        self.resolution_label.setText("Resolución: Desconocida")
        self.clear_info()

    def update_resolution_display(self) -> None:
        if self.scanner_thread and self.scanner_thread.cap:
            width = int(self.scanner_thread.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.scanner_thread.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.scanner_thread.cap.get(cv2.CAP_PROP_FPS))
            self.resolution_label.setText(f"Resolución: {width}x{height} @ {fps}fps")
            self.current_resolution = f"{width}x{height}"
        else:
            self.resolution_label.setText("Resolución: Desconocida")

    def update_frame(self, frame: np.ndarray) -> None:
        if frame is None or frame.size == 0:
            return

        height, width = frame.shape[:2]
        if height == 0 or width == 0:
            return

        display_frame = frame.copy()
        self.draw_guide_square(display_frame, width, height)

        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        if rgb_frame is None or rgb_frame.size == 0:
            return

        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        if q_image.isNull():
            return

        pixmap = QPixmap.fromImage(q_image)
        if pixmap.isNull():
            return

        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.video_label.setPixmap(scaled_pixmap)

    def draw_guide_square(self, frame: np.ndarray, width: int, height: int) -> None:
        try:
            guide_size = min(width, height) * 0.8
            x1 = int((width - guide_size) / 2)
            y1 = int((height - guide_size) / 2)
            x2 = int(x1 + guide_size)
            y2 = int(y1 + guide_size)

            color = (0, 255, 0)
            thickness = 3
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            inner_size = guide_size * 0.5
            inner_x1 = int((width - inner_size) / 2)
            inner_y1 = int((height - inner_size) / 2)
            inner_x2 = int(inner_x1 + inner_size)
            inner_y2 = int(inner_y1 + inner_size)
            cv2.rectangle(frame, (inner_x1, inner_y1), (inner_x2, inner_y2), color, 1)

            corner_length = int(guide_size * 0.15)
            corner_thickness = 6
            cv2.line(frame, (x1, y1), (x1 + corner_length, y1), color, corner_thickness)
            cv2.line(frame, (x1, y1), (x1, y1 + corner_length), color, corner_thickness)
            cv2.line(frame, (x2, y1), (x2 - corner_length, y1), color, corner_thickness)
            cv2.line(frame, (x2, y1), (x2, y1 + corner_length), color, corner_thickness)
            cv2.line(frame, (x1, y2), (x1 + corner_length, y2), color, corner_thickness)
            cv2.line(frame, (x1, y2), (x1, y2 - corner_length), color, corner_thickness)
            cv2.line(frame, (x2, y2), (x2 - corner_length, y2), color, corner_thickness)
            cv2.line(frame, (x2, y2), (x2, y2 - corner_length), color, corner_thickness)

            text = "QR dentro del area verde"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            text_color = (255, 255, 255)
            text_thickness = 2
            text_size = cv2.getTextSize(text, font, font_scale, text_thickness)[0]
            text_x = int((width - text_size[0]) / 2)
            text_y = int(y2 + 40)
            padding = 10
            cv2.rectangle(
                frame,
                (text_x - padding, text_y - text_size[1] - padding),
                (text_x + text_size[0] + padding, text_y + padding),
                (0, 0, 0),
                -1,
            )
            cv2.putText(
                frame,
                text,
                (text_x, text_y),
                font,
                font_scale,
                text_color,
                text_thickness,
            )
        except Exception as exc:
            print(f"Error dibujando cuadrado de guía: {exc}")

    # ------------------------------------------------------------------
    # Gestión de información y acciones
    # ------------------------------------------------------------------

    def set_info_content(self, html_text: str) -> None:
        self.qr_info_label.setText(html_text)
        self.info_frame.setVisible(True)

    def clear_info(self) -> None:
        self.qr_info_label.clear()
        self.clear_info_actions()
        self.info_frame.setVisible(False)

    def clear_info_actions(self) -> None:
        while self._info_actions_layout.count():
            item = self._info_actions_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def add_info_action(self, widget: QWidget) -> None:
        self._info_actions_layout.addWidget(widget)

    def set_register_button_visible(self, visible: bool) -> None:
        self.register_btn.setVisible(visible)

    def set_register_button_text(self, text: str) -> None:
        self.register_btn.setText(text)

    # ------------------------------------------------------------------
    # Limpieza
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        self.stop_camera()

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
            primary_accent = "#38bdf8"
            success_accent = "#22c55e"
            danger_accent = "#f87171"
            info_bg = "rgba(34, 197, 94, 0.12)"
            info_text = "#bbf7d0"
            camera_combo_bg = "#0f172a"
            camera_combo_fg = "#e2e8f0"
        else:
            card_bg = "#ffffff"
            main_bg = "#f3f4f6"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#0f172a"
            muted_color = "#64748b"
            primary_accent = "#0ea5e9"
            success_accent = "#22c55e"
            danger_accent = "#dc2626"
            info_bg = "rgba(34, 197, 94, 0.12)"
            info_text = "#166534"
            camera_combo_bg = "#ffffff"
            camera_combo_fg = "#1f2937"

        self.setStyleSheet(f"QWidget {{ background-color: {main_bg}; }}")
        self.camera_frame.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 14px; border: 1px solid {border_color}; padding: 15px; }}"
        )
        self.camera_label.setStyleSheet(f"color: {text_color};")
        combo_style = (
            f"""
            QComboBox {{
                background-color: {camera_combo_bg};
                color: {camera_combo_fg};
                border: 1px solid {border_color};
                border-radius: 10px;
                padding: 8px 12px;
                min-width: 220px;
            }}
            QComboBox::drop-down {{ border: none; width: 28px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {camera_combo_fg};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {card_bg};
                color: {camera_combo_fg};
                border: 1px solid {border_color};
                border-radius: 10px;
                padding: 6px;
                selection-background-color: {primary_accent};
                selection-color: #0f172a;
            }}
            """
        )
        self.camera_combo.setStyleSheet(combo_style)
        self.resolution_label.setStyleSheet(f"color: {muted_color}; padding: 5px;")

        self.video_frame.setStyleSheet(
            f"QFrame {{ background-color: #000000; border: 2px solid {border_color}; border-radius: 16px; }}"
        )
        self.video_label.setStyleSheet(
            f"QLabel {{ color: {primary_accent}; font-size: 18px; font-weight: 600; padding: 20px; }}"
        )

        self.info_frame.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px; }}"
        )
        self.info_title.setStyleSheet(f"color: {text_color}; font-weight: 700;")
        self.qr_info_label.setStyleSheet(
            f"color: {info_text}; background-color: {info_bg}; padding: 16px; border-radius: 12px;"
        )

        self.controls_frame.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px; }}"
        )
        self.controls_separator_top.setStyleSheet(f"background-color: {border_color}; max-height: 1px;")
        self.controls_separator_bottom.setStyleSheet(f"background-color: {border_color}; max-height: 1px;")

        self.controls_title.setStyleSheet(f"color: {text_color}; font-weight: 700;")
        self.start_btn.setStyleSheet(
            self._button_style(success_accent, text_color="#0f172a" if self.dark_mode else "#ffffff")
        )
        self.stop_btn.setStyleSheet(
            self._button_style(danger_accent, text_color="#0f172a" if self.dark_mode else "#ffffff")
        )
        self.register_btn.setStyleSheet(
            self._button_style(primary_accent, text_color="#0f172a")
        )
        self.close_btn.setStyleSheet(
            self._button_style(muted_color, text_color="#0f172a")
        )

    @staticmethod
    def _button_style(bg_color: str, text_color: str = "#ffffff") -> str:
        darker = CameraScannerSection.darken_color(bg_color, 0.15)
        return (
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 14px;
                padding: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {darker}; }}
            QPushButton:disabled {{
                background-color: rgba(148, 163, 184, 0.35);
                color: rgba(148, 163, 184, 0.8);
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


