from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint
import os
import sys

# Ruta de recursos compatible con PyInstaller
def ruta_recurso(rel_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

class ZigZagFondo(QWidget):
    def __init__(self):
        super().__init__()

        # === CONTENEDOR CON MARCO ===
        marco_contenido = QFrame()
        marco_contenido.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 240);
                border: 2px solid #ccc;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        marco_contenido.setMaximumWidth(500)

        marco_layout = QVBoxLayout()
        marco_layout.setAlignment(Qt.AlignCenter)

        # === Imagen central ===
        img = QLabel()
        ruta_logo = ruta_recurso("img/iconos/inicio2.ico")
        pixmap_logo = QPixmap(ruta_logo)
        if not pixmap_logo.isNull():
            img.setPixmap(pixmap_logo.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img.setAlignment(Qt.AlignCenter)

        # === Líneas decorativas ===
        linea_sup = self.crear_linea()
        linea_inf = self.crear_linea()

        # === Textos ===
        titulo = QLabel("Bienvenido a la Calculadora Científica")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")

        subtitulo = QLabel("Selecciona un módulo del menú lateral para comenzar.")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("font-size: 15px; color: #34495e;")

        pie = QLabel("🧮 Trabaja con matrices, polinomios, vectores, gráficas\n y ecuaciones diferenciales.")
        pie.setAlignment(Qt.AlignCenter)
        pie.setStyleSheet("font-size: 13px; color: #555; padding: 10px;")

        # === Agregar al marco ===
        marco_layout.addWidget(img)
        marco_layout.addSpacing(10)
        marco_layout.addWidget(linea_sup)
        marco_layout.addSpacing(10)
        marco_layout.addWidget(titulo)
        marco_layout.addWidget(subtitulo)
        marco_layout.addSpacing(10)
        marco_layout.addWidget(linea_inf)
        marco_layout.addSpacing(15)
        marco_layout.addWidget(pie)

        marco_contenido.setLayout(marco_layout)

        # === Layout principal ===
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.addWidget(marco_contenido)
        self.setLayout(layout)

    def crear_linea(self):
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        linea.setStyleSheet("color: #bbb;")
        return linea

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colores = [QColor("#ff7675"), QColor("#74b9ff"), QColor("#55efc4"), QColor("#ffeaa7")]
        ancho_linea = 2
        espacio = 20
        alto = self.height()
        ancho = self.width()

        # Zigzags horizontales arriba y abajo
        for y_offset in range(0, alto, 100):
            color = colores[(y_offset // 100) % len(colores)]
            pen = QPen(color, ancho_linea)
            painter.setPen(pen)

            for x in range(0, ancho, espacio * 2):
                p1 = QPoint(x, y_offset)
                p2 = QPoint(x + espacio, y_offset + 15)
                p3 = QPoint(x + espacio * 2, y_offset)
                painter.drawLine(p1, p2)
                painter.drawLine(p2, p3)
