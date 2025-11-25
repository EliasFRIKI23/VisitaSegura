"""
Módulo para manejar rutas de recursos que funcionan tanto en desarrollo como en EXE
"""
import sys
import os
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta absoluta a un recurso, funcionando tanto en desarrollo como en EXE.
    
    Args:
        relative_path: Ruta relativa del recurso desde la raíz del proyecto
                      (ej: "Logo Duoc .png", "core/ui/icons/Home.png")
    
    Returns:
        Ruta absoluta al recurso
    """
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        # cuando se ejecuta desde un EXE
        base_path = sys._MEIPASS
    except AttributeError:
        # Si no estamos en un EXE, usar el directorio del proyecto como base
        # Obtener la ruta del directorio raíz del proyecto
        # (subir desde core/ui/resource_paths.py hasta la raíz)
        base_path = Path(__file__).parent.parent.parent.absolute()
    
    return str(Path(base_path) / relative_path)


def get_logo_path() -> str:
    """
    Obtiene la ruta al logo de Duoc UC.
    
    Returns:
        Ruta al archivo "Logo Duoc .png"
    """
    return get_resource_path("Logo Duoc .png")


def resource_exists(relative_path: str) -> bool:
    """
    Verifica si un recurso existe.
    
    Args:
        relative_path: Ruta relativa del recurso
    
    Returns:
        True si el recurso existe, False en caso contrario
    """
    path = get_resource_path(relative_path)
    return os.path.exists(path)

