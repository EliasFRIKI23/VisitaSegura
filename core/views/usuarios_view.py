# usuarios_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QFrame, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QDialogButtonBox,
    QGroupBox, QSpacerItem, QSizePolicy, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from core.ui.icon_loader import get_icon_for_emoji
from core.auth_manager import AuthManager
from datetime import datetime

# Importar colores del tema
try:
    from core.theme import (
        DUOC_PRIMARY, DUOC_SECONDARY, DUOC_SUCCESS, DUOC_DANGER, DUOC_INFO,
        DUOC_GRAY, DUOC_GRAY_DARK,
        darken_color as duoc_darken, get_standard_button_style
    )
    from core.ui import configure_modern_table, apply_modern_table_theme
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
        resolved_color = text_color or ('#000000' if color in [DUOC_SECONDARY, "#ffc107"] else '#ffffff')
        return f"""
            QPushButton {{
                background-color: {color};
                color: {resolved_color};
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

    def configure_modern_table(*args, **kwargs):  # type: ignore
        table = args[0]
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)

    def apply_modern_table_theme(table, dark_mode=False):  # type: ignore
        base_bg = "#0f172a" if dark_mode else "#ffffff"
        base_fg = "#e2e8f0" if dark_mode else "#1f2937"
        table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {base_bg};
                color: {base_fg};
                border: none;
            }}
            """
        )

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
        apply_modern_table_theme(self.users_table, self.dark_mode)
    
    def apply_widget_theme(self):
        """Aplica el tema a otros widgets de la vista"""
        if self.dark_mode:
            outer_bg = "#0b1220"
            card_bg = "#111827"
            secondary_bg = DUOC_GRAY_DARK  # Gris institucional oscuro
            text_color = "#e2e8f0"
            muted_color = "#94a3b8"
        else:
            outer_bg = "#f3f4f6"
            card_bg = "#ffffff"
            secondary_bg = "#f8f9fa"  # Gris claro institucional para tarjetas secundarias
            text_color = "#0f172a"
            muted_color = DUOC_GRAY  # Gris institucional para texto secundario

        self.main_container.setStyleSheet(f"""
            QFrame#usersMainContainer {{
                background-color: {outer_bg};
            }}
        """)

        self.header_card.setStyleSheet(f"""
            QFrame#usersHeaderCard {{
                background-color: {card_bg};
                border-radius: 24px;
                border: 1px solid rgba(148, 163, 184, {'0.25' if not self.dark_mode else '0.18'});
            }}
        """)

        self.actions_card.setStyleSheet(f"""
            QFrame#usersActionsCard {{
                background-color: {secondary_bg};
                border-radius: 20px;
                border: 1px solid rgba(148, 163, 184, {'0.2' if not self.dark_mode else '0.16'});
            }}
        """)

        self.table_card.setStyleSheet(f"""
            QFrame#usersTableCard {{
                background-color: {card_bg if not self.dark_mode else '#0f172a'};
                border-radius: 20px;
                border: 1px solid rgba(148, 163, 184, {'0.2' if not self.dark_mode else '0.18'});
            }}
        """)

        self.title_label.setStyleSheet(f"color: {text_color};")
        self.subtitle_label.setStyleSheet(f"color: {muted_color};")
        self.badge_label.setStyleSheet(
            "padding: 6px 14px; border-radius: 12px; font-size: 12px;"
            + ("background-color: rgba(14, 165, 233, 0.16); color: #38bdf8;"
               if self.dark_mode
               else f"background-color: rgba(56, 189, 248, 0.18); color: {DUOC_PRIMARY};")
        )
        self.info_label.setStyleSheet(f"color: {muted_color}; font-size: 12px;")

        variants_light = {
            "primary": ("#0ea5e9", "#0f172a"),
            "info": ("#1d4ed8", "#f8fafc"),
            "danger": ("#dc2626", "#f8fafc"),
            "neutral": ("#e2e8f0", "#1f2937"),
        }
        variants_dark = {
            "primary": ("#38bdf8", "#0f172a"),
            "info": ("#60a5fa", "#0f172a"),
            "danger": ("#f87171", "#0f172a"),
            "neutral": ("#1f2937", "#e2e8f0"),
        }
        palette = variants_dark if self.dark_mode else variants_light

        for button in self.action_buttons:
            variant = button.property("variant")
            bg_color, fg_color = palette.get(variant, ("#64748b", "#f8fafc"))
            if self.dark_mode:
                hover_color = self._mix_color(bg_color, "#ffffff", 0.18)
            else:
                hover_color = duoc_darken(bg_color, 0.12)
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {fg_color};
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:disabled {{
                    background-color: rgba(148, 163, 184, 0.25);
                    color: rgba(148, 163, 184, 0.8);
                }}
                """
            )
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.main_container = QFrame()
        self.main_container.setObjectName("usersMainContainer")
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)
        outer_layout.addWidget(self.main_container)

        # Encabezado
        self.header_card = QFrame()
        self.header_card.setObjectName("usersHeaderCard")
        header_layout = QVBoxLayout(self.header_card)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(12)

        self.title_label = QLabel("Gestión de Usuarios")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("Administra cuentas, roles y accesos al panel administrativo.")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setWordWrap(True)
        header_layout.addWidget(self.subtitle_label)

        # Crear layout horizontal para badge con icono
        badge_layout = QHBoxLayout()
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(6)
        
        badge_icon = get_icon_for_emoji("🔐", 16)
        if not badge_icon.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(badge_icon.pixmap(16, 16))
            badge_layout.addWidget(icon_label)
        
        self.badge_label = QLabel("Solo administradores")
        self.badge_label.setAlignment(Qt.AlignCenter)
        badge_layout.addWidget(self.badge_label)
        badge_layout.addStretch()
        
        badge_container = QWidget()
        badge_container.setLayout(badge_layout)
        header_layout.addWidget(badge_container, alignment=Qt.AlignLeft)

        main_layout.addWidget(self.header_card)

        # Acciones rápidas
        self.actions_card = QFrame()
        self.actions_card.setObjectName("usersActionsCard")
        actions_layout = QHBoxLayout(self.actions_card)
        actions_layout.setContentsMargins(24, 24, 24, 24)
        actions_layout.setSpacing(16)

        self.action_buttons = []

        self.btn_add = QPushButton("Nuevo usuario")
        self.btn_add.setIcon(get_icon_for_emoji("➕", 18))
        self.btn_add.clicked.connect(self.add_user)
        self._configure_action_button(self.btn_add, "primary")

        self.btn_edit = QPushButton("Editar seleccionado")
        self.btn_edit.setIcon(get_icon_for_emoji("✏️", 18))
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_edit.setEnabled(False)
        self._configure_action_button(self.btn_edit, "info")

        self.btn_delete = QPushButton("Eliminar usuario")
        self.btn_delete.setIcon(get_icon_for_emoji("🗑️", 18))
        self.btn_delete.clicked.connect(self.delete_user)
        self.btn_delete.setEnabled(False)
        self._configure_action_button(self.btn_delete, "danger")

        self.btn_refresh = QPushButton("Actualizar lista")
        self.btn_refresh.setIcon(get_icon_for_emoji("🔄", 18))
        self.btn_refresh.clicked.connect(self.load_users)
        self._configure_action_button(self.btn_refresh, "neutral")

        actions_layout.addWidget(self.btn_add)
        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_delete)
        actions_layout.addWidget(self.btn_refresh)
        actions_layout.addStretch()

        main_layout.addWidget(self.actions_card)

        # Tabla y contenedor
        self.table_card = QFrame()
        self.table_card.setObjectName("usersTableCard")
        table_layout = QVBoxLayout(self.table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "Usuario", "Nombre completo", "Rol", "Estado", "Último acceso"
        ])
        configure_modern_table(self.users_table, row_height=60)
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setHighlightSections(False)
        header_font = QFont()
        header_font.setPointSize(11)
        header_font.setBold(True)
        self.users_table.horizontalHeader().setFont(header_font)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.users_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.users_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.users_table.itemSelectionChanged.connect(self.on_selection_changed)
        table_layout.addWidget(self.users_table)

        main_layout.addWidget(self.table_card)

        # Información adicional
        # Crear layout horizontal para info con icono
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(6)
        info_layout.setAlignment(Qt.AlignCenter)
        
        info_icon = get_icon_for_emoji("💡", 16)
        if not info_icon.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(info_icon.pixmap(16, 16))
            info_layout.addWidget(icon_label)
        
        self.info_label = QLabel("Solo los administradores pueden gestionar usuarios.")
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.info_label)
        
        info_container = QWidget()
        info_container.setLayout(info_layout)
        main_layout.addWidget(info_container)

        # Botón para volver al menú principal (ubicado al final como en otras vistas)
        self.back_button = QPushButton("Volver al Menú Principal")
        self.back_button.setIcon(get_icon_for_emoji("⬅️", 18))
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setFixedHeight(44)
        self.back_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 184, 28, 0.1);
                color: {DUOC_SECONDARY};
                border: 2px solid {DUOC_SECONDARY};
                border-radius: 14px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background-color: {DUOC_SECONDARY};
                color: #000000;
            }}
            """
        )
        self.back_button.clicked.connect(self.go_back_to_main)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.apply_table_theme()
        self.apply_widget_theme()

    def _configure_action_button(self, button: QPushButton, variant: str):
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(46)
        button.setProperty("variant", variant)
        button.setStyleSheet("border-radius: 12px; font-weight: 600;")
        self.action_buttons.append(button)

    @staticmethod
    def _mix_color(color_hex: str, target_hex: str, ratio: float) -> str:
        """Mezcla dos colores hex en el porcentaje indicado."""
        color_hex = color_hex.lstrip("#")
        target_hex = target_hex.lstrip("#")
        base = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        target = tuple(int(target_hex[i:i+2], 16) for i in (0, 2, 4))
        blended = tuple(
            int(base[i] * (1 - ratio) + target[i] * ratio)
            for i in range(3)
        )
        return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"
    
    
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
                role_item.setTextAlignment(Qt.AlignCenter)
                if self.dark_mode:
                    badge_color = QColor(248, 113, 113, 90) if user.get('role') == 'admin' else QColor(96, 165, 250, 90)
                else:
                    badge_color = QColor(220, 53, 69, 60) if user.get('role') == 'admin' else QColor(59, 130, 246, 45)
                role_item.setBackground(badge_color)
                self.users_table.setItem(row, 2, role_item)
                
                # Estado
                status = "Activo" if user.get('is_active', True) else "Inactivo"
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignCenter)
                if self.dark_mode:
                    badge_color = QColor(34, 197, 94, 90) if user.get('is_active', True) else QColor(248, 113, 113, 90)
                else:
                    badge_color = QColor(34, 197, 94, 60) if user.get('is_active', True) else QColor(248, 113, 113, 60)
                status_item.setBackground(badge_color)
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
                last_login_item = QTableWidgetItem(last_login_str)
                last_login_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.users_table.setItem(row, 4, last_login_item)

                self.users_table.setRowHeight(row, 60)
            
            # La altura se controla manualmente para mantener la estética de la tarjeta
            
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

    def go_back_to_main(self):
        """Vuelve al menú principal de la aplicación."""
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "navigation_manager"):
                parent.navigation_manager.navigate_to("main")
                return
            if hasattr(parent, "go_to_main"):
                parent.go_to_main()
                return
            parent = parent.parent()
