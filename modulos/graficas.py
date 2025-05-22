from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import re
from sympy import symbols, lambdify, sympify


class GraficasModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.setStyleSheet("background-color: #f5f2e7; font-family: Segoe UI;")

        self.modo_actual = "2D"

        # --- Botones de selección ---
        tipo_layout = QHBoxLayout()
        self.boton_2d = QPushButton("Gráfica 2D")
        self.boton_3d = QPushButton("Gráfica 3D")

        for btn in [self.boton_2d, self.boton_3d]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0d4fc;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #d4c2f4;
                }
            """)

        self.boton_2d.clicked.connect(self.set_modo_2d)
        self.boton_3d.clicked.connect(self.set_modo_3d)

        tipo_layout.addWidget(self.boton_2d)
        tipo_layout.addWidget(self.boton_3d)
        self.layout().addLayout(tipo_layout)

        # --- Entrada de función ---
        self.entrada_group = QGroupBox("📥 Ingreso de función")
        self.entrada_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #a9a9a9;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 0px;
            }
        """)

        self.entrada_layout = QVBoxLayout()
        self.funcion_input = QLineEdit()
        self.funcion_input.setPlaceholderText("Ej: sin(x) + x^2")
        self.funcion_input.setStyleSheet("background-color: white; padding: 4px;")
        self.label_variables = QLabel("Variable: x")

        self.xmin_input = QLineEdit(); self.xmin_input.setPlaceholderText("x mínimo (ej: -10)")
        self.xmax_input = QLineEdit(); self.xmax_input.setPlaceholderText("x máximo (ej: 10)")
        self.ymin_input = QLineEdit(); self.ymin_input.setPlaceholderText("y mínimo (solo 3D)")
        self.ymax_input = QLineEdit(); self.ymax_input.setPlaceholderText("y máximo (solo 3D)")

        for campo in [self.xmin_input, self.xmax_input, self.ymin_input, self.ymax_input]:
            campo.setStyleSheet("background-color: white; padding: 4px;")

        self.entrada_layout.addWidget(QLabel("Función a graficar:"))
        self.entrada_layout.addWidget(self.funcion_input)
        self.entrada_layout.addWidget(self.label_variables)

        self.h_rango_x = QHBoxLayout()
        self.h_rango_x.addWidget(self.xmin_input)
        self.h_rango_x.addWidget(self.xmax_input)
        self.entrada_layout.addLayout(self.h_rango_x)

        self.h_rango_y = QHBoxLayout()
        self.h_rango_y.addWidget(self.ymin_input)
        self.h_rango_y.addWidget(self.ymax_input)
        self.entrada_layout.addLayout(self.h_rango_y)

        self.entrada_group.setLayout(self.entrada_layout)
        self.layout().addWidget(self.entrada_group)

        # --- Botones de acción ---
        btn_layout = QHBoxLayout()
        self.boton_graficar = QPushButton("📈 Graficar")
        self.boton_limpiar = QPushButton("🧹 Limpiar")

        for btn in [self.boton_graficar, self.boton_limpiar]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #b8e4c9;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 6px 14px;
                }
                QPushButton:hover {
                    background-color: #a2d6b8;
                }
            """)

        self.boton_graficar.clicked.connect(self.graficar)
        self.boton_limpiar.clicked.connect(self.limpiar)
        btn_layout.addWidget(self.boton_graficar)
        btn_layout.addWidget(self.boton_limpiar)
        self.layout().addLayout(btn_layout)

        # --- Área de gráfica ---
        self.figura = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figura)
        self.layout().addWidget(self.canvas)

        self.set_modo_2d()
        self.graficar_plano_vacio()

    def set_modo_2d(self):
        self.modo_actual = "2D"
        self.label_variables.setText("Variable: x")
        self.ymin_input.hide()
        self.ymax_input.hide()
        self.boton_2d.setStyleSheet(self.boton_2d.styleSheet() + "background-color: #d0c4ff;")
        self.boton_3d.setStyleSheet(self.boton_3d.styleSheet() + "background-color: #e0d4fc;")
        self.graficar_plano_vacio()

    def set_modo_3d(self):
        self.modo_actual = "3D"
        self.label_variables.setText("Variables: x, y")
        self.ymin_input.show()
        self.ymax_input.show()
        self.boton_3d.setStyleSheet(self.boton_3d.styleSheet() + "background-color: #d0c4ff;")
        self.boton_2d.setStyleSheet(self.boton_2d.styleSheet() + "background-color: #e0d4fc;")
        self.graficar_plano_vacio()

    def graficar(self):
        expr_str = self.funcion_input.text().strip().replace("^", "**")
        xmin_str = self.xmin_input.text().strip()
        xmax_str = self.xmax_input.text().strip()
        ymin_str = self.ymin_input.text().strip()
        ymax_str = self.ymax_input.text().strip()

        # Validación de caracteres inválidos
        if re.search(r"[;:!¿?@#\$&_=~`ºª]", expr_str) or expr_str.strip() in ["+", "-", "*", "/", ".", "**"]:
            QMessageBox.critical(self, "Error de sintaxis", "La función contiene caracteres inválidos o está incompleta.")
            return

        if expr_str and expr_str.strip()[-1:] in "+-*/^":
            QMessageBox.critical(self, "Error de sintaxis", "La función está incompleta. Revisa operadores al final.")
            return

        funciones_permitidas = {
            "sin", "cos", "tan", "exp", "log", "sqrt", "abs",
            "asin", "acos", "atan", "sinh", "cosh", "tanh"
        }
        tokens = re.findall(r"[a-zA-Z_]+", expr_str)
        for token in tokens:
            if token not in funciones_permitidas and not token.isalpha():
                QMessageBox.critical(self, "Función inválida", f"La función '{token}' no está permitida.")
                return

        try:
            xmin = float(xmin_str)
            xmax = float(xmax_str)
            if xmin >= xmax:
                raise ValueError("x mínimo debe ser menor que x máximo.")
        except:
            QMessageBox.warning(self, "Error", "Rango X inválido.")
            return

        if self.modo_actual == "2D":
            x = symbols("x")
            try:
                f = lambdify(x, sympify(expr_str), modules=["numpy"])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo interpretar la función:\n{e}")
                return

            x_vals = np.linspace(xmin, xmax, 400)
            try:
                y_vals = f(x_vals)
            except:
                QMessageBox.critical(self, "Error", "No se pudo evaluar la función.")
                return

            self.figura.clear()
            ax = self.figura.add_subplot(111)
            ax.plot(x_vals, y_vals, label=f"f(x) = {expr_str}")
            ax.set_title("Gráfica 2D")
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.grid(True)
            ax.legend()
            self.canvas.draw()

        elif self.modo_actual == "3D":
            try:
                ymin = float(ymin_str)
                ymax = float(ymax_str)
                if ymin >= ymax:
                    raise ValueError("y mínimo debe ser menor que y máximo.")
            except:
                QMessageBox.warning(self, "Error", "Rango Y inválido.")
                return

            x, y = symbols("x y")
            try:
                f = lambdify((x, y), sympify(expr_str), modules=["numpy"])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo interpretar la función:\n{e}")
                return

            x_vals = np.linspace(xmin, xmax, 100)
            y_vals = np.linspace(ymin, ymax, 100)
            X, Y = np.meshgrid(x_vals, y_vals)

            try:
                Z = f(X, Y)
            except:
                QMessageBox.critical(self, "Error", "No se pudo evaluar la función.")
                return

            self.figura.clear()
            ax = self.figura.add_subplot(111, projection="3d")
            ax.plot_surface(X, Y, Z, cmap="viridis")
            ax.set_title("Gráfica 3D")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("f(x, y)")
            self.canvas.draw()

    def graficar_plano_vacio(self):
        self.figura.clear()
        if self.modo_actual == "2D":
            ax = self.figura.add_subplot(111)
            ax.axhline(0, color='gray', linestyle='--')
            ax.axvline(0, color='gray', linestyle='--')
            ax.set_title("Gráfica 2D")
        else:
            ax = self.figura.add_subplot(111, projection="3d")
            X, Y = np.meshgrid(np.linspace(-5, 5, 10), np.linspace(-5, 5, 10))
            Z = np.zeros_like(X)
            ax.plot_surface(X, Y, Z, alpha=0.3, color='lightgray')
            ax.set_title("Gráfica 3D")
        self.canvas.draw()

    def limpiar(self):
        self.funcion_input.clear()
        self.xmin_input.clear()
        self.xmax_input.clear()
        self.ymin_input.clear()
        self.ymax_input.clear()
        self.graficar_plano_vacio()
