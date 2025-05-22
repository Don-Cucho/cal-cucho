from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFormLayout,
    QLineEdit, QGroupBox, QMessageBox, QSpinBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import math
import numpy as np
import random


class VistaNumerosAleatorios(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.setStyleSheet("""
            QWidget { background-color: #f9fdfc; }
            QLabel { font-size: 13px; font-weight: bold; color: #333333; }
            QGroupBox {
                border: 2px solid #58b4ae;
                border-radius: 8px;
                font-size: 14px;
                background-color: #e7f8f5;
                padding: 10px;
                margin-top: 10px;
            }
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton#boton_generar {
                background-color: #3aa17e;
                color: white;
            }
            QPushButton#boton_generar:hover {
                background-color: #328b6d;
            }
            QPushButton#boton_semilla {
                background-color: #2b7ca6;
                color: white;
            }
            QPushButton#boton_semilla:hover {
                background-color: #256889;
            }
            QPushButton#boton_limpiar {
                background-color: #d84b4b;
                color: white;
            }
            QPushButton#boton_limpiar:hover {
                background-color: #ba3f3f;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #ffffff;
                border: 1px solid #b0c4c4;
                padding: 4px;
                border-radius: 4px;
                font-size: 13px;
            }
            QTableWidget {
                background-color: white;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #58b4ae;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)

        self.init_ui()

    def init_ui(self):
        titulo = QLabel("🎲 Generación de Números Aleatorios")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2f4f4f;")
        self.layout().addWidget(titulo)

        self.metodo_combo = QComboBox()
        self.metodo_combo.addItems([
            "Cuadrados Medios", "Productos Medios", "Congruencial Lineal",
            "Congruencial Multiplicativo", "Mersenne Twister",
            "Xorshift", "Tausworthe"
        ])
        self.metodo_combo.currentTextChanged.connect(self.actualizar_campos)

        self.distribucion_combo = QComboBox()
        self.distribucion_combo.addItems(["Uniforme", "Exponencial", "Normal", "Binomial", "Poisson"])
        self.distribucion_combo.currentTextChanged.connect(self.actualizar_campos)

        self.cantidad = QSpinBox()
        self.cantidad.setValue(10)
        self.cantidad.setRange(1, 10000)

        self.form_dinamico = QFormLayout()
        self.inputs = {}
        self.param_group = QGroupBox("📌 Parámetros de Entrada")
        self.param_group.setLayout(self.form_dinamico)

        form = QFormLayout()
        form.addRow("🎲 Método:", self.metodo_combo)
        form.addRow("📈 Distribución:", self.distribucion_combo)
        form.addRow("🔢 Cantidad de números:", self.cantidad)

        box = QGroupBox("⚙️ Configuración General")
        box.setLayout(form)

        self.boton_calcular = QPushButton("▶️ Generar")
        self.boton_calcular.setObjectName("boton_generar")
        self.boton_calcular.clicked.connect(self.generar)

        self.boton_semilla = QPushButton("🎲 Semilla Aleatoria")
        self.boton_semilla.setObjectName("boton_semilla")
        self.boton_semilla.clicked.connect(self.generar_semilla)
        self.boton_semilla.hide()

        self.boton_limpiar = QPushButton("🧽 Limpiar")
        self.boton_limpiar.setObjectName("boton_limpiar")
        self.boton_limpiar.clicked.connect(self.limpiar_campos)

        layout_btns = QHBoxLayout()
        layout_btns.addStretch()
        layout_btns.addWidget(self.boton_calcular)
        layout_btns.addWidget(self.boton_semilla)
        layout_btns.addWidget(self.boton_limpiar)
        layout_btns.addStretch()

        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(1)
        self.tabla_resultados.setHorizontalHeaderLabels(["Valor"])

        self.canvas = FigureCanvas(plt.Figure())
        self.canvas.figure.add_subplot(111)  # Para mostrar vacío al inicio

        self.layout().addWidget(box)
        self.layout().addWidget(self.param_group)
        self.layout().addLayout(layout_btns)

        grupo_resultado = QGroupBox("📊 Resultado y Gráfico")
        grupo_resultado.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #fff9f0;
            }
        """)

        h_resultado = QHBoxLayout()
        h_resultado.addWidget(self.tabla_resultados, 1)
        h_resultado.addWidget(self.canvas, 2)
        grupo_resultado.setLayout(h_resultado)

        self.layout().addWidget(grupo_resultado)
        self.actualizar_campos()

    def actualizar_campos(self):
        for i in reversed(range(self.form_dinamico.count())):
            self.form_dinamico.itemAt(i).widget().setParent(None)
        self.inputs.clear()

        metodo = self.metodo_combo.currentText()
        dist = self.distribucion_combo.currentText()

        self.boton_semilla.setVisible(metodo in [
            "Cuadrados Medios", "Productos Medios", "Congruencial Lineal",
            "Congruencial Multiplicativo", "Mersenne Twister", "Xorshift", "Tausworthe"
        ])

        def agregar(nombre, placeholder=""):
            campo = QLineEdit()
            campo.setPlaceholderText(placeholder)
            self.form_dinamico.addRow(nombre + ":", campo)
            self.inputs[nombre] = campo

        if metodo == "Cuadrados Medios": agregar("Semilla X0", "Ej: 1234")
        elif metodo == "Productos Medios":
            agregar("Semilla X0", "Ej: 1234")
            agregar("Semilla X1", "Ej: 5678")
        elif metodo == "Congruencial Lineal":
            agregar("X0", "Ej: 7")
            agregar("a", "Ej: 5")
            agregar("c", "Ej: 3")
            agregar("m", "Ej: 10007")
        elif metodo == "Congruencial Multiplicativo":
            agregar("X0", "Ej: 7")
            agregar("a", "Ej: 5")
            agregar("m", "Ej: 10007")
        elif metodo == "Mersenne Twister": agregar("Semilla (opcional)", "Ej: 12345")
        elif metodo == "Xorshift": agregar("Semilla", "Ej: 13579")
        elif metodo == "Tausworthe": agregar("Semilla", "Ej: 24680")

        if dist == "Uniforme":
            agregar("a (inicio)", "Ej: 0")
            agregar("b (fin)", "Ej: 1")
        elif dist == "Exponencial": agregar("Lambda λ", "Ej: 1.5")
        elif dist == "Normal":
            agregar("Media μ", "Ej: 0")
            agregar("Desviación σ", "Ej: 1")
        elif dist == "Binomial":
            agregar("n", "Ej: 10")
            agregar("Probabilidad p", "Ej: 0.5")
        elif dist == "Poisson": agregar("Lambda λ", "Ej: 2")

    def get_val(self, nombre, tipo=float, obligatorio=True):
        campo = self.inputs.get(nombre)
        if not campo:
            return None
        texto = campo.text().strip()
        if not texto:
            if obligatorio:
                raise ValueError(f"⚠ El campo '{nombre}' es obligatorio.")
            return None
        try:
            return tipo(texto)
        except:
            campo.setStyleSheet("background-color: #ffdddd;")
            raise ValueError(f"❌ El campo '{nombre}' debe ser un número válido.")

    def generar_semilla(self):
        for nombre, campo in self.inputs.items():
            if "semilla" in nombre.lower() or "x0" in nombre.lower():
                campo.setText(str(random.randint(1000, 9999)))

    def generar(self):
        try:
            metodo = self.metodo_combo.currentText()
            dist = self.distribucion_combo.currentText()
            n = self.cantidad.value()
            u = []

            if metodo == "Cuadrados Medios":
                u = self.cuadrados_medios(int(self.get_val("Semilla X0")), n)
            elif metodo == "Productos Medios":
                u = self.productos_medios(int(self.get_val("Semilla X0")), int(self.get_val("Semilla X1")), n)
            elif metodo == "Congruencial Lineal":
                u = self.congruencial_lineal(int(self.get_val("X0")), int(self.get_val("a")),
                                             int(self.get_val("c")), int(self.get_val("m")), n)
            elif metodo == "Congruencial Multiplicativo":
                u = self.congruencial_multiplicativo(int(self.get_val("X0")), int(self.get_val("a")),
                                                     int(self.get_val("m")), n)
            elif metodo == "Mersenne Twister":
                semilla = self.get_val("Semilla (opcional)", int, False)
                if semilla is not None:
                    np.random.seed(semilla)
                u = list(np.random.random(n))
            elif metodo == "Xorshift":
                u = self.xorshift(int(self.get_val("Semilla")), n)
            elif metodo == "Tausworthe":
                u = self.tausworthe(int(self.get_val("Semilla")), n)

            if dist == "Uniforme":
                r = self.dist_uniforme(u, self.get_val("a (inicio)"), self.get_val("b (fin)"))
            elif dist == "Exponencial":
                r = self.dist_exponencial(u, self.get_val("Lambda λ"))
            elif dist == "Normal":
                r = self.dist_normal(u, self.get_val("Media μ"), self.get_val("Desviación σ"))
            elif dist == "Poisson":
                r = self.dist_poisson(u, self.get_val("Lambda λ"))
            elif dist == "Binomial":
                r = self.dist_binomial(u, self.get_val("n"), self.get_val("Probabilidad p"))
            else:
                r = u

            self.mostrar_resultados(r)

        except Exception as e:
            QMessageBox.critical(self, "Error crítico", f"Ocurrió un error inesperado:\n{str(e)}")

    def mostrar_resultados(self, lista):
        self.tabla_resultados.setRowCount(len(lista))
        for i, val in enumerate(lista):
            self.tabla_resultados.setItem(i, 0, QTableWidgetItem(str(round(val, 4))))

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.plot(range(len(lista)), lista, color='orange', linestyle='-', marker='o')
        ax.set_title("Gráfico de Números Generados")
        ax.set_xlabel("Índice")
        ax.set_ylabel("Valor")
        self.canvas.draw()

    def limpiar_campos(self):
        for campo in self.inputs.values():
            campo.clear()
            campo.setStyleSheet("background-color: white;")
        self.tabla_resultados.setRowCount(0)
        self.canvas.figure.clear()
        self.canvas.draw()

    # Métodos de generación (sin cambios)
    def cuadrados_medios(self, x0, n):
        r = []
        for _ in range(n):
            x0 = str(int(x0)**2).zfill(8)
            medio = int(x0[2:6])
            r.append(medio / 10000)
            x0 = medio
        return r

    def productos_medios(self, x0, x1, n):
        r = []
        for _ in range(n):
            prod = str(x0 * x1).zfill(8)
            medio = int(prod[2:6])
            r.append(medio / 10000)
            x0, x1 = x1, medio
        return r

    def congruencial_lineal(self, x0, a, c, m, n):
        return [(x0 := (a * x0 + c) % m) / m for _ in range(n)]

    def congruencial_multiplicativo(self, x0, a, m, n):
        return [(x0 := (a * x0) % m) / m for _ in range(n)]

    def xorshift(self, x, n):
        r = []
        for _ in range(n):
            x ^= (x << 13) & 0xFFFFFFFF
            x ^= (x >> 17)
            x ^= (x << 5) & 0xFFFFFFFF
            r.append((x % 10000) / 10000)
        return r

    def tausworthe(self, s, n):
        r = []
        for _ in range(n):
            s = ((s << 1) ^ ((s >> 31) * 0x8ebfd028)) & 0xFFFFFFFF
            r.append((s % 10000) / 10000)
        return r

    # Distribuciones
    def dist_uniforme(self, u, a, b): return [round(a + (b - a) * x, 4) for x in u]
    def dist_exponencial(self, u, lamb): return [round(-math.log(x) / lamb, 4) for x in u if x > 0]
    def dist_normal(self, u, mu, sigma):
        z = []
        for i in range(0, len(u) - 1, 2):
            z1 = math.sqrt(-2 * math.log(u[i])) * math.cos(2 * math.pi * u[i + 1])
            z.append(round(mu + sigma * z1, 4))
        return z
    def dist_poisson(self, u, lamb):
        r = []
        for ui in u:
            L, k, p = math.exp(-lamb), 0, 1
            while p >= L:
                k += 1
                p *= ui
            r.append(k - 1)
        return r
    def dist_binomial(self, u, n, p):
        return [sum(1 for _ in range(int(n)) if x <= p) for x in u]
