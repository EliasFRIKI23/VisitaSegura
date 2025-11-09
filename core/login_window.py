# login_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QWidget, QSpacerItem, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QAction, QPalette, QColor, QGuiApplication, QFont, QPixmap
from PySide6.QtCore import Qt, Signal
from core.auth_manager import AuthManager
from core.theme import DUOC_PRIMARY

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
        self.resize(640, 640)
        self.setMinimumSize(600, 620)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Layout principal
        self.setup_ui()
        
        # Aplicar tema
        self.apply_theme()
        
        # Configurar conexiones
        self.setup_connections()
    
    def setup_ui(self):
        """Configura toda la interfaz de usuario"""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(0)

        container = QFrame()
        self.container_frame = container
        container.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border-radius: 24px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }
            """
        )
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        title_container = self.create_title_section()
        main_layout.addWidget(title_container)

        form_container = self.create_form_section()
        main_layout.addWidget(form_container)

        buttons_container = self.create_buttons_section()
        main_layout.addWidget(buttons_container)

        root_layout.addStretch(1)
        root_layout.addWidget(container)
        root_layout.addStretch(1)

    def create_title_section(self):
        """Crea la sección de títulos"""
        container = QFrame()
        container.setStyleSheet(
            """
            QFrame {
                background-color: transparent;
                border: none;
            }
            """
        )

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addStretch()

        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo Duoc .png")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("Duoc UC")
            logo_font = QFont()
            logo_font.setPointSize(16)
            logo_font.setBold(True)
            logo_label.setFont(logo_font)

        title_label = QLabel("VisitaSegura · Acceso Administrativo")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(logo_label, alignment=Qt.AlignLeft)
        layout.addWidget(title_label, alignment=Qt.AlignLeft)
        layout.addStretch()

        self.title_label = title_label
        self.subtitle_label = None
        return container

    def create_form_section(self):
        """Crea la sección del formulario"""
        container = QFrame()
        self.form_frame = container
        container.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 18px;
                border: 1px solid rgba(0, 0, 0, 0.06);
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(28)
        
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
        container.setStyleSheet(
            """
            QFrame {
                background-color: transparent;
                border: none;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Botón Cancelar
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setFixedHeight(48)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #6b7280;
                border: 1px solid rgba(0, 0, 0, 0.2);
                border-radius: 12px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
            """
        )

        # Botón Ingresar
        self.btn_login = QPushButton("Continuar")
        self.btn_login.setFixedHeight(48)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(16)
        buttons_row.addWidget(self.btn_cancel)
        buttons_row.addWidget(self.btn_login)
        layout.addLayout(buttons_row)

        tip_label = self.create_info_section()
        layout.addWidget(tip_label)

        return container

    def create_info_section(self):
        tip_label = QLabel("💡 Usa tu cuenta creada por el administrador para acceder al panel administrativo.")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        self.tip_label = tip_label
        return tip_label

    
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
            self.setStyleSheet(
                """
                QDialog {
                    background-color: #1f2a37;
                }
                """
            )
            if getattr(self, "title_label", None):
                self.title_label.setStyleSheet("color: #e2e8f0; background-color: transparent;")
            if getattr(self, "container_frame", None):
                self.container_frame.setStyleSheet(
                    """
                    QFrame {
                        background-color: #111827;
                        border-radius: 24px;
                        border: 1px solid rgba(255, 255, 255, 0.08);
                    }
                    """
                )
            if getattr(self, "form_frame", None):
                self.form_frame.setStyleSheet(
                    """
                    QFrame {
                        background-color: #1f2933;
                        border-radius: 18px;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                    }
                    """
                )
        else:
            self.setStyleSheet(
                """
                QDialog {
                    background-color: #eef1f6;
                }
                """
            )
            if getattr(self, "title_label", None):
                self.title_label.setStyleSheet("color: #1f2933; background-color: transparent;")
            if getattr(self, "container_frame", None):
                self.container_frame.setStyleSheet(
                    """
                    QFrame {
                        background-color: rgba(255, 255, 255, 0.92);
                        border-radius: 24px;
                        border: 1px solid rgba(0, 0, 0, 0.05);
                    }
                    """
                )
            if getattr(self, "form_frame", None):
                self.form_frame.setStyleSheet(
                    """
                    QFrame {
                        background-color: rgba(255, 255, 255, 0.9);
                        border-radius: 18px;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    }
                    """
                )
            if hasattr(self, "tip_label"):
                self.tip_label.setStyleSheet("color: #6b7280; font-size: 12px;")

        self.update_dark_mode_styles()

    def update_dark_mode_styles(self):
        """Actualiza los estilos para modo oscuro"""
        if self.dark_mode:
            input_style = """
                QLineEdit {
                    background-color: #1f2933;
                    border: 2px solid rgba(255, 255, 255, 0.15);
                    border-radius: 10px;
                    padding: 18px 25px;
                    font-size: 15px;
                    color: #f8fafc;
                    font-weight: 500;
                }
                QLineEdit:focus {
                    border-color: #38bdf8;
                    background-color: #25313d;
                }
                QLineEdit:hover {
                    border-color: #38bdf8;
                }
            """

            button_style = """
                QPushButton {
                    background-color: #1f2933;
                    color: #e2e8f0;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #25313d;
                }
            """

            primary_button_style = """
                QPushButton {
                    background-color: #0ea5e9;
                    color: #0f172a;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #38bdf8;
                }
            """

            if hasattr(self, "input_user"):
                self.input_user.setStyleSheet(input_style)
            if hasattr(self, "input_pass"):
                self.input_pass.setStyleSheet(input_style)
            if hasattr(self, "btn_cancel"):
                self.btn_cancel.setStyleSheet(button_style)
            if hasattr(self, "btn_login"):
                self.btn_login.setStyleSheet(primary_button_style)
            if hasattr(self, "tip_label"):
                self.tip_label.setStyleSheet("color: #cbd5f5; font-size: 12px;")
        else:
            default_input_style = """
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
                }
                QLineEdit:hover {
                    border-color: #007bff;
                    background-color: white;
                }
            """

            cancel_style = """
                QPushButton {
                    background-color: transparent;
                    color: #6b7280;
                    border: 1px solid rgba(0, 0, 0, 0.2);
                    border-radius: 12px;
                    padding: 10px 18px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.04);
                }
            """

            login_style = f"""
                QPushButton {{
                    background-color: {DUOC_PRIMARY};
                    color: #ffffff;
                    border-radius: 12px;
                    padding: 10px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #0059a5;
                }}
            """

            if hasattr(self, "input_user"):
                self.input_user.setStyleSheet(default_input_style)
            if hasattr(self, "input_pass"):
                self.input_pass.setStyleSheet(default_input_style)
            if hasattr(self, "btn_cancel"):
                self.btn_cancel.setStyleSheet(cancel_style)
            if hasattr(self, "btn_login"):
                self.btn_login.setStyleSheet(login_style)
            if hasattr(self, "tip_label"):
                self.tip_label.setStyleSheet("color: #6b7280; font-size: 12px;")
    
    def get_auth_manager(self) -> AuthManager:
        """Retorna el gestor de autenticación"""
        return self.auth_manager
