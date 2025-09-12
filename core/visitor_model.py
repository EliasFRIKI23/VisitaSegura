from datetime import datetime
from typing import List, Dict, Optional
import json
import os

class Visitor:
    def __init__(self, rut: str, nombre_completo: str, acompañante: str, 
                 sector: str, estado: str = "Dentro"):
        self.id = self._generate_id()
        self.rut = rut
        self.nombre_completo = nombre_completo
        self.fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.acompañante = acompañante
        self.sector = sector
        self.estado = estado  # "Dentro" o "Fuera"
    
    def _generate_id(self) -> str:
        """Genera un ID único basado en timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"VIS{timestamp}"
    
    def to_dict(self) -> Dict:
        """Convierte el visitante a diccionario para almacenamiento"""
        return {
            'id': self.id,
            'rut': self.rut,
            'nombre_completo': self.nombre_completo,
            'fecha_ingreso': self.fecha_ingreso,
            'acompañante': self.acompañante,
            'sector': self.sector,
            'estado': self.estado
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Visitor':
        """Crea un visitante desde un diccionario"""
        visitor = cls(
            rut=data['rut'],
            nombre_completo=data['nombre_completo'],
            acompañante=data['acompañante'],
            sector=data['sector'],
            estado=data['estado']
        )
        visitor.id = data['id']
        visitor.fecha_ingreso = data['fecha_ingreso']
        return visitor
    
    def toggle_estado(self):
        """Cambia el estado del visitante entre 'Dentro' y 'Fuera'"""
        if self.estado == "Dentro":
            self.estado = "Fuera"
        else:
            self.estado = "Dentro"

class VisitorManager:
    def __init__(self, data_file: str = "visitors.json"):
        self.data_file = data_file
        self.visitors: List[Visitor] = []
        self.load_visitors()
    
    def load_visitors(self):
        """Carga los visitantes desde el archivo JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.visitors = [Visitor.from_dict(visitor_data) for visitor_data in data]
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                self.visitors = []
        else:
            self.visitors = []
    
    def save_visitors(self):
        """Guarda los visitantes en el archivo JSON"""
        data = [visitor.to_dict() for visitor in self.visitors]
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar visitantes: {e}")
            return False
    
    def add_visitor(self, visitor: Visitor) -> bool:
        """Agrega un nuevo visitante"""
        # Verificar que no exista un RUT duplicado
        if any(v.rut == visitor.rut for v in self.visitors):
            return False
        
        self.visitors.append(visitor)
        return self.save_visitors()
    
    def get_visitor_by_id(self, visitor_id: str) -> Optional[Visitor]:
        """Obtiene un visitante por su ID"""
        for visitor in self.visitors:
            if visitor.id == visitor_id:
                return visitor
        return None
    
    def update_visitor(self, visitor_id: str, **kwargs) -> bool:
        """Actualiza los datos de un visitante"""
        visitor = self.get_visitor_by_id(visitor_id)
        if not visitor:
            return False
        
        for key, value in kwargs.items():
            if hasattr(visitor, key):
                setattr(visitor, key, value)
        
        return self.save_visitors()
    
    def delete_visitor(self, visitor_id: str) -> bool:
        """Elimina un visitante"""
        visitor = self.get_visitor_by_id(visitor_id)
        if not visitor:
            return False
        
        self.visitors.remove(visitor)
        return self.save_visitors()
    
    def toggle_visitor_status(self, visitor_id: str) -> bool:
        """Cambia el estado de un visitante"""
        visitor = self.get_visitor_by_id(visitor_id)
        if not visitor:
            return False
        
        visitor.toggle_estado()
        return self.save_visitors()
    
    def get_all_visitors(self) -> List[Visitor]:
        """Obtiene todos los visitantes"""
        return self.visitors.copy()
    
    def get_visitors_by_status(self, status: str) -> List[Visitor]:
        """Obtiene visitantes por estado"""
        return [v for v in self.visitors if v.estado == status]
    
    def get_visitors_by_sector(self, sector: str) -> List[Visitor]:
        """Obtiene visitantes por sector"""
        return [v for v in self.visitors if v.sector == sector]
