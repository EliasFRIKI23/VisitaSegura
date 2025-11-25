"""
Módulo para cargar iconos PNG desde core/ui/icons
"""
import os
import sys
from pathlib import Path
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

# Ruta base de los iconos - compatible con PyInstaller
def get_icons_dir() -> Path:
    """Obtiene el directorio de iconos, funcionando tanto en desarrollo como en EXE"""
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        # Los iconos están empaquetados en core/ui/icons dentro de _MEIPASS
        base_path = Path(sys._MEIPASS) / "core" / "ui"
    except AttributeError:
        # Si no estamos en un EXE, usar la ruta relativa normal
        base_path = Path(__file__).parent
    
    icons_path = base_path / "icons"
    return icons_path

# Mapeo de emojis a nombres de archivos PNG
EMOJI_TO_ICON = {
    "📋": "Clipboard.png",
    "👥": "Grupo_Personas.png",
    "🏢": "Zonas.png",
    "📊": "Reportes.png",
    "📖": "Manual.png",
    "🛡️": "Escudo.png",
    "🔐": "Administracion.png",
    "🔒": "Administracion.png",
    "⬅️": "Volver.png",
    "☀️": "Sol.png",
    "🌙": "Luna.png",
    "📱": "QR.png",
    "📷": "Camara.png",
    "✏️": "Editar.png",
    "📝": "Nota.png",
    "➕": "Agregar.png",
    "🗑️": "Borrar.png",
    "🔄": "Actualizar.png",
    "🆔": "ID.png",
    "📄": "Documento.png",
    "👤": "Usuario.png",
    "🤝": "Amigo.png",
    "📍": "Ubicacion.png",
    "⏰": "Hora.png",
    "👨‍💼": "Guardia.png",
    "🎯": "Diana.png",
    "🟢": "Circulo verde.png",
    "🔴": "Circulo Rojo.png",
    "⚪": "Circulo blanco.png",
    "💰": "Dinero.png",
    "🎓": "Educacion.png",
    "🎭": "Auditorio.png",
    "📈": "Grafico.png",
    "⏱️": "cronometro.png",
    "📅": "Calendario.png",
    "✅": "Exito.png",
    "⚠️": "Advertencia.png",
    "❌": "Equis.png",
    "🚫": "Prohibido.png",
    "🔍": "Lupa.png",
    "💾": "Guardar.png",
    "🚀": "Cohete.png",
    "⚡": "Rayo.png",
    "⚙️": "Tuerca.png",
    "⌨️": "Keyboard.png",
    "🖱️": "Mouse.png",
    "💡": "Idea.png",
    "🏠": "Home.png",
    "🔧": "Herramienta.png",
}


def get_icon_path(icon_name: str) -> Path:
    """Retorna la ruta completa de un icono"""
    icons_dir = get_icons_dir()
    return icons_dir / icon_name


def load_icon(icon_name: str, size: int = 24) -> QIcon:
    """
    Carga un icono PNG y retorna un QIcon
    
    Args:
        icon_name: Nombre del archivo PNG (ej: "Home.png")
        size: Tamaño del icono en píxeles (por defecto 24)
    
    Returns:
        QIcon con el icono cargado, o QIcon vacío si no se encuentra
    """
    icon_path = get_icon_path(icon_name)
    
    if not icon_path.exists():
        # Mensaje de depuración más detallado
        icons_dir = get_icons_dir()
        print(f"⚠️ Icono no encontrado: {icon_name}")
        print(f"   Buscado en: {icon_path}")
        print(f"   Directorio de iconos: {icons_dir}")
        print(f"   ¿Existe el directorio?: {icons_dir.exists()}")
        if icons_dir.exists():
            # Listar archivos disponibles para depuración
            available = list(icons_dir.glob("*.png"))
            if available:
                print(f"   Iconos disponibles: {[f.name for f in available[:5]]}...")
        return QIcon()
    
    pixmap = QPixmap(str(icon_path))
    if pixmap.isNull():
        print(f"⚠️ No se pudo cargar el icono (QPixmap vacío): {icon_path}")
        return QIcon()
    
    # Escalar si es necesario
    if size > 0:
        scaled = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon = QIcon(scaled)
    else:
        icon = QIcon(pixmap)
    
    return icon


def load_pixmap(icon_name: str, size: int = 24) -> QPixmap:
    """
    Carga un icono PNG y retorna un QPixmap
    
    Args:
        icon_name: Nombre del archivo PNG (ej: "Home.png")
        size: Tamaño del icono en píxeles (por defecto 24)
    
    Returns:
        QPixmap con el icono cargado, o QPixmap vacío si no se encuentra
    """
    icon_path = get_icon_path(icon_name)
    
    if not icon_path.exists():
        print(f"⚠️ Icono no encontrado: {icon_path}")
        return QPixmap()
    
    pixmap = QPixmap(str(icon_path))
    if pixmap.isNull():
        return QPixmap()
    
    # Escalar si es necesario
    if size > 0:
        return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    return pixmap


def get_icon_for_emoji(emoji: str, size: int = 24) -> QIcon:
    """
    Obtiene el icono PNG correspondiente a un emoji
    
    Args:
        emoji: El emoji a buscar (ej: "🏠")
        size: Tamaño del icono en píxeles (por defecto 24)
    
    Returns:
        QIcon con el icono correspondiente, o QIcon vacío si no se encuentra
    """
    icon_name = EMOJI_TO_ICON.get(emoji)
    if icon_name:
        return load_icon(icon_name, size)
    return QIcon()


def get_pixmap_for_emoji(emoji: str, size: int = 24) -> QPixmap:
    """
    Obtiene el pixmap PNG correspondiente a un emoji
    
    Args:
        emoji: El emoji a buscar (ej: "🏠")
        size: Tamaño del icono en píxeles (por defecto 24)
    
    Returns:
        QPixmap con el icono correspondiente, o QPixmap vacío si no se encuentra
    """
    icon_name = EMOJI_TO_ICON.get(emoji)
    if icon_name:
        return load_pixmap(icon_name, size)
    return QPixmap()


def create_icon_label(emoji: str, size: int = 24, parent=None) -> QLabel:
    """
    Crea un QLabel con un icono, sin bordes ni fondos
    
    Args:
        emoji: El emoji a buscar (ej: "🏠")
        size: Tamaño del icono en píxeles (por defecto 24)
        parent: Widget padre (opcional)
    
    Returns:
        QLabel con el icono configurado, o QLabel vacío si no se encuentra el icono
    """
    icon_label = QLabel(parent)
    icon_label.setStyleSheet("border: none; background-color: transparent; padding: 0; margin: 0;")
    
    icon = get_icon_for_emoji(emoji, size)
    if not icon.isNull():
        icon_label.setPixmap(icon.pixmap(size, size))
    
    return icon_label

