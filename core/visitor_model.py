from datetime import datetime
from typing import List, Dict, Optional
import json
import os
from database import get_visitantes_collection, connect_db

class Visitor:
    def __init__(self, rut: str, nombre_completo: str, acompañante: str, 
                 sector: str, estado: str = "Dentro"):
        self.id = self._generate_id()
        self.rut = rut
        self.nombre_completo = nombre_completo
        self.fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_salida = None  # Se establecerá cuando el visitante salga
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
            'fecha_salida': self.fecha_salida,
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
        visitor.fecha_salida = data.get('fecha_salida', None)
        return visitor
    
    def toggle_estado(self):
        """Cambia el estado del visitante entre 'Dentro' y 'Fuera'"""
        # Si ya está fuera, no permitir volver a "Dentro"
        if self.estado == "Fuera":
            return
        if self.estado == "Dentro":
            self.estado = "Fuera"
            self.fecha_salida = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Estado desconocido: no hacer nada
            return

class VisitorManager:
    def __init__(self, data_file: str = "visitors.json"):
        self.data_file = data_file
        self.visitors: List[Visitor] = []
        self.collection = None
        self.load_visitors()
    
    def _get_collection(self):
        """Obtiene la colección de MongoDB"""
        if self.collection is None:
            try:
                connect_db()
                self.collection = get_visitantes_collection()
            except Exception as e:
                print(f"Error al conectar con MongoDB: {e}")
                return None
        return self.collection
    
    def load_visitors(self):
        """Carga los visitantes desde MongoDB"""
        try:
            collection = self._get_collection()
            if collection is None:
                print("No se pudo conectar a MongoDB, cargando desde archivo JSON")
                self._load_from_json()
                return
            
            # Cargar desde MongoDB
            cursor = collection.find({})
            self.visitors = []
            for doc in cursor:
                # Convertir ObjectId a string si existe
                if '_id' in doc:
                    del doc['_id']
                visitor = Visitor.from_dict(doc)
                self.visitors.append(visitor)
            
            print(f"Cargados {len(self.visitors)} visitantes desde MongoDB")
            
        except Exception as e:
            print(f"Error al cargar desde MongoDB: {e}")
            print("Intentando cargar desde archivo JSON como respaldo")
            self._load_from_json()
    
    def _load_from_json(self):
        """Carga visitantes desde archivo JSON como respaldo"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.visitors = [Visitor.from_dict(visitor_data) for visitor_data in data]
                print(f"Cargados {len(self.visitors)} visitantes desde archivo JSON")
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                self.visitors = []
                print("No se encontraron visitantes en el archivo JSON")
        else:
            self.visitors = []
            print("No existe archivo JSON de respaldo")
    
    def save_visitors(self):
        """Guarda los visitantes en MongoDB"""
        try:
            collection = self._get_collection()
            if collection is None:
                print("No se pudo conectar a MongoDB, guardando en archivo JSON")
                return self._save_to_json()
            
            # Limpiar la colección y insertar todos los visitantes
            collection.delete_many({})
            if self.visitors:
                data = [visitor.to_dict() for visitor in self.visitors]
                collection.insert_many(data)
            
            print(f"Guardados {len(self.visitors)} visitantes en MongoDB")
            return True
            
        except Exception as e:
            print(f"Error al guardar en MongoDB: {e}")
            print("Guardando en archivo JSON como respaldo")
            return self._save_to_json()
    
    def _save_to_json(self):
        """Guarda visitantes en archivo JSON como respaldo"""
        data = [visitor.to_dict() for visitor in self.visitors]
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Guardados {len(self.visitors)} visitantes en archivo JSON")
            return True
        except Exception as e:
            print(f"Error al guardar visitantes en JSON: {e}")
            return False
    
    def add_visitor(self, visitor: Visitor) -> bool:
        """Agrega un nuevo visitante"""
        # Permitir reingreso si el RUT existente está "Fuera".
        # Bloquear solo si ya existe un visitante con ese RUT y estado "Dentro".
        if any((v.rut == visitor.rut and v.estado == "Dentro") for v in self.visitors):
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
        # Si el visitante ya está fuera, bloquear cualquier cambio
        if visitor.estado == "Fuera":
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
    
    def get_current_visitors(self) -> List[Visitor]:
        """Obtiene visitantes que están actualmente dentro (estado 'Dentro')"""
        return [v for v in self.visitors if v.estado == "Dentro"]
    
    def get_visitor_report_data(self, include_departed: bool = True) -> List[Dict]:
        """Obtiene datos de visitantes para reportes"""
        if include_departed:
            # Incluir todos los visitantes (actuales y que ya se fueron)
            all_visitors = self.visitors
        else:
            # Solo visitantes actuales
            all_visitors = self.get_current_visitors()
        
        report_data = []
        
        for visitor in all_visitors:
            # Determinar el estado de la fecha de salida
            if visitor.fecha_salida:
                fecha_salida = visitor.fecha_salida
                estado_visita = "Finalizada"
            else:
                fecha_salida = "Aún en el edificio"
                estado_visita = "En curso"
            
            report_data.append({
                'nombre': visitor.nombre_completo,
                'rut': visitor.rut,
                'fecha_entrada': visitor.fecha_ingreso,
                'fecha_salida': fecha_salida,
                'destino': visitor.sector,
                'acompañante': visitor.acompañante,
                'estado_visita': estado_visita
            })
        
        # Ordenar por fecha de entrada (más recientes primero)
        report_data.sort(key=lambda x: x['fecha_entrada'], reverse=True)
        
        return report_data
