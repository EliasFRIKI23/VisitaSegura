DUOC_PRIMARY = "#003A70"   # Azul institucional
DUOC_SECONDARY = "#FFB81C" # Amarillo institucional
DUOC_GRAY_DARK = "#495057"
DUOC_GRAY = "#6c757d"
DUOC_SUCCESS = "#28a745"
DUOC_INFO = "#17a2b8"
DUOC_DANGER = "#dc3545"
DUOC_BLUE = "#007bff"  # Mantener para acentos existentes

# Colores estandarizados para tablas y botones
DUOC_TABLE_HEADER_BG = "#2c3e50"      # Fondo del encabezado de tabla
DUOC_TABLE_HEADER_TEXT = "#ffffff"     # Texto del encabezado de tabla
DUOC_TABLE_ROW_ALT = "#f8f9fa"        # Fila alterna de tabla
DUOC_TABLE_BORDER = "#e8e8e8"         # Borde de tabla
DUOC_TABLE_SELECTION = DUOC_PRIMARY    # Color de selección de tabla
DUOC_TABLE_HOVER = "#e3f2fd"          # Color hover de tabla

# Colores estandarizados para botones
DUOC_BUTTON_PRIMARY = DUOC_PRIMARY     # Botón primario
DUOC_BUTTON_SECONDARY = DUOC_SECONDARY # Botón secundario
DUOC_BUTTON_SUCCESS = DUOC_SUCCESS     # Botón de éxito
DUOC_BUTTON_DANGER = DUOC_DANGER       # Botón de peligro
DUOC_BUTTON_INFO = DUOC_INFO           # Botón de información
DUOC_BUTTON_DISABLED = "#6c757d"       # Botón deshabilitado
DUOC_BUTTON_TEXT = "#ffffff"           # Texto de botón (claro)
DUOC_BUTTON_TEXT_DARK = "#000000"      # Texto de botón (oscuro)

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

def get_standard_table_style():
    """Retorna el estilo estandarizado para tablas"""
    return f"""
        QTableWidget {{
            gridline-color: {DUOC_TABLE_BORDER};
            background-color: #ffffff;
            alternate-background-color: {DUOC_TABLE_ROW_ALT};
            font-size: 12px;
            border: none;
            border-radius: 0px;
            selection-background-color: {DUOC_TABLE_SELECTION};
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #000000;
        }}
        QTableWidget::item {{
            padding: 12px 10px;
            border-bottom: 1px solid {DUOC_TABLE_BORDER};
            border-right: 1px solid {DUOC_TABLE_BORDER};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QTableWidget::item:selected {{
            background-color: {DUOC_TABLE_SELECTION};
            color: {DUOC_BUTTON_TEXT};
        }}
        QTableWidget::item:hover {{
            background-color: {DUOC_TABLE_HOVER};
        }}
               QHeaderView::section {{
                   background-color: {DUOC_TABLE_HEADER_BG};
                   color: {DUOC_TABLE_HEADER_TEXT};
                   font-weight: bold;
                   border: none;
                   padding: 14px 12px;
                   font-family: 'Segoe UI', Arial, sans-serif;
                   font-size: 13px;
                   border-bottom: 2px solid {DUOC_TABLE_SELECTION};
                   text-align: center;
               }}
        QHeaderView::section:hover {{
            background-color: {darken_color(DUOC_TABLE_HEADER_BG, 0.1)};
        }}
    """

def get_standard_button_style(color, text_color=None):
    """Retorna el estilo estandarizado para botones"""
    if text_color is None:
        # Determinar automáticamente el color del texto basado en el color de fondo
        text_color = DUOC_BUTTON_TEXT_DARK if color in [DUOC_SECONDARY, "#ffc107"] else DUOC_BUTTON_TEXT
    
    return f"""
        QPushButton {{
            background-color: {color};
            color: {text_color};
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QPushButton:hover {{
            background-color: {darken_color(color, 0.1)};
        }}
        QPushButton:pressed {{
            background-color: {darken_color(color, 0.2)};
        }}
        QPushButton:disabled {{
            background-color: {DUOC_BUTTON_DISABLED};
            color: #adb5bd;
        }}
    """

