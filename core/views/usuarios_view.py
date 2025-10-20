# usuarios_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QFrame, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QDialogButtonBox,
    QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from core.auth_manager import AuthManager
from datetime import datetime

# Importar colores del tema
try:
    from core.theme import (
        DUOC_PRIMARY, DUOC_SECONDARY, DUOC_SUCCESS, DUOC_DANGER, DUOC_INFO,
        darken_color as duoc_darken, get_standard_button_style, get_standard_table_style
    )
except Exception:
    DUOC_PRIMARY = "#003A70"
    DUOC_SECONDARY = "#FFB81C"
    DUOC_SUCCESS = "#28a745"
    DUOC_DANGER = "#dc3545"
    DUOC_INFO = "#17a2b8"
    def duoc_darken(color, factor=0.2):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    def get_standard_button_style(color, text_color=None):
        return f"""
            QPushButton {{
                background-color: {color};
                color: {'#000000' if color in [DUOC_SECONDARY, "#ffc107"] else '#ffffff'};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {duoc_darken(color, 0.1)};
            }}
            QPushButton:disabled {{
                background-color: #6c757d;
                color: #adb5bd;
            }}
        """
    def get_standard_table_style():
        return """
            QTableWidget {
                background: white;
                color: black;
                gridline-color: #e9ecef;
                alternate-background-color: #f8f9fa;
                selection-background-color: #003A70;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 10px;
            }
        """

