from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QMessageBox, QWidget, QToolButton, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
from .visitor_model import Visitor

class VisitorFormDialog(QDialog):
    def __init__(self, parent=None, visitor=None):
        super().__init__(parent)
        self.visitor = visitor
        self.is_edit_mode = visitor is not None
        
        self.setWindowTitle("Editar Visitante" if self.is_edit_mode else "Registrar Nuevo Visitante")
        self.setModal(True)
        self.resize(400, 350)
        
        self.setup_ui()
        self.setup_connections()
        
        if self.is_edit_mode:
            self.load_visitor_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título con icono
        title_layout = QHBoxLayout()
        title_icon = QLabel("👤")
        title_icon.setFont(QFont("Arial", 20))
        title = QLabel("Registro de Visitante" if not self.is_edit_mode else "Editar Visitante")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Grupo de información personal
        personal_group = QGroupBox("📋 Información Personal")
        personal_group.setFont(QFont("Arial", 10, QFont.Bold))
        personal_layout = QFormLayout(personal_group)
        personal_layout.setSpacing(12)
        personal_layout.setLabelAlignment(Qt.AlignRight)
        
        # RUT con tooltip
        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("Ej: 12345678-9")
        self.rut_input.setToolTip("🔍 Ingrese el RUT del visitante (ej: 12345678-9)")
        
        rut_help = QToolButton()
        rut_help.setText("?")
        rut_help.setToolTip("El RUT debe tener al menos 8 caracteres y ser único en el sistema")
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
        
        # Grupo de información de visita
        visit_group = QGroupBox("🏢 Información de Visita")
        visit_group.setFont(QFont("Arial", 10, QFont.Bold))
        visit_layout = QFormLayout(visit_group)
        visit_layout.setSpacing(12)
        visit_layout.setLabelAlignment(Qt.AlignRight)
        
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
        self.sector_combo.addItems(["Financiamiento", "CITT", "Auditorio"])
        self.sector_combo.setToolTip("🏢 Seleccione el sector al que se dirige el visitante")
        
        sector_help = QToolButton()
        sector_help.setText("?")
        sector_help.setToolTip("Sector del establecimiento donde se dirigirá el visitante")
        sector_help.setMaximumSize(25, 25)
        
        sector_layout = QHBoxLayout()
        sector_layout.addWidget(self.sector_combo)
        sector_layout.addWidget(sector_help)
        visit_layout.addRow("🏢 Sector:", sector_layout)
        
        layout.addWidget(personal_group)
        layout.addWidget(visit_group)
        
        # Botones con iconos
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.setToolTip("Cancelar y cerrar el formulario sin guardar")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        save_text = "💾 Guardar" if not self.is_edit_mode else "💾 Actualizar"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setToolTip("Guardar la información del visitante")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.save_visitor)
    
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
    
    def validate_form(self) -> bool:
        """Valida los datos del formulario"""
        errors = []
        
        # Validar RUT
        rut = self.rut_input.text().strip()
        if not rut:
            errors.append("El RUT es obligatorio")
        elif len(rut) < 8:
            errors.append("El RUT debe tener al menos 8 caracteres")
        
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
        
        try:
            if self.is_edit_mode and self.visitor:
                # Modo edición
                self.visitor.rut = self.rut_input.text().strip()
                self.visitor.nombre_completo = self.nombre_input.text().strip()
                self.visitor.acompañante = self.acompañante_input.text().strip()
                self.visitor.sector = self.sector_combo.currentText()
                self.accept()
            else:
                # Modo creación
                visitor = Visitor(
                    rut=self.rut_input.text().strip(),
                    nombre_completo=self.nombre_input.text().strip(),
                    acompañante=self.acompañante_input.text().strip(),
                    sector=self.sector_combo.currentText()
                )
                self.visitor = visitor
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"🚫 Error al guardar el visitante:<br><br>{str(e)}")
    
    def get_visitor(self) -> Visitor:
        """Retorna el visitante creado o editado"""
        return self.visitor

class QuickVisitorForm(QWidget):
    """Formulario rápido para registro de visitantes desde la lista"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título con icono
        title_layout = QHBoxLayout()
        title_icon = QLabel("⚡")
        title_icon.setFont(QFont("Arial", 16))
        title = QLabel("Registro Rápido")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Grupo de campos
        form_group = QGroupBox("📝 Datos del Visitante")
        form_group.setFont(QFont("Arial", 9, QFont.Bold))
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        # RUT
        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("Ej: 12345678-9")
        self.rut_input.setToolTip("🆔 RUT del visitante")
        form_layout.addRow("🆔 RUT:", self.rut_input)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre completo")
        self.nombre_input.setToolTip("👤 Nombre completo del visitante")
        form_layout.addRow("👤 Nombre:", self.nombre_input)
        
        # Acompañante
        self.acompañante_input = QLineEdit()
        self.acompañante_input.setPlaceholderText("Quien invita")
        self.acompañante_input.setToolTip("🤝 Persona que invita al visitante")
        form_layout.addRow("🤝 Acompañante:", self.acompañante_input)
        
        # Sector
        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["Financiamiento", "CITT", "Auditorio"])
        self.sector_combo.setToolTip("🏢 Sector de destino")
        form_layout.addRow("🏢 Sector:", self.sector_combo)
        
        layout.addWidget(form_group)
        
        # Botón de registro
        self.registrar_btn = QPushButton("🚀 Registrar Rápido")
        self.registrar_btn.setToolTip("Registrar el visitante con los datos ingresados")
        self.registrar_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        layout.addWidget(self.registrar_btn)
    
    def get_form_data(self) -> dict:
        """Retorna los datos del formulario"""
        return {
            'rut': self.rut_input.text().strip(),
            'nombre': self.nombre_input.text().strip(),
            'acompañante': self.acompañante_input.text().strip(),
            'sector': self.sector_combo.currentText()
        }
    
    def clear_form(self):
        """Limpia el formulario"""
        self.rut_input.clear()
        self.nombre_input.clear()
        self.acompañante_input.clear()
        self.sector_combo.setCurrentIndex(0)
