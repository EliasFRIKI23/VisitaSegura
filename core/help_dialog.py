from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QTabWidget, QWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 Ayuda - Sistema de Gestión de Visitantes")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title_layout = QHBoxLayout()
        title_icon = QLabel("📖")
        title_icon.setFont(QFont("Arial", 24))
        title = QLabel("Ayuda del Sistema")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Pestañas
        self.tab_widget = QTabWidget()
        
        # Pestaña de inicio rápido
        quick_start_tab = self.create_quick_start_tab()
        self.tab_widget.addTab(quick_start_tab, "🚀 Inicio Rápido")
        
        # Pestaña de funciones
        functions_tab = self.create_functions_tab()
        self.tab_widget.addTab(functions_tab, "⚙️ Funciones")
        
        # Pestaña de atajos
        shortcuts_tab = self.create_shortcuts_tab()
        self.tab_widget.addTab(shortcuts_tab, "⌨️ Atajos")
        
        # Pestaña de solución de problemas
        troubleshooting_tab = self.create_troubleshooting_tab()
        self.tab_widget.addTab(troubleshooting_tab, "🔧 Problemas")
        
        layout.addWidget(self.tab_widget)
        
        # Botón cerrar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("✅ Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_quick_start_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial; font-size: 12px;">
        <h2>🚀 Guía de Inicio Rápido</h2>
        
        <h3>📝 Registro de Visitantes</h3>
        <p><b>Método 1 - Formulario Completo:</b></p>
        <ul>
            <li>Hacer clic en "➕ Nuevo Visitante"</li>
            <li>Completar todos los campos obligatorios</li>
            <li>Hacer clic en "💾 Guardar"</li>
        </ul>
        
        <p><b>Método 2 - Registro Rápido:</b></p>
        <ul>
            <li>Usar el formulario del panel derecho</li>
            <li>Completar los campos básicos</li>
            <li>Hacer clic en "🚀 Registrar Rápido"</li>
        </ul>
        
        <h3>🔄 Cambio de Estado</h3>
        <ul>
            <li><b>Doble clic</b> en cualquier fila para cambiar estado</li>
            <li><b>Clic derecho</b> → "🔄 Cambiar Estado"</li>
            <li>Los colores indican el estado actual</li>
        </ul>
        
        <h3>🔍 Filtros</h3>
        <ul>
            <li>Usar el menú desplegable "🔍 Filtrar"</li>
            <li>Filtrar por estado: "Dentro", "Fuera"</li>
            <li>Filtrar por sector: "Financiamiento", "CITT", "Auditorio"</li>
        </ul>
        </div>
        """)
        
        layout.addWidget(content)
        return widget
    
    def create_functions_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial; font-size: 12px;">
        <h2>⚙️ Funciones Principales</h2>
        
        <h3>👥 Gestión de Visitantes</h3>
        <ul>
            <li><b>➕ Agregar:</b> Registrar nuevos visitantes</li>
            <li><b>✏️ Editar:</b> Modificar información existente</li>
            <li><b>🗑️ Eliminar:</b> Remover visitantes del sistema</li>
            <li><b>🔄 Cambiar Estado:</b> Marcar entrada/salida</li>
        </ul>
        
        <h3>📊 Información Disponible</h3>
        <ul>
            <li><b>🆔 ID:</b> Identificador único automático</li>
            <li><b>📄 RUT:</b> Documento de identidad</li>
            <li><b>👤 Nombre:</b> Nombre completo del visitante</li>
            <li><b>🤝 Acompañante:</b> Persona que invita</li>
            <li><b>🏢 Sector:</b> Destino en el establecimiento</li>
            <li><b>📍 Estado:</b> Dentro/Fuera del edificio</li>
            <li><b>⏰ Hora:</b> Momento de registro</li>
        </ul>
        
        <h3>📈 Estadísticas</h3>
        <ul>
            <li>Total de visitantes registrados</li>
            <li>Visitantes actualmente dentro</li>
            <li>Visitantes que han salido</li>
            <li>Actualización automática cada 30 segundos</li>
        </ul>
        </div>
        """)
        
        layout.addWidget(content)
        return widget
    
    def create_shortcuts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial; font-size: 12px;">
        <h2>⌨️ Atajos y Consejos</h2>
        
        <h3>🖱️ Interacciones con el Mouse</h3>
        <ul>
            <li><b>Doble clic:</b> Cambiar estado del visitante</li>
            <li><b>Clic derecho:</b> Menú contextual con opciones</li>
            <li><b>Clic simple:</b> Seleccionar visitante</li>
            <li><b>Hover:</b> Ver tooltips explicativos</li>
        </ul>
        
        <h3>⌨️ Atajos de Teclado</h3>
        <ul>
            <li><b>Tab:</b> Navegar entre campos del formulario</li>
            <li><b>Enter:</b> Confirmar en formularios</li>
            <li><b>Escape:</b> Cancelar operaciones</li>
            <li><b>Ctrl+F:</b> Enfocar campo de búsqueda (si está disponible)</li>
        </ul>
        
        <h3>💡 Consejos de Uso</h3>
        <ul>
            <li>Los <b>iconos</b> indican el tipo de acción</li>
            <li>Los <b>colores</b> muestran estados importantes</li>
            <li>Los <b>tooltips</b> explican cada función</li>
            <li>Los <b>filtros</b> ayudan a encontrar visitantes</li>
            <li>Las <b>estadísticas</b> se actualizan automáticamente</li>
        </ul>
        
        <h3>🎯 Indicadores Visuales</h3>
        <ul>
            <li>🟢 <b>Verde:</b> Visitante dentro del establecimiento</li>
            <li>🔴 <b>Rojo:</b> Visitante fuera del establecimiento</li>
            <li>❓ <b>Signo de pregunta:</b> Ayuda disponible</li>
            <li>⚡ <b>Rayo:</b> Acción rápida</li>
        </ul>
        </div>
        """)
        
        layout.addWidget(content)
        return widget
    
    def create_troubleshooting_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial; font-size: 12px;">
        <h2>🔧 Solución de Problemas</h2>
        
        <h3>❌ Errores Comunes</h3>
        
        <p><b>🔍 "Ya existe un visitante con ese RUT"</b></p>
        <ul>
            <li>Verificar que el RUT no esté duplicado</li>
            <li>Buscar el visitante existente en la lista</li>
            <li>Editar la información en lugar de crear nuevo</li>
        </ul>
        
        <p><b>📝 "Todos los campos son obligatorios"</b></p>
        <ul>
            <li>Completar todos los campos marcados con iconos</li>
            <li>Verificar que no haya campos vacíos</li>
            <li>Usar el botón "?" para ver ayuda específica</li>
        </ul>
        
        <p><b>🚫 "No se pudo guardar"</b></p>
        <ul>
            <li>Verificar permisos de escritura en el directorio</li>
            <li>Comprobar espacio en disco disponible</li>
            <li>Reiniciar la aplicación si persiste</li>
        </ul>
        
        <h3>🔄 Problemas de Rendimiento</h3>
        <ul>
            <li>La lista se actualiza automáticamente cada 30 segundos</li>
            <li>Usar filtros para mejorar la velocidad</li>
            <li>Eliminar visitantes antiguos si es necesario</li>
        </ul>
        
        <h3>📞 Soporte</h3>
        <p>Si los problemas persisten:</p>
        <ul>
            <li>Verificar que todos los archivos estén presentes</li>
            <li>Comprobar que PySide6 esté instalado correctamente</li>
            <li>Contactar al equipo de desarrollo</li>
        </ul>
        </div>
        """)
        
        layout.addWidget(content)
        return widget
