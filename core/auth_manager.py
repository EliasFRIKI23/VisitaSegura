# auth_manager.py
from database import get_db
from datetime import datetime
import hashlib
import os
import secrets
from .current_user_manager import set_current_user, clear_current_user

class AuthManager:
    """Gestor simple de autenticación que consulta directamente la BD"""
    
    def __init__(self):
        self.offline_mode = os.environ.get("VISITASEGURA_OFFLINE") == "1"
        self._offline_users = []

        self.db = None
        self.users_collection = None
        self.current_user = None

        if not self.offline_mode:
            self.db = get_db()
            if self.db is not None:
                try:
                    self.users_collection = self.db["Usuarios"]
                except Exception as exc:
                    print(f"Error accediendo a la colección 'Usuarios': {exc}")
                    self.users_collection = None
            else:
                self.offline_mode = True

        if self.users_collection is None and not self.offline_mode:
            # Si no se pudo obtener la colección, activar modo offline
            print("⚠️ No se pudo acceder a la colección 'Usuarios'. Activando modo offline.")
            self.offline_mode = True

        self._ensure_default_users()
    
    def _ensure_default_users(self):
        """Asegura que existen usuarios por defecto"""
        if self.offline_mode or self.users_collection is None:
            self._setup_offline_users()
            return

        # Verificar si ya existen usuarios
        if self.users_collection.count_documents({}) == 0:
            default_users = self._build_default_users()
            self.users_collection.insert_many(default_users)
            print("✅ Usuarios por defecto creados:")
            print("   - admin / admin123 (Administrador)")
            print("   - guardia1 / guardia123 (Guardia)")

    def _build_default_users(self):
        now = datetime.now()
        return [
            {
                "username": "admin",
                "password": "admin123",
                "full_name": "Administrador",
                "role": "admin",
                "is_active": True,
                "created_at": now,
                "last_login": None,
            },
            {
                "username": "guardia1",
                "password": "guardia123",
                "full_name": "Guardia Principal",
                "role": "guardia",
                "is_active": True,
                "created_at": now,
                "last_login": None,
            },
        ]

    def _setup_offline_users(self):
        if self._offline_users:
            return

        self._offline_users = self._build_default_users()
        print("⚠️ Modo offline: usando usuarios locales por defecto.")
        print("   - admin / admin123 (Administrador)")
        print("   - guardia1 / guardia123 (Guardia)")
    
    def login(self, username: str, password: str) -> bool:
        """Intenta hacer login con usuario y contraseña"""
        if self.offline_mode or self.users_collection is None:
            return self._offline_login(username, password)

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
                self.current_user = self._sanitize_user(user)
                
                # Establecer usuario en el sistema centralizado
                set_current_user(username)
                
                return True
            
            return False
        except Exception as e:
            print(f"Error en login: {e}")
            return False
    
    def _offline_login(self, username: str, password: str) -> bool:
        """Login simplificado usando usuarios locales."""
        user = next(
            (
                u for u in self._offline_users
                if u.get("username") == username
                and u.get("password") == password
                and u.get("is_active", True)
            ),
            None,
        )

        if user:
            user["last_login"] = datetime.now()
            self.current_user = self._sanitize_user(user)
            set_current_user(username)
            return True

        return False
    
    def logout(self):
        """Cierra la sesión actual"""
        self.current_user = None
        clear_current_user()
    
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

        if self.offline_mode or self.users_collection is None:
            if any(user.get("username") == username for user in self._offline_users):
                return False

            new_user = {
                "username": username,
                "password": password,
                "full_name": full_name,
                "role": role,
                "is_active": True,
                "created_at": datetime.now(),
                "last_login": None,
            }
            self._offline_users.append(new_user)
            return True
        
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

        if self.offline_mode or self.users_collection is None:
            return [self._sanitize_user(user) for user in self._offline_users]
        
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

        if self.offline_mode or self.users_collection is None:
            user = self._get_offline_user(username)
            if not user:
                return False

            updated = False
            if 'full_name' in kwargs:
                user['full_name'] = kwargs['full_name']
                updated = True
            if 'role' in kwargs:
                user['role'] = kwargs['role']
                updated = True
            if 'is_active' in kwargs:
                user['is_active'] = kwargs['is_active']
                updated = True
            if 'password' in kwargs and kwargs['password']:
                user['password'] = kwargs['password']
                updated = True

            return updated
        
        try:
            update_data = {}
            if 'full_name' in kwargs:
                update_data['full_name'] = kwargs['full_name']
            if 'role' in kwargs:
                update_data['role'] = kwargs['role']
            if 'is_active' in kwargs:
                update_data['is_active'] = kwargs['is_active']
            if 'password' in kwargs and kwargs['password']:
                update_data['password'] = kwargs['password']
            
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

        if self.offline_mode or self.users_collection is None:
            user = self._get_offline_user(username)
            if not user:
                return False

            admin_count = sum(1 for u in self._offline_users if u.get("role") == "admin")
            if admin_count <= 1 and user.get('role') == 'admin':
                return False

            self._offline_users.remove(user)
            return True
        
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

    def _sanitize_user(self, user: dict) -> dict:
        sanitized = dict(user)
        sanitized.pop("password", None)
        return sanitized

    def _get_offline_user(self, username: str):
        for user in self._offline_users:
            if user.get("username") == username:
                return user
        return None
