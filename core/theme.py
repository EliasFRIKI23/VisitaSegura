DUOC_PRIMARY = "#003A70"   # Azul institucional
DUOC_SECONDARY = "#FFB81C" # Amarillo institucional
DUOC_GRAY_DARK = "#495057"
DUOC_GRAY = "#6c757d"
DUOC_SUCCESS = "#28a745"
DUOC_INFO = "#17a2b8"
DUOC_DANGER = "#dc3545"
DUOC_BLUE = "#007bff"  # Mantener para acentos existentes

def darken_color(color: str, factor: float = 0.2) -> str:
    color = color.lstrip('#')
    r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return f"#{r:02x}{g:02x}{b:02x}"

def lighten_color(color: str, factor: float = 0.1) -> str:
    color = color.lstrip('#')
    r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"



