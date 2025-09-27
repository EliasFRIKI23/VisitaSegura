from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

class VisitasView(QWidget):
    """Vista para el registro de visitas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header con título y logo
        header_layout = QHBoxLayout()
        
        # Título
        title_layout = QVBoxLayout()
        title = QLabel("📋 Registro de Visitas")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        
        subtitle = QLabel("Sistema de registro y gestión de visitas con escaneo QR")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignLeft)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        
        # Logo Duoc
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🏢 Duoc UC")
            logo_font = QFont("Arial", 12, QFont.Bold)
            logo_label.setFont(logo_font)
        
        logo_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(logo_label)
        
        main_layout.addLayout(header_layout)
        
        # Contenido principal con opciones de registro
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.StyledPanel)
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)
        
        # Título de opciones
        options_title = QLabel("🎯 Opciones de Registro")
        options_title.setFont(QFont("Arial", 16, QFont.Bold))
        options_title.setAlignment(Qt.AlignCenter)
        options_title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        content_layout.addWidget(options_title)
        
        # Grid de opciones
        options_grid = QGridLayout()
        options_grid.setSpacing(20)
        
        # Opción 1: Escaneo QR
        qr_group = QGroupBox("📱 Escaneo de Código QR")
        qr_group.setFont(QFont("Arial", 12, QFont.Bold))
        qr_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #007bff;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #007bff;
            }
        """)
        qr_layout = QVBoxLayout(qr_group)
        
        qr_description = QLabel("""
        <p style="font-size: 14px; color: #495057; margin: 10px 0;">
        Escanea el código QR del visitante usando la cámara del dispositivo.
        </p>
        <p style="font-size: 12px; color: #6c757d; margin: 5px 0;">
        • Rápido y eficiente<br>
        • Datos pre-cargados<br>
        • Menos errores de tipeo
        </p>
        """)
        qr_description.setWordWrap(True)
        qr_layout.addWidget(qr_description)
        
        self.qr_scan_btn = QPushButton("📷 Escanear QR")
        self.qr_scan_btn.setFixedHeight(50)
        self.qr_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.qr_scan_btn.clicked.connect(self.open_qr_scanner)
        qr_layout.addWidget(self.qr_scan_btn)
        
        options_grid.addWidget(qr_group, 0, 0)
        
        # Opción 2: Registro Manual
        manual_group = QGroupBox("✏️ Registro Manual")
        manual_group.setFont(QFont("Arial", 12, QFont.Bold))
        manual_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #28a745;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #28a745;
            }
        """)
        manual_layout = QVBoxLayout(manual_group)
        
        manual_description = QLabel("""
        <p style="font-size: 14px; color: #495057; margin: 10px 0;">
        Registra visitantes ingresando los datos manualmente.
        </p>
        <p style="font-size: 12px; color: #6c757d; margin: 5px 0;">
        • Control total de los datos<br>
        • Validación en tiempo real<br>
        • Ideal para casos especiales
        </p>
        """)
        manual_description.setWordWrap(True)
        manual_layout.addWidget(manual_description)
        
        self.manual_register_btn = QPushButton("📝 Registro Manual")
        self.manual_register_btn.setFixedHeight(50)
        self.manual_register_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.manual_register_btn.clicked.connect(self.open_manual_registration)
        manual_layout.addWidget(self.manual_register_btn)
        
        options_grid.addWidget(manual_group, 0, 1)
        
        
        # Opción 4: Ver Visitantes Actuales
        visitors_group = QGroupBox("👥 Ver Visitantes")
        visitors_group.setFont(QFont("Arial", 12, QFont.Bold))
        visitors_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #6f42c1;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #6f42c1;
            }
        """)
        visitors_layout = QVBoxLayout(visitors_group)
        
        visitors_description = QLabel("""
        <p style="font-size: 14px; color: #495057; margin: 10px 0;">
        Consulta los visitantes actualmente en el establecimiento.
        </p>
        <p style="font-size: 12px; color: #6c757d; margin: 5px 0;">
        • Lista en tiempo real<br>
        • Gestión de salidas<br>
        • Historial completo
        </p>
        """)
        visitors_description.setWordWrap(True)
        visitors_layout.addWidget(visitors_description)
        
        self.view_visitors_btn = QPushButton("👥 Ver Visitantes")
        self.view_visitors_btn.setFixedHeight(50)
        self.view_visitors_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a32a3;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #4c2a85;
            }
        """)
        self.view_visitors_btn.clicked.connect(self.open_visitors_view)
        visitors_layout.addWidget(self.view_visitors_btn)
        
        options_grid.addWidget(visitors_group, 1, 0)
        
        content_layout.addLayout(options_grid)
        main_layout.addWidget(content_frame)
        
        # Botón de regreso
        back_button = QPushButton("⬅️ Volver al Menú Principal")
        back_button.setFixedSize(200, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        back_button.clicked.connect(self.go_to_main)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
    
    def open_qr_scanner(self):
        """Abre el escáner de códigos QR"""
        try:
            from ..qr_scanner import QRScannerDialog
            scanner_dialog = QRScannerDialog(self)
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
            form_dialog = VisitorFormDialog(self)
            if form_dialog.exec():
                visitor = form_dialog.get_visitor()
                if visitor:
                    from ..visitor_model import VisitorManager
                    manager = VisitorManager()
                    if manager.add_visitor(visitor):
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.information(
                            self, 
                            "✅ Éxito", 
                            f"Visitante {visitor.nombre_completo} registrado correctamente"
                        )
                    else:
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.warning(
                            self, 
                            "⚠️ Advertencia", 
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
