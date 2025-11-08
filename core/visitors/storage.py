from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Iterable, List

from .models import Visitor


class VisitorStorageError(RuntimeError):
    """Excepción base para problemas de almacenamiento de visitantes."""


class BaseVisitorStorage(ABC):
    """Interfaz base para almacenar y recuperar visitantes."""

    @abstractmethod
    def load(self) -> List[Visitor]:
        raise NotImplementedError

    @abstractmethod
    def save(self, visitors: Iterable[Visitor]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete_all(self) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Almacenamiento JSON
# ---------------------------------------------------------------------------


class JsonVisitorStorage(BaseVisitorStorage):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> List[Visitor]:
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

        return [Visitor.from_dict(item) for item in data]

    def save(self, visitors: Iterable[Visitor]) -> bool:
        payload = [visitor.to_dict() for visitor in visitors]
        try:
            with open(self.filepath, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
            return True
        except OSError as exc:
            raise VisitorStorageError(f"Error al guardar visitantes en JSON: {exc}") from exc

    def delete_all(self) -> bool:
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            return True
        except OSError as exc:
            raise VisitorStorageError(f"No se pudo eliminar el archivo JSON: {exc}") from exc


# ---------------------------------------------------------------------------
# Almacenamiento MongoDB
# ---------------------------------------------------------------------------


class MongoVisitorStorage(BaseVisitorStorage):
    def __init__(self):
        try:
            from database import connect_db, get_visitantes_collection
        except ImportError as exc:
            raise VisitorStorageError("MongoDB no está disponible en este entorno") from exc

        if not connect_db():
            raise VisitorStorageError("No se pudo establecer conexión con MongoDB")

        self.collection = get_visitantes_collection()
        if self.collection is None:
            raise VisitorStorageError("No se pudo obtener la colección de visitantes")

    def load(self) -> List[Visitor]:
        documents = list(self.collection.find({}))
        visitors: List[Visitor] = []

        for document in documents:
            document.pop("_id", None)
            visitors.append(Visitor.from_dict(document))

        return visitors

    def save(self, visitors: Iterable[Visitor]) -> bool:
        visitors = list(visitors)
        try:
            self.collection.delete_many({})
            if visitors:
                payload = [visitor.to_dict() for visitor in visitors]
                self.collection.insert_many(payload)
            return True
        except Exception as exc:
            raise VisitorStorageError(f"Error al guardar visitantes en MongoDB: {exc}") from exc

    def delete_all(self) -> bool:
        try:
            self.collection.delete_many({})
            return True
        except Exception as exc:
            raise VisitorStorageError(f"Error al eliminar visitantes en MongoDB: {exc}") from exc


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def create_default_storage(json_filepath: str) -> BaseVisitorStorage:
    """
    Intenta usar MongoDB y cae a JSON si no está disponible.
    """
    try:
        return MongoVisitorStorage()
    except VisitorStorageError as exc:
        print(f"⚠️ MongoDB no disponible ({exc}). Usando almacenamiento JSON.")
        return JsonVisitorStorage(json_filepath)

