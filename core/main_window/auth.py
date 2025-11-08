from __future__ import annotations

import traceback

from PySide6.QtWidgets import QMessageBox

from .dependencies import LoginDialog


class AuthMixin:
    """Gestiona el ciclo de autenticación y actualización de la UI."""

    def check_authentication(self) -> bool:
        if self.auth_manager.is_logged_in():
            return True

        reply = QMessageBox.question(
            self,
            "🔐 Autenticación Requerida",
            "Debe iniciar sesión para acceder a esta función.\n\n¿Desea iniciar sesión ahora?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            self.open_login()
            return self.auth_manager.is_logged_in()

        return False

    def open_login(self) -> None:
        print("🔍 Intentando abrir ventana de login...")
        try:
            login = LoginDialog(self.dark_mode)
            print("✅ Ventana de login creada correctamente")
            result = login.exec()
            print(f"🔍 Resultado del login: {result}")
            if result:
                print("✅ Login aceptado")
                self.auth_manager = login.get_auth_manager()
                self.update_ui_for_authentication()
            else:
                print("❌ Login cancelado")
        except Exception as exc:
            print(f"❌ Error al abrir ventana de login: {exc}")
            traceback.print_exc()

    def update_ui_for_authentication(self) -> None:
        if self.auth_manager.is_logged_in():
            user = self.auth_manager.get_current_user()
            self.btn_open_login.setText(f"👤 {user['full_name']} (Cerrar Sesión)")
            self.btn_open_login.clicked.disconnect()
            self.btn_open_login.clicked.connect(self.logout)

            self.btn_usuarios.setVisible(self.auth_manager.is_admin())

            usuarios_view = self.navigation_manager.get_view("usuarios")
            if usuarios_view:
                usuarios_view.update_auth_manager(self.auth_manager)
                usuarios_view.set_theme(self.dark_mode)

            reportes_view = self.navigation_manager.get_view("reportes")
            if reportes_view:
                reportes_view.update_auth_manager(self.auth_manager)
        else:
            self.btn_open_login.setText("🔐 Administración")
            self.btn_open_login.clicked.disconnect()
            self.btn_open_login.clicked.connect(self.open_login)
            self.btn_usuarios.setVisible(False)

        self.btn_open_login.adjustSize()

    def logout(self) -> None:
        reply = QMessageBox.question(
            self,
            "🚪 Cerrar Sesión",
            "¿Está seguro de que desea cerrar la sesión?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.auth_manager.logout()
            self.update_ui_for_authentication()
            QMessageBox.information(
                self,
                "✅ Sesión Cerrada",
                "Ha cerrado sesión correctamente.",
            )

