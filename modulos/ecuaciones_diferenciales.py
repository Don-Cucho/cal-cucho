from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QGroupBox, QFormLayout, QSizePolicy, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from sympy import  symbols, sympify, diff
from sympy.core.sympify import SympifyError  
import numpy as np
import re 

class EcuacionesDiferencialesModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.x, self.y = symbols('x y')

        self.setStyleSheet("""
            QWidget {
                background-color: #F1EFE5;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #444;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                background-color: white;
                padding: 6px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #aacfcf;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #93b8b8;
            }
            QTableWidget {
                background-color: #F7F7F7;
                gridline-color: #999;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #aacfcf;
                font-weight: bold;
                padding: 6px;
                font-size: 13px;
                border: 1px solid #888;
            }
        """)

        self.init_ui()
        self.aplicar_validadores()

    def aplicar_validadores(self):
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.x0_input.setValidator(validator)
        self.y0_input.setValidator(validator)
        self.h_input.setValidator(validator)
        self.xf_input.setValidator(validator)

    def init_ui(self):
        entrada_group = QGroupBox("📥 Parámetros de Entrada")
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(12)

        self.ecuacion_input = QLineEdit()
        self.ecuacion_input.setPlaceholderText("Ej: x*y")
        self.ecuacion_input.setMaximumWidth(250)

        self.x0_input = QLineEdit()
        self.x0_input.setPlaceholderText("Ej: 1")
        self.x0_input.setMaximumWidth(100)

        self.y0_input = QLineEdit()
        self.y0_input.setPlaceholderText("Ej: 2")
        self.y0_input.setMaximumWidth(100)

        self.h_input = QLineEdit()
        self.h_input.setPlaceholderText("Ej: 0.1")
        self.h_input.setMaximumWidth(100)

        self.xf_input = QLineEdit()
        self.xf_input.setPlaceholderText("Ej: 5")
        self.xf_input.setMaximumWidth(100)

        self.metodo_box = QComboBox()
        self.metodo_box.addItems(["Euler", "Heun", "Runge-Kutta 4", "Taylor orden 2"])
        self.metodo_box.setMaximumWidth(180)

        form_layout.addRow("Ecuación dy/dx =", self.ecuacion_input)
        form_layout.addRow("x₀ =", self.x0_input)
        form_layout.addRow("y₀ =", self.y0_input)
        form_layout.addRow("Paso h =", self.h_input)
        form_layout.addRow("x final =", self.xf_input)
        form_layout.addRow("Método:", self.metodo_box)

        entrada_group.setLayout(form_layout)
        self.layout().addWidget(entrada_group)

        botones_layout = QHBoxLayout()
        self.boton_calcular = QPushButton("▶️ Calcular")
        self.boton_calcular.setFixedWidth(120)
        self.boton_calcular.clicked.connect(self.ejecutar)

        self.boton_limpiar = QPushButton("🧽 Limpiar")
        self.boton_limpiar.setFixedWidth(120)
        self.boton_limpiar.clicked.connect(self.limpiar)

        botones_layout.addStretch()
        botones_layout.addWidget(self.boton_calcular)
        botones_layout.addWidget(self.boton_limpiar)
        botones_layout.addStretch()
        self.layout().addLayout(botones_layout)

        splitter = QSplitter(Qt.Horizontal)

        grafico_group = QGroupBox("📈 Gráfica")
        grafico_layout = QVBoxLayout()
        self.figura = Figure()
        self.canvas = FigureCanvas(self.figura)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.figura.add_subplot(111)
        grafico_layout.addWidget(self.canvas)
        grafico_group.setLayout(grafico_layout)
        grafico_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        tabla_group = QGroupBox("📊 Resultados")
        tabla_layout = QVBoxLayout()
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["x", "y", "f(x,y)"])
        self.tabla.setRowCount(5)
        for i in range(5):
            for j in range(3):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(i, j, item)

        self.tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tabla_layout.addWidget(self.tabla)
        tabla_group.setLayout(tabla_layout)
        tabla_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        splitter.addWidget(grafico_group)
        splitter.addWidget(tabla_group)
        splitter.setSizes([1, 1])

        self.layout().addWidget(splitter)

    def ejecutar(self):
        try:
            expr_str = self.ecuacion_input.text().replace("^", "**").strip()

            # Validación: caracteres no permitidos
            caracteres_invalidos = r"[;:!¿?@#\$&_=~`%ºª|\\]"
            if re.search(caracteres_invalidos, expr_str):
                QMessageBox.critical(self, "Error de sintaxis", "La ecuación contiene símbolos inválidos como %, ;, !, etc.")
                return

            # Validación: división entera //
            if '//' in expr_str:
                QMessageBox.critical(self, "Error de sintaxis", "La operación '//' no está permitida. Usa '/' para dividir.")
                return

            try:
                f_expr = sympify(expr_str)
            except (SympifyError, SyntaxError):
                QMessageBox.critical(self, "Error", "La ecuación ingresada no es válida. Revisa que esté bien escrita.")
                return
            # Validación de caracteres inválidos
            if not expr_str or expr_str[-1] in "+-*/^." or expr_str in "+-*/^.":
                raise ValueError("La expresión está vacía o incompleta.")

            if any(c in expr_str for c in ";:!¿?@#\$&_=~`ºª[]{}"):
                raise ValueError("La expresión contiene caracteres no válidos.")

            funciones_permitidas = {
                "sin", "cos", "tan", "exp", "log", "sqrt", "abs",
                "asin", "acos", "atan", "sinh", "cosh", "tanh"
            }
            tokens = re.findall(r"[a-zA-Z_]+", expr_str)
            for token in tokens:
                if token not in funciones_permitidas and token not in ['x', 'y']:
                    raise ValueError(f"La función '{token}' no está permitida.")

            f_expr = sympify(expr_str)
            f = lambda x, y: float(f_expr.subs({self.x: x, self.y: y}))

            # Validación: campos vacíos
            if not self.ecuacion_input.text().strip() or not self.x0_input.text().strip() or not self.y0_input.text().strip() or not self.h_input.text().strip() or not self.xf_input.text().strip():
                QMessageBox.critical(self, "Error", "Por favor, llena todos los campos antes de calcular.")
                return

            # Validación: campos numéricos válidos
            try:
                x0 = float(self.x0_input.text())
            except ValueError:
                QMessageBox.critical(self, "Error", "El valor de x₀ debe ser un número válido.")
                return

            try:
                y0 = float(self.y0_input.text())
            except ValueError:
                QMessageBox.critical(self, "Error", "El valor de y₀ debe ser un número válido.")
                return

            try:
                h = float(self.h_input.text())
                if h <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.critical(self, "Error", "El paso h debe ser un número positivo y mayor que cero.")
                return

            try:
                xf = float(self.xf_input.text())
                if xf <= x0:
                    QMessageBox.critical(self, "Error", "El valor de x final debe ser mayor que x₀.")
                    return
            except ValueError:
                QMessageBox.critical(self, "Error", "El valor de x final debe ser un número válido.")
                return


            if h <= 0:
                raise ValueError("El paso h debe ser mayor que cero.")
            if x0 >= xf:
                raise ValueError("x₀ debe ser menor que x final.")

            pasos = int(np.ceil((xf - x0) / h))

            xs = [x0]
            ys = [y0]
            fs = [round(f(x0, y0), 5)]

            for _ in range(pasos):
                xi = xs[-1]
                yi = ys[-1]
                metodo = self.metodo_box.currentText()

                if metodo == "Euler":
                    yi1 = yi + h * f(xi, yi)
                elif metodo == "Heun":
                    k1 = f(xi, yi)
                    k2 = f(xi + h, yi + h * k1)
                    yi1 = yi + (h / 2) * (k1 + k2)
                elif metodo == "Runge-Kutta 4":
                    k1 = f(xi, yi)
                    k2 = f(xi + h / 2, yi + h * k1 / 2)
                    k3 = f(xi + h / 2, yi + h * k2 / 2)
                    k4 = f(xi + h, yi + h * k3)
                    yi1 = yi + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
                elif metodo == "Taylor orden 2":
                    f1 = f(xi, yi)
                    dfx = float(diff(f_expr, self.x).subs({self.x: xi, self.y: yi}))
                    dfy = float(diff(f_expr, self.y).subs({self.x: xi, self.y: yi}))
                    yi1 = yi + h * f1 + (h**2 / 2) * (dfx + dfy * f1)
                else:
                    raise ValueError("Método no soportado.")

                xi1 = xi + h
                xs.append(round(xi1, 5))
                ys.append(round(yi1, 5))
                fs.append(round(f(xi1, yi1), 5))

            self.tabla.setRowCount(len(xs))
            for i in range(len(xs)):
                self.tabla.setItem(i, 0, QTableWidgetItem(str(xs[i])))
                self.tabla.setItem(i, 1, QTableWidgetItem(str(ys[i])))
                item_fxy = QTableWidgetItem(str(fs[i]))
                item_fxy.setForeground(QColor("#004080"))
                font = item_fxy.font()
                font.setBold(True)
                item_fxy.setFont(font)
                self.tabla.setItem(i, 2, item_fxy)

            self.figura.clear()
            ax = self.figura.add_subplot(111)
            ax.plot(xs, ys, marker='o', color='royalblue')
            ax.set_title("Solución Aproximada")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"{str(e)}")

    def limpiar(self):
        self.ecuacion_input.clear()
        self.x0_input.clear()
        self.y0_input.clear()
        self.h_input.clear()
        self.xf_input.clear()
        self.tabla.clearContents()
        self.tabla.setRowCount(5)
        for i in range(5):
            for j in range(3):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(i, j, item)

        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.grid(True)
        self.canvas.draw()