class UserFormDialog(QDialog):
    """Diálogo para crear/editar usuarios"""
    
    def __init__(self, parent=None, user_data=None, is_edit=False, auth_manager=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit = is_edit
        self.auth_manager = auth_manager or AuthManager()
        
        self.setWindowTitle("Editar Usuario" if is_edit else "Nuevo Usuario")
        self.setModal(True)
        self.setFixedSize(450, 400)  # Aumenté de 400x350 a 450x400
        
        self.setup_ui()
        self.setup_connections()
        
        if is_edit and user_data:
            self.load_user_data()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Editar Usuario" if self.is_edit else "Nuevo Usuario")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Formulario
        form_group = QGroupBox("Información del Usuario")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        # Usuario
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Ingrese nombre de usuario")
        form_layout.addRow("Usuario:", self.username_edit)
        
        # Contraseña
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Ingrese contraseña")
        form_layout.addRow("Contraseña:", self.password_edit)
        
        # Nombre completo
        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("Ingrese nombre completo")
        form_layout.addRow("Nombre Completo:", self.fullname_edit)
        
        # Rol
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "guardia"])
        form_layout.addRow("Rol:", self.role_combo)
        
        # Estado activo
        self.active_checkbox = QCheckBox("Usuario activo")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("Estado:", self.active_checkbox)
        
        layout.addWidget(form_group)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.cancel_button = button_box.button(QDialogButtonBox.Cancel)
        
        self.ok_button.setText("Guardar")
        self.cancel_button.setText("Cancelar")
        
        layout.addWidget(button_box)
        
        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #007bff;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton[text="Guardar"] {
                background-color: #28a745;
                color: white;
                border: none;
            }
            QPushButton[text="Guardar"]:hover {
                background-color: #218838;
            }
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
                color: white;
                border: none;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)
    
    def setup_connections(self):
        """Configura las conexiones"""
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def load_user_data(self):
        """Carga los datos del usuario en el formulario"""
        if self.user_data:
            self.username_edit.setText(self.user_data.get('username', ''))
            self.fullname_edit.setText(self.user_data.get('full_name', ''))
            
            role = self.user_data.get('role', 'guardia')
            index = self.role_combo.findText(role)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
            
            self.active_checkbox.setChecked(self.user_data.get('is_active', True))
            
            # En modo edición, hacer el campo usuario de solo lectura
            self.username_edit.setReadOnly(True)
            self.username_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #e9ecef;
                    color: #6c757d;
                }
            """)
    
    def get_form_data(self):
        """Retorna los datos del formulario"""
        return {
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'full_name': self.fullname_edit.text().strip(),
            'role': self.role_combo.currentText(),
            'is_active': self.active_checkbox.isChecked()
        }
    
    def validate_form(self):
        """Valida el formulario"""
        data = self.get_form_data()
        
        if not data['username']:
            QMessageBox.warning(self, "Error", "El nombre de usuario es requerido.")
            return False
        
        if not self.is_edit and not data['password']:
            QMessageBox.warning(self, "Error", "La contraseña es requerida.")
            return False
        
        if not data['full_name']:
            QMessageBox.warning(self, "Error", "El nombre completo es requerido.")
            return False
        
        return True

class UsuariosView(QWidget):
    """Vista para gestión de usuarios (solo administradores)"""
    
    def __init__(self, parent=None, auth_manager=None):
        super().__init__(parent)
        self.auth_manager = auth_manager or AuthManager()
        self.dark_mode = False  # Estado del tema
        self.setup_ui()
        # No cargar usuarios automáticamente, solo cuando se acceda a la vista
    
    def showEvent(self, event):
        """Se ejecuta cuando la vista se muestra"""
        super().showEvent(event)
        # Solo cargar usuarios cuando se muestre la vista
        self.load_users()
    
    def update_auth_manager(self, auth_manager):
        """Actualiza la instancia del AuthManager"""
        self.auth_manager = auth_manager
    
    def set_theme(self, dark_mode):
        """Establece el tema de la vista"""
        self.dark_mode = dark_mode
        self.apply_table_theme()
        self.apply_widget_theme()
    
    def apply_table_theme(self):
        """Aplica el tema a la tabla"""
        if self.dark_mode:
            # Tema oscuro
            self.users_table.setStyleSheet(f"""
                QTableWidget {{
                    gridline-color: #404040;
                    background-color: #2b2b2b;
                    alternate-background-color: #353535;
                    font-size: 12px;
                    border: none;
                    border-radius: 0px;
                    selection-background-color: {DUOC_SECONDARY};
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #ffffff;
                }}
                QTableWidget::item {{
                    padding: 12px 10px;
                    border-bottom: 1px solid #404040;
                    border-right: 1px solid #404040;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #ffffff;
                }}
                QTableWidget::item:selected {{
                    background-color: {DUOC_SECONDARY};
                    color: #000000;
                }}
                QTableWidget::item:hover {{
                    background-color: #404040;
                }}
                QHeaderView::section {{
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-weight: bold;
                    border: none;
                    padding: 12px 10px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    border-bottom: 2px solid {DUOC_SECONDARY};
                }}
                QHeaderView::section:hover {{
                    background-color: #404040;
                }}
            """)
        else:
            # Tema claro - usar estilo estandarizado
            self.users_table.setStyleSheet(get_standard_table_style())
    
    def apply_widget_theme(self):
        """Aplica el tema a otros widgets de la vista"""
        if self.dark_mode:
            # Tema oscuro para otros elementos
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            # Tema claro para otros elementos
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
            """)
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("👥 Gestión de Usuarios")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Administrar usuarios del sistema")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(subtitle_label)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Agregar Usuario")
        self.btn_add.clicked.connect(self.add_user)
        self.btn_add.setStyleSheet(get_standard_button_style(DUOC_SUCCESS))
        
        self.btn_edit = QPushButton("✏️ Editar Usuario")
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_edit.setEnabled(False)
        self.btn_edit.setStyleSheet(get_standard_button_style(DUOC_INFO))
        
        self.btn_delete = QPushButton("🗑️ Eliminar Usuario")
        self.btn_delete.clicked.connect(self.delete_user)
        self.btn_delete.setEnabled(False)
        self.btn_delete.setStyleSheet(get_standard_button_style(DUOC_DANGER))
        
        self.btn_refresh = QPushButton("🔄 Actualizar")
        self.btn_refresh.clicked.connect(self.load_users)
        self.btn_refresh.setStyleSheet(get_standard_button_style("#6c757d"))
        
        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_edit)
        buttons_layout.addWidget(self.btn_delete)
        buttons_layout.addWidget(self.btn_refresh)
        
        # Espaciador
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttons_layout.addItem(spacer)
        
        layout.addLayout(buttons_layout)
        
        # Tabla de usuarios
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "Usuario", "Nombre Completo", "Rol", "Estado", "Último Login"
        ])
        
        # Configurar tabla
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Usuario
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Rol
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Último Login
        
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.apply_table_theme()
        
        # Conectar selección
        self.users_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.users_table)
        
        # Información de usuarios
        info_label = QLabel("💡 Solo los administradores pueden gestionar usuarios")
        info_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
    
    
    def load_users(self):
        """Carga los usuarios en la tabla"""
        if not self.auth_manager.is_admin():
            QMessageBox.warning(
                self, 
                "Acceso Denegado", 
                "Solo los administradores pueden gestionar usuarios."
            )
            return
        
        try:
            users = self.auth_manager.get_all_users()
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                # Usuario
                self.users_table.setItem(row, 0, QTableWidgetItem(user.get('username', '')))
                
                # Nombre completo
                self.users_table.setItem(row, 1, QTableWidgetItem(user.get('full_name', '')))
                
                # Rol
                role_item = QTableWidgetItem(user.get('role', '').title())
                if self.dark_mode:
                    if user.get('role') == 'admin':
                        role_item.setBackground(QColor(220, 53, 69, 80))  # Rojo más visible en oscuro
                    else:
                        role_item.setBackground(QColor(40, 167, 69, 80))  # Verde más visible en oscuro
                else:
                    if user.get('role') == 'admin':
                        role_item.setBackground(QColor(220, 53, 69, 50))  # Rojo suave en claro
                    else:
                        role_item.setBackground(QColor(40, 167, 69, 50))  # Verde suave en claro
                self.users_table.setItem(row, 2, role_item)
                
                # Estado
                status = "Activo" if user.get('is_active', True) else "Inactivo"
                status_item = QTableWidgetItem(status)
                if self.dark_mode:
                    if user.get('is_active', True):
                        status_item.setBackground(QColor(40, 167, 69, 80))  # Verde más visible en oscuro
                    else:
                        status_item.setBackground(QColor(220, 53, 69, 80))  # Rojo más visible en oscuro
                else:
                    if user.get('is_active', True):
                        status_item.setBackground(QColor(40, 167, 69, 50))  # Verde suave en claro
                    else:
                        status_item.setBackground(QColor(220, 53, 69, 50))  # Rojo suave en claro
                self.users_table.setItem(row, 3, status_item)
                
                # Último login
                last_login = user.get('last_login')
                if last_login:
                    if isinstance(last_login, datetime):
                        last_login_str = last_login.strftime("%d/%m/%Y %H:%M")
                    else:
                        last_login_str = str(last_login)
                else:
                    last_login_str = "Nunca"
                self.users_table.setItem(row, 4, QTableWidgetItem(last_login_str))
            
            # Ajustar altura de filas
            self.users_table.resizeRowsToContents()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al cargar usuarios: {str(e)}"
            )
    
    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        selected_rows = self.users_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)
    
    def get_selected_user(self):
        """Retorna el usuario seleccionado"""
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            username = self.users_table.item(current_row, 0).text()
            users = self.auth_manager.get_all_users()
            for user in users:
                if user.get('username') == username:
                    return user
        return None
    
    def add_user(self):
        """Abre el diálogo para agregar un nuevo usuario"""
        dialog = UserFormDialog(self, is_edit=False, auth_manager=self.auth_manager)
        if dialog.exec() == QDialog.Accepted:
            if dialog.validate_form():
                data = dialog.get_form_data()
                
                # Verificar que el usuario no exista
                users = self.auth_manager.get_all_users()
                if any(user.get('username') == data['username'] for user in users):
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "Ya existe un usuario con ese nombre."
                    )
                    return
                
                # Crear usuario usando AuthManager
                if self.auth_manager.add_user(
                    data['username'],
                    data['password'],
                    data['full_name'],
                    data['role']
                ):
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        f"Usuario '{data['username']}' creado correctamente."
                    )
                    self.load_users()
                else:
                    QMessageBox.critical(
                        self, 
                        "Error", 
                        "No se pudo crear el usuario."
                    )
    
    def edit_user(self):
        """Abre el diálogo para editar el usuario seleccionado"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para editar.")
            return
        
        dialog = UserFormDialog(self, user_data=user, is_edit=True, auth_manager=self.auth_manager)
        if dialog.exec() == QDialog.Accepted:
            if dialog.validate_form():
                data = dialog.get_form_data()
                
                # Actualizar usuario
                update_data = {
                    'full_name': data['full_name'],
                    'role': data['role'],
                    'is_active': data['is_active']
                }
                
                # Si se proporcionó nueva contraseña, actualizarla
                if data['password']:
                    update_data['password'] = data['password']
                
                if self.auth_manager.update_user(user['username'], **update_data):
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        f"Usuario '{user['username']}' actualizado correctamente."
                    )
                    self.load_users()
                else:
                    QMessageBox.critical(
                        self, 
                        "Error", 
                        "No se pudo actualizar el usuario."
                    )
    
    def delete_user(self):
        """Elimina el usuario seleccionado"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar.")
            return
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            f"¿Está seguro de que desea eliminar el usuario '{user['username']}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.auth_manager.delete_user(user['username']):
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"Usuario '{user['username']}' eliminado correctamente."
                )
                self.load_users()
            else:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    "No se pudo eliminar el usuario. Verifique que no sea el último administrador."
                )
