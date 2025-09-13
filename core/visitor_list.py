from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit, QHeaderView, QMessageBox,
    QMenu, QAbstractItemView, QFrame, QSplitter, QToolButton, QGroupBox,
    QDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QAction, QIcon, QColor, QPixmap
from datetime import datetime
from .visitor_model import VisitorManager
from .visitor_form import VisitorFormDialog, QuickVisitorForm
from .help_dialog import HelpDialog

class VisitorListWidget(QWidget):
    """Widget principal para la gestión de visitantes"""
    
    # Señales
    visitor_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.visitor_manager = VisitorManager()
        self.setup_ui()
        self.setup_connections()
        self.refresh_list()
        
        # Timer para actualizar la lista cada 30 segundos
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_list)
        self.refresh_timer.start(30000)  # 30 segundos
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Título y controles superiores
        header_layout = QHBoxLayout()
        
        # Título con icono
        title_icon = QLabel("👥")
        title_icon.setFont(QFont("Arial", 20))
        title = QLabel("Gestión de Visitantes")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_icon)
        header_layout.addWidget(title)
        
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
        
        # Botón de ayuda
        self.help_btn = QToolButton()
        self.help_btn.setText("?")
        self.help_btn.setToolTip("📖 Ayuda: Doble clic para cambiar estado | Clic derecho para menú | Filtros por estado y sector")
        self.help_btn.setMaximumSize(30, 30)
        self.help_btn.setStyleSheet("""
            QToolButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #138496;
            }
        """)
        header_layout.addWidget(self.help_btn)
        
        # Filtros
        filter_label = QLabel("🔍 Filtrar:")
        filter_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Dentro", "Fuera", "Financiamiento", "CITT", "Auditorio"])
        self.filter_combo.setMaximumWidth(150)
        self.filter_combo.setToolTip("Filtrar visitantes por estado o sector")
        header_layout.addWidget(filter_label)
        header_layout.addWidget(self.filter_combo)
        
        # Botón de actualizar
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.setMaximumWidth(120)
        self.refresh_btn.setToolTip("Actualizar la lista de visitantes")
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Splitter para dividir la pantalla
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Lista de visitantes
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Controles de la lista
        list_controls = QHBoxLayout()
        
        # Grupo de botones principales
        main_buttons_group = QGroupBox("🛠️ Acciones Principales")
        main_buttons_group.setFont(QFont("Arial", 9, QFont.Bold))
        main_buttons_layout = QHBoxLayout(main_buttons_group)
        
        self.add_btn = QPushButton("➕ Nuevo Visitante")
        self.add_btn.setToolTip("Agregar un nuevo visitante al sistema")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        self.edit_btn = QPushButton("✏️ Editar")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setToolTip("Editar la información del visitante seleccionado")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: white;
            }
        """)
        
        self.delete_btn = QPushButton("🗑️ Eliminar")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setToolTip("Eliminar el visitante seleccionado (acción irreversible)")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: white;
            }
        """)
        
        main_buttons_layout.addWidget(self.add_btn)
        main_buttons_layout.addWidget(self.edit_btn)
        main_buttons_layout.addWidget(self.delete_btn)
        
        list_controls.addWidget(main_buttons_group)
        list_controls.addStretch()
        
        left_layout.addLayout(list_controls)
        
        # Tabla de visitantes
        self.visitor_table = QTableWidget()
        self.visitor_table.setColumnCount(7)
        self.visitor_table.setHorizontalHeaderLabels([
            "🆔 ID", "📄 RUT", "👤 Nombre", "🤝 Acompañante", "🏢 Sector", "📍 Estado", "⏰ Hora Ingreso"
        ])
        
        # Configurar tabla
        self.visitor_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.visitor_table.setAlternatingRowColors(True)
        self.visitor_table.setSortingEnabled(True)
        self.visitor_table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Ajustar columnas
        header = self.visitor_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # RUT
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Acompañante
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Sector
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Estado
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Hora
        
        left_layout.addWidget(self.visitor_table)
        
        # Panel derecho - Formulario rápido
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Título del panel derecho
        right_title = QLabel("Registro Rápido")
        right_title.setFont(QFont("Arial", 12, QFont.Bold))
        right_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(right_title)
        
        # Formulario rápido
        self.quick_form = QuickVisitorForm()
        right_layout.addWidget(self.quick_form)
        
        # Botón de registro rápido
        self.quick_register_btn = QPushButton("🚀 Registrar Rápido")
        self.quick_register_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        right_layout.addWidget(self.quick_register_btn)
        
        # Estadísticas
        stats_group = QGroupBox("📊 Estadísticas")
        stats_group.setFont(QFont("Arial", 10, QFont.Bold))
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setFont(QFont("Arial", 10))
        self.stats_label.setToolTip("Estadísticas actualizadas en tiempo real")
        stats_layout.addWidget(self.stats_label)
        
        right_layout.addWidget(stats_group)
        right_layout.addStretch()
        
        # Configurar splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        
        # Botón de regreso al menú principal
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
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.add_btn.clicked.connect(self.add_visitor)
        self.edit_btn.clicked.connect(self.edit_visitor)
        self.delete_btn.clicked.connect(self.delete_visitor)
        self.refresh_btn.clicked.connect(self.refresh_list)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        self.quick_register_btn.clicked.connect(self.quick_register)
        
        self.visitor_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.visitor_table.itemDoubleClicked.connect(self.toggle_visitor_status)
        self.visitor_table.customContextMenuRequested.connect(self.show_context_menu)
        self.help_btn.clicked.connect(self.show_help)
    
    def add_visitor(self):
        """Abre el formulario para agregar un nuevo visitante"""
        dialog = VisitorFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            visitor = dialog.get_visitor()
            if self.visitor_manager.add_visitor(visitor):
                self.refresh_list()
                QMessageBox.information(self, "✅ Éxito", "👤 Visitante registrado correctamente en el sistema")
            else:
                QMessageBox.warning(self, "⚠️ Error", "🔍 Ya existe un visitante con ese RUT en el sistema")
    
    def edit_visitor(self):
        """Edita el visitante seleccionado"""
        current_row = self.visitor_table.currentRow()
        if current_row < 0:
            return
        
        visitor_id = self.visitor_table.item(current_row, 0).text()
        visitor = self.visitor_manager.get_visitor_by_id(visitor_id)
        
        if visitor:
            dialog = VisitorFormDialog(self, visitor)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_list()
                QMessageBox.information(self, "✅ Éxito", "✏️ Información del visitante actualizada correctamente")
    
    def delete_visitor(self):
        """Elimina el visitante seleccionado"""
        current_row = self.visitor_table.currentRow()
        if current_row < 0:
            return
        
        visitor_id = self.visitor_table.item(current_row, 0).text()
        visitor = self.visitor_manager.get_visitor_by_id(visitor_id)
        
        if visitor:
            reply = QMessageBox.question(
                self, "🗑️ Confirmar Eliminación",
                f"⚠️ ¿Está seguro de que desea eliminar al visitante:\n\n👤 {visitor.nombre_completo}\n🆔 {visitor.rut}\n\n❌ Esta acción no se puede deshacer",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.visitor_manager.delete_visitor(visitor_id):
                    self.refresh_list()
                    QMessageBox.information(self, "✅ Éxito", "🗑️ Visitante eliminado correctamente del sistema")
                else:
                    QMessageBox.critical(self, "❌ Error", "🚫 No se pudo eliminar el visitante del sistema")
    
    def quick_register(self):
        """Registro rápido usando el formulario del panel derecho"""
        form_data = self.quick_form.get_form_data()
        
        # Validar datos
        if not all(form_data.values()):
            QMessageBox.warning(self, "⚠️ Error", "📝 Todos los campos son obligatorios para el registro")
            return
        
        try:
            from .visitor_model import Visitor
            visitor = Visitor(
                rut=form_data['rut'],
                nombre_completo=form_data['nombre'],
                acompañante=form_data['acompañante'],
                sector=form_data['sector']
            )
            
            if self.visitor_manager.add_visitor(visitor):
                self.refresh_list()
                self.quick_form.clear_form()
                QMessageBox.information(self, "✅ Éxito", "🚀 Visitante registrado correctamente usando registro rápido")
            else:
                QMessageBox.warning(self, "⚠️ Error", "🔍 Ya existe un visitante con ese RUT en el sistema")
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"🚫 Error al registrar visitante: {str(e)}")
    
    def toggle_visitor_status(self, item):
        """Cambia el estado del visitante (doble clic)"""
        row = item.row()
        visitor_id = self.visitor_table.item(row, 0).text()
        
        if self.visitor_manager.toggle_visitor_status(visitor_id):
            self.refresh_list()
            
            visitor = self.visitor_manager.get_visitor_by_id(visitor_id)
            if visitor:
                if visitor.estado == "Dentro":
                    status_text = "entró"
                    icon = "🟢"
                else:
                    status_text = "salió"
                    icon = "🔴"
                
                QMessageBox.information(
                    self, "🔄 Estado Actualizado",
                    f"{icon} <b>{visitor.nombre_completo}</b> {status_text} del establecimiento\n\n📍 Estado actual: <b>{visitor.estado}</b>"
                )
    
    def show_context_menu(self, position):
        """Muestra el menú contextual"""
        if self.visitor_table.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        menu.setTitle("🎯 Acciones")
        
        toggle_action = QAction("🔄 Cambiar Estado", self)
        toggle_action.setToolTip("Cambiar entre 'Dentro' y 'Fuera'")
        toggle_action.triggered.connect(lambda: self.toggle_visitor_status(
            self.visitor_table.itemAt(position)
        ))
        menu.addAction(toggle_action)
        
        edit_action = QAction("✏️ Editar Información", self)
        edit_action.setToolTip("Modificar datos del visitante")
        edit_action.triggered.connect(self.edit_visitor)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("🗑️ Eliminar Visitante", self)
        delete_action.setToolTip("Eliminar permanentemente del sistema")
        delete_action.triggered.connect(self.delete_visitor)
        menu.addAction(delete_action)
        
        menu.exec(self.visitor_table.mapToGlobal(position))
    
    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        has_selection = self.visitor_table.currentRow() >= 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def apply_filter(self, filter_text):
        """Aplica filtros a la lista"""
        self.refresh_list()
    
    def show_help(self):
        """Muestra el diálogo de ayuda"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()
    
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
    
    def refresh_list(self):
        """Actualiza la lista de visitantes"""
        visitors = self.visitor_manager.get_all_visitors()
        
        # Aplicar filtros
        filter_text = self.filter_combo.currentText()
        if filter_text != "Todos":
            if filter_text in ["Dentro", "Fuera"]:
                visitors = [v for v in visitors if v.estado == filter_text]
            else:
                visitors = [v for v in visitors if v.sector == filter_text]
        
        # Ordenar por fecha de ingreso (más recientes primero)
        visitors.sort(key=lambda x: x.fecha_ingreso, reverse=True)
        
        # Actualizar tabla
        self.visitor_table.setRowCount(len(visitors))
        
        for row, visitor in enumerate(visitors):
            # ID
            self.visitor_table.setItem(row, 0, QTableWidgetItem(visitor.id))
            
            # RUT
            self.visitor_table.setItem(row, 1, QTableWidgetItem(visitor.rut))
            
            # Nombre
            self.visitor_table.setItem(row, 2, QTableWidgetItem(visitor.nombre_completo))
            
            # Acompañante
            self.visitor_table.setItem(row, 3, QTableWidgetItem(visitor.acompañante))
            
            # Sector
            self.visitor_table.setItem(row, 4, QTableWidgetItem(visitor.sector))
            
            # Estado
            estado_item = QTableWidgetItem(visitor.estado)
            if visitor.estado == "Dentro":
                estado_item.setBackground(QColor(144, 238, 144))  # Verde claro
            else:
                estado_item.setBackground(QColor(255, 182, 193))  # Rosa claro
            self.visitor_table.setItem(row, 5, estado_item)
            
            # Fecha de ingreso
            fecha_formatted = datetime.strptime(visitor.fecha_ingreso, "%Y-%m-%d %H:%M:%S")
            fecha_str = fecha_formatted.strftime("%d/%m/%Y %H:%M")
            self.visitor_table.setItem(row, 6, QTableWidgetItem(fecha_str))
        
        # Actualizar estadísticas
        self.update_stats(visitors)
    
    def update_stats(self, visitors):
        """Actualiza las estadísticas mostradas"""
        total = len(visitors)
        dentro = len([v for v in visitors if v.estado == "Dentro"])
        fuera = total - dentro
        
        # Iconos dinámicos según el estado
        dentro_icon = "🟢" if dentro > 0 else "⚪"
        fuera_icon = "🔴" if fuera > 0 else "⚪"
        
        stats_text = f"""
        <div style="text-align: center;">
        <b>📊 Resumen de Visitantes</b><br><br>
        👥 <b>Total:</b> {total}<br>
        {dentro_icon} <b>Dentro:</b> {dentro}<br>
        {fuera_icon} <b>Fuera:</b> {fuera}<br><br>
        <small>💡 Actualizado automáticamente</small>
        </div>
        """
        self.stats_label.setText(stats_text)
