from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QLineEdit,
    QMessageBox, QGroupBox, QFormLayout, QTextEdit
)
from PyQt5.QtCore import Qt
from sympy import Matrix, exp, symbols, simplify


class SistemaEcuacionesAnalitico(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.setStyleSheet("""
            QWidget { background-color: #e8f5f2; }
            QGroupBox {
                font-weight: bold; font-size: 15px;
                border: 2px solid #006666; border-radius: 8px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 12px;
            }
            QLabel {
                font-size: 14px; font-weight: bold; padding: 4px;
            }
            QLineEdit, QSpinBox {
                background-color: white;
                padding: 6px; font-size: 14px;
                border: 1px solid #ccc; border-radius: 4px;
                max-width: 100px;
            }
            QPushButton {
                background-color: #33b5b5;
                padding: 8px 14px; border-radius: 6px;
                font-weight: bold; font-size: 14px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2a9999;
            }
            QTextEdit {
                background-color: #f0f0f0;
                border: 1px solid #aaa;
                font-family: Consolas, monospace;
                font-size: 13px;
                padding: 8px;
            }
            QTableWidget {
                background-color: white;
                font-size: 13px;
                border: 1px solid #ccc;
            }
            QHeaderView::section {
                background-color: #b3e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)

        self.t = symbols('t')
        self.init_ui()

    def init_ui(self):
        # Parámetros del sistema
        config_group = QGroupBox("🔧 Parámetros del Sistema")
        form = QFormLayout()
        self.tamano = QSpinBox()
        self.tamano.setRange(2, 3)
        self.tamano.valueChanged.connect(self.generar_tablas)
        self.incremento = QLineEdit()
        self.incremento.setPlaceholderText("Ej: 0.1")
        self.iteraciones = QSpinBox()
        self.iteraciones.setRange(1, 100)
        self.iteraciones.setValue(10)
        form.addRow("Tamaño matriz:", self.tamano)
        form.addRow("Incremento Δt:", self.incremento)
        form.addRow("Iteraciones:", self.iteraciones)
        config_group.setLayout(form)

        # Entrada A y Y0
        entrada_group = QGroupBox("📥 Matriz A y condición inicial Y(0)")
        lay_in = QHBoxLayout()
        self.tabla_matriz = QTableWidget(2, 2)
        self.tabla_condicion = QTableWidget(2, 1)
        lay_in.addWidget(QLabel("A:"))
        lay_in.addWidget(self.tabla_matriz)
        lay_in.addWidget(QLabel("Y(0):"))
        lay_in.addWidget(self.tabla_condicion)
        entrada_group.setLayout(lay_in)

        # Botones
        botones = QHBoxLayout()
        self.btn_calc = QPushButton("▶️ Calcular")
        self.btn_calc.clicked.connect(self.calcular)
        self.btn_clear = QPushButton("🧽 Limpiar")
        self.btn_clear.clicked.connect(self.limpiar)
        botones.addStretch()
        botones.addWidget(self.btn_calc)
        botones.addWidget(self.btn_clear)
        botones.addStretch()

        # Vectores y valores propios
        self.propios_texto = QTextEdit()
        self.propios_texto.setReadOnly(True)
        grafica_group = QGroupBox("📌 Vectores y Valores Propios")
        lay_g = QVBoxLayout()
        lay_g.addWidget(self.propios_texto)
        grafica_group.setLayout(lay_g)

        # Resultados
        self.tabla_resultados = QTableWidget()
        resultados_group = QGroupBox("📊 Resultados")
        lay_r = QVBoxLayout()
        lay_r.addWidget(self.tabla_resultados)
        resultados_group.setLayout(lay_r)

        # Dos columnas debajo de botones
        resultados_layout = QHBoxLayout()
        resultados_layout.addWidget(grafica_group, 1)
        resultados_layout.addWidget(resultados_group, 2)

        # Montaje final
        self.layout().addWidget(config_group)
        self.layout().addWidget(entrada_group)
        self.layout().addLayout(botones)
        self.layout().addLayout(resultados_layout)

        self.generar_tablas()

    def generar_tablas(self):
        n = self.tamano.value()
        self.tabla_matriz.setRowCount(n)
        self.tabla_matriz.setColumnCount(n)
        self.tabla_condicion.setRowCount(n)
        self.tabla_condicion.setColumnCount(1)

    def calcular(self):
        try:
            # Validar Δt
            try:
                h = float(self.incremento.text())
                if h <= 0:
                    raise ValueError
            except:
                QMessageBox.warning(self, "⚠️ Valor inválido", "El incremento Δt debe ser un número positivo.")
                return

            n_iter = self.iteraciones.value()
            n = self.tamano.value()

            # Leer A
            A_list = []
            for i in range(n):
                row = []
                for j in range(n):
                    item = self.tabla_matriz.item(i, j)
                    if not item or not item.text().strip():
                        QMessageBox.warning(self, "⚠️ Campo vacío", f"Falta valor en A({i+1},{j+1}).")
                        return
                    try:
                        row.append(float(item.text()))
                    except:
                        QMessageBox.warning(self, "⚠️ Valor inválido", f"A({i+1},{j+1}) no es numérico.")
                        return
                A_list.append(row)

            # Leer Y0
            Y0_list = []
            for i in range(n):
                item = self.tabla_condicion.item(i, 0)
                if not item or not item.text().strip():
                    QMessageBox.warning(self, "⚠️ Campo vacío", f"Falta valor en Y(0) fila {i+1}.")
                    return
                try:
                    Y0_list.append(float(item.text()))
                except:
                    QMessageBox.warning(self, "⚠️ Valor inválido", f"Y(0) fila {i+1} no es numérico.")
                    return

            A = Matrix(A_list)
            Y0 = Matrix(Y0_list)

            # Diagonalizar
            try:
                P, D = A.diagonalize()
            except:
                QMessageBox.critical(self, "❌ No diagonalizable", "La matriz A no se puede diagonalizar.")
                return

            # Valores y vectores propios
            vals = D.diagonal()
            vecs = [P.col(i) for i in range(P.cols)]
            html = "<b>• Valores propios:</b><br>" + "<br>".join(
                [f"λ{i+1} = {round(v.evalf(), 4)}" for i, v in enumerate(vals)]
            )
            html += "<br><br><b>• Vectores propios:</b><br>"
            for i, vec in enumerate(vecs):
                html += f"v{i+1} =<br>"
                for v in vec:
                    html += f"[ {round(v.evalf(),4):>7} ]<br>"
                html += "<br>"
            self.propios_texto.setHtml(html)

            # Cálculo de la solución
            resultados = []
            for k in range(n_iter + 1):
                t_val = round(k * h, 3)
                Yt = simplify(P * exp(D * t_val) * P.inv() * Y0)
                resultados.append([t_val] + [round(y.evalf(), 4) for y in Yt])

            # Mostrar en tabla
            self.tabla_resultados.setColumnCount(n + 1)
            self.tabla_resultados.setRowCount(len(resultados))
            self.tabla_resultados.setHorizontalHeaderLabels(["t"] + [f"y{i+1}" for i in range(n)])
            self.tabla_resultados.setVerticalHeaderLabels([str(i+1) for i in range(len(resultados))])
            for i, fila in enumerate(resultados):
                for j, val in enumerate(fila):
                    it = QTableWidgetItem(str(val))
                    it.setTextAlignment(Qt.AlignCenter)
                    self.tabla_resultados.setItem(i, j, it)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado:\n{e}")

    def limpiar(self):
        self.incremento.clear()
        self.propios_texto.clear()
        self.tabla_resultados.clear()
        self.tabla_resultados.setRowCount(0)
        self.generar_tablas()
