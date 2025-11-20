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
    Formatea un RUT al formato XX.XXX.XXX-X (o X.XXX.XXX-X para RUTs de 7 dígitos) 
    sin validar el dígito verificador. Maneja correctamente el dígito verificador 'K'.
    """
    if not rut_input:
        return ""

    # Limpiar el RUT: solo números y K/k (convertir a mayúscula)
    rut_clean = "".join(c for c in str(rut_input).upper() if c.isdigit() or c == "K")

    if len(rut_clean) < 8 or len(rut_clean) > 9:
        return ""

    # Separar número y dígito verificador
    if len(rut_clean) == 8:
        # Caso: 7 dígitos + 1 dígito verificador (formato X.XXX.XXX-X)
        numero = rut_clean[:7]
        dv = rut_clean[7]
    else:
        # Caso: 8 dígitos + 1 dígito verificador (formato XX.XXX.XXX-X)
        numero = rut_clean[:-1]
        dv = rut_clean[-1]

    # Formatear según la longitud del número
    if len(numero) == 7:
        # Formato: X.XXX.XXX-X
        numero_formateado = f"{numero[:1]}.{numero[1:4]}.{numero[4:]}"
        return f"{numero_formateado}-{dv}"
    elif len(numero) == 8:
        # Formato: XX.XXX.XXX-X (formato estándar preferido)
        numero_formateado = f"{numero[:2]}.{numero[2:5]}.{numero[5:]}"
        return f"{numero_formateado}-{dv}"
    else:
        # Fallback para otros casos
        return f"{numero}-{dv}"


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

        rut_pattern = r"\b\d{7,8}[-]?[0-9Kk]\b"
        if re.search(rut_pattern, qr_data):
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
                r"(\d{7,8}[-]?[0-9Kk])",
                r"(\d{8}[-]?[0-9Kk])",
                r"(\d{7}[-]?[0-9Kk])",
            ]
            for pattern in fallback_patterns:
                rut_match = re.search(pattern, clean_text)
                if rut_match:
                    parsed_data["rut"] = format_rut_without_validation(rut_match.group(1))
                    break

        if parsed_data["rut"]:
            parsed_data["nombre_completo"] = "Presione 'Iniciar Registro' para obtener nombre"

    if not parsed_data["rut"]:
        rut_patterns = [
            r"\b(\d{7,8}[-]?[0-9Kk])\b",
            r"RUT[:\s]*(\d{7,8}[-]?[0-9Kk])",
            r"RUN[:\s]*(\d{7,8}[-]?[0-9Kk])",
        ]
        for pattern in rut_patterns:
            rut_match = re.search(pattern, clean_text, re.IGNORECASE)
            if rut_match:
                parsed_data["rut"] = format_rut_without_validation(rut_match.group(1))
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
        rut_flexible = re.search(r"\b(\d{7,8})[-]?([0-9Kk])\b", clean_text)
        if rut_flexible:
            parsed_data["rut"] = format_rut_without_validation(
                f"{rut_flexible.group(1)}{rut_flexible.group(2)}"
            )

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

