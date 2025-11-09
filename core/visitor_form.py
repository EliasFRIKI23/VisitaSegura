from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QLabel,
    QMessageBox,
    QWidget,
    QToolButton,
    QGroupBox,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .visitors import Visitor, VisitorManager

# Importar funciones de normalización de RUT
try:
    from .theme import normalize_rut, format_rut_display, validate_rut_dv
    from .current_user_manager import get_current_user
except Exception:
    def normalize_rut(rut_input):
        """Fallback si no se puede importar la función"""
        return rut_input
    def format_rut_display(rut):
        """Fallback si no se puede importar la función"""
        return rut
    def validate_rut_dv(numero, dv):
        """Fallback si no se puede importar la función"""
        return True
    def get_current_user():
        """Fallback si no se puede importar la función"""
        return "Sistema"

class VisitorFormDialog(QDialog):
    def __init__(self, parent=None, visitor=None, auth_manager=None, use_modern_theme=False):
        super().__init__(parent)
        self.visitor = visitor
        self.is_edit_mode = visitor is not None
        self.visitor_manager = VisitorManager()
        self.auth_manager = auth_manager  # Guardar referencia al AuthManager
        self.dark_mode = getattr(parent, "dark_mode", False)
        self.use_modern_theme = use_modern_theme
        
        self.setWindowTitle("Editar Visitante" if self.is_edit_mode else "Registrar Nuevo Visitante")
        self.setModal(True)
        self.resize(500, 480)
        
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
        if self.is_edit_mode:
            self.load_visitor_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.main_container = QFrame()
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(28, 28, 28, 20)
        container_layout.setSpacing(20)
        outer_layout.addWidget(self.main_container)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        header_layout.setAlignment(Qt.AlignLeft)

        self.title_icon = QLabel("👤")
        self.title_icon.setFont(QFont("Segoe UI Emoji", 28))
        header_layout.addWidget(self.title_icon)

        self.title_label = QLabel("Registro de visitante" if not self.is_edit_mode else "Editar visitante")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()
        container_layout.addLayout(header_layout)

        self.personal_group = QGroupBox("Información personal")
        self.personal_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        personal_layout = QFormLayout(self.personal_group)
        personal_layout.setSpacing(16)
        personal_layout.setLabelAlignment(Qt.AlignLeft)
        
        # RUT con tooltip y normalización automática
        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("Ej: 12345678-9 o 123456789")
        self.rut_input.setToolTip("🔍 Ingrese el RUT del visitante (se formateará automáticamente)")
        
        rut_help = QToolButton()
        rut_help.setText("?")
        rut_help.setToolTip("El RUT se normaliza automáticamente al formato XX.XXX.XXX-X. Acepta cualquier formato de entrada.")
        rut_help.setMaximumSize(25, 25)
        
        rut_layout = QHBoxLayout()
        rut_layout.addWidget(self.rut_input)
        rut_layout.addWidget(rut_help)
        personal_layout.addRow("🆔 RUT:", rut_layout)
        
        # Nombre completo con tooltip
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre y apellidos completos")
        self.nombre_input.setToolTip("👤 Ingrese el nombre completo del visitante")
        
        nombre_help = QToolButton()
        nombre_help.setText("?")
        nombre_help.setToolTip("Ingrese nombre y apellidos completos (mínimo 3 caracteres)")
        nombre_help.setMaximumSize(25, 25)
        
        nombre_layout = QHBoxLayout()
        nombre_layout.addWidget(self.nombre_input)
        nombre_layout.addWidget(nombre_help)
        personal_layout.addRow("👤 Nombre Completo:", nombre_layout)
        
        self.visit_group = QGroupBox("Información de visita")
        self.visit_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        visit_layout = QFormLayout(self.visit_group)
        visit_layout.setSpacing(16)
        visit_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Acompañante con tooltip
        self.acompañante_input = QLineEdit()
        self.acompañante_input.setPlaceholderText("Persona que invita o recibe al visitante")
        self.acompañante_input.setToolTip("🤝 Ingrese el nombre de quien invita al visitante")
        
        acompañante_help = QToolButton()
        acompañante_help.setText("?")
        acompañante_help.setToolTip("Nombre de la persona que invita o recibe al visitante en el establecimiento")
        acompañante_help.setMaximumSize(25, 25)
        
        acompañante_layout = QHBoxLayout()
        acompañante_layout.addWidget(self.acompañante_input)
        acompañante_layout.addWidget(acompañante_help)
        visit_layout.addRow("🤝 Acompañante:", acompañante_layout)
        
        # Sector con tooltip
        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["Financiamiento", "CITT", "Auditorio", "Administración"])
        self.sector_combo.setToolTip("🏢 Seleccione el sector al que se dirige el visitante")
        
        sector_help = QToolButton()
        sector_help.setText("?")
        sector_help.setToolTip("Sector del establecimiento donde se dirigirá el visitante")
        sector_help.setMaximumSize(25, 25)
        
        sector_layout = QHBoxLayout()
        sector_layout.addWidget(self.sector_combo)
        sector_layout.addWidget(sector_help)
        visit_layout.addRow("🏢 Sector:", sector_layout)
        container_layout.addWidget(self.personal_group)
        container_layout.addWidget(self.visit_group)

        button_row = QHBoxLayout()
        button_row.addStretch()

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setMinimumHeight(42)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)

        save_text = "Guardar" if not self.is_edit_mode else "Actualizar"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setMinimumHeight(42)
        self.save_btn.setCursor(Qt.PointingHandCursor)

        button_row.addWidget(self.cancel_btn)
        button_row.addWidget(self.save_btn)
        container_layout.addLayout(button_row)
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.save_visitor)
        
        # Conectar normalización automática del RUT
        self.rut_input.textChanged.connect(self.normalize_rut_input)
        self.rut_input.editingFinished.connect(self.finalize_rut_format)
    
    def load_visitor_data(self):
        """Carga los datos del visitante en el formulario"""
        if self.visitor:
            self.rut_input.setText(self.visitor.rut)
            self.nombre_input.setText(self.visitor.nombre_completo)
            self.acompañante_input.setText(self.visitor.acompañante)
            
            # Establecer el sector en el combo
            sector_index = self.sector_combo.findText(self.visitor.sector)
            if sector_index >= 0:
                self.sector_combo.setCurrentIndex(sector_index)
    
    def normalize_rut_input(self):
        """Normaliza el RUT mientras el usuario escribe"""
        current_text = self.rut_input.text()
        if current_text:
            # Solo normalizar si el texto tiene más de 7 caracteres
            if len(current_text.replace('.', '').replace('-', '').replace(' ', '')) >= 8:
                normalized = normalize_rut(current_text)
                if normalized and normalized != current_text:
                    # Evitar bucles infinitos desconectando temporalmente la señal
                    self.rut_input.textChanged.disconnect()
                    self.rut_input.setText(normalized)
                    self.rut_input.textChanged.connect(self.normalize_rut_input)
    
    def finalize_rut_format(self):
        """Formatea el RUT cuando el usuario termina de escribir"""
        current_text = self.rut_input.text().strip()
        if current_text:
            # Usar la función mejorada con información detallada
            try:
                from .theme import normalize_rut_with_info
                normalized, error_msg, correct_dv = normalize_rut_with_info(current_text)
                
                if normalized:
                    self.rut_input.setText(normalized)
                else:
                    # Mostrar mensaje de error más informativo
                    if correct_dv:
                        # Sugerir el RUT correcto
                        rut_clean = ''.join(c for c in current_text.upper() if c.isdigit() or c == 'K')
                        if len(rut_clean) >= 8:
                            numero = rut_clean[:-1] if len(rut_clean) > 8 else rut_clean[:7]
                            rut_correcto = f"{numero}-{correct_dv}"
                            
                            reply = QMessageBox.question(
                                self,
                                "RUT Inválido",
                                f"{error_msg}\n\n¿Desea usar el RUT correcto: {rut_correcto}?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes
                            )
                            
                            if reply == QMessageBox.Yes:
                                self.rut_input.setText(normalize_rut(rut_correcto))
                                return
                    
                    QMessageBox.warning(
                        self, 
                        "RUT Inválido", 
                        f"{error_msg}\n\nPor favor, ingrese un RUT válido con formato:\n"
                        "• 12345678-5\n"
                        "• 123456785\n"
                        "• 12.345.678-5"
                    )
                    self.rut_input.setFocus()
            except ImportError:
                # Fallback a la función original
                normalized = normalize_rut(current_text)
                if normalized:
                    self.rut_input.setText(normalized)
                else:
                    QMessageBox.warning(
                        self, 
                        "RUT Inválido", 
                        f"El RUT ingresado '{current_text}' no es válido.\n\n"
                        "Por favor, ingrese un RUT válido con formato:\n"
                        "• 12345678-9\n"
                        "• 123456789\n"
                        "• 12.345.678-9"
                    )
                    self.rut_input.setFocus()
    
    def validate_form(self) -> bool:
        """Valida los datos del formulario"""
        errors = []
        
        # Validar RUT
        rut = self.rut_input.text().strip()
        if not rut:
            errors.append("El RUT es obligatorio")
        else:
            # Normalizar y validar el RUT
            normalized_rut = normalize_rut(rut)
            if not normalized_rut:
                errors.append("El RUT ingresado no es válido")
            else:
                # Actualizar el campo con el RUT normalizado
                self.rut_input.setText(normalized_rut)
        
        # Validar nombre
        nombre = self.nombre_input.text().strip()
        if not nombre:
            errors.append("El nombre completo es obligatorio")
        elif len(nombre) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
        
        # Validar acompañante
        acompañante = self.acompañante_input.text().strip()
        if not acompañante:
            errors.append("El acompañante es obligatorio")
        elif len(acompañante) < 3:
            errors.append("El nombre del acompañante debe tener al menos 3 caracteres")
        
        if errors:
            error_text = "⚠️ <b>Errores de Validación:</b><br><br>" + "<br>".join([f"• {error}" for error in errors])
            QMessageBox.warning(self, "⚠️ Errores de Validación", error_text)
            return False
        
        return True
    
    def save_visitor(self):
        """Guarda o actualiza el visitante"""
        if not self.validate_form():
            return
        
        # Verificar cupo máximo solo para nuevos visitantes
        if not self.is_edit_mode:
            selected_sector = self.sector_combo.currentText()
            current_visitors = self.visitor_manager.get_visitors_by_sector(selected_sector)
            current_count = len([v for v in current_visitors if v.estado == "Dentro"])
            
            if current_count >= 20:
                reply = QMessageBox.question(
                    self, 
                    "⚠️ Cupo Máximo Alcanzado",
                    f"La zona {selected_sector} ya tiene {current_count} visitantes (cupo máximo: 20).\n\n"
                    f"¿Estás seguro que quieres agregar más visitantes a esta zona?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
        
        try:
            if self.is_edit_mode and self.visitor:
                # Modo edición - usar RUT normalizado
                normalized_rut = normalize_rut(self.rut_input.text().strip())
                self.visitor.rut = normalized_rut if normalized_rut else self.rut_input.text().strip()
                self.visitor.nombre_completo = self.nombre_input.text().strip()
                self.visitor.acompañante = self.acompañante_input.text().strip()
                self.visitor.sector = self.sector_combo.currentText()
                # No cambiar el usuario registrador en modo edición
                self.accept()
            else:
                # Modo creación - usar RUT normalizado y capturar usuario registrador
                normalized_rut = normalize_rut(self.rut_input.text().strip())
                
                # Obtener usuario actual del sistema centralizado
                current_user = get_current_user()
                
                visitor = Visitor(
                    rut=normalized_rut if normalized_rut else self.rut_input.text().strip(),
                    nombre_completo=self.nombre_input.text().strip(),
                    acompañante=self.acompañante_input.text().strip(),
                    sector=self.sector_combo.currentText(),
                    usuario_registrador=current_user
                )
                self.visitor = visitor
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"🚫 Error al guardar el visitante:<br><br>{str(e)}")
    
    def get_visitor(self) -> Visitor:
        """Retorna el visitante creado o editado"""
        return self.visitor

    def apply_theme(self):
        if not self.use_modern_theme:
            return

        if self.dark_mode:
            main_bg = "#0b1220"
            card_bg = "#111827"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#e2e8f0"
            muted_color = "#94a3b8"
            input_bg = "#0f172a"
            input_border = "rgba(148, 163, 184, 0.35)"
            input_fg = "#f8fafc"
            danger = "#f87171"
            success = "#38bdf8"
        else:
            main_bg = "#f3f4f6"
            card_bg = "#ffffff"
            border_color = "rgba(148, 163, 184, 0.2)"
            text_color = "#0f172a"
            muted_color = "#64748b"
            input_bg = "#ffffff"
            input_border = "rgba(148, 163, 184, 0.3)"
            input_fg = "#1f2937"
            danger = "#dc2626"
            success = "#0ea5e9"

        self.setStyleSheet(f"QDialog {{ background-color: {main_bg}; }}")
        self.main_container.setStyleSheet(
            f"QFrame {{ background-color: {card_bg}; border-radius: 24px; border: 1px solid {border_color}; }}"
        )
        self.title_label.setStyleSheet(f"color: {text_color};")
        self.subtitle_label = None  # compatibilidad
        self.title_icon.setStyleSheet(f"color: {success};")

        for group in (self.personal_group, self.visit_group):
            group.setStyleSheet(
                f"QGroupBox {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 18px; margin-top: 16px; padding: 20px; color: {text_color}; }}"
            )

        input_style = (
            f"QLineEdit {{ background-color: {input_bg}; color: {input_fg}; border: 1px solid {input_border}; border-radius: 12px; padding: 12px; font-size: 14px; }}"
            "QLineEdit:focus { border: 1px solid #38bdf8; }"
        )
        self.rut_input.setStyleSheet(input_style)
        self.nombre_input.setStyleSheet(input_style)
        self.acompañante_input.setStyleSheet(input_style)

        combo_style = (
            f"QComboBox {{ background-color: {input_bg}; color: {input_fg}; border: 1px solid {input_border}; border-radius: 12px; padding: 0 12px; min-height: 40px; }}"
            "QComboBox::drop-down { border: none; width: 28px; }"
            f"QComboBox::down-arrow {{ border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid {input_fg}; margin-right: 10px; }}"
            f"QComboBox QAbstractItemView {{ background-color: {card_bg}; color: {input_fg}; border: 1px solid {border_color}; border-radius: 12px; padding: 6px; selection-background-color: {success}; selection-color: #0f172a; }}"
        )
        self.sector_combo.setStyleSheet(combo_style)

        action_style = (
            f"QToolButton {{ background-color: transparent; border: 1px solid {border_color}; border-radius: 10px; padding: 4px 8px; color: {muted_color}; font-weight: 600; }}"
        )
        for tool_btn in self.findChildren(QToolButton):
            tool_btn.setStyleSheet(action_style)

        self.cancel_btn.setStyleSheet(self._button_style(danger, "#ffffff"))
        self.save_btn.setStyleSheet(self._button_style(success, "#0f172a" if self.dark_mode else "#ffffff"))

    @staticmethod
    def _button_style(bg_color: str, text_color: str) -> str:
        darker = VisitorFormDialog._darken_color(bg_color, 0.15)
        return (
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 16px;
                padding: 0 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {darker}; }}
            """
        )

    @staticmethod
    def _darken_color(color: str, factor: float = 0.2) -> str:
        color = color.lstrip("#")
        r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

class QuickVisitorForm(QWidget):
    """Formulario rápido para registro de visitantes desde la lista"""
    def __init__(self, parent=None, auth_manager=None):
        super().__init__(parent)
        self.visitor_manager = VisitorManager()
        self.auth_manager = auth_manager  # Guardar referencia al AuthManager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        title_layout = QHBoxLayout()
        self.title_icon = QLabel("⚡")
        self.title_icon.setFont(QFont("Arial", 20))
        self.title_label = QLabel("Registro Rápido")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setStyleSheet("padding-bottom: 6px;")
        title_layout.addWidget(self.title_icon)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        self.form_group = QGroupBox("📝 Datos del Visitante")
        self.form_group.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout = QFormLayout(self.form_group)
        form_layout.setSpacing(18)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setHorizontalSpacing(20)

        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("Ej: 12.345.678-9")
        self.rut_input.setMinimumHeight(42)
        form_layout.addRow("🆔 RUT", self.rut_input)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre completo del visitante")
        self.nombre_input.setMinimumHeight(42)
        form_layout.addRow("👤 Nombre", self.nombre_input)

        self.acompañante_input = QLineEdit()
        self.acompañante_input.setPlaceholderText("Nombre de quien invita")
        self.acompañante_input.setMinimumHeight(42)
        form_layout.addRow("🤝 Acompañante", self.acompañante_input)

        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["Financiamiento", "CITT", "Auditorio", "Administración"])
        self.sector_combo.setMinimumHeight(42)
        form_layout.addRow("🏢 Sector", self.sector_combo)

        layout.addWidget(self.form_group)

        self.registrar_btn = QPushButton("🚀 Registrar Rápido")
        self.registrar_btn.setMinimumHeight(46)
        self.registrar_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.registrar_btn)

        layout.addStretch()
        self.setMinimumHeight(400)

    def apply_theme(self, dark_mode: bool):
        if dark_mode:
            card_bg = "#111827"
            border = "rgba(148, 163, 184, 0.25)"
            title_color = "#e2e8f0"
            label_color = "#cbd5f5"
            input_bg = "#0f172a"
            input_fg = "#f8fafc"
            input_border = "rgba(148, 163, 184, 0.35)"
            button_bg = "#38bdf8"
            button_fg = "#0f172a"
            button_hover = "#0ea5e9"
        else:
            card_bg = "#ffffff"
            border = "rgba(148, 163, 184, 0.2)"
            title_color = "#0f172a"
            label_color = "#475569"
            input_bg = "#ffffff"
            input_fg = "#1f2937"
            input_border = "rgba(148, 163, 184, 0.35)"
            button_bg = "#0f172a"
            button_fg = "#f8fafc"
            button_hover = "#1e293b"

        self.title_label.setStyleSheet(f"color: {title_color};")
        self.form_group.setStyleSheet(
            f"QGroupBox {{ background-color: {card_bg}; border-radius: 18px;"
            f"border: 1px solid {border}; margin-top: 18px; padding: 16px; color: {label_color}; }}"
        )

        input_style = (
            f"QLineEdit {{ background-color: {input_bg}; color: {input_fg};"
            f"border: 1px solid {input_border}; border-radius: 12px; padding: 0 14px; }}"
            f"QLineEdit:focus {{ border: 1px solid #38bdf8; }}"
        )
        combo_style = (
            f"QComboBox {{ background-color: {input_bg}; color: {input_fg};"
            f"border: 1px solid {input_border}; border-radius: 12px; padding: 0 14px; }}"
            "QComboBox::drop-down { border: none; }"
            f"QComboBox QAbstractItemView {{ background-color: {card_bg}; color: {input_fg}; border-radius: 12px; border: 1px solid {border}; }}"
        )
        self.rut_input.setStyleSheet(input_style)
        self.nombre_input.setStyleSheet(input_style)
        self.acompañante_input.setStyleSheet(input_style)
        self.sector_combo.setStyleSheet(combo_style)

        self.registrar_btn.setStyleSheet(
            f"QPushButton {{ background-color: {button_bg}; color: {button_fg};"
            "border-radius: 14px; font-weight: 600; }}"
            f"QPushButton:hover {{ background-color: {button_hover}; }}"
        )

        self.title_icon.setStyleSheet(f"color: {title_color};")
    
    def normalize_rut_input(self):
        """Normaliza el RUT mientras el usuario escribe"""
        current_text = self.rut_input.text()
        if current_text:
            # Solo normalizar si el texto tiene más de 7 caracteres
            if len(current_text.replace('.', '').replace('-', '').replace(' ', '')) >= 8:
                normalized = normalize_rut(current_text)
                if normalized and normalized != current_text:
                    # Evitar bucles infinitos desconectando temporalmente la señal
                    self.rut_input.textChanged.disconnect()
                    self.rut_input.setText(normalized)
                    self.rut_input.textChanged.connect(self.normalize_rut_input)
    
    def finalize_rut_format(self):
        """Formatea el RUT cuando el usuario termina de escribir"""
        current_text = self.rut_input.text().strip()
        if current_text:
            normalized = normalize_rut(current_text)
            if normalized:
                self.rut_input.setText(normalized)
    
    def get_form_data(self) -> dict:
        """Retorna los datos del formulario"""
        rut_text = self.rut_input.text().strip()
        normalized_rut = normalize_rut(rut_text) if rut_text else ""
        
        # Obtener usuario actual del sistema centralizado
        current_user = get_current_user()
        
        return {
            'rut': normalized_rut if normalized_rut else rut_text,
            'nombre': self.nombre_input.text().strip(),
            'acompañante': self.acompañante_input.text().strip(),
            'sector': self.sector_combo.currentText(),
            'usuario_registrador': current_user
        }
    
    def validate_capacity(self) -> bool:
        """Valida si la zona seleccionada tiene cupo disponible"""
        selected_sector = self.sector_combo.currentText()
        current_visitors = self.visitor_manager.get_visitors_by_sector(selected_sector)
        current_count = len([v for v in current_visitors if v.estado == "Dentro"])
        
        if current_count >= 20:
            reply = QMessageBox.question(
                self, 
                "⚠️ Cupo Máximo Alcanzado",
                f"La zona {selected_sector} ya tiene {current_count} visitantes (cupo máximo: 20).\n\n"
                f"¿Estás seguro que quieres agregar más visitantes a esta zona?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        
        return True
    
    def clear_form(self):
        """Limpia el formulario"""
        self.rut_input.clear()
        self.nombre_input.clear()
        self.acompañante_input.clear()
        self.sector_combo.setCurrentIndex(0)
    
    def validate_form(self) -> bool:
        """Valida los datos del formulario rápido"""
        errors = []
        
        # Validar RUT
        rut = self.rut_input.text().strip()
        if not rut:
            errors.append("El RUT es obligatorio")
        else:
            # Normalizar y validar el RUT
            normalized_rut = normalize_rut(rut)
            if not normalized_rut:
                errors.append("El RUT ingresado no es válido")
            else:
                # Actualizar el campo con el RUT normalizado
                self.rut_input.setText(normalized_rut)
        
        # Validar nombre
        nombre = self.nombre_input.text().strip()
        if not nombre:
            errors.append("El nombre completo es obligatorio")
        elif len(nombre) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
        
        # Validar acompañante
        acompañante = self.acompañante_input.text().strip()
        if not acompañante:
            errors.append("El acompañante es obligatorio")
        elif len(acompañante) < 3:
            errors.append("El nombre del acompañante debe tener al menos 3 caracteres")
        
        if errors:
            error_text = "⚠️ <b>Errores de Validación:</b><br><br>" + "<br>".join([f"• {error}" for error in errors])
            QMessageBox.warning(self, "⚠️ Errores de Validación", error_text)
            return False
        
        return True
    
    def register_visitor(self) -> bool:
        """Registra el visitante con los datos del formulario rápido"""
        if not self.validate_form():
            return False
        
        # Validar cupo de la zona
        if not self.validate_capacity():
            return False
        
        try:
            # Obtener datos del formulario
            form_data = self.get_form_data()
            
            # Crear el visitante
            from .visitors import Visitor
            visitor = Visitor(
                rut=form_data['rut'],
                nombre_completo=form_data['nombre'],
                acompañante=form_data['acompañante'],
                sector=form_data['sector'],
                usuario_registrador=form_data['usuario_registrador']
            )
            
            # Intentar agregar el visitante
            if self.visitor_manager.add_visitor(visitor):
                # Limpiar el formulario después del registro exitoso
                self.clear_form()
                return True
            else:
                QMessageBox.warning(
                    self, 
                    "⚠️ Error", 
                    "🔍 Ya existe un visitante con ese RUT en el sistema"
                )
                return False
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "❌ Error", 
                f"🚫 Error al registrar el visitante:<br><br>{str(e)}"
            )
            return False