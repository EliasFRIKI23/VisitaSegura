import cv2
import numpy as np
from pyzbar import pyzbar
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QMessageBox, QWidget, QSizePolicy, QLineEdit, QComboBox,
    QScrollArea, QScrollBar, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QPixmap, QImage
import json
import re


def validate_rut_dv(numero, dv):
    """
    Valida el dígito verificador de un RUT chileno
    
    Args:
        numero (str): Número del RUT (sin dígito verificador)
        dv (str): Dígito verificador
    
    Returns:
        bool: True si el dígito verificador es válido
    """
    try:
        # Convertir número a entero
        numero_int = int(numero)
        
        # Calcular dígito verificador usando algoritmo chileno
        suma = 0
        multiplicador = 2
        
        # Recorrer el número de derecha a izquierda
        for digito in reversed(str(numero_int)):
            suma += int(digito) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        # Calcular resto y dígito verificador esperado
        resto = suma % 11
        dv_calculado = 11 - resto
        
        # Casos especiales
        if dv_calculado == 11:
            dv_calculado = 0
        elif dv_calculado == 10:
            dv_calculado = 'K'
        
        # Comparar con el dígito verificador proporcionado
        return str(dv_calculado) == str(dv).upper()
    
    except (ValueError, TypeError):
        return False


def format_rut_without_validation(rut_input):
    """
    Formatea un RUT al formato chileno estándar XX.XXX.XXX-X sin validar el dígito verificador.
    Útil cuando no sabemos si el dígito verificador es correcto pero queremos formatear.
    Maneja la ambigüedad de RUTs de 8 caracteres sin guión.
    
    Args:
        rut_input (str): RUT en cualquier formato (con o sin puntos, guiones, espacios)
    
    Returns:
        str: RUT formateado en formato XX.XXX.XXX-X o cadena vacía si no es válido
    """
    if not rut_input:
        return ""
    
    # Limpiar el RUT: solo números y K/k
    rut_clean = ''.join(c for c in str(rut_input).upper() if c.isdigit() or c == 'K')
    
    # Validar longitud mínima y máxima (7-8 dígitos + dígito verificador)
    if len(rut_clean) < 8 or len(rut_clean) > 9:
        return ""
    
    # Separar número y dígito verificador
    if len(rut_clean) == 8:
        # AMBIGÜEDAD: 8 caracteres puede ser:
        # - Caso 1: 7 dígitos + 1 dv: 12345678 (usar como 1.234.567-8)
        # - Caso 2: 8 dígitos sin dv (no válido, todos los RUT tienen dv)
        # Intentar validar si es 7+1 o si el dv es inválido
        numero_7 = rut_clean[:7]
        dv_7 = rut_clean[7]
        
        # Si el dv es válido para 7 dígitos, usar esa interpretación
        if validate_rut_dv(numero_7, dv_7):
            numero = numero_7
            dv = dv_7
        else:
            # Si el dv no es válido, probablemente el RUT está incompleto
            # Por defecto, usar 7 dígitos + 1 dv (formatear aunque sea incorrecto)
            numero = numero_7
            dv = dv_7
    else:
        # Caso: 123456789 o 12345678K (9 caracteres - 8 dígitos + 1 verificador)
        numero = rut_clean[:-1]
        dv = rut_clean[-1]
    
    # Formatear al estilo chileno: XX.XXX.XXX-X
    if len(numero) == 7:
        # RUT de 7 dígitos: X.XXX.XXX-X
        numero_formateado = f"{numero[:1]}.{numero[1:4]}.{numero[4:]}"
        return f"{numero_formateado}-{dv}"
    elif len(numero) == 8:
        # RUT de 8 dígitos: XX.XXX.XXX-X
        numero_formateado = f"{numero[:2]}.{numero[2:5]}.{numero[5:]}"
        return f"{numero_formateado}-{dv}"
    else:
        # Casos inesperados
        return f"{numero}-{dv}"


