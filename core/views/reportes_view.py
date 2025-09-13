from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

class ReportesView(QWidget):
    """Vista para reportes y estadísticas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
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
        
        # Contenido principal
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.StyledPanel)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)
        
        # Estadísticas actuales
        stats_title = QLabel("📈 Estadísticas Actuales")
        stats_title.setFont(QFont("Arial", 16, QFont.Bold))
        stats_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(stats_title)
        
        # Grid de estadísticas
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Estadística 1
        stat1 = self.create_stat_card("👥 Visitantes Hoy", "0", "#28a745", "Visitantes registrados hoy")
        stats_grid.addWidget(stat1, 0, 0)
        
        # Estadística 2
        stat2 = self.create_stat_card("🏢 Zonas Activas", "4", "#007bff", "Zonas disponibles")
        stats_grid.addWidget(stat2, 0, 1)
        
        # Estadística 3
        stat3 = self.create_stat_card("📋 Visitas Totales", "0", "#ffc107", "Visitas registradas")
        stats_grid.addWidget(stat3, 1, 0)
        
        # Estadística 4
        stat4 = self.create_stat_card("⏰ Promedio Visita", "0 min", "#dc3545", "Tiempo promedio de visita")
        stats_grid.addWidget(stat4, 1, 1)
        
        content_layout.addLayout(stats_grid)
        
        # Reportes disponibles
        reports_title = QLabel("📋 Reportes Disponibles")
        reports_title.setFont(QFont("Arial", 16, QFont.Bold))
        reports_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(reports_title)
        
        # Grid de reportes
        reports_grid = QGridLayout()
        reports_grid.setSpacing(15)
        
        # Reporte 1
        report1 = self.create_report_card("📊 Reporte Diario", "#17a2b8", "Visitas del día actual")
        reports_grid.addWidget(report1, 0, 0)
        
        # Reporte 2
        report2 = self.create_report_card("📅 Reporte Semanal", "#6f42c1", "Visitas de la semana")
        reports_grid.addWidget(report2, 0, 1)
        
        # Reporte 3
        report3 = self.create_report_card("📈 Reporte Mensual", "#fd7e14", "Visitas del mes")
        reports_grid.addWidget(report3, 1, 0)
        
        # Reporte 4
        report4 = self.create_report_card("🎯 Reporte por Zona", "#20c997", "Visitas por zona específica")
        reports_grid.addWidget(report4, 1, 1)
        
        content_layout.addLayout(reports_grid)
        
        # Mensaje de desarrollo
        dev_label = QLabel("""
        <div style="text-align: center; padding: 20px; background-color: #d1ecf1; border-radius: 8px;">
        <h3 style="color: #0c5460; margin: 0 0 10px 0;">🚧 Módulo en Desarrollo</h3>
        <p style="color: #0c5460; margin: 0;">
        Los reportes detallados y exportación de datos estarán disponibles próximamente.
        </p>
        </div>
        """)
        content_layout.addWidget(dev_label)
        
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
        """Crea una tarjeta de estadística"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Valor
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 9))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(desc_label)
        
        return card
    
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
