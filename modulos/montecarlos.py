from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox, QGroupBox, QComboBox, QSizePolicy
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from sympy import sympify, lambdify, symbols, integrate, Abs
import numpy as np
import random

class VistaMonteCarlo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Integración Monte Carlo")
        self.setMinimumSize(950, 600)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #f4f7f9; }
            QLabel#titulo { font-size: 22px; font-weight: bold; margin: 10px 0; color: #2c3e50; }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #eaf2f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
            }
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 6px 16px;
                font-size: 13px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1f618d;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                padding: 3px;
                font-size: 13px;
                max-width: 130px;
            }
        """)

        main_layout = QVBoxLayout()
        titulo = QLabel("📐 Simulación de Integración Monte Carlo")
        titulo.setObjectName("titulo")
        main_layout.addWidget(titulo)

        columnas_layout = QHBoxLayout()

        # -------- CONFIGURACIÓN --------
        configuracion_box = QGroupBox("⚙️ Configuración")
        form_layout = QFormLayout()

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Área bajo una curva", "Área entre dos curvas"])
        self.tipo_combo.currentIndexChanged.connect(self.actualizar_formulario)
        form_layout.addRow("Tipo de integración:", self.tipo_combo)

        self.a_input = QLineEdit(); self.a_input.setValidator(QDoubleValidator())
        self.a_input.setPlaceholderText("Ejemplo: 0")
        self.b_input = QLineEdit(); self.b_input.setValidator(QDoubleValidator())
        self.b_input.setPlaceholderText("Ejemplo: 1")
        self.fx_input = QLineEdit(); self.fx_input.setPlaceholderText("Ejemplo: x**2")
        self.gx_input = QLineEdit(); self.gx_input.setPlaceholderText("Ejemplo: sqrt(x)")
        self.num_input = QLineEdit(); self.num_input.setValidator(QIntValidator(1, 1000000))
        self.num_input.setPlaceholderText("Ejemplo: 10000")

        form_layout.addRow("Límite inferior a:", self.a_input)
        form_layout.addRow("Límite superior b:", self.b_input)
        form_layout.addRow("Función f(x):", self.fx_input)
        form_layout.addRow("Función g(x):", self.gx_input)
        form_layout.addRow("N° de puntos:", self.num_input)

        configuracion_box.setLayout(form_layout)
        columnas_layout.addWidget(configuracion_box, 1)

        # -------- RESULTADOS --------
        self.resultados_box = QGroupBox("📊 Resultados")
        self.valor_exacto_label = QLabel("✅ Exacto:")
        self.valor_mc_label = QLabel("🎯 Monte Carlo:")
        self.error_label = QLabel("📉 Error %:")
        self.dentro_label = QLabel("🔵 Dentro:")

        for lbl in [self.valor_exacto_label, self.valor_mc_label, self.error_label, self.dentro_label]:
            lbl.setStyleSheet("font-size: 14px;")

        layout_resultado = QVBoxLayout()
        layout_resultado.addWidget(self.valor_exacto_label)
        layout_resultado.addWidget(self.valor_mc_label)
        layout_resultado.addWidget(self.error_label)
        layout_resultado.addWidget(self.dentro_label)
        self.resultados_box.setLayout(layout_resultado)

        columnas_layout.addWidget(self.resultados_box, 1)
        main_layout.addLayout(columnas_layout)

        # -------- BOTONES --------
        botones = QHBoxLayout()
        self.btn_simular = QPushButton("🎯 Ejecutar Simulación")
        self.btn_simular.clicked.connect(self.ejecutar_simulacion)

        self.btn_limpiar = QPushButton("🧽 Limpiar")
        self.btn_limpiar.setStyleSheet("background-color: #e74c3c; font-weight: bold;")
        self.btn_limpiar.clicked.connect(self.limpiar_campos)

        botones.addStretch()
        botones.addWidget(self.btn_simular)
        botones.addWidget(self.btn_limpiar)
        botones.addStretch()
        main_layout.addLayout(botones)

        # -------- GRÁFICA --------
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)
        self.actualizar_formulario()

    def actualizar_formulario(self):
        self.gx_input.setVisible(self.tipo_combo.currentIndex() == 1)

    def ejecutar_simulacion(self):
        try:
            if not self.a_input.text() or not self.b_input.text() or not self.fx_input.text() or not self.num_input.text():
                QMessageBox.warning(self, "Campos incompletos", "Por favor completa todos los campos obligatorios.")
                return
            if self.tipo_combo.currentIndex() == 1 and not self.gx_input.text():
                QMessageBox.warning(self, "Campos incompletos", "Debes ingresar también la función g(x).")
                return

            x = symbols('x')
            a = float(self.a_input.text())
            b = float(self.b_input.text())
            n = int(self.num_input.text())

            fx_expr = sympify(self.fx_input.text())
            fx = lambdify(x, fx_expr, 'numpy')
            x_vals = np.linspace(a, b, 300)
            y_fx = fx(x_vals)

            if self.tipo_combo.currentIndex() == 1:
                gx_expr = sympify(self.gx_input.text())
                gx = lambdify(x, gx_expr, 'numpy')
                y_gx = gx(x_vals)
                ymin, ymax = min(min(y_fx), min(y_gx)), max(max(y_fx), max(y_gx))
            else:
                ymin, ymax = 0, max(y_fx)

            puntos_dentro, puntos_x, puntos_y, colores = 0, [], [], []
            for _ in range(n):
                rx = random.uniform(a, b)
                ry = random.uniform(ymin, ymax)
                y1 = fx(rx)
                if self.tipo_combo.currentIndex() == 1:
                    y2 = gx(rx)
                    y_lower, y_upper = min(y1, y2), max(y1, y2)
                else:
                    y_lower, y_upper = 0, y1
                if y_lower <= ry <= y_upper:
                    puntos_dentro += 1
                    colores.append('blue')
                else:
                    colores.append('red')
                puntos_x.append(rx)
                puntos_y.append(ry)

            area_total = (b - a) * (ymax - ymin)
            area_mc = area_total * (puntos_dentro / n)

            if self.tipo_combo.currentIndex() == 0:
                area_exacta = float(integrate(fx_expr, (x, a, b)))
            else:
                area_exacta = float(integrate(gx_expr - fx_expr, (x, a, b)))

            error = Abs((area_mc - area_exacta) / area_exacta) * 100

            self.valor_exacto_label.setText(f"✅ Exacto: {area_exacta:.6f}")
            self.valor_mc_label.setText(f"🎯 Monte Carlo: {area_mc:.6f}")
            self.error_label.setText(f"📉 Error %: {error:.2f}")
            self.dentro_label.setText(f"🔵 Dentro: {puntos_dentro} / {n}")

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(x_vals, y_fx, label=f"f(x) = {self.fx_input.text()}", color='blue')
            if self.tipo_combo.currentIndex() == 1:
                y_gx = gx(x_vals)
                ax.plot(x_vals, y_gx, label=f"g(x) = {self.gx_input.text()}", color='green')
            ax.scatter(puntos_x, puntos_y, s=5, c=colores, alpha=0.5)
            ax.set_title("Monte Carlo")
            ax.legend()
            ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def limpiar_campos(self):
        self.valor_exacto_label.setText("✅ Exacto:")
        self.valor_mc_label.setText("🎯 Monte Carlo:")
        self.error_label.setText("📉 Error %:")
        self.dentro_label.setText("🔵 Dentro:")
        self.a_input.clear()
        self.b_input.clear()
        self.fx_input.clear()
        self.gx_input.clear()
        self.num_input.clear()
        self.figure.clear()
        self.canvas.draw()