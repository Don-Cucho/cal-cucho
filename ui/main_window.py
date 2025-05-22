from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QWidget, QStackedWidget, QHBoxLayout, QSizePolicy
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

from modulos.inicio import ZigZagFondo
from modulos.matrices import MatricesModule
from modulos.polinomios import PolinomiosModule
from modulos.vectores import VectoresModule
from modulos.graficas import GraficasModule
from modulos.calculo import DerivacionIntegracionModule
from modulos.ecuaciones_diferenciales import EcuacionesDiferencialesModule
from modulos.valores_propios import SistemaEcuacionesAnalitico
from modulos.numeros_aleatorios import VistaNumerosAleatorios
from modulos.modelo_rt import ModeloRt
from modulos.montecarlos import VistaMonteCarlo


from modulos.acerca_de import AcercaDeModule

import sys
import os

def ruta_recurso(rel_path):
    """Devuelve la ruta al recurso, compatible con PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cal-cucho")
        self.setGeometry(100, 100, 900, 600)

        # Contenedor principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        self.main_layout = QHBoxLayout()

        # --- Menú lateral con fondo personalizado ---
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setSpacing(15)
        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_layout)
        self.menu_widget.setStyleSheet("background-color: #dfe6e9;")  # Fondo claro para el menú

        # --- Área central con módulos ---
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #f8f8f8;")  # Fondo claro para los módulos

        self.botones_menu = {}

        # Estilo
        self.estilo_base = """
            QPushButton {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #dcdcdc;
            }
        """
        self.estilo_activo = """
            QPushButton {
                background-color: #e2c9a2;
                border-radius: 10px;
                font-weight: bold;
                padding: 8px;
                font-size: 14px;
                text-align: left;
            }
        """

        # Diccionario de módulos con rutas a íconos
        self.modulos = {
            "Inicio": (ruta_recurso("img/iconos/inicio.ico"), ZigZagFondo()),
            "Matrices": (ruta_recurso("img/iconos/matriz.ico"), MatricesModule()),
            "Polinomios": (ruta_recurso("img/iconos/polinomio.ico"), PolinomiosModule()),
            "Vectores": (ruta_recurso("img/iconos/vector.ico"), VectoresModule()),
            "Gráficas 2D y 3D": (ruta_recurso("img/iconos/grafica.ico"), GraficasModule()),
            "Derivación e Integración": (ruta_recurso("img/iconos/calculo.ico"), DerivacionIntegracionModule()),
            "Diferenciales": (ruta_recurso("img/iconos/diferenciales.ico"), EcuacionesDiferencialesModule()),
            "Vectores y Valores Propios": ("img/iconos/valores_vectores.ico", SistemaEcuacionesAnalitico()),
            "Generador Aleatorio": (ruta_recurso("img/iconos/numeros_aleatorios.ico"), VistaNumerosAleatorios()),
            "Modelo Epidémico Rₜ": (ruta_recurso("img/iconos/epidemia.ico"), ModeloRt()),
            "Montecarlo": (ruta_recurso("img/iconos/montecarlos.ico"), VistaMonteCarlo()),

            "Acerca de": (ruta_recurso("img/iconos/acerca_de.ico"), AcercaDeModule())
        }


        for nombre, (icono_path, modulo) in self.modulos.items():
            btn = QPushButton(f"  {nombre}")
            btn.setIcon(QIcon(icono_path))
            btn.setIconSize(QSize(24, 24))
            btn.setStyleSheet(self.estilo_base)
            btn.setFixedHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, n=nombre: self.seleccionar_opcion(n))
            self.menu_layout.addWidget(btn)
            self.botones_menu[nombre] = btn
            self.stack.addWidget(modulo)

        # Armar interfaz con el menú como widget
        self.main_layout.addWidget(self.menu_widget, 1)
        self.main_layout.addWidget(self.stack, 4)
        central_widget.setLayout(self.main_layout)

        # Mostrar por defecto
        self.seleccionar_opcion("Inicio")

    def seleccionar_opcion(self, nombre_opcion):
        for nombre, boton in self.botones_menu.items():
            if nombre == nombre_opcion:
                boton.setStyleSheet(self.estilo_activo)
            else:
                boton.setStyleSheet(self.estilo_base)
        self.stack.setCurrentWidget(self.modulos[nombre_opcion][1])
