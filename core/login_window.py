from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QWidget, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QAction, QPalette, QColor, QGuiApplication, QFont, QPixmap
from PySide6.QtCore import Qt

class LoginWindow(QDialog):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.dark_mode = dark_mode
        self.setWindowTitle("🔐 Acceso Administrativo - VisitaSegura")
        self.setModal(True)
        
        # Configuración de ventana
        self.setFixedSize(480, 650)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Layout principal
        self.setup_ui()
        
        # Aplicar tema
        self.apply_theme()

    def setup_ui(self):
        """Configura toda la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)
        
        # === LOGO SECTION ===
        logo_container = self.create_logo_section()
        main_layout.addWidget(logo_container)
        
        # Espaciador
        main_layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # === TITLE SECTION ===
        title_container = self.create_title_section()
        main_layout.addWidget(title_container)
        
        # Espaciador
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # === FORM SECTION ===
        form_container = self.create_form_section()
        main_layout.addWidget(form_container)
        
        # Espaciador flexible
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # === BUTTONS SECTION ===
        buttons_container = self.create_buttons_section()
        main_layout.addWidget(buttons_container)

    def create_logo_section(self):
        """Crea la sección del logo"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            # Logo grande y bien visible
            scaled_pixmap = logo_pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setFixedSize(300, 150)
        else:
            logo_label.setText("🏢 Duoc UC")
            logo_font = QFont()
            logo_font.setPointSize(24)
            logo_font.setBold(True)
            logo_label.setFont(logo_font)
            logo_label.setFixedHeight(100)
        
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        return container

    def create_title_section(self):
        """Crea la sección de títulos"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Título principal
        self.title_label = QLabel("Acceso Administrativo")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # Subtítulo
        self.subtitle_label = QLabel("VisitaSegura - San Bernardo")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        return container

    def create_form_section(self):
        """Crea la sección del formulario"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e1e8ed;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Campo Correo Electrónico
        email_section = self.create_input_section("Correo electrónico:", "Ingrese su correo")
        layout.addLayout(email_section)
        
        # Campo Contraseña
        password_section = self.create_input_section("Contraseña:", "Ingrese su contraseña", is_password=True)
        layout.addLayout(password_section)
        
        return container

    def create_input_section(self, label_text, placeholder_text, is_password=False):
        """Crea una sección de entrada con etiqueta arriba"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Etiqueta
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        layout.addWidget(label)
        
        # Campo de entrada
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        input_field.setFixedHeight(55)  # Altura fija más grande
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 18px 25px;
                font-size: 15px;
                color: #2c3e50;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #007bff;
                background-color: white;
                box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
            }
            QLineEdit:hover {
                border-color: #007bff;
                background-color: white;
            }
        """)
        
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
            self.input_pass = input_field
        else:
            self.input_user = input_field
            
        layout.addWidget(input_field)
        return layout

    def create_buttons_section(self):
        """Crea la sección de botones"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Botón Cancelar
        self.btn_cancel = QPushButton("❌ Cancelar")
        self.btn_cancel.setFixedHeight(50)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #5a6268;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        # Botón Ingresar
        self.btn_login = QPushButton("✅ Ingresar")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #218838;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.btn_login.clicked.connect(self.accept)
        
        layout.addWidget(self.btn_cancel)
        layout.addWidget(self.btn_login)
        
        return container

    def apply_theme(self):
        """Aplica el tema actual (claro u oscuro)"""
        if self.dark_mode:
            # Modo oscuro
            self.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2c3e50, stop:1 #34495e);
                }
            """)
            
            # Textos en blanco para modo oscuro
            if hasattr(self, 'title_label'):
                self.title_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        background-color: transparent;
                        border: none;
                        margin: 0px;
                        padding: 0px;
                    }
                """)
            
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        background-color: transparent;
                        border: none;
                        margin: 0px;
                        padding: 0px;
                    }
                """)
            
            # Actualizar estilos para modo oscuro
            self.update_dark_mode_styles()
        else:
            # Modo claro
            self.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                }
            """)
            
            # Textos en negro para modo claro
            if hasattr(self, 'title_label'):
                self.title_label.setStyleSheet("""
                    QLabel {
                        color: #2c3e50;
                        background-color: transparent;
                        border: none;
                        margin: 0px;
                        padding: 0px;
                    }
                """)
            
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.setStyleSheet("""
                    QLabel {
                        color: #7f8c8d;
                        background-color: transparent;
                        border: none;
                        margin: 0px;
                        padding: 0px;
                    }
                """)

    def update_dark_mode_styles(self):
        """Actualiza los estilos para modo oscuro"""
        if self.dark_mode:
            # Actualizar campos de entrada para modo oscuro
            input_style = """
                QLineEdit {
                    background-color: white;
                    border: 2px solid #6c757d;
                    border-radius: 10px;
                    padding: 18px 25px;
                    font-size: 15px;
                    color: #2c3e50;
                    font-weight: 500;
                }
                QLineEdit:focus {
                    border-color: #17a2b8;
                    background-color: white;
                    box-shadow: 0 0 0 3px rgba(23, 162, 184, 0.1);
                }
                QLineEdit:hover {
                    border-color: #17a2b8;
                    background-color: white;
                }
            """
            
            if hasattr(self, 'input_user'):
                self.input_user.setStyleSheet(input_style)
            if hasattr(self, 'input_pass'):
                self.input_pass.setStyleSheet(input_style)