class QRScannerThread(QThread):
    """Hilo para el escaneo de QR en segundo plano"""
    qr_detected = Signal(str)  # Señal cuando se detecta un QR
    frame_ready = Signal(np.ndarray)  # Señal para mostrar el frame
    
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.capturing = False
        self.cap = None
    
    def run(self):
        """Ejecuta el escaneo de QR"""
        try:
            # Configurar captura con diferentes backends
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
            self.cap = None
            
            for backend in backends:
                try:
                    self.cap = cv2.VideoCapture(self.camera_index, backend)
                    if self.cap.isOpened():
                        # Configurar propiedades de la cámara para mejor calidad
                        # Intentar resolución más alta primero
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                        self.cap.set(cv2.CAP_PROP_FPS, 30)
                        
                        # Configuraciones adicionales para mejor calidad
                        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)  # Brillo medio
                        self.cap.set(cv2.CAP_PROP_CONTRAST, 0.5)     # Contraste medio
                        self.cap.set(cv2.CAP_PROP_SATURATION, 0.5)   # Saturación media
                        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Exposición automática
                        
                        # Si la resolución alta falla, intentar con resolución media
                        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        
                        if actual_width < 1000:  # Si no soporta HD
                            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
                            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
                        
                        # Probar leer un frame
                        ret, test_frame = self.cap.read()
                        if ret and test_frame is not None:
                            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                            print(f"Cámara abierta con backend {backend} - Resolución: {int(actual_width)}x{int(actual_height)}")
                            break
                        else:
                            self.cap.release()
                            self.cap = None
                except:
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    continue
            
            if not self.cap or not self.cap.isOpened():
                self.qr_detected.emit("ERROR: No se pudo abrir la cámara con ningún backend")
                return
            
            self.capturing = True
            frame_count = 0
            
            while self.capturing:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    # Intentar reconectar
                    frame_count += 1
                    if frame_count > 10:  # Después de 10 frames fallidos
                        self.qr_detected.emit("ERROR: Pérdida de conexión con la cámara")
                        break
                    self.msleep(100)
                    continue
                
                frame_count = 0  # Reset contador si frame es válido
                
                # Enviar frame para mostrar
                self.frame_ready.emit(frame)
                
                # Buscar códigos QR con múltiples métodos mejorados
                try:
                    # Método 1: Detección directa en imagen original
                    qr_codes = pyzbar.decode(frame)
                    
                    # Si no encuentra QR, aplicar procesamiento avanzado
                    if not qr_codes:
                        qr_codes = self.enhanced_qr_detection(frame)
                    
                    # Procesar QR encontrados
                    for qr_code in qr_codes:
                        try:
                            qr_data = qr_code.data.decode('utf-8')
                            if qr_data and len(qr_data.strip()) > 0:
                                self.qr_detected.emit(qr_data)
                                break  # Solo procesar el primer QR válido
                        except UnicodeDecodeError:
                            # Intentar con diferentes encodings
                            try:
                                qr_data = qr_code.data.decode('latin-1')
                                if qr_data and len(qr_data.strip()) > 0:
                                    self.qr_detected.emit(qr_data)
                                    break
                            except:
                                continue
                                
                except Exception as e:
                    print(f"Error decodificando QR: {e}")
                
                # Pequeña pausa para no sobrecargar el CPU
                self.msleep(33)  # ~30 FPS
                
        except Exception as e:
            self.qr_detected.emit(f"ERROR: {str(e)}")
        finally:
            if self.cap:
                self.cap.release()
    
    def stop(self):
        """Detiene el escaneo"""
        self.capturing = False
        self.wait()
    
    def enhanced_qr_detection(self, frame):
        """Detección mejorada de QR con múltiples técnicas de procesamiento"""
        qr_codes = []
        
        try:
            # Crear copia para procesar
            processed_frame = frame.copy()
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
            
            # Método 1: Mejora de contraste con CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            qr_codes = pyzbar.decode(enhanced)
            if qr_codes:
                return qr_codes
            
            # Método 2: Reducción de ruido con filtro bilateral
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            qr_codes = pyzbar.decode(denoised)
            if qr_codes:
                return qr_codes
            
            # Método 3: Filtro gaussiano + umbralización adaptativa
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            qr_codes = pyzbar.decode(thresh)
            if qr_codes:
                return qr_codes
            
            # Método 4: Imagen invertida
            inverted = cv2.bitwise_not(thresh)
            qr_codes = pyzbar.decode(inverted)
            if qr_codes:
                return qr_codes
            
            # Método 5: Umbralización de Otsu
            _, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            qr_codes = pyzbar.decode(otsu_thresh)
            if qr_codes:
                return qr_codes
            
            # Método 6: Morfología para limpiar la imagen
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            qr_codes = pyzbar.decode(morphed)
            if qr_codes:
                return qr_codes
            
            # Método 7: Escalado de imagen para QR pequeños
            height, width = gray.shape
            if height > 480:  # Solo escalar si la imagen es grande
                scale_factor = 1.5
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                scaled = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                qr_codes = pyzbar.decode(scaled)
                if qr_codes:
                    return qr_codes
            
            # Método 8: Combinación de técnicas
            # Aplicar CLAHE + filtro bilateral + umbralización
            clahe_enhanced = clahe.apply(gray)
            bilateral_filtered = cv2.bilateralFilter(clahe_enhanced, 9, 75, 75)
            final_thresh = cv2.adaptiveThreshold(
                bilateral_filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            qr_codes = pyzbar.decode(final_thresh)
            if qr_codes:
                return qr_codes
            
            # Método 9: Detección en múltiples escalas
            for scale in [0.8, 1.2, 1.5]:
                if scale != 1.0:
                    scaled_frame = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                    qr_codes = pyzbar.decode(scaled_frame)
                    if qr_codes:
                        return qr_codes
            
        except Exception as e:
            print(f"Error en detección mejorada: {e}")
        
        return qr_codes

class QRScannerDialog(QDialog):
    """Diálogo para escanear códigos QR"""
    
    def __init__(self, parent=None, auth_manager=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.setWindowTitle("📱 Escáner de QR - VisitaSegura")
        self.setModal(True)
        
        # Hacer que la ventana sea maximizable y redimensionable
        from PySide6.QtCore import Qt
        # Habilitar todos los botones de ventana (minimizar, maximizar, cerrar)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | 
                          Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Tamaño inicial grande pero no forzado
        self.resize(1400, 900)
        
        # Configuración de la cámara
        self.camera_index = 0
        self.available_cameras = []
        self.scanner_thread = None
        self.current_resolution = "Desconocida"
        self.current_carnet_data = None  # Almacenar datos del carnet actual
        
        # Timer para auto-procesamiento de pistola QR
        self.scanner_input_timer = QTimer()
        self.scanner_input_timer.setSingleShot(True)
        self.scanner_input_timer.timeout.connect(self.auto_process_scanner_input)
        self.scanner_auto_process_delay = 300  # 300ms de delay después del último carácter
        
        # Detectar cámaras disponibles
        self.detect_available_cameras()
        
        # IMPORTANTE: Inicializar la interfaz
        self.setup_ui()
        self.setup_connections()
    
    def get_auth_manager(self):
        """Obtiene el AuthManager de la ventana principal"""
        # Si ya tenemos auth_manager, usarlo
        if self.auth_manager:
            return self.auth_manager
        
        # Buscar la ventana principal que contiene el auth_manager
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'auth_manager'):
                return parent.auth_manager
            parent = parent.parent()
        
        # Si no se encuentra, crear una nueva instancia
        try:
            from core.auth_manager import AuthManager
            return AuthManager()
        except Exception:
            return None
    
    def detect_available_cameras(self):
        """Detecta las cámaras disponibles en el sistema"""
        self.available_cameras = []
        
        # Probar índices de cámara del 0 al 10
        for i in range(11):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Verificar si realmente puede leer un frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    self.available_cameras.append({
                        'index': i,
                        'name': f'Cámara {i}',
                        'resolution': f'{frame.shape[1]}x{frame.shape[0]}' if frame is not None else 'Desconocida'
                    })
                cap.release()
        
        # Si no se encontraron cámaras, agregar opciones de ayuda
        if not self.available_cameras:
            self.available_cameras.append({
                'index': -1,
                'name': 'No se detectaron cámaras',
                'resolution': 'Verificar conexión'
            })
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal del diálogo
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear scroll area para todo el contenido
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Widget contenedor del contenido
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Selector de método de escaneo
        method_frame = QFrame()
        method_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 3px solid #ffc107;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        method_layout = QHBoxLayout(method_frame)
        
        method_label = QLabel("⚙️ Método de Escaneo:")
        method_label.setFont(QFont("Arial", 14, QFont.Bold))
        method_label.setStyleSheet("color: #856404;")
        
        # Botones de radio para seleccionar el método
        self.method_group = QButtonGroup()
        self.camera_radio = QRadioButton("📷 Cámara")
        self.scanner_radio = QRadioButton("🔫 Pistola QR")
        
        # Estilo para los radio buttons
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
            QRadioButton::indicator:checked::after {
                content: '';
            }
        """
        
        self.camera_radio.setStyleSheet(radio_style)
        self.scanner_radio.setStyleSheet(radio_style)
        
        self.method_group.addButton(self.camera_radio, 0)
        self.method_group.addButton(self.scanner_radio, 1)
        
        # Por defecto seleccionar cámara
        self.camera_radio.setChecked(True)
        
        # Conectar señal de cambio
        self.camera_radio.toggled.connect(self.on_method_changed)
        
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.camera_radio)
        method_layout.addWidget(self.scanner_radio)
        method_layout.addStretch()
        
        main_layout.addWidget(method_frame)
        
        # Header compacto
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #003A70, stop:1 #0056b3);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Lado izquierdo con título
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
        
        # Lado derecho con instrucciones
        guide_label = QLabel("💡 <b>Instrucciones:</b><br>"
                            "• Mantén distancia menos a 15cm<br>"
                            "• QR dentro del área verde<br>"
                            "• Buena iluminación")
        guide_label.setFont(QFont("Arial", 11))
        guide_label.setStyleSheet("color: white; background-color: rgba(255,255,255,0.2); "
                                  "padding: 15px; border-radius: 8px;")
        header_layout.addWidget(guide_label)
        
        main_layout.addWidget(header_frame)
        
        # === CONTENEDOR PARA MODO CÁMARA ===
        self.camera_container = QWidget()
        camera_container_layout = QVBoxLayout(self.camera_container)
        camera_container_layout.setContentsMargins(0, 0, 0, 0)
        camera_container_layout.setSpacing(15)
        
        # Contenedor principal con dos columnas (para cámara)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Columna izquierda - Video (75% del ancho)
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        
        # Selector de cámara en la parte superior del video
        camera_frame = QFrame()
        camera_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border: 2px solid #dee2e6;
            }
        """)
        camera_layout = QHBoxLayout(camera_frame)
        
        camera_label = QLabel("📷 Cámara:")
        camera_label.setFont(QFont("Arial", 13, QFont.Bold))
        camera_label.setStyleSheet("color: #2c3e50;")
        
        self.camera_combo = QComboBox()
        self.camera_combo.setFont(QFont("Arial", 12))
        self.camera_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #2c3e50;
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 250px;
                min-height: 35px;
            }
            QComboBox:hover {
                border-color: #007bff;
            }
            QComboBox:focus {
                border-color: #0056b3;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #2c3e50;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 5px;
                selection-background-color: #007bff;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                min-height: 30px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e3f2fd;
                color: #0056b3;
            }
        """)
        
        # Llenar combo con cámaras disponibles
        for camera in self.available_cameras:
            if camera['index'] == -1:
                self.camera_combo.addItem(f"❌ {camera['name']}")
            else:
                self.camera_combo.addItem(f"📷 {camera['name']} ({camera['resolution']})")
        
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        
        # Label para mostrar resolución actual
        self.resolution_label = QLabel("Resolución: Desconocida")
        self.resolution_label.setFont(QFont("Arial", 11))
        self.resolution_label.setStyleSheet("color: #6c757d; padding: 5px;")
        
        camera_layout.addWidget(camera_label)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.addWidget(self.resolution_label)
        camera_layout.addStretch()
        
        left_column.addWidget(camera_frame)
        
        # Área de video GRANDE (ocupa todo el espacio disponible)
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 3px solid #003A70;
                border-radius: 12px;
            }
        """)
        self.video_frame.setMinimumSize(800, 600)  # Tamaño mucho más grande
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        video_layout = QVBoxLayout(self.video_frame)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label para mostrar el video
        self.video_label = QLabel("Presione 'Iniciar Cámara' para comenzar")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                color: #e3f2fd;
                font-size: 18px;
                font-weight: bold;
                background-color: transparent;
                padding: 20px;
            }
        """)
        video_layout.addWidget(self.video_label)
        
        left_column.addWidget(self.video_frame, 1)  # El 1 hace que tome todo el espacio disponible
        
        # Agregar columna izquierda al layout principal
        content_layout.addLayout(left_column, 3)  # 75% del ancho
        
        # Columna derecha - Información y controles (25% del ancho)
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        
        # Área de información del QR escaneado
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e9;
                border: 3px solid #4caf50;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        self.info_frame.setVisible(False)
        self.info_frame.setMinimumHeight(200)
        
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setSpacing(10)
        
        info_title = QLabel("📱 QR Detectado")
        info_title.setFont(QFont("Arial", 16, QFont.Bold))
        info_title.setAlignment(Qt.AlignCenter)
        info_title.setStyleSheet("color: #2e7d32; padding-bottom: 10px;")
        info_layout.addWidget(info_title)
        
        self.qr_info_label = QLabel()
        self.qr_info_label.setFont(QFont("Arial", 12))
        self.qr_info_label.setWordWrap(True)
        self.qr_info_label.setStyleSheet("color: #1b5e20; background-color: white; "
                                         "padding: 15px; border-radius: 8px;")
        self.qr_info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        info_layout.addWidget(self.qr_info_label)
        
        right_column.addWidget(self.info_frame)
        
        # Panel de control con botones en la columna derecha
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(12)
        
        control_title = QLabel("🎮 Controles")
        control_title.setFont(QFont("Arial", 16, QFont.Bold))
        control_title.setAlignment(Qt.AlignCenter)
        control_title.setStyleSheet("color: #2c3e50; padding-bottom: 10px;")
        controls_layout.addWidget(control_title)
        
        # Botón iniciar cámara
        self.start_btn = QPushButton("🎥 Iniciar Cámara")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        controls_layout.addWidget(self.start_btn)
        
        # Botón detener cámara
        self.stop_btn = QPushButton("⏹️ Detener Cámara")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        controls_layout.addWidget(self.stop_btn)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #dee2e6; max-height: 2px;")
        controls_layout.addWidget(separator)
        
        # Botón de registro
        self.register_btn = QPushButton("📝 Iniciar Registro")
        self.register_btn.setVisible(True)
        self.register_btn.setMinimumHeight(50)
        self.register_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        controls_layout.addWidget(self.register_btn)
        
        # Espacio flexible
        controls_layout.addStretch()
        
        # Separador
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background-color: #dee2e6; max-height: 2px;")
        controls_layout.addWidget(separator2)
        
        # Botón cerrar
        self.close_btn = QPushButton("❌ Cerrar")
        self.close_btn.setMinimumHeight(50)
        self.close_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        controls_layout.addWidget(self.close_btn)
        
        right_column.addWidget(controls_frame)
        
        # Agregar columna derecha al layout principal
        content_layout.addLayout(right_column, 1)  # 25% del ancho
        
        # Agregar el layout de contenido (dos columnas) al contenedor de cámara
        camera_container_layout.addLayout(content_layout, 1)
        
        # Agregar contenedor de cámara al layout principal
        main_layout.addWidget(self.camera_container, 1)
        
        # === CONTENEDOR PARA MODO PISTOLA QR ===
        self.scanner_container = QWidget()
        scanner_container_layout = QVBoxLayout(self.scanner_container)
        scanner_container_layout.setContentsMargins(0, 0, 0, 0)
        scanner_container_layout.setSpacing(20)
        
        # Área central para pistola QR
        scanner_main_frame = QFrame()
        scanner_main_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 3px solid #003A70;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        scanner_main_layout = QVBoxLayout(scanner_main_frame)
        scanner_main_layout.setSpacing(25)
        scanner_main_layout.setAlignment(Qt.AlignCenter)
        
        # Título de instrucciones
        scanner_title = QLabel("🔫 Modo Pistola QR")
        scanner_title.setFont(QFont("Arial", 28, QFont.Bold))
        scanner_title.setAlignment(Qt.AlignCenter)
        scanner_title.setStyleSheet("color: #003A70; padding: 20px;")
        scanner_main_layout.addWidget(scanner_title)
        
        # Icono grande
        scanner_icon = QLabel("📡")
        scanner_icon.setFont(QFont("Arial", 80))
        scanner_icon.setAlignment(Qt.AlignCenter)
        scanner_icon.setStyleSheet("padding: 30px;")
        scanner_main_layout.addWidget(scanner_icon)
        
        # Instrucciones
        instructions = QLabel(
            "<b>Instrucciones:</b><br><br>"
            "1. Haga clic en el campo de entrada<br>"
            "2. Apunte la pistola QR al código<br>"
            "3. Presione el gatillo<br>"
            "4. El sistema detectará automáticamente el QR"
        )
        instructions.setFont(QFont("Arial", 14))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            color: #495057;
            background-color: #e3f2fd;
            padding: 25px;
            border-radius: 10px;
            border: 2px solid #90caf9;
        """)
        scanner_main_layout.addWidget(instructions)
        
        # Campo de entrada para pistola QR
        scanner_input_frame = QFrame()
        scanner_input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #28a745;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        scanner_input_layout = QVBoxLayout(scanner_input_frame)
        
        input_label = QLabel("📥 Esperando escaneo...")
        input_label.setFont(QFont("Arial", 16, QFont.Bold))
        input_label.setAlignment(Qt.AlignCenter)
        input_label.setStyleSheet("color: #28a745; padding: 10px;")
        scanner_input_layout.addWidget(input_label)
        
        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText("Haga clic aquí y escanee con la pistola QR...")
        self.scanner_input.setFont(QFont("Arial", 14))
        self.scanner_input.setMinimumHeight(60)
        self.scanner_input.setAlignment(Qt.AlignCenter)
        self.scanner_input.setStyleSheet("""
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
        """)
        
        # Conectar evento de Enter para procesar el QR (para pistolas que envían Enter)
        self.scanner_input.returnPressed.connect(self.process_scanner_input)
        
        # Conectar evento de cambio de texto para auto-procesamiento (para pistolas sin Enter)
        self.scanner_input.textChanged.connect(self.on_scanner_text_changed)
        
        scanner_input_layout.addWidget(self.scanner_input)
        
        # Botón manual de procesar (opcional)
        process_btn = QPushButton("✅ Procesar QR Manualmente")
        process_btn.setFont(QFont("Arial", 13, QFont.Bold))
        process_btn.setMinimumHeight(50)
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        process_btn.clicked.connect(self.process_scanner_input)
        scanner_input_layout.addWidget(process_btn)
        
        scanner_main_layout.addWidget(scanner_input_frame)
        
        # Espacio flexible
        scanner_main_layout.addStretch()
        
        scanner_container_layout.addWidget(scanner_main_frame)
        
        # Agregar contenedor de pistola al layout principal (inicialmente oculto)
        main_layout.addWidget(self.scanner_container, 1)
        self.scanner_container.setVisible(False)
        
        # Configurar scroll area
        scroll_area.setWidget(content_widget)
        dialog_layout.addWidget(scroll_area)
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.close_btn.clicked.connect(self.close)
        self.register_btn.clicked.connect(self.on_register_clicked)
    
    def on_method_changed(self, checked):
        """Maneja el cambio entre modo cámara y pistola QR"""
        if self.camera_radio.isChecked():
            # Modo cámara
            self.camera_container.setVisible(True)
            self.scanner_container.setVisible(False)
            # Detener el timer de auto-procesamiento
            self.scanner_input_timer.stop()
        else:
            # Modo pistola QR
            self.camera_container.setVisible(False)
            self.scanner_container.setVisible(True)
            # Detener la cámara si está activa
            if self.scanner_thread:
                self.stop_camera()
            # Poner foco en el campo de entrada
            self.scanner_input.setFocus()
            self.scanner_input.clear()
    
    def on_scanner_text_changed(self, text):
        """Maneja cambios en el campo de texto de la pistola QR"""
        # Si hay texto, reiniciar el timer de auto-procesamiento
        if text.strip():
            # Detener el timer anterior si existe
            self.scanner_input_timer.stop()
            # Iniciar nuevo timer (se procesará automáticamente después de 300ms sin cambios)
            self.scanner_input_timer.start(self.scanner_auto_process_delay)
            print(f"DEBUG: Pistola QR - Texto detectado ({len(text)} caracteres), esperando más entrada...")
    
    def auto_process_scanner_input(self):
        """Procesa automáticamente el input de la pistola QR después del delay"""
        qr_data = self.scanner_input.text().strip()
        
        # Solo procesar si hay datos y tienen longitud razonable para un QR
        if qr_data and len(qr_data) >= 10:  # QR típicamente tiene al menos 10 caracteres
            print(f"DEBUG: Pistola QR - Auto-procesamiento activado")
            self.process_scanner_input()
        else:
            print(f"DEBUG: Pistola QR - Datos insuficientes para auto-procesar ({len(qr_data)} caracteres)")
    
    def process_scanner_input(self):
        """Procesa el input de la pistola QR"""
        qr_data = self.scanner_input.text().strip()
        
        if not qr_data:
            QMessageBox.warning(
                self,
                "⚠️ Campo Vacío",
                "Por favor, escanee un código QR con la pistola."
            )
            return
        
        # Log para debugging
        print(f"DEBUG: Pistola QR - Datos recibidos: {qr_data[:100]}...")
        print(f"DEBUG: Pistola QR - Longitud: {len(qr_data)} caracteres")
        
        # Limpiar el campo para el próximo escaneo
        self.scanner_input.clear()
        
        # Mostrar feedback visual verde (éxito)
        self.scanner_input.setStyleSheet("""
            QLineEdit {
                background-color: #d4edda;
                color: #155724;
                border: 3px solid #28a745;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
            }
        """)
        
        # Mostrar notificación temporal
        from PySide6.QtWidgets import QLabel
        notification = QLabel("✅ QR Escaneado Exitosamente", self)
        notification.setStyleSheet("""
            QLabel {
                background-color: #28a745;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        notification.setAlignment(Qt.AlignCenter)
        notification.setGeometry(
            int(self.width() / 2 - 150),
            int(self.height() - 100),
            300,
            50
        )
        notification.show()
        
        # Ocultar notificación después de 2 segundos
        QTimer.singleShot(2000, notification.deleteLater)
        
        # Restaurar estilo después de 500ms
        QTimer.singleShot(500, lambda: self.scanner_input.setStyleSheet("""
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
        """))
        
        # Procesar el QR usando la misma lógica que la cámara
        print(f"DEBUG: Pistola QR - Procesando QR...")
        self.on_qr_detected(qr_data)
        print(f"DEBUG: Pistola QR - QR procesado exitosamente")
        
        # Volver a poner foco en el campo después de un breve delay
        QTimer.singleShot(100, lambda: self.scanner_input.setFocus())
    
    def on_camera_changed(self, index):
        """Maneja el cambio de cámara seleccionada"""
        if 0 <= index < len(self.available_cameras):
            camera = self.available_cameras[index]
            if camera['index'] != -1:
                self.camera_index = camera['index']
                self.video_label.setText(f"Cámara seleccionada: {camera['name']}")
            else:
                self.camera_index = 0
                self.video_label.setText("❌ No hay cámaras disponibles")
        else:
            self.camera_index = 0
    
    def start_camera(self):
        """Inicia la cámara y el escaneo"""
        # Verificar si hay cámaras disponibles
        if not self.available_cameras or self.available_cameras[0]['index'] == -1:
            QMessageBox.warning(
                self, 
                "⚠️ Sin Cámaras", 
                "No se detectaron cámaras disponibles.\n\n"
                "💡 Soluciones:\n"
                "• Verifica que el celular esté conectado por USB\n"
                "• Habilita la depuración USB en el celular\n"
                "• Prueba con una cámara web externa\n"
                "• Reinicia la aplicación"
            )
            return
        
        try:
            # Verificar que la cámara seleccionada esté disponible
            selected_camera = self.available_cameras[self.camera_combo.currentIndex()]
            if selected_camera['index'] == -1:
                QMessageBox.warning(self, "⚠️ Cámara No Disponible", "La cámara seleccionada no está disponible.")
                return
            
            self.scanner_thread = QRScannerThread(selected_camera['index'])
            self.scanner_thread.qr_detected.connect(self.on_qr_detected)
            self.scanner_thread.frame_ready.connect(self.update_frame)
            self.scanner_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Actualizar resolución después de un breve delay (500ms)
            # para dar tiempo a que el hilo inicialice la cámara
            QTimer.singleShot(500, self.update_resolution_display)
            
            self.video_label.setText(f"🎥 Cámara iniciada: {selected_camera['name']}\nApunta hacia un código QR...")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "❌ Error de Cámara", 
                f"No se pudo iniciar la cámara:\n\n{str(e)}\n\n"
                "💡 Soluciones:\n"
                "• Verifica que la cámara no esté siendo usada por otra aplicación\n"
                "• Prueba con otra cámara\n"
                "• Reinicia la aplicación"
            )
    
    def stop_camera(self):
        """Detiene la cámara y el escaneo"""
        if self.scanner_thread:
            self.scanner_thread.stop()
            self.scanner_thread = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.video_label.setText("Cámara detenida")
        self.info_frame.setVisible(False)
        self.resolution_label.setText("Resolución: Desconocida")
    
    def update_resolution_display(self):
        """Actualiza la información de resolución en la interfaz"""
        try:
            if self.scanner_thread and self.scanner_thread.cap:
                width = int(self.scanner_thread.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.scanner_thread.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(self.scanner_thread.cap.get(cv2.CAP_PROP_FPS))
                self.resolution_label.setText(f"Resolución: {width}x{height} @ {fps}fps")
                self.current_resolution = f"{width}x{height}"
            else:
                self.resolution_label.setText("Resolución: Desconocida")
        except Exception as e:
            print(f"Error actualizando resolución: {e}")
            self.resolution_label.setText("Resolución: Error")
    
    def update_frame(self, frame):
        """Actualiza el frame de video"""
        try:
            # Verificar que el frame sea válido
            if frame is None or frame.size == 0:
                return
            
            # Verificar dimensiones del frame
            height, width = frame.shape[:2]
            if height == 0 or width == 0:
                return
            
            # Crear una copia del frame para dibujar el cuadrado de guía
            display_frame = frame.copy()
            
            # Dibujar cuadrado de guía para QR
            self.draw_guide_square(display_frame, width, height)
            
            # Convertir BGR a RGB
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Verificar que la conversión fue exitosa
            if rgb_frame is None or rgb_frame.size == 0:
                return
            
            # Crear QImage
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Verificar que QImage sea válido
            if q_image.isNull():
                return
            
            # Escalar para ajustar al label
            pixmap = QPixmap.fromImage(q_image)
            if pixmap.isNull():
                return
            
            # Escalar manteniendo aspecto
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"Error actualizando frame: {e}")
            # Mostrar mensaje de error en lugar de pantalla verde
            self.video_label.setText(f"Error de video: {str(e)}")
    
    def draw_guide_square(self, frame, width, height):
        """Dibuja un cuadrado de guía para ayudar al usuario a apuntar el QR"""
        try:
            # Calcular el tamaño del cuadrado de guía (aproximadamente 80% del frame para mayor distancia)
            guide_size = min(width, height) * 0.8
            
            # Calcular posición centrada
            x1 = int((width - guide_size) / 2)
            y1 = int((height - guide_size) / 2)
            x2 = int(x1 + guide_size)
            y2 = int(y1 + guide_size)
            
            # Color del cuadrado (verde brillante para mejor visibilidad)
            color = (0, 255, 0)  # Verde en BGR
            thickness = 3
            
            # Dibujar el cuadrado principal (más grande para distancia cómoda)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Dibujar un cuadrado interno más pequeño para precisión (50% del cuadrado principal)
            inner_size = guide_size * 0.5
            inner_x1 = int((width - inner_size) / 2)
            inner_y1 = int((height - inner_size) / 2)
            inner_x2 = int(inner_x1 + inner_size)
            inner_y2 = int(inner_y1 + inner_size)
            
            # Dibujar cuadrado interno con línea más delgada
            cv2.rectangle(frame, (inner_x1, inner_y1), (inner_x2, inner_y2), color, 1)
            
            # Dibujar esquinas más gruesas para mejor visibilidad
            corner_length = int(guide_size * 0.15)  # 15% del tamaño del cuadrado
            corner_thickness = 6
            
            # Esquina superior izquierda
            cv2.line(frame, (x1, y1), (x1 + corner_length, y1), color, corner_thickness)
            cv2.line(frame, (x1, y1), (x1, y1 + corner_length), color, corner_thickness)
            
            # Esquina superior derecha
            cv2.line(frame, (x2, y1), (x2 - corner_length, y1), color, corner_thickness)
            cv2.line(frame, (x2, y1), (x2, y1 + corner_length), color, corner_thickness)
            
            # Esquina inferior izquierda
            cv2.line(frame, (x1, y2), (x1 + corner_length, y2), color, corner_thickness)
            cv2.line(frame, (x1, y2), (x1, y2 - corner_length), color, corner_thickness)
            
            # Esquina inferior derecha
            cv2.line(frame, (x2, y2), (x2 - corner_length, y2), color, corner_thickness)
            cv2.line(frame, (x2, y2), (x2, y2 - corner_length), color, corner_thickness)
            
            # Agregar texto instructivo
            text = "QR dentro del area verde"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            text_color = (255, 255, 255)  # Blanco
            text_thickness = 2
            
            # Calcular posición del texto (centrado debajo del cuadrado)
            text_size = cv2.getTextSize(text, font, font_scale, text_thickness)[0]
            text_x = int((width - text_size[0]) / 2)
            text_y = int(y2 + 40)
            
            # Dibujar fondo para el texto (rectángulo negro semitransparente)
            padding = 10
            cv2.rectangle(frame, 
                         (text_x - padding, text_y - text_size[1] - padding),
                         (text_x + text_size[0] + padding, text_y + padding),
                         (0, 0, 0), -1)
            
            # Dibujar el texto
            cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_color, text_thickness)
            
        except Exception as e:
            print(f"Error dibujando cuadrado de guía: {e}")
    
    def on_qr_detected(self, qr_data):
        """Maneja la detección de un código QR"""
        if qr_data.startswith("ERROR:"):
            QMessageBox.critical(self, "Error", qr_data)
            return
        
        # Mostrar información del QR
        self.info_frame.setVisible(True)
        
        # Detectar tipo de QR
        qr_type = self.detect_qr_type(qr_data)
        
        if qr_type == "visitor":
            self.show_visitor_info_from_qr(qr_data)
        elif qr_type == "carnet":
            self.show_carnet_info(qr_data)
        else:
            self.show_generic_qr_info(qr_data)
    
    def detect_qr_type(self, qr_data):
        """Detecta el tipo de QR basado en su contenido"""
        try:
            # Intentar parsear como JSON (QR de visitante)
            json.loads(qr_data)
            return "visitor"
        except json.JSONDecodeError:
            # Verificar si parece ser un QR de carnet
            qr_lower = qr_data.lower()
            
            # Detectar URLs del Registro Civil (carnets chilenos)
            if any(url in qr_lower for url in ['registrocivil.cl', 'sidiv.registrocivil.cl']):
                print(f"DEBUG: QR detectado como carnet por URL del Registro Civil")
                return "carnet"
            
            # Detectar por palabras clave comunes en carnets
            carnet_keywords = ['rut', 'run', 'nombre', 'apellido', 'fecha', 'nacimiento', 'cédula', 'identidad']
            if any(keyword in qr_lower for keyword in carnet_keywords):
                print(f"DEBUG: QR detectado como carnet por palabras clave")
                return "carnet"
            
            # Detectar RUT en el texto (formato 12345678-9 o 12345678-K)
            import re
            rut_pattern = r'\b\d{7,8}[-]?[0-9Kk]\b'
            if re.search(rut_pattern, qr_data):
                print(f"DEBUG: QR detectado como carnet por patrón de RUT")
                return "carnet"
            
            print(f"DEBUG: QR detectado como genérico")
            return "generic"
    
    def parse_carnet_data(self, qr_data):
        """Extrae RUT y nombre del QR del carnet"""
        try:
            print(f"DEBUG: Parseando QR data: {qr_data[:100]}...")
            
            parsed_data = {
                'rut': '',
                'nombre_completo': '',
                'raw_data': qr_data
            }
            
            # Limpiar el texto del QR
            clean_text = qr_data.strip()
            print(f"DEBUG: Texto limpio: {clean_text[:100]}...")
            
            # Método 1: Detectar URL del Registro Civil y extraer RUT
            if 'registrocivil.cl' in clean_text.lower() or 'sidiv.registrocivil.cl' in clean_text.lower():
                print(f"DEBUG: URL del Registro Civil detectada")
                print(f"DEBUG: URL completa: {clean_text}")
                
                # Buscar RUT en parámetros de URL con patrones más amplios (incluyendo K)
                url_rut_patterns = [
                    r'RUN=(\d{7,8}[-]?[0-9Kk])',  # RUN=12345678-9 o RUN=12345678-K
                    r'run=(\d{7,8}[-]?[0-9Kk])',   # run=12345678-9 o run=12345678-K
                    r'RUT=(\d{7,8}[-]?[0-9Kk])',  # RUT=12345678-9 o RUT=12345678-K
                    r'rut=(\d{7,8}[-]?[0-9Kk])',  # rut=12345678-9 o rut=12345678-K
                    r'RUN%3D(\d{7,8}[-]?[0-9Kk])',  # RUN codificado en URL
                    r'run%3D(\d{7,8}[-]?[0-9Kk])',   # run codificado en URL
                    r'RUT%3D(\d{7,8}[-]?[0-9Kk])',  # RUT codificado en URL
                    r'rut%3D(\d{7,8}[-]?[0-9Kk])',  # rut codificado en URL
                    r'RUN%253D(\d{7,8}[-]?[0-9Kk])',  # RUN doblemente codificado
                    r'run%253D(\d{7,8}[-]?[0-9Kk])',   # run doblemente codificado
                ]
                
                rut_found = False
                for pattern in url_rut_patterns:
                    rut_match = re.search(pattern, clean_text, re.IGNORECASE)
                    if rut_match:
                        rut = rut_match.group(1)
                        print(f"DEBUG: RUT encontrado con patrón {pattern}: {rut}")
                        # Formatear RUT con formato chileno estándar XX.XXX.XXX-X
                        rut = format_rut_without_validation(rut)
                        parsed_data['rut'] = rut
                        print(f"DEBUG: RUT formateado: {rut}")
                        rut_found = True
                        break
                
                if not rut_found:
                    print(f"DEBUG: No se encontró RUT en la URL con patrones estándar")
                    # Intentar extraer cualquier secuencia de dígitos que parezca RUT (incluyendo K)
                    rut_flexible_patterns = [
                        r'(\d{7,8}[-]?[0-9Kk])',  # Cualquier RUT en la URL
                        r'(\d{8}[-]?[0-9Kk])',    # RUT de 8 dígitos + verificador
                        r'(\d{7}[-]?[0-9Kk])',    # RUT de 7 dígitos + verificador
                    ]
                    
                    for pattern in rut_flexible_patterns:
                        rut_match = re.search(pattern, clean_text)
                        if rut_match:
                            rut = rut_match.group(1)
                            print(f"DEBUG: RUT encontrado con patrón flexible {pattern}: {rut}")
                            # Formatear RUT con formato chileno estándar XX.XXX.XXX-X
                            rut = format_rut_without_validation(rut)
                            parsed_data['rut'] = rut
                            print(f"DEBUG: RUT formateado flexible: {rut}")
                            rut_found = True
                            break
                
                if not rut_found:
                    print(f"DEBUG: No se encontró RUT en la URL con ningún patrón")
                
                # Si encontramos RUT en URL, no obtener nombre automáticamente
                # El nombre se obtendrá solo cuando se presione el botón de registro
                if parsed_data['rut']:
                    parsed_data['nombre_completo'] = "Presione 'Iniciar Registro' para obtener nombre"
            
            # Método 2: Buscar RUT con formato estándar (12345678-9 o 12345678-K) si no es URL
            if not parsed_data['rut']:
                rut_patterns = [
                    r'\b(\d{7,8}[-]?[0-9Kk])\b',  # RUT con o sin guión (incluyendo K)
                    r'RUT[:\s]*(\d{7,8}[-]?[0-9Kk])',  # RUT: 12345678-9 o RUT: 12345678-K
                    r'RUN[:\s]*(\d{7,8}[-]?[0-9Kk])',  # RUN: 12345678-9 o RUN: 12345678-K
                ]
                
                for pattern in rut_patterns:
                    rut_match = re.search(pattern, clean_text, re.IGNORECASE)
                    if rut_match:
                        rut = rut_match.group(1)
                        # Formatear RUT con formato chileno estándar XX.XXX.XXX-X
                        rut = format_rut_without_validation(rut)
                        parsed_data['rut'] = rut
                        break
            
            # Método 2: Buscar nombre completo
            # Patrones comunes para nombres en carnets chilenos
            name_patterns = [
                r'NOMBRE[:\s]+([A-ZÁÉÍÓÚÑ\s]+)',
                r'APELLIDOS[:\s]+([A-ZÁÉÍÓÚÑ\s]+)',
                r'NOMBRES[:\s]+([A-ZÁÉÍÓÚÑ\s]+)',
                r'([A-ZÁÉÍÓÚÑ]{2,}\s+[A-ZÁÉÍÓÚÑ]{2,}\s+[A-ZÁÉÍÓÚÑ]{2,})',  # Patrón general
            ]
            
            for pattern in name_patterns:
                name_match = re.search(pattern, clean_text, re.IGNORECASE)
                if name_match:
                    nombre = name_match.group(1).strip()
                    # Limpiar y formatear el nombre
                    nombre = re.sub(r'\s+', ' ', nombre)  # Eliminar espacios múltiples
                    nombre = nombre.title()  # Capitalizar primera letra de cada palabra
                    parsed_data['nombre_completo'] = nombre
                    break
            
            # Método 3: Si no encontramos patrón específico, intentar extraer líneas que parezcan nombres
            if not parsed_data['nombre_completo']:
                lines = clean_text.split('\n')
                for line in lines:
                    line = line.strip()
                    # Buscar líneas que contengan solo letras y espacios (posibles nombres)
                    if re.match(r'^[A-ZÁÉÍÓÚÑ\s]{4,}$', line) and len(line.split()) >= 2:
                        nombre = line.title()
                        parsed_data['nombre_completo'] = nombre
                        break
            
            # Método 4: Buscar RUT en formato más flexible (incluyendo K)
            if not parsed_data['rut']:
                # Buscar cualquier secuencia de 7-8 dígitos seguida de un dígito verificador (incluyendo K)
                rut_flexible = re.search(r'\b(\d{7,8})[-]?([0-9Kk])\b', clean_text)
                if rut_flexible:
                    rut = f"{rut_flexible.group(1)}{rut_flexible.group(2)}"
                    # Formatear RUT con formato chileno estándar XX.XXX.XXX-X
                    rut = format_rut_without_validation(rut)
                    parsed_data['rut'] = rut
            
            print(f"DEBUG: Resultado final del parsing: {parsed_data}")
            return parsed_data
            
        except Exception as e:
            print(f"Error parseando datos del carnet: {e}")
            return {
                'rut': '',
                'nombre_completo': '',
                'raw_data': qr_data
            }
    
    def get_name_from_registry(self, rut):
        """Intenta obtener el nombre desde API del Registro Civil"""
        try:
            # Usar la API gratuita de Rutificador Chile (25 consultas diarias gratis)
            import requests
            
            # Limpiar RUT (quitar guión para la consulta)
            rut_clean = rut.replace('-', '')
            
            # URL de la API gratuita
            api_url = f"https://api.boostr.cl/rutificador/{rut_clean}"
            
            # Headers para la API
            headers = {
                'User-Agent': 'VisitaSegura/1.0',
                'Accept': 'application/json'
            }
            
            # Realizar consulta con timeout
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraer nombre completo
                if 'nombre' in data and data['nombre']:
                    nombre_completo = data['nombre'].strip()
                    if nombre_completo:
                        return nombre_completo.title()  # Capitalizar primera letra de cada palabra
                
                # Si no hay nombre, intentar con otros campos
                if 'razon_social' in data and data['razon_social']:
                    return data['razon_social'].strip().title()
                    
            elif response.status_code == 404:
                print(f"RUT {rut} no encontrado en la API")
                return "RUT no encontrado - Ingrese manualmente"
            else:
                print(f"Error en API: {response.status_code}")
                return "Error en consulta - Ingrese manualmente"
                
        except requests.exceptions.Timeout:
            print("Timeout en consulta a API")
            return "Timeout en consulta - Ingrese manualmente"
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión a API: {e}")
            return "Error de conexión - Ingrese manualmente"
        except Exception as e:
            print(f"Error obteniendo nombre del registro: {e}")
            return "Error en consulta - Ingrese manualmente"
        
        return "Nombre no disponible - Ingrese manualmente"
    
    def show_carnet_info(self, qr_data):
        """Muestra información de QR de carnet"""
        print(f"DEBUG: === INICIO show_carnet_info ===")
        print(f"DEBUG: QR data recibido: {qr_data[:200]}...")
        
        # Parsear datos del carnet
        parsed_data = self.parse_carnet_data(qr_data)
        print(f"DEBUG: Datos parseados: {parsed_data}")
        
        # Verificar que el RUT se extrajo correctamente
        if parsed_data.get('rut'):
            print(f"DEBUG: ✅ RUT extraído exitosamente: {parsed_data['rut']}")
        else:
            print(f"DEBUG: ❌ ERROR: No se pudo extraer RUT del QR")
            print(f"DEBUG: QR completo para análisis: {qr_data}")
        
        # Almacenar para el botón
        self.current_carnet_data = parsed_data
        print(f"DEBUG: current_carnet_data establecido: {self.current_carnet_data}")
        
        # Verificar que se almacenó correctamente
        if self.current_carnet_data and self.current_carnet_data.get('rut'):
            print(f"DEBUG: ✅ Datos almacenados correctamente para el botón de registro")
        else:
            print(f"DEBUG: ❌ ERROR: Los datos no se almacenaron correctamente")
        
        # Mostrar información en el área principal
        self.show_carnet_info_in_main_area(qr_data, parsed_data)
        print(f"DEBUG: === FIN show_carnet_info ===")
    
    def show_carnet_info_in_main_area(self, qr_data, parsed_data):
        """Muestra información del carnet en el área principal con botón de registro"""
        # Construir texto informativo
        info_text = f"""
        <b>🆔 Carnet Detectado:</b><br><br>
        """
        
        if parsed_data['rut']:
            info_text += f"<b>RUT:</b> <font color='#28a745' size='4'>{parsed_data['rut']}</font><br><br>"
            info_text += "<i>✅ RUT extraído automáticamente del carnet.</i><br>"
            info_text += "<i>💡 Presione 'Iniciar Registro' para obtener el nombre completo.</i><br>"
        else:
            info_text += f"<b>Contenido:</b> {qr_data[:100]}...<br><br>"
            info_text += "<i>No se pudo extraer el RUT automáticamente.</i><br>"
        
        self.qr_info_label.setText(info_text)
        
        # Mostrar el botón de registro si tenemos RUT
        if parsed_data['rut']:
            self.register_btn.setVisible(True)
            self.register_btn.setText("📝 Iniciar Registro")
        else:
            self.register_btn.setVisible(False)
        
        # Mostrar el área de información
        self.info_frame.setVisible(True)
    
    def on_register_clicked(self):
        """Maneja el clic del botón de registro"""
        print(f"DEBUG: Botón registro clickeado")
        print(f"DEBUG: current_carnet_data existe: {self.current_carnet_data is not None}")
        if self.current_carnet_data:
            print(f"DEBUG: current_carnet_data: {self.current_carnet_data}")
            print(f"DEBUG: RUT en current_carnet_data: {self.current_carnet_data.get('rut', 'NO ENCONTRADO')}")
        
        if self.current_carnet_data and self.current_carnet_data['rut']:
            # Si hay datos de carnet, usar esos datos
            print(f"DEBUG: Usando datos de carnet")
            self.open_registration_with_carnet_data(self.current_carnet_data)
        else:
            # Si no hay datos de carnet, abrir registro manual normal
            print(f"DEBUG: Abriendo registro manual")
            self.open_manual_registration()
    
    def open_registration_with_carnet_data(self, parsed_data):
        """Abre registro manual con datos del carnet"""
        try:
            print(f"DEBUG: Método llamado con parsed_data: {parsed_data}")
            print(f"DEBUG: RUT en parsed_data: {parsed_data.get('rut', 'NO ENCONTRADO')}")
            print(f"DEBUG: Nombre en parsed_data: {parsed_data.get('nombre_completo', 'NO ENCONTRADO')}")
            
            from core.visitor_form import VisitorFormDialog
            # Obtener el auth_manager de la ventana principal
            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)
            
            # Esperar un momento para que el formulario se inicialice completamente
            import time
            time.sleep(0.1)
            
            # Pre-rellenar RUT
            if parsed_data['rut']:
                print(f"DEBUG: Estableciendo RUT: {parsed_data['rut']}")
                form_dialog.rut_input.setText(parsed_data['rut'])
                print(f"DEBUG: RUT establecido en campo: {form_dialog.rut_input.text()}")
                
                # Forzar actualización del campo
                form_dialog.rut_input.update()
            
            # Intentar obtener nombre desde la API solo cuando se presiona el botón
            nombre_obtenido = ""
            if parsed_data['rut']:
                # Mostrar mensaje de carga
                QMessageBox.information(
                    self,
                    "🔍 Consultando API",
                    f"Obteniendo nombre para RUT {parsed_data['rut']}...\n\nPor favor espere un momento."
                )
                
                # Consultar API
                nombre_obtenido = self.get_name_from_registry(parsed_data['rut'])
                print(f"DEBUG: Nombre obtenido de API: {nombre_obtenido}")
                
                # Pre-rellenar nombre si se obtuvo exitosamente
                if nombre_obtenido and nombre_obtenido not in ["Nombre no disponible - Ingrese manualmente", "RUT no encontrado - Ingrese manualmente", "Error en consulta - Ingrese manualmente", "Timeout en consulta - Ingrese manualmente", "Error de conexión - Ingrese manualmente"]:
                    print(f"DEBUG: Estableciendo nombre: {nombre_obtenido}")
                    form_dialog.nombre_input.setText(nombre_obtenido)
                    print(f"DEBUG: Nombre establecido en campo: {form_dialog.nombre_input.text()}")
                    
                    # Forzar actualización del campo
                    form_dialog.nombre_input.update()
                else:
                    print(f"DEBUG: Nombre no válido o error en API: {nombre_obtenido}")
            
            # Mostrar mensaje informativo
            message = f"El RUT {parsed_data['rut']} ha sido extraído automáticamente del carnet.\n\n"
            if nombre_obtenido and nombre_obtenido not in ["Nombre no disponible - Ingrese manualmente", "RUT no encontrado - Ingrese manualmente", "Error en consulta - Ingrese manualmente", "Timeout en consulta - Ingrese manualmente", "Error de conexión - Ingrese manualmente"]:
                message += f"El nombre {nombre_obtenido} ha sido obtenido automáticamente de la API.\n\n"
            else:
                message += "No se pudo obtener el nombre automáticamente. Por favor, ingrese el nombre completo manualmente.\n\n"
            
            message += "Complete los campos restantes:\n• Acompañante\n• Sector\n\nY confirme el registro."
            
            QMessageBox.information(
                self,
                "📋 Datos Pre-rellenados",
                message
            )
            
            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitor_model import VisitorManager
                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self, 
                            "✅ Éxito", 
                            f"Visitante {visitor.nombre_completo} registrado correctamente"
                        )
                        self.info_frame.setVisible(False)
                        self.register_btn.setVisible(False)
                    else:
                        QMessageBox.warning(
                            self, 
                            "⚠️ Advertencia", 
                            "El visitante ya existe en el sistema"
                        )
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al abrir registro:\n{str(e)}")
    
    def open_manual_registration(self):
        """Abre registro manual sin datos de carnet"""
        try:
            from core.visitor_form import VisitorFormDialog
            # Obtener el auth_manager de la ventana principal
            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)
            
            # Mostrar mensaje informativo
            QMessageBox.information(
                self,
                "📝 Registro Manual",
                "Se abrirá el formulario de registro manual.\n\n"
                "Por favor, complete todos los campos:\n"
                "• RUT\n"
                "• Nombre completo\n"
                "• Acompañante\n"
                "• Sector\n\n"
                "Y confirme el registro."
            )
            
            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitor_model import VisitorManager
                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self, 
                            "✅ Éxito", 
                            f"Visitante {visitor.nombre_completo} registrado correctamente"
                        )
                    else:
                        QMessageBox.warning(
                            self, 
                            "⚠️ Advertencia", 
                            "El visitante ya existe en el sistema"
                        )
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al abrir registro manual:\n{str(e)}")
    
    def show_simple_carnet_dialog(self, parsed_data):
        """Muestra ventana simple con RUT extraído"""
        # Crear diálogo simple
        dialog = QDialog(self)
        dialog.setWindowTitle("🆔 Datos del Carnet")
        dialog.setModal(True)
        dialog.resize(400, 250)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("✅ Datos Extraídos del Carnet")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Información del RUT
        rut_frame = QFrame()
        rut_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e8;
                border: 2px solid #28a745;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        rut_layout = QVBoxLayout(rut_frame)
        
        rut_label = QLabel(f"<b>RUT Detectado:</b><br><font size='5' color='#28a745'>{parsed_data['rut']}</font>")
        rut_label.setAlignment(Qt.AlignCenter)
        rut_label.setFont(QFont("Arial", 12))
        rut_layout.addWidget(rut_label)
        
        layout.addWidget(rut_frame)
        
        # Información adicional
        info_label = QLabel("""
        <b>📋 Próximos pasos:</b><br>
        • Se abrirá el formulario de registro<br>
        • El RUT ya estará pre-rellenado<br>
        • Complete: Nombre, Acompañante y Sector<br>
        • Confirme el registro
        """)
        info_label.setFont(QFont("Arial", 10))
        info_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(info_label)
        
        # Botones
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton("📝 Registrar Visitante")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        register_btn.clicked.connect(lambda: self.open_registration_with_rut(dialog, parsed_data))
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(register_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Mostrar diálogo
        dialog.exec()
    
    def show_full_carnet_info(self, qr_data, parsed_data):
        """Muestra información completa del carnet cuando no se puede extraer RUT"""
        # Construir texto informativo
        info_text = f"""
        <b>🆔 Carnet Detectado:</b><br><br>
        """
        
        if parsed_data['rut']:
            info_text += f"<b>RUT:</b> {parsed_data['rut']}<br>"
        
        if parsed_data['nombre_completo']:
            info_text += f"<b>Nombre:</b> {parsed_data['nombre_completo']}<br>"
        
        if not parsed_data['rut'] and not parsed_data['nombre_completo']:
            info_text += f"<b>Contenido:</b> {qr_data}<br>"
            info_text += "<i>No se pudieron extraer datos automáticamente.</i><br>"
        else:
            info_text += "<br><i>✅ Datos extraídos automáticamente del carnet.</i><br>"
        
        info_text += "<i>¿Desea registrar este visitante?</i>"
        
        self.qr_info_label.setText(info_text)
        
        # Mostrar botón para registro automático si tenemos datos
        if parsed_data['rut'] or parsed_data['nombre_completo']:
            self.show_auto_register_button(parsed_data)
        else:
            # Mostrar botón para registro manual si no se pudieron extraer datos
            self.show_manual_register_button(qr_data)
    
    def show_visitor_info_from_qr(self, qr_data):
        """Muestra información de QR de visitante"""
        try:
            visitor_data = json.loads(qr_data)
            if self.is_valid_visitor_qr(visitor_data):
                self.show_visitor_info(visitor_data)
            else:
                self.show_generic_qr_info(qr_data)
        except json.JSONDecodeError:
            self.show_generic_qr_info(qr_data)
    
    def is_valid_visitor_qr(self, data):
        """Verifica si el QR contiene datos válidos de visitante"""
        required_fields = ['rut', 'nombre_completo', 'acompañante', 'sector']
        return all(field in data for field in required_fields)
    
    def show_visitor_info(self, visitor_data):
        """Muestra información específica de visitante"""
        info_text = f"""
        <b>👤 Visitante Detectado:</b><br><br>
        <b>Nombre:</b> {visitor_data.get('nombre_completo', 'N/A')}<br>
        <b>RUT:</b> {visitor_data.get('rut', 'N/A')}<br>
        <b>Acompañante:</b> {visitor_data.get('acompañante', 'N/A')}<br>
        <b>Sector:</b> {visitor_data.get('sector', 'N/A')}<br><br>
        <i>¿Desea registrar este visitante?</i>
        """
        self.qr_info_label.setText(info_text)
        
        # Mostrar botón para registrar
        self.show_register_button(visitor_data)
    
    def show_generic_qr_info(self, qr_data):
        """Muestra información genérica del QR"""
        self.qr_info_label.setText(f"<b>Contenido del QR:</b><br>{qr_data}")
    
    def show_register_button(self, visitor_data):
        """Muestra botón para registrar visitante"""
        # Crear botón temporal para registrar
        register_btn = QPushButton("✅ Registrar Visitante")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        # Conectar señal
        register_btn.clicked.connect(lambda: self.register_visitor_from_qr(visitor_data))
        
        # Agregar al layout
        info_layout = self.info_frame.layout()
        if info_layout:
            info_layout.addWidget(register_btn)
    
    def show_auto_register_button(self, parsed_data):
        """Muestra botón para registro automático con datos del carnet"""
        # Crear botón temporal para registro automático
        auto_btn = QPushButton("✅ Registrar Automáticamente")
        auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        # Conectar señal
        auto_btn.clicked.connect(lambda: self.open_auto_registration_with_carnet(parsed_data))
        
        # Agregar al layout
        info_layout = self.info_frame.layout()
        if info_layout:
            info_layout.addWidget(auto_btn)
    
    def show_manual_register_button(self, qr_data):
        """Muestra botón para registro manual desde QR de carnet"""
        # Crear botón temporal para registro manual
        manual_btn = QPushButton("📝 Registro Manual")
        manual_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        # Conectar señal
        manual_btn.clicked.connect(lambda: self.open_manual_registration_with_qr(qr_data))
        
        # Agregar al layout
        info_layout = self.info_frame.layout()
        if info_layout:
            info_layout.addWidget(manual_btn)
    
    def open_registration_with_rut(self, dialog, parsed_data):
        """Abre registro manual con RUT pre-rellenado"""
        try:
            # Cerrar el diálogo actual
            dialog.accept()
            
            # Cerrar también el info frame del escáner
            self.info_frame.setVisible(False)
            
            from core.visitor_form import VisitorFormDialog
            # Obtener el auth_manager de la ventana principal
            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)
            
            # Pre-rellenar RUT
            if parsed_data['rut']:
                form_dialog.rut_input.setText(parsed_data['rut'])
            
            # Mostrar mensaje informativo
            QMessageBox.information(
                self,
                "📋 RUT Pre-rellenado",
                f"El RUT {parsed_data['rut']} ha sido extraído automáticamente del carnet.\n\n"
                f"Por favor, complete los campos restantes:\n"
                f"• Nombre completo\n"
                f"• Acompañante\n"
                f"• Sector\n\n"
                f"Y confirme el registro."
            )
            
            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitor_model import VisitorManager
                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self, 
                            "✅ Éxito", 
                            f"Visitante {visitor.nombre_completo} registrado correctamente"
                        )
                    else:
                        QMessageBox.warning(
                            self, 
                            "⚠️ Advertencia", 
                            "El visitante ya existe en el sistema"
                        )
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al abrir registro:\n{str(e)}")
    
    def open_auto_registration_with_carnet(self, parsed_data):
        """Abre registro automático con datos extraídos del carnet"""
        try:
            from core.visitor_form import VisitorFormDialog
            # Obtener el auth_manager de la ventana principal
            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)
            
            # Pre-rellenar campos con datos extraídos
            if parsed_data['rut']:
                form_dialog.rut_input.setText(parsed_data['rut'])
            
            if parsed_data['nombre_completo']:
                form_dialog.nombre_input.setText(parsed_data['nombre_completo'])
            
            # Mostrar mensaje informativo
            QMessageBox.information(
                self,
                "📋 Datos Pre-rellenados",
                f"Se han extraído automáticamente:\n\n"
                f"• RUT: {parsed_data['rut'] if parsed_data['rut'] else 'No detectado'}\n"
                f"• Nombre: {parsed_data['nombre_completo'] if parsed_data['nombre_completo'] else 'No detectado'}\n\n"
                f"Por favor, completa los campos restantes y confirma el registro."
            )
            
            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitor_model import VisitorManager
                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self, 
                            "✅ Éxito", 
                            f"Visitante {visitor.nombre_completo} registrado correctamente"
                        )
                        self.info_frame.setVisible(False)
                    else:
                        QMessageBox.warning(
                            self, 
                            "⚠️ Advertencia", 
                            "El visitante ya existe en el sistema"
                        )
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al abrir registro automático:\n{str(e)}")
    
    def open_manual_registration_with_qr(self, qr_data):
        """Abre registro manual con datos del QR de carnet"""
        try:
            from core.visitor_form import VisitorFormDialog
            # Obtener el auth_manager de la ventana principal
            auth_manager = self.get_auth_manager()
            form_dialog = VisitorFormDialog(self, auth_manager=auth_manager)
            
            # Intentar extraer RUT del QR si es posible
            if 'rut' in qr_data.lower():
                # Buscar patrón de RUT en el texto
                import re
                rut_match = re.search(r'\d{7,8}[-]?\d', qr_data)
                if rut_match:
                    form_dialog.rut_input.setText(rut_match.group())
            
            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from core.visitor_model import VisitorManager
                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        QMessageBox.information(
                            self, 
                            "✅ Éxito", 
                            f"Visitante {visitor.nombre_completo} registrado correctamente"
                        )
                        self.info_frame.setVisible(False)
                    else:
                        QMessageBox.warning(
                            self, 
                            "⚠️ Advertencia", 
                            "El visitante ya existe en el sistema"
                        )
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al abrir registro manual:\n{str(e)}")
    
    def register_visitor_from_qr(self, visitor_data):
        """Registra el visitante desde los datos del QR"""
        try:
            from core.visitor_model import Visitor, VisitorManager
            
            # Crear visitante
            visitor = Visitor(
                rut=visitor_data['rut'],
                nombre_completo=visitor_data['nombre_completo'],
                acompañante=visitor_data['acompañante'],
                sector=visitor_data['sector']
            )
            
            # Agregar al manager
            manager = VisitorManager()
            if manager.add_visitor(visitor):
                QMessageBox.information(
                    self, 
                    "✅ Éxito", 
                    f"Visitante {visitor.nombre_completo} registrado correctamente"
                )
                self.info_frame.setVisible(False)
            else:
                QMessageBox.warning(
                    self, 
                    "⚠️ Advertencia", 
                    "El visitante ya existe en el sistema"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al registrar visitante:\n{str(e)}")
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        self.stop_camera()
        # Detener el timer de auto-procesamiento
        if hasattr(self, 'scanner_input_timer'):
            self.scanner_input_timer.stop()
        event.accept()

