# auth_manager.py
from database import get_db
from datetime import datetime
import hashlib
import secrets

class AuthManager:
    """Gestor simple de autenticación que consulta directamente la BD"""
    
    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db["Usuarios"]
        self.current_user = None
        self._ensure_default_users()
    
    def _ensure_default_users(self):
        """Asegura que existen usuarios por defecto"""
        # Verificar si ya existen usuarios
        if self.users_collection.count_documents({}) == 0:
            # Crear usuarios por defecto
            default_users = [
                {
                    "username": "admin",
                    "password": "admin123",
                    "full_name": "Administrador",
                    "role": "admin",
                    "is_active": True,
                    "created_at": datetime.now()
                },
                {
                    "username": "guardia1",
                    "password": "guardia123",
                    "full_name": "Guardia Principal",
                    "role": "guardia",
                    "is_active": True,
                    "created_at": datetime.now()
                }
            ]
            
            self.users_collection.insert_many(default_users)
            print("✅ Usuarios por defecto creados:")
            print("   - admin / admin123 (Administrador)")
            print("   - guardia1 / guardia123 (Guardia)")
    
    def login(self, username: str, password: str) -> bool:
        """Intenta hacer login con usuario y contraseña"""
        try:
            # Buscar usuario en la base de datos
            user = self.users_collection.find_one({
                "username": username,
                "password": password,  # Comparación directa (simple)
                "is_active": True
            })
            
            if user:
                # Actualizar último login
                self.users_collection.update_one(
                    {"username": username},
                    {"$set": {"last_login": datetime.now()}}
                )
                
                # Guardar usuario actual
                self.current_user = user
                return True
            
            return False
        except Exception as e:
            print(f"Error en login: {e}")
            return False
    
    def logout(self):
        """Cierra la sesión actual"""
        self.current_user = None
    
    def is_logged_in(self) -> bool:
        """Verifica si hay un usuario logueado"""
        return self.current_user is not None
    
    def get_current_user(self) -> dict:
        """Retorna el usuario actual"""
        return self.current_user
    
    def get_current_username(self) -> str:
        """Retorna el nombre de usuario actual"""
        return self.current_user.get("username", "") if self.current_user else ""
    
    def get_current_role(self) -> str:
        """Retorna el rol del usuario actual"""
        return self.current_user.get("role", "") if self.current_user else ""
    
    def is_admin(self) -> bool:
        """Verifica si el usuario actual es administrador"""
        return self.get_current_role() == "admin"
    
    def add_user(self, username: str, password: str, full_name: str, role: str = "guardia") -> bool:
        """Añade un nuevo usuario (solo administradores)"""
        if not self.is_admin():
            return False
        
        try:
            # Verificar que el usuario no exista
            if self.users_collection.find_one({"username": username}):
                return False
            
            # Crear nuevo usuario
            new_user = {
                "username": username,
                "password": password,
                "full_name": full_name,
                "role": role,
                "is_active": True,
                "created_at": datetime.now()
            }
            
            self.users_collection.insert_one(new_user)
            return True
        except Exception as e:
            print(f"Error añadiendo usuario: {e}")
            return False
    
    def get_all_users(self) -> list:
        """Obtiene todos los usuarios (solo administradores)"""
        if not self.is_admin():
            return []
        
        try:
            users = list(self.users_collection.find({}, {"password": 0}))  # Excluir contraseñas
            return users
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            return []
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Actualiza un usuario (solo administradores)"""
        if not self.is_admin():
            return False
        
        try:
            update_data = {}
            if 'full_name' in kwargs:
                update_data['full_name'] = kwargs['full_name']
            if 'role' in kwargs:
                update_data['role'] = kwargs['role']
            if 'is_active' in kwargs:
                update_data['is_active'] = kwargs['is_active']
            
            if update_data:
                result = self.users_collection.update_one(
                    {"username": username},
                    {"$set": update_data}
                )
                return result.modified_count > 0
            
            return False
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """Elimina un usuario (solo administradores)"""
        if not self.is_admin():
            return False
        
        # No permitir eliminar el último administrador
        admin_count = self.users_collection.count_documents({"role": "admin"})
        user = self.users_collection.find_one({"username": username})
        
        if admin_count <= 1 and user and user.get('role') == 'admin':
            return False
        
        try:
            result = self.users_collection.delete_one({"username": username})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            return False
