from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QSizePolicy, QGroupBox
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
import numpy as np


class ModeloRt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modelo SIR con Rₜ(t)")
        self.setStyleSheet("""
            QWidget {
                background-color: #eef6f9;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                font-size: 14px;
                border-radius: 6px;
                border: 1px solid #a3c1d1;
                max-width: 140px;
                background-color: white;
            }
            QPushButton {
                background-color: #00a8e8;
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007ea7;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QGroupBox {
                border: 2px solid #007ea7;
                border-radius: 8px;
                margin-top: 10px;
                padding: 8px;
                background-color: #F5D279;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                font-weight: bold;
                color: #007ea7;
            }
        """)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        titulo = QLabel("Modelo SIR con número de reproducción efectivo Rₜ(t)")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #005073;")
        main_layout.addWidget(titulo)

        cita = QLabel("Basado en: Zhang, H. et al. (2025). A Novel Approach to Forecasting Reproduction Numbers of Epidemics. Scientific Reports. https://www.nature.com/articles/s41598-025-91811-5")
        cita.setWordWrap(True)
        cita.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 10px;")
        main_layout.addWidget(cita)

        contenido_layout = QHBoxLayout()

        # Columna izquierda: formulario y tabla
        formulario_layout = QVBoxLayout()

        form_group = QGroupBox("Parámetros del modelo")
        form_layout = QFormLayout()
        self.poblacion_input = QLineEdit("10000")
        self.infectados_input = QLineEdit("10")
        self.gamma_input = QLineEdit("0.1")
        self.tiempo_input = QLineEdit("160")

        self.beta_tipo = QComboBox()
        self.beta_tipo.addItems(["Constante", "Variable (senoidal)"])

        validator = QDoubleValidator(0.0, 1e8, 10)
        int_validator = QIntValidator(1, 1000)

        for field in [self.poblacion_input, self.infectados_input]:
            field.setValidator(int_validator)
        for field in [self.gamma_input]:
            field.setValidator(validator)
        self.tiempo_input.setValidator(int_validator)

        form_layout.addRow("Población total S₀:", self.poblacion_input)
        form_layout.addRow("Infectados iniciales I₀:", self.infectados_input)
        form_layout.addRow("Tasa de recuperación γ:", self.gamma_input)
        form_layout.addRow("Días de simulación:", self.tiempo_input)
        form_layout.addRow("Tipo de β(t):", self.beta_tipo)
        form_group.setLayout(form_layout)

        formulario_layout.addWidget(form_group)

        boton = QPushButton("Simular")
        boton.clicked.connect(self.simular)
        formulario_layout.addWidget(boton)

        tabla_group = QGroupBox("Tabla de Resultados")
        tabla_layout = QVBoxLayout()
        self.tabla = QTableWidget()
        tabla_layout.addWidget(self.tabla)
        tabla_group.setLayout(tabla_layout)

        formulario_layout.addWidget(tabla_group)

        formulario_widget = QWidget()
        formulario_widget.setLayout(formulario_layout)
        formulario_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Columna derecha: gráficas verticales
        graficas_layout = QVBoxLayout()

        graficas_group = QGroupBox("Gráficas del Modelo SIR")
        graficas_inner_layout = QVBoxLayout()

        self.canvas = FigureCanvas(Figure(figsize=(6, 10)))
        self.ax1 = self.canvas.figure.add_subplot(2, 1, 1)
        self.ax2 = self.canvas.figure.add_subplot(2, 1, 2)
        graficas_inner_layout.addWidget(self.canvas)

        graficas_group.setLayout(graficas_inner_layout)
        graficas_layout.addWidget(graficas_group)

        graficas_widget = QWidget()
        graficas_widget.setLayout(graficas_layout)
        graficas_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        contenido_layout.addWidget(formulario_widget)
        contenido_layout.addWidget(graficas_widget)

        main_layout.addLayout(contenido_layout)
        self.setLayout(main_layout)
        self.simular()

    def beta_func(self, t, tipo):
        if tipo == "Constante":
            return 0.3
        elif tipo == "Variable (senoidal)":
            return 0.25 + 0.05 * np.sin(0.2 * t)

    def modelo_sir(self, t, y, gamma, tipo_beta):
        S, I, R = y
        beta = self.beta_func(t, tipo_beta)
        dSdt = -beta * S * I
        dIdt = beta * S * I - gamma * I
        dRdt = gamma * I
        return [dSdt, dIdt, dRdt]

    def simular(self):
        try:
            N = int(self.poblacion_input.text())
            I0 = int(self.infectados_input.text())
            S0 = N - I0
            R0 = 0
            gamma = float(self.gamma_input.text())
            dias = int(self.tiempo_input.text())
            tipo_beta = self.beta_tipo.currentText()

            y0 = [S0 / N, I0 / N, R0 / N]
            t_eval = np.linspace(0, dias, 300)

            sol = solve_ivp(
                self.modelo_sir, (0, dias), y0,
                args=(gamma, tipo_beta), t_eval=t_eval
            )

            self.graficar(sol, gamma, tipo_beta)
            self.mostrar_tabla(sol, gamma, tipo_beta)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def graficar(self, sol, gamma, tipo_beta):
        self.ax1.clear()
        self.ax2.clear()

        t = sol.t
        S, I, R = sol.y

        self.ax1.plot(t, S, label="S(t)")
        self.ax1.plot(t, I, label="I(t)")
        self.ax1.plot(t, R, label="R(t)")
        self.ax1.set_title("Evolución SIR")
        self.ax1.set_ylabel("Proporción")
        self.ax1.legend()
        self.ax1.grid(True)

        Rt = [self.beta_func(ti, tipo_beta) / gamma * S[i] for i, ti in enumerate(t)]
        self.ax2.plot(t, Rt, label="Rₜ(t)", color='orange')
        self.ax2.set_title("Rₜ(t) Dinámico")
        self.ax2.set_xlabel("Días")
        self.ax2.axhline(1, linestyle="--", color="gray", label="Rₜ = 1")
        self.ax2.legend()
        self.ax2.grid(True)

        self.canvas.draw()

    def mostrar_tabla(self, sol, gamma, tipo_beta):
        t = sol.t
        S, I, R = sol.y
        Rt_vals = [self.beta_func(ti, tipo_beta) / gamma * S[i] for i, ti in enumerate(t)]

        indices = range(0, len(t), 30)
        self.tabla.clear()
        self.tabla.setRowCount(len(indices))
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Día", "S", "I", "R", "Rₜ"])

        for row, i in enumerate(indices):
            self.tabla.setItem(row, 0, QTableWidgetItem(f"{t[i]:.0f}"))
            self.tabla.setItem(row, 1, QTableWidgetItem(f"{S[i]:.3f}"))
            self.tabla.setItem(row, 2, QTableWidgetItem(f"{I[i]:.3f}"))
            self.tabla.setItem(row, 3, QTableWidgetItem(f"{R[i]:.3f}"))
            self.tabla.setItem(row, 4, QTableWidgetItem(f"{Rt_vals[i]:.2f}"))

        self.tabla.resizeColumnsToContents()
