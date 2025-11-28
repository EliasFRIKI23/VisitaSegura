from __future__ import annotations

import json
import re
from typing import Dict

# ---------------------------------------------------------------------------
# Utilidades de RUT
# ---------------------------------------------------------------------------


def validate_rut_dv(numero: str, dv: str) -> bool:
    """
    Valida el dígito verificador de un RUT chileno.
    """
    try:
        numero_int = int(numero)
    except (ValueError, TypeError):
        return False

    suma = 0
    multiplicador = 2

    for digito in reversed(str(numero_int)):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    dv_calculado = 11 - resto

    if dv_calculado == 11:
        dv_calculado = 0
    elif dv_calculado == 10:
        dv_calculado = "K"

    return str(dv_calculado) == str(dv).upper()


def format_rut_without_validation(rut_input: str) -> str:
    """
    Formatea un RUT al formato estándar chileno XX.XXX.XXX-X.
    Maneja correctamente el dígito verificador 'K' y siempre usa formato de 8 dígitos.
    """
    if not rut_input:
        return ""

    # Limpiar el RUT: solo números y K/k (convertir a mayúscula)
    # También preservar guiones si existen para separar correctamente
    rut_str = str(rut_input).upper().strip()
    
    # Si tiene guión, separar número y DV explícitamente
    if "-" in rut_str:
        parts = rut_str.split("-", 1)
        # Limpiar puntos y espacios del número
        numero_raw = "".join(c for c in parts[0] if c.isdigit())
        dv_raw = parts[1].strip()
        # El DV puede ser un dígito o K
        if len(dv_raw) > 0 and (dv_raw[0].isdigit() or dv_raw[0] == "K"):
            dv = dv_raw[0].upper()  # Asegurar mayúscula para K
        else:
            dv = ""
    else:
        # No tiene guión, extraer todo junto
        rut_clean = "".join(c for c in rut_str if c.isdigit() or c == "K")
        
        if len(rut_clean) < 8 or len(rut_clean) > 9:
            return ""
        
        # Separar número y dígito verificador
        if len(rut_clean) == 8:
            # Caso: 7 dígitos + 1 dígito verificador
            numero_raw = rut_clean[:7]
            dv = rut_clean[7].upper()  # Asegurar mayúscula para K
        else:
            # Caso: 8 dígitos + 1 dígito verificador
            numero_raw = rut_clean[:-1]
            dv = rut_clean[-1].upper()  # Asegurar mayúscula para K
    
    # Validar que tenemos número y DV
    if not numero_raw or not dv:
        return ""
    
    # Asegurar que el número tenga exactamente 8 dígitos (rellenar con 0 al inicio si tiene 7)
    numero = numero_raw.zfill(8)
    
    # Validar longitud final
    if len(numero) != 8:
        return ""
    
    # Formatear siempre como XX.XXX.XXX-X (formato estándar chileno)
    numero_formateado = f"{numero[:2]}.{numero[2:5]}.{numero[5:]}"
    return f"{numero_formateado}-{dv}"


# ---------------------------------------------------------------------------
# Detección y parsing de QR
# ---------------------------------------------------------------------------


def detect_qr_type(qr_data: str) -> str:
    """
    Determina el tipo de QR basado en su contenido.
    """
    try:
        json.loads(qr_data)
        return "visitor"
    except json.JSONDecodeError:
        qr_lower = qr_data.lower()
        if any(url in qr_lower for url in ["registrocivil.cl", "sidiv.registrocivil.cl"]):
            return "carnet"

        carnet_keywords = [
            "rut",
            "run",
            "nombre",
            "apellido",
            "fecha",
            "nacimiento",
            "cédula",
            "identidad",
        ]
        if any(keyword in qr_lower for keyword in carnet_keywords):
            return "carnet"

        # Patrón mejorado que acepta RUTs con o sin puntos y con K
        rut_pattern = r"\b\d{1,2}\.?\d{3}\.?\d{3}[-]?[0-9Kk]\b|\b\d{7,8}[-]?[0-9Kk]\b"
        if re.search(rut_pattern, qr_data, re.IGNORECASE):
            return "carnet"

        return "generic"


