from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QAction, QPalette, QColor, QGuiApplication

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        # === Tamaño inicial relativo y centrado (robusto) ===
        available = QGuiApplication.primaryScreen().availableGeometry()
        w = int(available.width() * 0.2)
        h = int(available.height() * 0.2)
        self.resize(w, h)

        layout = QVBoxLayout(self)

        self.label_user = QLabel("Usuario:")
        self.input_user = QLineEdit()

        self.label_pass = QLabel("Contraseña:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Ingresar")

        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.btn_login)
