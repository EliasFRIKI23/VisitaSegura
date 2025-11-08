"""
Dependencias compartidas para la ventana principal.
Centraliza las importaciones con fallbacks para mantener compatibilidad.
"""

try:
    from core.login_window import LoginDialog
    from core.visitor_list import VisitorListWidget
    from core.views import VisitasView, ZonasView, ReportesView, UsuariosView
    from core.navigation_manager import NavigationManager
    from core.auth_manager import AuthManager
except ImportError:
    from login_window import LoginDialog  # type: ignore
    from visitor_list import VisitorListWidget  # type: ignore
    from views import VisitasView, ZonasView, ReportesView, UsuariosView  # type: ignore
    from navigation_manager import NavigationManager  # type: ignore
    from auth_manager import AuthManager  # type: ignore

try:
    from core.theme import (
        DUOC_PRIMARY,
        DUOC_SECONDARY,
        DUOC_SUCCESS,
        DUOC_DANGER,
        DUOC_INFO,
        darken_color as duoc_darken,
        get_standard_button_style,
    )
except Exception:
    DUOC_PRIMARY = "#003A70"
    DUOC_SECONDARY = "#FFB81C"
    DUOC_SUCCESS = "#28a745"
    DUOC_DANGER = "#dc3545"
    DUOC_INFO = "#17a2b8"

    def duoc_darken(color: str, factor: float = 0.2) -> str:
        color = color.lstrip("#")
        r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_standard_button_style(color: str, text_color: str | None = None) -> str:  # type: ignore
        return f"""
            QPushButton {{
                background-color: {color};
                color: {{text_color}};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {duoc_darken(color, 0.1)};
            }}
            QPushButton:disabled {{
                background-color: #6c757d;
                color: #adb5bd;
            }}
        """.replace("{text_color}", "#000000" if color in [DUOC_SECONDARY, "#ffc107"] else "#ffffff")

__all__ = [
    "LoginDialog",
    "VisitorListWidget",
    "VisitasView",
    "ZonasView",
    "ReportesView",
    "UsuariosView",
    "NavigationManager",
    "AuthManager",
    "DUOC_PRIMARY",
    "DUOC_SECONDARY",
    "DUOC_SUCCESS",
    "DUOC_DANGER",
    "DUOC_INFO",
    "duoc_darken",
    "get_standard_button_style",
]

