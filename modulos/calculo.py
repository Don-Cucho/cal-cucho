from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QPixmap
from sympy import sympify, symbols, diff, integrate, latex
import re
import matplotlib.pyplot as plt
import os

class DerivacionIntegracionModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.operacion_actual = None
        self.botones = {}

        self.setStyleSheet("""
            QWidget { background-color: #F1EFE5; }
            QPushButton {
                background-color: #aacfcf; padding: 6px 12px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #93b8b8; }
            QLineEdit { background-color: white; padding: 4px; }
            QGroupBox {
                font-weight: bold; font-size: 13px;
                border: 2px solid #444; border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }
        """)

        # --- Entrada ---
        entrada_group = QGroupBox("🔢 Ingresar función")
        entrada_layout = QVBoxLayout()

        self.funcion_input = QLineEdit()
        self.funcion_input.setPlaceholderText("Ej: x^3 + sin(x)")
        self.funcion_input.setFixedWidth(250)

        self.variable_input = QLineEdit()
        self.variable_input.setPlaceholderText("Variable (ej: x)")
        self.variable_input.setFixedWidth(100)

        val_func = QRegExpValidator(QRegExp(r"[0-9a-zA-Z+\-*/^(). ]+"))
        val_var = QRegExpValidator(QRegExp(r"[a-zA-Z]"))
        self.funcion_input.setValidator(val_func)
        self.variable_input.setValidator(val_var)

        entrada_layout.addWidget(QLabel("<b>Función:</b>"))
        entrada_layout.addWidget(self.funcion_input)
        entrada_layout.addWidget(QLabel("<b>Variable:</b>"))
        entrada_layout.addWidget(self.variable_input)
        entrada_group.setLayout(entrada_layout)
        self.layout().addWidget(entrada_group)

        # --- Operaciones ---
        operaciones_group = QGroupBox("⚙️ Operación")
        oper_layout = QHBoxLayout()

        for nombre, clave in [("Derivar", "derivar"), ("Integrar", "integrar")]:
            btn = QPushButton(nombre)
            btn.clicked.connect(lambda _, op=clave: self.set_operacion(op))
            self.botones[clave] = btn
            oper_layout.addWidget(btn)

        operaciones_group.setLayout(oper_layout)
        self.layout().addWidget(operaciones_group)

        # --- Ejecutar ---
        self.boton_ejecutar = QPushButton("▶️ Ejecutar operación")
        self.boton_ejecutar.setFixedWidth(160)
        self.boton_ejecutar.setStyleSheet("background-color: #b6deb9; font-weight: bold;")
        self.boton_ejecutar.clicked.connect(self.ejecutar)
        exec_layout = QHBoxLayout()
        exec_layout.addStretch()
        exec_layout.addWidget(self.boton_ejecutar)
        exec_layout.addStretch()
        self.layout().addLayout(exec_layout)

        # --- Limpiar ---
        self.boton_limpiar = QPushButton("🧽 Limpiar")
        self.boton_limpiar.setFixedWidth(100)
        self.boton_limpiar.setStyleSheet("background-color: #f0c4c4; font-weight: bold;")
        self.boton_limpiar.clicked.connect(self.limpiar)
        limpiar_layout = QHBoxLayout()
        limpiar_layout.addStretch()
        limpiar_layout.addWidget(self.boton_limpiar)
        self.layout().addLayout(limpiar_layout)

        # --- Resultado ---
        resultado_group = QGroupBox("📤 Resultado")
        resultado_layout = QVBoxLayout()
        self.resultado_label = QLabel()
        self.resultado_label.setAlignment(Qt.AlignCenter)
        self.resultado_label.setFixedHeight(130)  # más altura
        resultado_layout.addWidget(self.resultado_label)
        resultado_group.setLayout(resultado_layout)
        self.layout().addWidget(resultado_group)

    def set_operacion(self, operacion):
        self.operacion_actual = operacion
        for clave, btn in self.botones.items():
            color = "#ffeb99" if clave == operacion else "#aacfcf"
            btn.setStyleSheet(f"background-color: {color}; font-weight: bold;")

    def ejecutar(self):
        funcion_texto = self.funcion_input.text().strip()
        variable_texto = self.variable_input.text().strip()

        if not funcion_texto or not variable_texto:
            QMessageBox.warning(self, "Faltan datos", "Debes ingresar una función y una variable.")
            return

        try:
            funcion_texto = funcion_texto.replace("^", "**")
            funcion_texto = re.sub(r'(?<=\d)(?=[a-zA-Z(])', '*', funcion_texto)
            funcion_texto = re.sub(r'(?<=\))(?=[a-zA-Z(])', '*', funcion_texto)
            funcion = sympify(funcion_texto)
            variable = symbols(variable_texto)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al interpretar la función o variable:\n{e}")
            return

        try:
            if self.operacion_actual == "derivar":
                resultado = diff(funcion, variable)
            elif self.operacion_actual == "integrar":
                resultado = integrate(funcion, variable)
                latex_code = latex(resultado) +  r" + C"
            else:
                raise ValueError("Selecciona una operación.")
            
            if self.operacion_actual == "derivar":
                latex_code = latex(resultado)

            # Convertir a LaTeX y mostrar como imagen
            fig, ax = plt.subplots(figsize=(9, 2.3))  # más grande
            ax.text(0.5, 0.5, f"${latex_code}$", fontsize=30, ha='center', va='center')
            ax.axis('off')
            fig.tight_layout()

            ruta = "resultado.png"
            fig.savefig(ruta, dpi=100)
            plt.close(fig)

            self.resultado_label.setPixmap(QPixmap(ruta).scaledToHeight(150))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def limpiar(self):
        self.funcion_input.clear()
        self.variable_input.clear()
        self.resultado_label.clear()
