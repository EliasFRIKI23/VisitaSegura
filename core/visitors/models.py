from __future__ import annotations

from datetime import datetime
from typing import Dict


class Visitor:
    """
    Representa a un visitante registrado en el sistema.
    """

    def __init__(
        self,
        rut: str,
        nombre_completo: str,
        acompañante: str,
        sector: str,
        estado: str = "Dentro",
        usuario_registrador: str | None = None,
    ):
        self.id = self._generate_id()
        self.rut = rut
        self.nombre_completo = nombre_completo
        self.fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_salida = None
        self.acompañante = acompañante
        self.sector = sector
        self.estado = estado
        self.usuario_registrador = usuario_registrador

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------

    def _generate_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"VIS{timestamp}"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "rut": self.rut,
            "nombre_completo": self.nombre_completo,
            "fecha_ingreso": self.fecha_ingreso,
            "fecha_salida": self.fecha_salida,
            "acompañante": self.acompañante,
            "sector": self.sector,
            "estado": self.estado,
            "usuario_registrador": self.usuario_registrador,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Visitor":
        visitor = cls(
            rut=data["rut"],
            nombre_completo=data["nombre_completo"],
            acompañante=data["acompañante"],
            sector=data["sector"],
            estado=data.get("estado", "Dentro"),
            usuario_registrador=data.get("usuario_registrador"),
        )
        visitor.id = data.get("id", visitor.id)
        visitor.fecha_ingreso = data.get("fecha_ingreso", visitor.fecha_ingreso)
        visitor.fecha_salida = data.get("fecha_salida")
        return visitor

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------

    def toggle_estado(self) -> None:
        if self.estado == "Fuera":
            return
        if self.estado == "Dentro":
            self.estado = "Fuera"
            self.fecha_salida = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


