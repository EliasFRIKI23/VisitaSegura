from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QGridLayout, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QFileDialog, QProgressBar, QComboBox,
                               QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QColor, QGuiApplication
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.visitor_model import VisitorManager
    from core.excel_exporter import ExcelExporter
except ImportError:
    from visitor_model import VisitorManager
    from excel_exporter import ExcelExporter

class ReportesView(QWidget):
    """Vista para reportes y estadísticas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.visitor_manager = VisitorManager()
        self.excel_exporter = ExcelExporter()
        self.setup_ui()
        
        # Timer para actualizar automáticamente cada 10 segundos
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_visitors_data)
        self.refresh_timer.start(10000)  # 10 segundos
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        
        # Hacer responsivo basado en el tamaño de pantalla
        available = QGuiApplication.primaryScreen().availableGeometry()
        if available.width() >= 1920:
            margin = 30
            spacing = 25
        elif available.width() >= 1366:
            margin = 20
            spacing = 20
        else:
            margin = 15
            spacing = 15
            
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(spacing)
        
        # Header con título y logo
        header_layout = QHBoxLayout()
        
        # Título
        title_layout = QVBoxLayout()
        title = QLabel("📊 Reportes y Estadísticas")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        
        subtitle = QLabel("Análisis y reportes del sistema de visitas")
        subtitle.setFont(QFont("Arial", 12))
        title.setAlignment(Qt.AlignLeft)
        
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
        
        # Contenido principal responsivo
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.StyledPanel)
        content_layout = QVBoxLayout(content_frame)
        
        # Márgenes responsivos
        if available.width() >= 1920:
            content_margin = 50
            content_spacing = 25
        elif available.width() >= 1366:
            content_margin = 40
            content_spacing = 20
        else:
            content_margin = 30
            content_spacing = 15
            
        content_layout.setContentsMargins(content_margin, content_margin, content_margin, content_margin)
        content_layout.setSpacing(content_spacing)
        
        # Estadísticas actuales
        stats_title = QLabel("📈 Estadísticas Actuales")
        # Fuente responsiva
        if available.width() >= 1920:
            title_font_size = 20
        elif available.width() >= 1366:
            title_font_size = 18
        else:
            title_font_size = 16
            
        stats_title.setFont(QFont("Arial", title_font_size, QFont.Bold))
        stats_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(stats_title)
        
        # Grid de estadísticas responsivo
        stats_grid = QGridLayout()
        # Espaciado responsivo
        if available.width() >= 1920:
            grid_spacing = 20
        elif available.width() >= 1366:
            grid_spacing = 15
        else:
            grid_spacing = 10
        stats_grid.setSpacing(grid_spacing)
        
        # Crear las tarjetas de estadísticas dinámicas con referencias a los labels
        self.stat1, self.stat1_value = self.create_stat_card_with_reference("👥 Visitantes Hoy", "0", "#28a745", "Visitantes registrados hoy")
        stats_grid.addWidget(self.stat1, 0, 0)
        
        self.stat2, self.stat2_value = self.create_stat_card_with_reference("🏢 Zonas Activas", "0", "#007bff", "Zonas con visitantes")
        stats_grid.addWidget(self.stat2, 0, 1)
        
        self.stat3, self.stat3_value = self.create_stat_card_with_reference("📋 Visitas Totales", "0", "#ffc107", "Visitas registradas")
        stats_grid.addWidget(self.stat3, 1, 0)
        
        self.stat4, self.stat4_value = self.create_stat_card_with_reference("⏰ Promedio Visita", "0 min", "#dc3545", "Tiempo promedio de visita")
        stats_grid.addWidget(self.stat4, 1, 1)
        
        content_layout.addLayout(stats_grid)
        
        # Estadísticas detalladas
        detailed_stats_title = QLabel("📊 Estadísticas Detalladas")
        detailed_stats_title.setFont(QFont("Arial", 16, QFont.Bold))
        detailed_stats_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(detailed_stats_title)
        
        # Grid de estadísticas detalladas
        detailed_stats_grid = QGridLayout()
        detailed_stats_grid.setSpacing(15)
        
        # Crear las tarjetas de estadísticas detalladas con referencias
        self.detailed_stat1, self.detailed_stat1_value = self.create_stat_card_with_reference("🏢 Zona Más Visitada", "N/A", "#17a2b8", "Zona con más visitantes")
        detailed_stats_grid.addWidget(self.detailed_stat1, 0, 0)
        
        self.detailed_stat2, self.detailed_stat2_value = self.create_stat_card_with_reference("👥 Visitantes Actuales", "0", "#28a745", "Visitantes dentro del edificio")
        detailed_stats_grid.addWidget(self.detailed_stat2, 0, 1)
        
        self.detailed_stat3, self.detailed_stat3_value = self.create_stat_card_with_reference("📅 Visitas Esta Semana", "0", "#6f42c1", "Visitas de los últimos 7 días")
        detailed_stats_grid.addWidget(self.detailed_stat3, 1, 0)
        
        self.detailed_stat4, self.detailed_stat4_value = self.create_stat_card_with_reference("⏰ Visita Más Larga", "N/A", "#fd7e14", "Duración de la visita más larga")
        detailed_stats_grid.addWidget(self.detailed_stat4, 1, 1)
        
        content_layout.addLayout(detailed_stats_grid)
        
        # Reporte de Visitantes
        current_visitors_title = QLabel("👥 Reporte de Visitantes")
        current_visitors_title.setFont(QFont("Arial", 18, QFont.Bold))
        current_visitors_title.setAlignment(Qt.AlignCenter)
        current_visitors_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin: 10px 0px;
            }
        """)
        content_layout.addWidget(current_visitors_title)
        
        # Botones de acción para el reporte
        action_layout = QHBoxLayout()
        
        # Botón para actualizar datos responsivo
        self.btn_refresh = QPushButton("🔄 Actualizar Datos")
        # Tamaños responsivos para botones
        if available.width() >= 1920:
            btn_width, btn_height = 180, 50
            btn_font_size = 16
        elif available.width() >= 1366:
            btn_width, btn_height = 150, 40
            btn_font_size = 14
        else:
            btn_width, btn_height = 120, 35
            btn_font_size = 12
            
        self.btn_refresh.setMinimumSize(btn_width, btn_height)
        self.btn_refresh.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {btn_font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
        """)
        self.btn_refresh.clicked.connect(self.refresh_visitors_data)
        action_layout.addWidget(self.btn_refresh)
        
        # Filtro de visitantes responsivo
        filter_label = QLabel("Filtrar:")
        filter_label.setFont(QFont("Arial", btn_font_size, QFont.Bold))
        action_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos los visitantes", "Solo visitantes actuales", "Solo visitantes que se fueron"])
        self.filter_combo.setMinimumSize(btn_width * 1.3, btn_height)
        self.filter_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.filter_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 5px;
                border: 2px solid #ced4da;
                border-radius: 5px;
                font-size: {btn_font_size}px;
            }}
            QComboBox:focus {{
                border-color: #007bff;
            }}
        """)
        self.filter_combo.currentTextChanged.connect(self.refresh_visitors_data)
        action_layout.addWidget(self.filter_combo)
        
        # Botón para exportar a Excel responsivo
        self.btn_export = QPushButton("📊 Exportar a Excel")
        self.btn_export.setMinimumSize(btn_width, btn_height)
        self.btn_export.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn_export.setStyleSheet(f"""
            QPushButton {{
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {btn_font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
        """)
        self.btn_export.clicked.connect(self.export_to_excel)
        action_layout.addWidget(self.btn_export)
        
        action_layout.addStretch()
        content_layout.addLayout(action_layout)
        
        # Tabla de visitantes
        self.visitors_table = QTableWidget()
        self.visitors_table.setColumnCount(7)
        self.visitors_table.setHorizontalHeaderLabels([
            "Nombre del Visitante",
            "RUT", 
            "Fecha y Hora de Entrada",
            "Fecha y Hora de Salida",
            "Destino/Lugar",
            "Acompañante",
            "Estado de Visita"
        ])
        
        # Configurar tabla responsiva
        self.visitors_table.horizontalHeader().setStretchLastSection(True)
        self.visitors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.visitors_table.setAlternatingRowColors(True)
        self.visitors_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Configurar altura de filas responsiva
        available = QGuiApplication.primaryScreen().availableGeometry()
        if available.width() >= 1920:
            row_height = 45
            font_size = 12
        elif available.width() >= 1366:
            row_height = 40
            font_size = 11
        else:
            row_height = 35
            font_size = 10
            
        self.visitors_table.verticalHeader().setDefaultSectionSize(row_height)
        
        # Estilo mejorado para la tabla
        self.visitors_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                font-size: 12px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #495057;
                color: white;
                padding: 12px 8px;
                border: 1px solid #6c757d;
                font-weight: bold;
                font-size: 13px;
                text-align: center;
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
            }
            QTableCornerButton::section {
                background-color: #495057;
                border: 1px solid #6c757d;
                border-top-left-radius: 8px;
            }
        """)
        
        content_layout.addWidget(self.visitors_table)
        
        # Información del reporte
        self.info_label = QLabel()
        self.info_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.info_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #e8f4fd;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin: 10px 0px;
            }
        """)
        content_layout.addWidget(self.info_label)
        
        # Cargar datos iniciales
        self.refresh_visitors_data()
        self.update_statistics()
        
        main_layout.addWidget(content_frame)
        main_layout.addStretch()
        
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
    
    def create_stat_card(self, title, value, color, description):
        """Crea una tarjeta de estadística responsiva"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        
        # Tamaños responsivos
        available = QGuiApplication.primaryScreen().availableGeometry()
        if available.width() >= 1920:
            padding = 25
            value_font_size = 28
            title_font_size = 14
            desc_font_size = 11
            border_radius = 15
        elif available.width() >= 1366:
            padding = 20
            value_font_size = 24
            title_font_size = 12
            desc_font_size = 9
            border_radius = 12
        else:
            padding = 15
            value_font_size = 20
            title_font_size = 10
            desc_font_size = 8
            border_radius = 10
            
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: {border_radius}px;
                padding: {padding}px;
            }}
            QFrame:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Valor
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", value_font_size, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", title_font_size, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", desc_font_size))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(desc_label)
        
        return card
    
    def create_stat_card_with_reference(self, title, value, color, description):
        """Crea una tarjeta de estadística responsiva y devuelve la tarjeta y el label de valor"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        
        # Tamaños responsivos
        available = QGuiApplication.primaryScreen().availableGeometry()
        if available.width() >= 1920:
            padding = 25
            value_font_size = 28
            title_font_size = 14
            desc_font_size = 11
            border_radius = 15
        elif available.width() >= 1366:
            padding = 20
            value_font_size = 24
            title_font_size = 12
            desc_font_size = 9
            border_radius = 12
        else:
            padding = 15
            value_font_size = 20
            title_font_size = 10
            desc_font_size = 8
            border_radius = 10
            
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: {border_radius}px;
                padding: {padding}px;
            }}
            QFrame:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Valor (con referencia)
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", value_font_size, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", title_font_size, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", desc_font_size))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(desc_label)
        
        return card, value_label
    
    def create_report_card(self, title, color, description):
        """Crea una tarjeta de reporte"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 12px;
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(desc_label)
        
        # Botón de generar
        generate_btn = QPushButton("📄 Generar")
        generate_btn.setFixedHeight(35)
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        layout.addWidget(generate_btn)
        
        return card
    
    def refresh_visitors_data(self):
        """Actualiza los datos de visitantes en la tabla"""
        try:
            # Recargar los datos desde el archivo JSON para obtener la información más actualizada
            self.visitor_manager.load_visitors()
            
            # Determinar qué datos mostrar según el filtro
            filter_text = self.filter_combo.currentText()
            if filter_text == "Solo visitantes actuales":
                visitors_data = self.visitor_manager.get_visitor_report_data(include_departed=False)
            elif filter_text == "Solo visitantes que se fueron":
                # Filtrar solo los que se fueron
                all_data = self.visitor_manager.get_visitor_report_data(include_departed=True)
                visitors_data = [v for v in all_data if v['estado_visita'] == "Finalizada"]
            else:  # "Todos los visitantes"
                visitors_data = self.visitor_manager.get_visitor_report_data(include_departed=True)
            
            # Configurar número de filas
            self.visitors_table.setRowCount(len(visitors_data))
            
            # Llenar la tabla con los datos
            for row, visitor in enumerate(visitors_data):
                # Crear items con texto centrado y mejor formato
                items = [
                    QTableWidgetItem(str(visitor['nombre'])),
                    QTableWidgetItem(str(visitor['rut'])),
                    QTableWidgetItem(str(visitor['fecha_entrada'])),
                    QTableWidgetItem(str(visitor['fecha_salida'])),
                    QTableWidgetItem(str(visitor['destino'])),
                    QTableWidgetItem(str(visitor['acompañante'])),
                    QTableWidgetItem(str(visitor['estado_visita']))
                ]
                
                # Configurar alineación y estilo para cada item
                available = QGuiApplication.primaryScreen().availableGeometry()
                if available.width() >= 1920:
                    font_size = 12
                elif available.width() >= 1366:
                    font_size = 11
                else:
                    font_size = 10
                    
                for col, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    item.setFont(QFont("Arial", font_size))
                    
                    # Colorear según el estado
                    if col == 3:  # Fecha de salida
                        if visitor['fecha_salida'] == "Aún en el edificio":
                            item.setBackground(QColor(220, 248, 198))  # Verde claro
                            item.setForeground(QColor(40, 167, 69))   # Verde oscuro
                        else:
                            item.setBackground(QColor(248, 249, 250))  # Gris claro
                            item.setForeground(QColor(108, 117, 125)) # Gris oscuro
                    
                    elif col == 6:  # Estado de visita
                        if visitor['estado_visita'] == "En curso":
                            item.setBackground(QColor(220, 248, 198))  # Verde claro
                            item.setForeground(QColor(40, 167, 69))   # Verde oscuro
                        else:  # Finalizada
                            item.setBackground(QColor(248, 215, 218))  # Rojo claro
                            item.setForeground(QColor(220, 53, 69))   # Rojo oscuro
                    
                    self.visitors_table.setItem(row, col, item)
            
            # Ajustar altura de filas
            for row in range(len(visitors_data)):
                self.visitors_table.setRowHeight(row, 40)
            
            # Actualizar información del reporte
            self.update_report_info(visitors_data)
            
            # Actualizar estadísticas
            self.update_statistics()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar datos: {str(e)}")
    
    def update_report_info(self, visitors_data):
        """Actualiza la información del reporte"""
        total_visitors = len(visitors_data)
        
        # Contar visitantes por destino
        destinations = {}
        for visitor in visitors_data:
            dest = visitor['destino']
            destinations[dest] = destinations.get(dest, 0) + 1
        
        # Crear texto informativo
        info_text = f"📊 Total de visitantes actuales: {total_visitors}"
        if destinations:
            dest_info = ", ".join([f"{dest}: {count}" for dest, count in destinations.items()])
            info_text += f" | 📍 Distribución por destino: {dest_info}"
        
        self.info_label.setText(info_text)
    
    def update_statistics(self):
        """Actualiza las estadísticas dinámicas"""
        try:
            # Obtener todos los visitantes
            all_visitors = self.visitor_manager.get_all_visitors()
            print(f"Debug: Encontrados {len(all_visitors)} visitantes")
            
            # Calcular estadísticas
            stats = self.calculate_statistics(all_visitors)
            print(f"Debug: Estadísticas calculadas: {stats}")
            
            # Actualizar las tarjetas de estadísticas básicas usando referencias directas
            self.stat1_value.setText(str(stats['visitors_today']))
            self.stat2_value.setText(str(stats['active_zones']))
            self.stat3_value.setText(str(stats['total_visits']))
            self.stat4_value.setText(str(stats['avg_visit_time']))
            
            # Actualizar las tarjetas de estadísticas detalladas usando referencias directas
            self.detailed_stat1_value.setText(str(stats['most_visited_zone']))
            self.detailed_stat2_value.setText(str(stats['current_visitors']))
            self.detailed_stat3_value.setText(str(stats['visits_this_week']))
            self.detailed_stat4_value.setText(str(stats['longest_visit']))
            
            print("Debug: Estadísticas actualizadas en la interfaz")
            
        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")
            import traceback
            traceback.print_exc()
    
    def calculate_statistics(self, visitors):
        """Calcula las estadísticas basadas en los datos de visitantes"""
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        current_time = datetime.now()
        
        # Visitantes de hoy
        visitors_today = 0
        for visitor in visitors:
            try:
                visit_date = datetime.strptime(visitor.fecha_ingreso, "%Y-%m-%d %H:%M:%S").date()
                if visit_date == today:
                    visitors_today += 1
            except:
                continue
        
        # Zonas activas (con visitantes actuales)
        active_zones = set()
        for visitor in visitors:
            if visitor.estado == "Dentro":
                active_zones.add(visitor.sector)
        
        # Total de visitas
        total_visits = len(visitors)
        
        # Tiempo promedio de visita
        avg_visit_time = self.calculate_average_visit_time(visitors)
        
        # Estadísticas adicionales
        most_visited_zone = self.get_most_visited_zone(visitors)
        current_visitors = len([v for v in visitors if v.estado == "Dentro"])
        visits_this_week = self.get_visits_this_week(visitors)
        longest_visit = self.get_longest_visit(visitors)
        
        return {
            'visitors_today': str(visitors_today),
            'active_zones': str(len(active_zones)),
            'total_visits': str(total_visits),
            'avg_visit_time': avg_visit_time,
            'most_visited_zone': most_visited_zone,
            'current_visitors': str(current_visitors),
            'visits_this_week': str(visits_this_week),
            'longest_visit': longest_visit
        }
    
    def calculate_average_visit_time(self, visitors):
        """Calcula el tiempo promedio de visita en minutos"""
        completed_visits = []
        
        for visitor in visitors:
            if visitor.fecha_salida:
                try:
                    entry_time = datetime.strptime(visitor.fecha_ingreso, "%Y-%m-%d %H:%M:%S")
                    exit_time = datetime.strptime(visitor.fecha_salida, "%Y-%m-%d %H:%M:%S")
                    duration = (exit_time - entry_time).total_seconds() / 60  # en minutos
                    completed_visits.append(duration)
                except:
                    continue
        
        if completed_visits:
            avg_minutes = sum(completed_visits) / len(completed_visits)
            if avg_minutes < 60:
                return f"{avg_minutes:.0f} min"
            else:
                hours = avg_minutes / 60
                return f"{hours:.1f} h"
        else:
            return "N/A"
    
    def get_most_visited_zone(self, visitors):
        """Obtiene la zona más visitada"""
        zone_counts = {}
        for visitor in visitors:
            zone = visitor.sector
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
        
        if zone_counts:
            most_visited = max(zone_counts, key=zone_counts.get)
            count = zone_counts[most_visited]
            return f"{most_visited} ({count})"
        else:
            return "N/A"
    
    def get_visits_this_week(self, visitors):
        """Calcula las visitas de esta semana"""
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        visits_this_week = 0
        for visitor in visitors:
            try:
                visit_date = datetime.strptime(visitor.fecha_ingreso, "%Y-%m-%d %H:%M:%S").date()
                if visit_date >= week_ago:
                    visits_this_week += 1
            except:
                continue
        
        return visits_this_week
    
    def get_longest_visit(self, visitors):
        """Obtiene la duración de la visita más larga"""
        longest_duration = 0
        
        for visitor in visitors:
            if visitor.fecha_salida:
                try:
                    entry_time = datetime.strptime(visitor.fecha_ingreso, "%Y-%m-%d %H:%M:%S")
                    exit_time = datetime.strptime(visitor.fecha_salida, "%Y-%m-%d %H:%M:%S")
                    duration = (exit_time - entry_time).total_seconds() / 60  # en minutos
                    longest_duration = max(longest_duration, duration)
                except:
                    continue
        
        if longest_duration > 0:
            if longest_duration < 60:
                return f"{longest_duration:.0f} min"
            else:
                hours = longest_duration / 60
                return f"{hours:.1f} h"
        else:
            return "N/A"
    
    def update_stat_card(self, card, value):
        """Actualiza el valor de una tarjeta de estadística"""
        # Buscar el label de valor en la tarjeta (es el primer QLabel con font bold)
        layout = card.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel) and widget.font().bold():
                    # Verificar que sea el label de valor (no el título)
                    if widget.text() != "0" and not any(keyword in widget.text() for keyword in ["Visitantes", "Zonas", "Visitas", "Promedio", "Zona Más", "Actuales", "Semana", "Larga"]):
                        widget.setText(str(value))
                        print(f"Debug: Actualizando tarjeta con valor: {value}")
                        return
                    elif widget.text() == "0" or widget.text() == "N/A":
                        widget.setText(str(value))
                        print(f"Debug: Actualizando tarjeta con valor: {value}")
                        return
        print(f"Debug: No se encontró el label para actualizar en la tarjeta")
    
    def export_to_excel(self):
        """Exporta los datos de visitantes a Excel"""
        try:
            # Recargar los datos desde el archivo JSON para obtener la información más actualizada
            self.visitor_manager.load_visitors()
            
            # Determinar qué datos exportar según el filtro
            filter_text = self.filter_combo.currentText()
            if filter_text == "Solo visitantes actuales":
                visitors_data = self.visitor_manager.get_visitor_report_data(include_departed=False)
            elif filter_text == "Solo visitantes que se fueron":
                # Filtrar solo los que se fueron
                all_data = self.visitor_manager.get_visitor_report_data(include_departed=True)
                visitors_data = [v for v in all_data if v['estado_visita'] == "Finalizada"]
            else:  # "Todos los visitantes"
                visitors_data = self.visitor_manager.get_visitor_report_data(include_departed=True)
            
            if not visitors_data:
                QMessageBox.information(self, "Información", f"No hay visitantes para exportar con el filtro '{filter_text}'.")
                return
            
            # Solicitar ubicación del archivo
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte de Visitantes",
                f"reporte_visitantes_actuales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Archivos Excel (*.xlsx);;Todos los archivos (*)"
            )
            
            if filename:
                # Crear DataFrame con los datos
                import pandas as pd
                df = pd.DataFrame(visitors_data)
                
                # Renombrar columnas para mejor presentación
                df.columns = [
                    'Nombre del Visitante',
                    'RUT',
                    'Fecha y Hora de Entrada',
                    'Fecha y Hora de Salida',
                    'Destino/Lugar',
                    'Acompañante',
                    'Estado de Visita'
                ]
                
                # Crear archivo Excel con formato
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Visitantes Actuales', index=False)
                    
                    # Obtener el workbook y worksheet para aplicar formato
                    workbook = writer.book
                    worksheet = writer.sheets['Visitantes Actuales']
                    
                    # Aplicar formato a las columnas
                    self._format_excel_worksheet(worksheet, len(visitors_data))
                
                # Mostrar mensaje de éxito
                QMessageBox.information(
                    self, 
                    "Exportación Exitosa", 
                    f"El reporte se ha guardado exitosamente en:\n{filename}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar a Excel: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _format_excel_worksheet(self, worksheet, num_rows):
        """Aplica formato al worksheet de Excel"""
        try:
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            
            # Estilo para el encabezado
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            # Estilo para las celdas de datos
            data_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Aplicar formato al encabezado (fila 1)
            for col in range(1, 8):  # 7 columnas
                cell = worksheet.cell(row=1, column=col)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
            
            # Aplicar formato a las celdas de datos
            for row in range(2, num_rows + 2):  # +2 porque empezamos desde la fila 2
                for col in range(1, 8):
                    cell = worksheet.cell(row=row, column=col)
                    cell.alignment = data_alignment
                    cell.border = border
            
            # Ajustar ancho de columnas
            column_widths = [25, 15, 20, 20, 20, 20, 15]  # Anchos para cada columna
            for i, width in enumerate(column_widths, 1):
                worksheet.column_dimensions[worksheet.cell(row=1, column=i).column_letter].width = width
                
        except Exception as e:
            print(f"Error al aplicar formato al Excel: {e}")
    
    def lighten_color(self, color, factor=0.1):
        """Aclara un color hexadecimal"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, color, factor=0.2):
        """Oscurece un color hexadecimal"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
