# login_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QWidget, QSpacerItem, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QAction, QPalette, QColor, QGuiApplication, QFont, QPixmap
from PySide6.QtCore import Qt, Signal
from core.auth_manager import AuthManager

class LoginDialog(QDialog):
    """Ventana de login con diseño profesional mejorado"""
    
    login_successful = Signal()  # Señal emitida cuando el login es exitoso
    
    def __init__(self, dark_mode=False, parent=None):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.auth_manager = AuthManager()
        self.setWindowTitle("🔐 Acceso Administrativo - VisitaSegura")
        self.setModal(True)
        
        # Configuración de ventana
        self.setFixedSize(520, 720)  # Aumenté de 480x650 a 520x720
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Layout principal
        self.setup_ui()
        
        # Aplicar tema
        self.apply_theme()
        
        # Configurar conexiones
        self.setup_connections()
    
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
        
        # === INFO SECTION ===
        info_container = self.create_info_section()
        main_layout.addWidget(info_container)

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
        layout.setSpacing(35)  # Aumenté de 25 a 35 para más espacio entre campos
        
        # Campo Usuario
        user_section = self.create_input_section("Usuario:", "Ingrese su nombre de usuario")
        layout.addLayout(user_section)
        
        # Campo Contraseña
        password_section = self.create_input_section("Contraseña:", "Ingrese su contraseña", is_password=True)
        layout.addLayout(password_section)
        
        return container

    def create_input_section(self, label_text, placeholder_text, is_password=False):
        """Crea una sección de entrada con etiqueta arriba"""
        layout = QVBoxLayout()
        layout.setSpacing(12)  # Aumenté de 8 a 12 para más espacio entre label y campo
        
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
        
        layout.addWidget(self.btn_cancel)
        layout.addWidget(self.btn_login)
        
        return container
    
    def create_info_section(self):
        """Crea la sección de información"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(5)
        
        # Información de usuarios por defecto
        info_label = QLabel("💡 Usuarios por defecto:")
        info_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        users_label = QLabel("• admin / admin123\n• guardia1 / guardia123")
        users_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 11px;
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
                line-height: 1.4;
            }
        """)
        users_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(users_label)
        
        return container
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.btn_login.clicked.connect(self.attempt_login)
        self.btn_cancel.clicked.connect(self.reject)
        self.input_pass.returnPressed.connect(self.attempt_login)
        self.input_user.returnPressed.connect(self.input_pass.setFocus)
    
    def attempt_login(self):
        """Intenta realizar el login"""
        username = self.input_user.text().strip()
        password = self.input_pass.text()
        
        if not username or not password:
            QMessageBox.warning(
                self, 
                "Campos Requeridos", 
                "Por favor, complete todos los campos."
            )
            return
        
        # Deshabilitar botón durante la autenticación
        self.btn_login.setEnabled(False)
        self.btn_login.setText("🔄 Verificando...")
        
        # Intentar autenticación usando el AuthManager
        if self.auth_manager.login(username, password):
            # Login exitoso
            user = self.auth_manager.get_current_user()
            QMessageBox.information(
                self, 
                "Login Exitoso", 
                f"Bienvenido, {user['full_name']}!\n\nRol: {user['role'].title()}"
            )
            
            # Emitir señal de éxito
            self.login_successful.emit()
            self.accept()
        else:
            # Login fallido
            QMessageBox.critical(
                self, 
                "Error de Autenticación", 
                "Usuario o contraseña incorrectos.\n\nVerifique sus credenciales e intente nuevamente."
            )
            
            # Limpiar campo de contraseña
            self.input_pass.clear()
            self.input_pass.setFocus()
        
        # Rehabilitar botón
        self.btn_login.setEnabled(True)
        self.btn_login.setText("✅ Ingresar")

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
    
    def get_auth_manager(self) -> AuthManager:
        """Retorna el gestor de autenticación"""
        return self.auth_manager
