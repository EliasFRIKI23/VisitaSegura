#!/usr/bin/env python3
"""
Sistema centralizado para obtener el usuario actual
"""

import threading
from typing import Optional

# Variable global para almacenar el usuario actual
_current_user = None
_lock = threading.Lock()

def set_current_user(username: str):
    """Establece el usuario actual en el sistema"""
    global _current_user
    with _lock:
        _current_user = username
        print(f"[AUTH] Usuario establecido: {username}")

def get_current_user() -> str:
    """Obtiene el usuario actual del sistema"""
    global _current_user
    with _lock:
        if _current_user:
            print(f"[AUTH] Usuario obtenido: {_current_user}")
            return _current_user
        else:
            print("[AUTH] No hay usuario establecido, devolviendo 'Sistema'")
            return "Sistema"

def clear_current_user():
    """Limpia el usuario actual"""
    global _current_user
    with _lock:
        print(f"[AUTH] Usuario limpiado: {_current_user}")
        _current_user = None

def is_user_logged_in() -> bool:
    """Verifica si hay un usuario logueado"""
    global _current_user
    with _lock:
        return _current_user is not None

# Función para debug
def debug_current_user():
    """Muestra información de debug del usuario actual"""
    global _current_user
    with _lock:
        print(f"[DEBUG] Usuario actual: {repr(_current_user)}")
        print(f"[DEBUG] Tipo: {type(_current_user)}")
        print(f"[DEBUG] Es None?: {_current_user is None}")
        print(f"[DEBUG] Es vacio?: {_current_user == ''}")
        print(f"[DEBUG] Es falsy?: {not _current_user}")