def parse_carnet_data(qr_data: str) -> Dict[str, str]:
    """
    Extrae información relevante desde un QR de carnet chileno.
    """
    parsed_data: Dict[str, str] = {
        "rut": "",
        "nombre_completo": "",
        "raw_data": qr_data,
    }

    clean_text = qr_data.strip()

    url_patterns = [
        r"RUN=(\d{7,8}[-]?[0-9Kk])",
        r"run=(\d{7,8}[-]?[0-9Kk])",
        r"RUT=(\d{7,8}[-]?[0-9Kk])",
        r"rut=(\d{7,8}[-]?[0-9Kk])",
        r"RUN%3D(\d{7,8}[-]?[0-9Kk])",
        r"run%3D(\d{7,8}[-]?[0-9Kk])",
        r"RUT%3D(\d{7,8}[-]?[0-9Kk])",
        r"rut%3D(\d{7,8}[-]?[0-9Kk])",
        r"RUN%253D(\d{7,8}[-]?[0-9Kk])",
        r"run%253D(\d{7,8}[-]?[0-9Kk])",
        # Patrones que incluyen puntos en el número
        r"RUN=([\d.]+[-]?[0-9Kk])",
        r"run=([\d.]+[-]?[0-9Kk])",
        r"RUT=([\d.]+[-]?[0-9Kk])",
        r"rut=([\d.]+[-]?[0-9Kk])",
    ]

    if any("registrocivil.cl" in clean_text.lower() for _ in [0]):
        for pattern in url_patterns:
            rut_match = re.search(pattern, clean_text, re.IGNORECASE)
            if rut_match:
                rut = format_rut_without_validation(rut_match.group(1))
                parsed_data["rut"] = rut
                break

        if not parsed_data["rut"]:
            fallback_patterns = [
                # Patrones que pueden tener puntos y guión
                r"\b(\d{1,2}\.?\d{3}\.?\d{3}[-]?[0-9Kk])\b",
                r"\b(\d{7,8}[-]?[0-9Kk])\b",
                r"\b(\d{8}[-]?[0-9Kk])\b",
                r"\b(\d{7}[-]?[0-9Kk])\b",
            ]
            for pattern in fallback_patterns:
                rut_match = re.search(pattern, clean_text, re.IGNORECASE)
                if rut_match:
                    parsed_data["rut"] = format_rut_without_validation(rut_match.group(1))
                    if parsed_data["rut"]:  # Solo salir si el formateo fue exitoso
                        break

        if parsed_data["rut"]:
            parsed_data["nombre_completo"] = "Presione 'Iniciar Registro' para obtener nombre"

    if not parsed_data["rut"]:
        rut_patterns = [
            # Patrones que pueden tener puntos en el formato chileno
            r"\b(\d{1,2}\.?\d{3}\.?\d{3}[-]?[0-9Kk])\b",
            r"\b(\d{7,8}[-]?[0-9Kk])\b",
            r"RUT[:\s]*(\d{1,2}\.?\d{3}\.?\d{3}[-]?[0-9Kk])",
            r"RUT[:\s]*(\d{7,8}[-]?[0-9Kk])",
            r"RUN[:\s]*(\d{1,2}\.?\d{3}\.?\d{3}[-]?[0-9Kk])",
            r"RUN[:\s]*(\d{7,8}[-]?[0-9Kk])",
        ]
        for pattern in rut_patterns:
            rut_match = re.search(pattern, clean_text, re.IGNORECASE)
            if rut_match:
                parsed_data["rut"] = format_rut_without_validation(rut_match.group(1))
                if parsed_data["rut"]:  # Solo salir si el formateo fue exitoso
                    break

    name_patterns = [
        r"NOMBRE[:\s]+([A-ZÁÉÍÓÚÑ\s]+)",
        r"APELLIDOS[:\s]+([A-ZÁÉÍÓÚÑ\s]+)",
        r"NOMBRES[:\s]+([A-ZÁÉÍÓÚÑ\s]+)",
        r"([A-ZÁÉÍÓÚÑ]{2,}\s+[A-ZÁÉÍÓÚÑ]{2,}\s+[A-ZÁÉÍÓÚÑ]{2,})",
    ]

    for pattern in name_patterns:
        name_match = re.search(pattern, clean_text, re.IGNORECASE)
        if name_match:
            nombre = re.sub(r"\s+", " ", name_match.group(1).strip())
            parsed_data["nombre_completo"] = nombre.title()
            break

    if not parsed_data["rut"]:
        # Patrón flexible que puede capturar RUTs con puntos o sin ellos
        # Busca número con puntos seguido opcionalmente de guión y DV
        rut_flexible = re.search(r"\b(\d{1,2}\.?\d{3}\.?\d{3})[-]?\s*([0-9Kk])\b", clean_text, re.IGNORECASE)
        if rut_flexible:
            # Limpiar puntos del número antes de formatear
            numero_limpio = rut_flexible.group(1).replace(".", "")
            dv = rut_flexible.group(2).upper() if rut_flexible.group(2) else ""
            if numero_limpio and dv:
                parsed_data["rut"] = format_rut_without_validation(f"{numero_limpio}-{dv}")
        
        # Si aún no hay RUT, intentar sin puntos pero con DV separado
        if not parsed_data["rut"]:
            # Buscar 7 u 8 dígitos seguidos de guión opcional y DV
            rut_flexible = re.search(r"\b(\d{7,8})[-]?\s*([0-9Kk])\b", clean_text, re.IGNORECASE)
            if rut_flexible:
                numero_limpio = rut_flexible.group(1)
                dv = rut_flexible.group(2).upper() if rut_flexible.group(2) else ""
                if numero_limpio and dv:
                    parsed_data["rut"] = format_rut_without_validation(f"{numero_limpio}-{dv}")
        
        # Si aún no hay RUT, buscar patrón más flexible: número seguido de cualquier carácter y luego DV
        if not parsed_data["rut"]:
            # Patrón que busca número con puntos seguido de cualquier carácter no numérico y luego DV
            rut_flexible = re.search(r"\b(\d{1,2}\.?\d{3}\.?\d{3})[^\d]*([0-9Kk])\b", clean_text, re.IGNORECASE)
            if rut_flexible:
                numero_limpio = rut_flexible.group(1).replace(".", "")
                dv = rut_flexible.group(2).upper() if rut_flexible.group(2) else ""
                if numero_limpio and dv and len(numero_limpio) >= 7:
                    parsed_data["rut"] = format_rut_without_validation(f"{numero_limpio}-{dv}")

    if not parsed_data["nombre_completo"]:
        for line in clean_text.splitlines():
            line = line.strip()
            if re.match(r"^[A-ZÁÉÍÓÚÑ\s]{4,}$", line) and len(line.split()) >= 2:
                parsed_data["nombre_completo"] = re.sub(r"\s+", " ", line.title())
                break

    return parsed_data


