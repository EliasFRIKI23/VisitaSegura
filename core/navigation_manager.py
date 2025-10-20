from PySide6.QtWidgets import QStackedWidget, QWidget
from PySide6.QtCore import QObject, Signal

class NavigationManager(QObject):
    """Manejador central de navegación entre vistas"""
    
    # Señales para comunicación entre vistas
    view_changed = Signal(str)  # Emite el nombre de la vista activa
    theme_changed = Signal(bool)  # Emite el estado del tema (True=oscuro, False=claro)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_view = None
        self.dark_mode = False
        self.views = {}
        self.stacked_widget = None
    
    def set_stacked_widget(self, stacked_widget):
        """Establece el widget apilado para la navegación"""
        self.stacked_widget = stacked_widget
    
    def register_view(self, name, widget):
        """Registra una vista en el sistema de navegación"""
        self.views[name] = widget
        if self.stacked_widget:
            self.stacked_widget.addWidget(widget)
    
    def navigate_to(self, view_name):
        """Navega a una vista específica"""
        if view_name in self.views and self.stacked_widget:
            widget = self.views[view_name]
            index = self.stacked_widget.indexOf(widget)
            if index >= 0:
                self.stacked_widget.setCurrentIndex(index)
                self.current_view = view_name
                self.view_changed.emit(view_name)
                return True
        return False
    
    def get_current_view(self):
        """Retorna la vista actual"""
        return self.current_view
    
    def get_view(self, view_name):
        """Retorna una vista específica por nombre"""
        return self.views.get(view_name)
    
    def set_theme(self, dark_mode):
        """Establece el tema y lo propaga a todas las vistas"""
        self.dark_mode = dark_mode
        self.theme_changed.emit(dark_mode)
    
    def get_theme(self):
        """Retorna el estado actual del tema"""
        return self.dark_mode
