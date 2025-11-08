from __future__ import annotations

from typing import Dict, List, Optional

from .models import Visitor
from .storage import (
    BaseVisitorStorage,
    JsonVisitorStorage,
    VisitorStorageError,
    create_default_storage,
)


class VisitorManager:
    """
    Gestiona la lista de visitantes utilizando el almacenamiento disponible.
    Se mantiene como singleton para preservar el comportamiento histórico.
    """

    _instance: "VisitorManager" | None = None

    def __new__(cls, data_file: str = "visitors.json"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, data_file: str = "visitors.json"):
        if getattr(self, "_initialized", False):
            # Permitir que otras instancias usen diferente archivo
            self.data_file = data_file
            return

        self.data_file = data_file
        self.visitors: List[Visitor] = []
        self.storage: BaseVisitorStorage = create_default_storage(self.data_file)
        self._initialized = True

        self.load_visitors()

    # ------------------------------------------------------------------
    # Almacenamiento
    # ------------------------------------------------------------------

    def _switch_to_json_storage(self) -> None:
        self.storage = JsonVisitorStorage(self.data_file)

    def load_visitors(self) -> None:
        try:
            self.visitors = self.storage.load()
            print(f"Cargados {len(self.visitors)} visitantes desde almacenamiento principal")
        except VisitorStorageError as exc:
            print(f"Error al cargar visitantes: {exc}")
            print("Intentando cargar desde archivo JSON como respaldo")
            self._switch_to_json_storage()
            self.visitors = self.storage.load()
            print(f"Cargados {len(self.visitors)} visitantes desde archivo JSON")

    def save_visitors(self) -> bool:
        try:
            return self.storage.save(self.visitors)
        except VisitorStorageError as exc:
            print(f"Error al guardar visitantes: {exc}")
            if isinstance(self.storage, JsonVisitorStorage):
                return False

            print("Guardando en archivo JSON como respaldo")
            self._switch_to_json_storage()
            return self.storage.save(self.visitors)

    # ------------------------------------------------------------------
    # CRUD Visitantes
    # ------------------------------------------------------------------

    def add_visitor(self, visitor: Visitor) -> bool:
        if any(v.rut == visitor.rut and v.estado == "Dentro" for v in self.visitors):
            return False

        self.visitors.append(visitor)
        if not self.save_visitors():
            self.visitors.pop()
            return False
        return True

    def get_visitor_by_id(self, visitor_id: str) -> Optional[Visitor]:
        return next((visitor for visitor in self.visitors if visitor.id == visitor_id), None)

    def update_visitor(self, visitor_id: str, **kwargs) -> bool:
        visitor = self.get_visitor_by_id(visitor_id)
        if not visitor:
            return False

        for key, value in kwargs.items():
            if hasattr(visitor, key):
                setattr(visitor, key, value)

        return self.save_visitors()

    def delete_visitor(self, visitor_id: str) -> bool:
        visitor = self.get_visitor_by_id(visitor_id)
        if not visitor:
            return False

        self.visitors.remove(visitor)
        return self.save_visitors()

    def toggle_visitor_status(self, visitor_id: str) -> bool:
        visitor = self.get_visitor_by_id(visitor_id)
        if not visitor or visitor.estado == "Fuera":
            return False

        visitor.toggle_estado()
        return self.save_visitors()

    def delete_all_visitors(self) -> bool:
        try:
            self.storage.delete_all()
            self.visitors.clear()
            if not isinstance(self.storage, JsonVisitorStorage):
                # Limpiar también el respaldo JSON para consistencia
                JsonVisitorStorage(self.data_file).delete_all()
            return True
        except VisitorStorageError as exc:
            print(f"Error al eliminar todos los visitantes: {exc}")
            self._switch_to_json_storage()
            self.visitors.clear()
            return self.save_visitors()

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def get_all_visitors(self) -> List[Visitor]:
        return list(self.visitors)

    def get_visitors_by_status(self, status: str) -> List[Visitor]:
        return [visitor for visitor in self.visitors if visitor.estado == status]

    def get_visitors_by_sector(self, sector: str) -> List[Visitor]:
        return [visitor for visitor in self.visitors if visitor.sector == sector]

    def get_current_visitors(self) -> List[Visitor]:
        return [visitor for visitor in self.visitors if visitor.estado == "Dentro"]

    def get_visitor_report_data(self, include_departed: bool = True) -> List[Dict]:
        if include_departed:
            visitors = self.visitors
        else:
            visitors = self.get_current_visitors()

        report_data: List[Dict] = []
        for visitor in visitors:
            if visitor.fecha_salida:
                fecha_salida = visitor.fecha_salida
                estado_visita = "Finalizada"
            else:
                fecha_salida = "Aún en el edificio"
                estado_visita = "En curso"

            report_data.append(
                {
                    "nombre": visitor.nombre_completo,
                    "rut": visitor.rut,
                    "fecha_entrada": visitor.fecha_ingreso,
                    "fecha_salida": fecha_salida,
                    "destino": visitor.sector,
                    "acompañante": visitor.acompañante,
                    "estado_visita": estado_visita,
                    "usuario_registrador": visitor.usuario_registrador or "Sistema",
                }
            )

        report_data.sort(key=lambda item: item["fecha_entrada"], reverse=True)
        return report_data

    def force_reload(self) -> int:
        print("Forzando recarga de visitantes...")
        self.load_visitors()
        return len(self.visitors)