# ---------------------------------------------------------------------------
# Consultas externas
# ---------------------------------------------------------------------------


def get_name_from_registry(rut: str) -> str:
    """
    Consulta una API externa para obtener el nombre según RUT.
    """
    try:
        import requests  # Import local para evitar dependencia global
    except ImportError:
        return "API no disponible - Ingrese manualmente"

    rut_clean = rut.replace("-", "")
    api_url = f"https://api.boostr.cl/rutificador/{rut_clean}"
    headers = {
        "User-Agent": "VisitaSegura/1.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        return "Timeout en consulta - Ingrese manualmente"
    except requests.exceptions.RequestException:
        return "Error de conexión - Ingrese manualmente"

    if response.status_code == 200:
        try:
            # Verificar que la respuesta tenga contenido antes de parsear
            if not response.text or not response.text.strip():
                return "Respuesta vacía de la API - Ingrese manualmente"
            
            data = response.json()
            if "nombre" in data and data["nombre"]:
                return data["nombre"].strip().title()
            if "razon_social" in data and data["razon_social"]:
                return data["razon_social"].strip().title()
        except (ValueError, json.JSONDecodeError) as e:
            # Error al parsear JSON (respuesta vacía o inválida)
            return "Error en respuesta de la API - Ingrese manualmente"
    elif response.status_code == 404:
        return "RUT no encontrado - Ingrese manualmente"
    else:
        return "Error en consulta - Ingrese manualmente"

    return "Nombre no disponible - Ingrese manualmente"

