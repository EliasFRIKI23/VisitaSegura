#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Prueba para Pistola QR
=================================

Este script te permite verificar que tu pistola QR está funcionando correctamente
ANTES de usarla en producción con VisitaSegura.

Uso:
    python test_pistola_qr.py

Qué hace:
    1. Abre una ventana simple con un campo de entrada
    2. Puedes escanear códigos QR con tu pistola
    3. Te muestra el contenido escaneado y estadísticas
    4. Valida que la pistola esté configurada correctamente

Autor: VisitaSegura
Fecha: Octubre 2024
"""

import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import re


class PistolaQRTester(QMainWindow):
    """Ventana de prueba para pistola QR"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔫 Test de Pistola QR - VisitaSegura")
        self.setGeometry(100, 100, 800, 600)
        
        # Estadísticas
        self.scan_count = 0
        self.successful_scans = 0
        self.failed_scans = 0
        self.total_chars = 0
        self.scan_times = []
        self.last_scan_time = None
        
        # Timer para auto-procesamiento
        self.input_timer = QTimer()
        self.input_timer.setSingleShot(True)
        self.input_timer.timeout.connect(self.auto_process_input)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title = QLabel("🔫 Test de Pistola QR")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #003A70; padding: 15px;")
        main_layout.addWidget(title)
        
        # Instrucciones
        instructions = QLabel(
            "📋 <b>Instrucciones:</b><br>"
            "1. Conecta tu pistola QR al USB<br>"
            "2. Haz clic en el campo de entrada abajo<br>"
            "3. Escanea un código QR con la pistola<br>"
            "4. Verifica que aparezca el contenido correctamente"
        )
        instructions.setFont(QFont("Arial", 12))
        instructions.setStyleSheet("""
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #90caf9;
            color: #1976d2;
        """)
        main_layout.addWidget(instructions)
        
        # Campo de entrada
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #28a745;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        
        input_label = QLabel("📥 Campo de Entrada (Haz clic aquí y escanea)")
        input_label.setFont(QFont("Arial", 14, QFont.Bold))
        input_label.setStyleSheet("color: #28a745;")
        input_layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Haz clic aquí y escanea con la pistola QR...")
        self.input_field.setFont(QFont("Courier New", 12))
        self.input_field.setMinimumHeight(50)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px;
            }
            QLineEdit:focus {
                border-color: #28a745;
                background-color: white;
            }
        """)
        
        # Conectar eventos
        self.input_field.returnPressed.connect(self.process_input)
        self.input_field.textChanged.connect(self.on_text_changed)
        
        input_layout.addWidget(self.input_field)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("✅ Procesar")
        self.process_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.process_btn.setMinimumHeight(40)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.process_btn.clicked.connect(self.process_input)
        
        self.clear_btn = QPushButton("🗑️ Limpiar")
        self.clear_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.process_btn)
        button_layout.addWidget(self.clear_btn)
        input_layout.addLayout(button_layout)
        
        main_layout.addWidget(input_frame)
        
        # Área de resultados
        results_label = QLabel("📊 Resultados del Escaneo")
        results_label.setFont(QFont("Arial", 14, QFont.Bold))
        results_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(results_label)
        
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setFont(QFont("Courier New", 10))
        self.results_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.results_area.setPlaceholderText("Los resultados aparecerán aquí...")
        main_layout.addWidget(self.results_area, 1)
        
        # Panel de estadísticas
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.stats_label = QLabel("📈 Estadísticas: 0 escaneos | 0 exitosos | 0 fallidos")
        self.stats_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.stats_label.setStyleSheet("color: #856404;")
        stats_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(stats_frame)
        
        # Poner foco en el campo
        self.input_field.setFocus()
    
    def on_text_changed(self, text):
        """Detecta cambios en el campo de entrada"""
        if text.strip():
            # Registrar tiempo de inicio si es el primer carácter
            if len(text) == 1:
                self.last_scan_time = datetime.now()
            
            # Reiniciar timer de auto-procesamiento
            self.input_timer.stop()
            self.input_timer.start(300)  # 300ms de delay
    
    def auto_process_input(self):
        """Procesa automáticamente después del delay"""
        text = self.input_field.text().strip()
        if text and len(text) >= 10:
            self.process_input()
    
    def process_input(self):
        """Procesa el input de la pistola"""
        qr_data = self.input_field.text().strip()
        
        if not qr_data:
            QMessageBox.warning(self, "⚠️ Campo Vacío", "No hay datos para procesar.")
            return
        
        # Calcular tiempo de escaneo
        scan_time = None
        if self.last_scan_time:
            scan_time = (datetime.now() - self.last_scan_time).total_milliseconds()
            self.scan_times.append(scan_time)
        
        # Actualizar estadísticas
        self.scan_count += 1
        self.total_chars += len(qr_data)
        
        # Validar el escaneo
        is_valid = self.validate_scan(qr_data)
        
        if is_valid:
            self.successful_scans += 1
        else:
            self.failed_scans += 1
        
        # Mostrar resultados
        self.display_results(qr_data, scan_time, is_valid)
        
        # Actualizar estadísticas
        self.update_stats()
        
        # Limpiar campo
        self.input_field.clear()
        self.input_field.setFocus()
        
        # Reset tiempo de escaneo
        self.last_scan_time = None
    
    def validate_scan(self, qr_data):
        """Valida el escaneo"""
        # Validaciones básicas
        if len(qr_data) < 5:
            return False
        
        # Verificar caracteres extraños
        if any(ord(c) < 32 and c not in '\n\r\t' for c in qr_data):
            return False
        
        return True
    
    def display_results(self, qr_data, scan_time, is_valid):
        """Muestra los resultados del escaneo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = f"\n{'='*80}\n"
        result += f"🕐 Timestamp: {timestamp}\n"
        result += f"📊 Escaneo #{self.scan_count}\n"
        result += f"{'='*80}\n\n"
        
        # Estado
        if is_valid:
            result += "✅ ESCANEO EXITOSO\n\n"
        else:
            result += "❌ ESCANEO FALLIDO (datos incompletos o inválidos)\n\n"
        
        # Información del QR
        result += f"📏 Longitud: {len(qr_data)} caracteres\n"
        if scan_time:
            result += f"⏱️ Tiempo de escaneo: {scan_time:.0f} ms\n"
        result += f"\n📄 Contenido:\n{'-'*80}\n{qr_data}\n{'-'*80}\n\n"
        
        # Análisis adicional
        result += "🔍 Análisis:\n"
        
        # Detectar tipo de QR
        qr_type = self.detect_qr_type(qr_data)
        result += f"   • Tipo detectado: {qr_type}\n"
        
        # Detectar RUT chileno
        rut_matches = re.findall(r'\b(\d{7,8})[-]?([0-9Kk])\b', qr_data)
        if rut_matches:
            result += f"   • RUT detectado: {len(rut_matches)} coincidencia(s)\n"
            for i, (num, dv) in enumerate(rut_matches[:3], 1):
                result += f"     - RUT {i}: {num}-{dv}\n"
        
        # Detectar URL
        if 'http://' in qr_data or 'https://' in qr_data:
            result += f"   • Contiene URL\n"
        
        # Detectar JSON
        if qr_data.startswith('{') and qr_data.endswith('}'):
            result += f"   • Formato JSON detectado\n"
        
        result += "\n"
        
        # Agregar a área de resultados
        self.results_area.append(result)
        
        # Scroll automático al final
        cursor = self.results_area.textCursor()
        cursor.movePosition(cursor.End)
        self.results_area.setTextCursor(cursor)
    
    def detect_qr_type(self, qr_data):
        """Detecta el tipo de QR"""
        qr_lower = qr_data.lower()
        
        # Carnet chileno
        if 'registrocivil.cl' in qr_lower or 'sidiv.registrocivil.cl' in qr_lower:
            return "🆔 Carnet Chileno (Registro Civil)"
        
        # JSON (posible visitante)
        if qr_data.startswith('{') and qr_data.endswith('}'):
            return "👤 JSON (Posible visitante)"
        
        # URL genérica
        if 'http://' in qr_data or 'https://' in qr_data:
            return "🌐 URL"
        
        # RUT en texto plano
        if re.search(r'\b\d{7,8}[-]?[0-9Kk]\b', qr_data):
            return "🔢 Texto con RUT"
        
        return "❓ Genérico"
    
    def update_stats(self):
        """Actualiza las estadísticas"""
        avg_time = ""
        if self.scan_times:
            avg = sum(self.scan_times) / len(self.scan_times)
            avg_time = f" | ⏱️ Promedio: {avg:.0f}ms"
        
        avg_chars = ""
        if self.scan_count > 0:
            avg = self.total_chars / self.scan_count
            avg_chars = f" | 📏 Promedio: {avg:.0f} caracteres"
        
        self.stats_label.setText(
            f"📈 Estadísticas: {self.scan_count} escaneos | "
            f"✅ {self.successful_scans} exitosos | "
            f"❌ {self.failed_scans} fallidos{avg_time}{avg_chars}"
        )
    
    def clear_all(self):
        """Limpia todo"""
        reply = QMessageBox.question(
            self,
            "🗑️ Limpiar Todo",
            "¿Deseas limpiar el historial y reiniciar las estadísticas?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.results_area.clear()
            self.input_field.clear()
            self.scan_count = 0
            self.successful_scans = 0
            self.failed_scans = 0
            self.total_chars = 0
            self.scan_times = []
            self.update_stats()
            self.input_field.setFocus()


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Configurar estilo de la aplicación
    app.setStyle("Fusion")
    
    # Crear y mostrar ventana
    window = PistolaQRTester()
    window.show()
    
    # Mensaje de bienvenida
    QMessageBox.information(
        window,
        "🎉 Bienvenido al Test de Pistola QR",
        "Esta herramienta te ayudará a verificar que tu pistola QR funciona correctamente.\n\n"
        "Instrucciones:\n"
        "1. Conecta tu pistola QR\n"
        "2. Haz clic en el campo de entrada\n"
        "3. Escanea algunos códigos QR de prueba\n"
        "4. Verifica que los datos aparezcan correctamente\n\n"
        "Si todo funciona bien aquí, funcionará en VisitaSegura."
    )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