def normalize_rut(rut_input):
    """
    Normaliza un RUT chileno al formato estándar XX.XXX.XXX-X
    
    Args:
        rut_input (str): RUT en cualquier formato (con o sin puntos, guiones, espacios)
    
    Returns:
        str: RUT normalizado en formato XX.XXX.XXX-X o cadena vacía si es inválido
    
    Examples:
        normalize_rut("12345678-9") -> "12.345.678-9"
        normalize_rut("123456789") -> "12.345.678-9"
        normalize_rut("12.345.678-9") -> "12.345.678-9"
        normalize_rut("12 345 678 9") -> "12.345.678-9"
    """
    if not rut_input:
        return ""
    
    # Limpiar el RUT: solo números y K/k
    rut_clean = ''.join(c for c in str(rut_input).upper() if c.isdigit() or c == 'K')
    
    # Validar longitud mínima (7 dígitos + dígito verificador)
    if len(rut_clean) < 8:
        return ""
    
    # Separar número y dígito verificador
    if len(rut_clean) == 8:
        # Caso: 12345678 (sin dígito verificador)
        numero = rut_clean[:7]
        dv = rut_clean[7]
    else:
        # Caso: 123456789 o 12345678K
        numero = rut_clean[:-1]
        dv = rut_clean[-1]
    
    # Validar que el dígito verificador sea válido
    if not validate_rut_dv(numero, dv):
        return ""
    
    # Formatear al estilo chileno: XX.XXX.XXX-X
    if len(numero) <= 3:
        return f"{numero}-{dv}"
    elif len(numero) == 7:
        # RUT de 7 dígitos: XX.XXX.XX-X
        return f"{numero[:2]}.{numero[2:5]}.{numero[5:]}-{dv}"
    elif len(numero) == 8:
        # RUT de 8 dígitos: XX.XXX.XXX-X
        return f"{numero[:2]}.{numero[2:5]}.{numero[5:]}-{dv}"
    else:
        # Para otros casos, usar formato genérico
        return f"{numero[:-6]}.{numero[-6:-3]}.{numero[-3:]}-{dv}"

def validate_rut_dv(numero, dv):
    """
    Valida el dígito verificador de un RUT chileno
    
    Args:
        numero (str): Número del RUT (sin dígito verificador)
        dv (str): Dígito verificador
    
    Returns:
        bool: True si el dígito verificador es válido
    """
    try:
        # Convertir número a entero
        numero_int = int(numero)
        
        # Calcular dígito verificador usando algoritmo chileno
        suma = 0
        multiplicador = 2
        
        # Recorrer el número de derecha a izquierda
        for digito in reversed(str(numero_int)):
            suma += int(digito) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        # Calcular resto y dígito verificador esperado
        resto = suma % 11
        dv_calculado = 11 - resto
        
        # Casos especiales
        if dv_calculado == 11:
            dv_calculado = 0
        elif dv_calculado == 10:
            dv_calculado = 'K'
        
        # Comparar con el dígito verificador proporcionado
        return str(dv_calculado) == str(dv).upper()
    
    except (ValueError, TypeError):
        return False

def format_rut_display(rut):
    """
    Formatea un RUT para mostrar en la interfaz (solo si ya está normalizado)
    
    Args:
        rut (str): RUT en cualquier formato
    
    Returns:
        str: RUT formateado para mostrar
    """
    if not rut:
        return ""
    
    # Si ya está en formato correcto, devolverlo tal como está
    normalized = normalize_rut(rut)
    if normalized:
        return normalized
    
    # Si no se puede normalizar, devolver el original limpio
    rut_clean = ''.join(c for c in str(rut).upper() if c.isdigit() or c == 'K')
    return rut_clean

def get_current_user():
    """
    Obtiene el usuario actualmente autenticado
    
    Returns:
        str: Nombre de usuario actual o "Sistema" si no hay usuario autenticado
    """
    try:
        from .auth_manager import AuthManager
        auth_manager = AuthManager()
        if auth_manager.current_user:
            return auth_manager.current_user.get('username', 'Sistema')
        return "Sistema"
    except Exception:
        return "Sistema"



