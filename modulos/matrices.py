from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem, QMessageBox, QStackedLayout,
    QGroupBox,QStyledItemDelegate, QScrollArea 
)
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegExpValidator, QColor
from sympy import sympify, Matrix
import numpy as np
import re

# --- Clase para limitar lo que el usuario puede escribir en las celdas ---
class CeldaValidadora(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)

        # Expresión regular para validar entrada segura
        # - Letras y números opcionales con punto decimal único
        # - Operaciones entre términos válidos
        regex = QRegExp(r"^-?[a-zA-Z0-9]*(\.\d+)?([+\-*/]-?[a-zA-Z0-9]*(\.\d+)?)?$")
        validator = QRegExpValidator(regex, editor)
        editor.setValidator(validator)
        return editor



# --- Lógica de operaciones con matrices usando sympy ---
class MatrizMayor:
    @staticmethod
    def sumar(A, B): return A + B
    @staticmethod
    def restar(A, B): return A - B
    @staticmethod
    def multiplicar(A, B): return A * B
    @staticmethod
    def determinante(A): return A.det()
    @staticmethod
    def inversa(A): return A.inv()
    @staticmethod
    def resolver_sistema(A, b): return A.LUsolve(b)

# --- Interfaz gráfica del módulo de matrices ---
class MatricesModule(QWidget):
    def __init__(self):
        super().__init__()
        self.estilo_boton_generar = """
            QPushButton {
                background-color:#b6deb9 ;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px;
            }
        """
        self.estilo_boton = """
            QPushButton {
                background-color:#ced1c0 ;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px;
            }
        """
        self.estilo_boton_base = """
            QPushButton {
                background-color: #82b3ae;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px;
            }
        """

        self.estilo_boton_activo = """
            QPushButton {
                background-color: yellow;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px;
            }
        """


        self.stack_layout = QStackedLayout()
        self.setLayout(self.stack_layout)
        self.menu_view = QWidget()
        self.menu_view.setStyleSheet("background-color: #EAE4C7;")  # 🎨 Color de fondo general del módulo
        self.menu_layout = QVBoxLayout(self.menu_view)

        # --- Grupo de operaciones ---
        operaciones_group = QGroupBox("🧮 Operaciones con matrices")
        operaciones_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 0px;
            }
        """)
        op_layout = QHBoxLayout()
        self.botones_operacion = []

        operaciones = [
            ("Suma", self.set_operacion_suma),
            ("Resta", self.set_operacion_resta),
            ("Multiplicación", self.set_operacion_multiplicacion),
            ("Determinante", self.set_operacion_determinante),
            ("Inversa", self.set_operacion_inversa),
            ("Resolver sistema", self.set_operacion_sistema)
        ]
        for nombre, funcion in operaciones:
            btn = QPushButton(nombre)
            btn.setFixedWidth(130)
            btn.setStyleSheet(self.estilo_boton_base)
            btn.clicked.connect(funcion)
            op_layout.addWidget(btn)
            self.botones_operacion.append(btn)
        operaciones_group.setLayout(op_layout)
        self.menu_layout.addWidget(operaciones_group)

        # --- Grupo dimensiones ---
        dimensiones_group = QGroupBox("📏 Tamaño de matrices")
        dimensiones_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 0px;
            }
        """)

        size_layout = QHBoxLayout()
        self.rows_spin = QSpinBox(); self.rows_spin.setRange(1, 10); self.rows_spin.setValue(2)
        self.cols_spin = QSpinBox(); self.cols_spin.setRange(1, 10); self.cols_spin.setValue(2)
        self.generar_btn = QPushButton("📐 Generar")
        self.generar_btn.setStyleSheet(self.estilo_boton_generar)
        self.generar_btn.setFixedWidth(100)
        self.generar_btn.clicked.connect(self.generar_tablas)

        # Etiquetas en negrita
        label_filas = QLabel("Filas:")
        label_filas.setStyleSheet("font-weight: bold;")
        label_columnas = QLabel("Columnas:")
        label_columnas.setStyleSheet("font-weight: bold;")

        size_layout.addWidget(label_filas)
        size_layout.addWidget(self.rows_spin)
        size_layout.addWidget(label_columnas)
        size_layout.addWidget(self.cols_spin)
        size_layout.addWidget(self.generar_btn)

        dimensiones_group.setLayout(size_layout)
        self.menu_layout.addWidget(dimensiones_group)


        # --- Botón limpiar ---
        self.limpiar_btn = QPushButton("🧽 Limpiar celdas")
        self.limpiar_btn.setFixedWidth(130)
        self.limpiar_btn.setStyleSheet(self.estilo_boton)
        self.limpiar_btn.clicked.connect(self.limpiar_celdas)
        self.menu_layout.addWidget(self.limpiar_btn, alignment=Qt.AlignLeft)

        # --- Contenedor de tablas ---
        self.tablas_layout = QHBoxLayout()
        self.tabla_A = QTableWidget(2, 2)
        self.tabla_B = QTableWidget(2, 2)
        self.b_container = self.crear_contenedor_tabla("Vector b", QTableWidget(2, 1))
        self.b_container.setStyleSheet("background-color: none;")


        for tabla in [self.tabla_A, self.tabla_B, self.b_container.findChild(QTableWidget)]:
            if tabla:
                tabla.setStyleSheet("font-size: 13px;")
                tabla.horizontalHeader().setDefaultSectionSize(50)
                tabla.verticalHeader().setDefaultSectionSize(35)

        self.tabla_b = self.b_container.findChild(QTableWidget)
        self.a_container = self.crear_contenedor_tabla("Matriz A", self.tabla_A)
        self.b_matrix_container = self.crear_contenedor_tabla("Matriz B", self.tabla_B)
        self.tablas_layout.addWidget(self.a_container)
        self.tablas_layout.addWidget(self.b_matrix_container)
        self.tablas_layout.addWidget(self.b_container)
        self.menu_layout.addLayout(self.tablas_layout)
        self.b_matrix_container.hide()
        self.b_container.hide()

        # --- Botón ejecutar ---
        self.ejecutar_btn = QPushButton("▶️ Ejecutar operación")
        self.ejecutar_btn.setFixedWidth(160)
        self.ejecutar_btn.setStyleSheet(self.estilo_boton)
        self.ejecutar_btn.clicked.connect(self.ejecutar_operacion)

        centro_layout = QHBoxLayout()
        centro_layout.addStretch()
        centro_layout.addWidget(self.ejecutar_btn)
        centro_layout.addStretch()
        self.menu_layout.addLayout(centro_layout)

        # --- Resultado centrado con scroll---
        resultado_group = QGroupBox("📤 Resultado")
        resultado_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 0px;
            }
        """)
        resultado_group.setMinimumHeight(150)

        resultado_layout = QVBoxLayout()

        # Creamos un QLabel para mostrar el contenido
        # Crear el QLabel
        self.resultado_label = QLabel("")
        self.resultado_label.setAlignment(Qt.AlignCenter)
        self.resultado_label.setStyleSheet("font-size: 14px; padding: 10px;")
        self.resultado_label.setWordWrap(True)

        # Contenedor para centrar el QLabel
        contenedor_centrado = QWidget()
        layout_centrado = QHBoxLayout(contenedor_centrado)
        layout_centrado.addStretch()
        layout_centrado.addWidget(self.resultado_label)
        layout_centrado.addStretch()

        # Scroll con el contenedor centrado
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(contenedor_centrado)


        resultado_layout.addWidget(scroll)
        resultado_group.setLayout(resultado_layout)
        self.menu_layout.addWidget(resultado_group)

        # Aplicar y mostrar
        self.stack_layout.addWidget(self.menu_view)
        self.operacion_actual = None
        self.generar_tablas()

        # Delegados
        validador = CeldaValidadora()
        self.tabla_A.setItemDelegate(validador)
        self.tabla_B.setItemDelegate(validador)
        self.tabla_b.setItemDelegate(validador)
        self.tabla_A.cellChanged.connect(lambda: self.validar_celda(self.tabla_A))
        self.tabla_B.cellChanged.connect(lambda: self.validar_celda(self.tabla_B))
        self.tabla_b.cellChanged.connect(lambda: self.validar_celda(self.tabla_b))
    
    def set_operacion_suma(self):
        self.operacion_actual = "suma"
        self.generar_tablas()
        self.resaltar_boton("Suma")

    def set_operacion_resta(self):
        self.operacion_actual = "resta"
        self.generar_tablas()
        self.resaltar_boton("Resta")

    def set_operacion_multiplicacion(self):
        self.operacion_actual = "multiplicacion"
        self.generar_tablas()
        self.resaltar_boton("Multiplicación")

    def set_operacion_determinante(self):
        self.operacion_actual = "determinante"
        self.generar_tablas()
        self.resaltar_boton("Determinante")

    def set_operacion_inversa(self):
        self.operacion_actual = "inversa"
        self.generar_tablas()
        self.resaltar_boton("Inversa")

    def set_operacion_sistema(self):
        self.operacion_actual = "sistema"
        self.generar_tablas()
        self.resaltar_boton("Resolver sistema")

    # para color de los botones 
    def resaltar_boton(self, nombre_operacion):
        for boton in self.botones_operacion:
            if boton.text() == nombre_operacion:
                boton.setStyleSheet(self.estilo_boton_activo)
            else:
                boton.setStyleSheet(self.estilo_boton_base)



    def generar_tablas(self):
        filas = self.rows_spin.value()
        columnas = self.cols_spin.value()

        self.tabla_A.setRowCount(filas)
        self.tabla_A.setColumnCount(columnas)

        if self.operacion_actual in ["suma", "resta", "multiplicacion"]:
            cols_B = columnas if self.operacion_actual != "multiplicacion" else filas
            self.tabla_B.setRowCount(filas)
            self.tabla_B.setColumnCount(cols_B)
            self.b_matrix_container.show()
        else:
            self.b_matrix_container.hide()

        if self.operacion_actual == "sistema":
            self.tabla_b.setRowCount(filas)
            self.tabla_b.setColumnCount(1)
            self.b_container.show()
        else:
            self.b_container.hide()

    def crear_contenedor_tabla(self, titulo, tabla):
        contenedor = QWidget()
        contenedor.setFixedWidth(250)
        contenedor.setFixedHeight(250)
        vbox = QVBoxLayout()

        label = QLabel(titulo)
        label.setStyleSheet("font-size: 13px; font-weight: bold;")
        tabla.setStyleSheet("background-color: white; font-size: 13px;")  # 👈 Fondo blanco SOLO para la tabla
        vbox.addWidget(label)
        vbox.addWidget(tabla)

        contenedor.setLayout(vbox)
        return contenedor


    def leer_tabla(self, tabla):
        filas, columnas = tabla.rowCount(), tabla.columnCount()
        matriz = []

        for i in range(filas):
            fila = []
            for j in range(columnas):
                item = tabla.item(i, j)
                texto = item.text().strip() if item and item.text().strip() else "0"

                # Completa expresiones decimales incompletas como ".9" -> "0.9", "6." -> "6.0"
                if re.match(r"^\.\d+$", texto):
                    texto = "0" + texto
                elif re.match(r"^\d+\.$", texto):
                    texto = texto + "0"

                # Insertar * implícito entre número y letra, por ejemplo 2a -> 2*a
                texto = re.sub(r'(?<=[0-9])(?=[a-zA-Z])', '*', texto)

                try:
                    valor = sympify(texto)
                except Exception as e:
                    raise ValueError(f"Error al interpretar '{texto}': {e}")
                fila.append(valor)
            matriz.append(fila)

        return Matrix(matriz)

    def limpiar_celdas(self):
        for tabla in [self.tabla_A, self.tabla_B, self.tabla_b]:
            if tabla is not None:
                for i in range(tabla.rowCount()):
                    for j in range(tabla.columnCount()):
                        tabla.setItem(i, j, QTableWidgetItem(""))
        self.resultado_label.setText("")  # Limpiar resultado

    def validar_celda(self, tabla):
        fila = tabla.currentRow()
        columna = tabla.currentColumn()
        item = tabla.item(fila, columna)
        if item is None:
            return

        texto = item.text().strip()

        # Corrige decimales tipo ".9" → "0.9" y "5." → "5.0"
        if re.fullmatch(r"\.\d+", texto):
            texto = "0" + texto
        elif re.fullmatch(r"-\.\d+", texto):
            texto = "-0" + texto[1:]
        elif re.fullmatch(r"\d+\.", texto):
            texto += "0"
        elif re.fullmatch(r"-\d+\.", texto):
            texto += "0"

        # Reemplaza multiplicación implícita (2x → 2*x)
        texto = re.sub(r'(?<=[0-9])(?=[a-zA-Z])', '*', texto)

        # Validación final: solo se permiten expresiones tipo: número, número + letra, letra + número, letras solas, etc.
        patron = r'^-?[\d\.a-zA-Z]+([+\-*/]-?[\d\.a-zA-Z]+)?$'
        if not re.fullmatch(patron, texto):
            item.setBackground(QColor("red"))
            return

        try:
            sympify(texto)
            item.setBackground(QColor("white"))
        except:
            item.setBackground(QColor("red"))

    def ejecutar_operacion(self):
        if not self.operacion_actual:
            QMessageBox.warning(self, "Operación no seleccionada", "Debes seleccionar una operación antes de ejecutar.")
            return
        try:
            if self.operacion_actual == "suma":
                resultado = self.resolver_suma()
            elif self.operacion_actual == "resta":
                resultado = self.resolver_resta()
            elif self.operacion_actual == "multiplicacion":
                resultado = self.resolver_multiplicacion()
            elif self.operacion_actual == "determinante":
                resultado = self.resolver_determinante()
            elif self.operacion_actual == "inversa":
                resultado = self.resolver_inversa()
            elif self.operacion_actual == "sistema":
                resultado = self.resolver_sistema()
            else:
                raise ValueError("Operación no válida.")

            if hasattr(resultado, 'shape'):
                filas = resultado.shape[0]
                columnas = resultado.shape[1] if len(resultado.shape) > 1 else 1
                texto = "<b>Resultado:</b><br><table style='border:1px solid #ccc; border-collapse: collapse;'>"
                for i in range(filas):
                    texto += "<tr>"
                    for j in range(columnas):
                        val = resultado[i, j] if columnas > 1 else resultado[i]
                        if hasattr(val, 'free_symbols') and len(val.free_symbols) == 0:
                            val = val.evalf()
                            val = int(val) if val == int(val) else float(val)
                        texto += f"<td style='border:1px solid #ccc; padding:4px 8px;'>{val}</td>"

                    texto += "</tr>"
                texto += "</table>"
                self.resultado_label.setText(texto)
            else:
                self.resultado_label.setText(f"<b>Resultado:</b><br>{resultado}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def resolver_suma(self):
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B)
        if A.shape != B.shape:
            raise ValueError("Las matrices A y B deben tener el mismo tamaño.")
        return MatrizMayor.sumar(A, B)

    def resolver_resta(self):
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B)
        if A.shape != B.shape:
            raise ValueError("Las matrices A y B deben tener el mismo tamaño.")
        return MatrizMayor.restar(A, B)

    def resolver_multiplicacion(self):
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B)
        if A.shape[1] != B.shape[0]:
            raise ValueError("Las columnas de A deben coincidir con las filas de B para multiplicar.")
        return MatrizMayor.multiplicar(A, B)

    def resolver_determinante(self):
        A = self.leer_tabla(self.tabla_A)
        if A.shape[0] != A.shape[1]:
            raise ValueError("La matriz debe ser cuadrada para calcular el determinante.")
        return MatrizMayor.determinante(A)

    def resolver_inversa(self):
        A = self.leer_tabla(self.tabla_A)
        if A.shape[0] != A.shape[1]:
            raise ValueError("La matriz debe ser cuadrada para calcular la inversa.")
        if A.det() == 0:
            raise ValueError("La matriz no tiene inversa porque su determinante es 0 (matriz singular).")
        return MatrizMayor.inversa(A)

    def resolver_sistema(self):
        A = self.leer_tabla(self.tabla_A)
        b = self.leer_tabla(self.tabla_b)
        if A.shape[0] != A.shape[1]:
            raise ValueError("La matriz A debe ser cuadrada.")
        if A.shape[0] != b.shape[0] or b.shape[1] != 1:
            raise ValueError("Las dimensiones de A y b no coinciden.")
        return MatrizMayor.resolver_sistema(A, b)
