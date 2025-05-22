from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QMessageBox, QGroupBox 
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from sympy import symbols, sympify, integrate, diff
import re

x = symbols('x')

# --- Lógica de operaciones con polinomios ---
class PolinomioMayor:
    @staticmethod
    def sumar(p1, p2): return p1 + p2
    @staticmethod
    def restar(p1, p2): return p1 - p2
    @staticmethod
    def multiplicar(p1, p2): return p1 * p2
    @staticmethod
    def derivar(p, variable): return diff(p, variable)
    @staticmethod
    def integrar(p): return integrate(p, x)
    @staticmethod
    def evaluar(p, valor): return p.subs(x, valor)

# --- Interfaz gráfica del módulo ---
class PolinomiosModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.operacion_actual = None
        self.botones_operacion = {}

        # Fondo general
        self.setStyleSheet("background-color: #D2D3E4;")

        

        # Estilos reutilizables
        self.estilo_boton = """
            QPushButton {
                background-color: #E4DD8C;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #E03D00;
            }
        """
        self.estilo_activo = """
            QPushButton {
                background-color: #E0582D;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """

        # --- Grupo de operaciones ---
        grupo_operaciones = QGroupBox("🧮 Operaciones disponibles")
        grupo_operaciones.setStyleSheet(self._estilo_groupbox())
        op_layout = QHBoxLayout()

        acciones = [
            ("Sumar", lambda: self.set_operacion("sumar")),
            ("Restar", lambda: self.set_operacion("restar")),
            ("Multiplicar", lambda: self.set_operacion("multiplicar")),
            ("Derivar", lambda: self.set_operacion("derivar")),
            ("Integrar", lambda: self.set_operacion("integrar")),
            ("Evaluar", lambda: self.set_operacion("evaluar"))
        ]
        for nombre, funcion in acciones:
            btn = QPushButton(nombre)
            btn.setStyleSheet(self.estilo_boton)
            btn.clicked.connect(funcion)
            self.botones_operacion[nombre.lower()] = btn
            op_layout.addWidget(btn)

        self.boton_limpiar = QPushButton("🧽 Limpiar todo")
        self.boton_limpiar.setFixedWidth(120)
        self.boton_limpiar.setStyleSheet(self.estilo_boton)
        self.boton_limpiar.clicked.connect(self.limpiar_campos)
        op_layout.addWidget(self.boton_limpiar)

        grupo_operaciones.setLayout(op_layout)
        self.layout().addWidget(grupo_operaciones)

        # --- Entradas ---
        grupo_entradas = QGroupBox("📥 Entradas de polinomios")
        grupo_entradas.setStyleSheet(self._estilo_groupbox())
        entradas_layout = QVBoxLayout()

        self.entrada1 = QLineEdit()
        self.entrada1.setPlaceholderText("Ej: 2x^2 + 3x - 1")
        self.entrada1.setFixedWidth(200)

        self.label2 = QLabel("<b>Polinomio 2:</b>")
        self.entrada2 = QLineEdit()
        self.entrada2.setPlaceholderText("Ej: x^2 - x + 5")
        self.entrada2.setFixedWidth(200)

        entradas_layout.addWidget(QLabel("<b>Polinomio 1:</b>"))
        entradas_layout.addWidget(self.entrada1)
        entradas_layout.addWidget(self.label2)
        entradas_layout.addWidget(self.entrada2)

        self.boton_ejecutar = QPushButton("▶️ Ejecutar operación")
        self.boton_ejecutar.setFixedWidth(160)
        self.boton_ejecutar.setStyleSheet(self.estilo_boton)

                # Estilo personalizado para botón Limpiar
        self.boton_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #f6c1c1;
                color: black;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #f29e9e;
            }
        """)

        # Estilo personalizado para botón Ejecutar
        self.boton_ejecutar.setStyleSheet("""
            QPushButton {
                background-color: #77DF6B;
                color: black;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2CE184;
            }
        """)


        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.boton_ejecutar)
        btn_layout.addStretch()

        self.boton_ejecutar.clicked.connect(self.ejecutar_operacion)
        entradas_layout.addLayout(btn_layout)
        grupo_entradas.setLayout(entradas_layout)
        self.layout().addWidget(grupo_entradas)

        # --- Evaluación / derivación ---
        grupo_extra = QGroupBox("⚙️ Evaluación / derivación")
        grupo_extra.setStyleSheet(self._estilo_groupbox())
        extra_layout = QVBoxLayout()

        self.label_eval = QLabel("Valor para evaluación:")
        self.label_eval.setStyleSheet("font-weight: bold;")
        self.valor_eval = QLineEdit()
        self.valor_eval.setPlaceholderText("Ej: 2")
        self.valor_eval.setFixedWidth(180)

        self.label_variable = QLabel("Variable para derivar:")
        self.label_variable.setStyleSheet("font-weight: bold;")
        self.campo_variable = QLineEdit()
        self.campo_variable.setPlaceholderText("Ej: x")
        self.campo_variable.setFixedWidth(180)

        for widget in [self.label_eval, self.valor_eval, self.label_variable, self.campo_variable]:
            widget.hide()
            extra_layout.addWidget(widget)

        grupo_extra.setLayout(extra_layout)
        self.layout().addWidget(grupo_extra)

        # --- Resultado ---
        grupo_resultado = QGroupBox("📤 Resultado")
        grupo_resultado.setStyleSheet("""
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
        grupo_resultado.setFixedHeight(120)  # 👈 Altura más pequeña
        grupo_resultado.setFixedWidth(400)   # 👈 Ancho más pequeño

        resultado_layout = QVBoxLayout()

        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setAlignment(Qt.AlignCenter)
        self.resultado.setStyleSheet("font-size: 14px; background-color: white;")
        self.resultado.setMaximumHeight(70)  # Limitar altura del QTextEdit
        self.resultado.setMaximumWidth(380)
        self.resultado.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.resultado.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Centrado
        centrado_resultado = QHBoxLayout()
        centrado_resultado.addStretch()
        centrado_resultado.addWidget(self.resultado)
        centrado_resultado.addStretch()

        resultado_layout.addLayout(centrado_resultado)
        grupo_resultado.setLayout(resultado_layout)
        self.layout().addWidget(grupo_resultado, alignment=Qt.AlignCenter)

        # --- Validadores ---
        self._agregar_validadores()

    def _estilo_groupbox(self):
        return """
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
        """

    def _agregar_validadores(self):
        self.entrada1.setValidator(QRegExpValidator(QRegExp(r"[0-9a-zA-Z+\-*/^(). ]+")))
        self.entrada2.setValidator(QRegExpValidator(QRegExp(r"[0-9a-zA-Z+\-*/^(). ]+")))
        self.campo_variable.setValidator(QRegExpValidator(QRegExp(r"[a-zA-Z]+")))
        self.valor_eval.setValidator(QRegExpValidator(QRegExp(r"-?[0-9.]+")))

            # Estilo para que los campos de texto no tengan fondo
        campos_texto = [self.entrada1, self.entrada2, self.valor_eval, self.campo_variable, self.resultado]
        for campo in campos_texto:
            campo.setStyleSheet("background-color: none;")

    

        


    # --- Selección de operación ---
    def set_operacion(self, operacion):
        self.operacion_actual = operacion

        # Resaltar botón seleccionado
        for nombre, boton in self.botones_operacion.items():
            if nombre == operacion:
                boton.setStyleSheet(self.estilo_activo)
            else:
                boton.setStyleSheet(self.estilo_boton)

        # Mostrar campo de evaluación solo para 'evaluar'
        self.label_eval.setVisible(operacion == "evaluar")
        self.valor_eval.setVisible(operacion == "evaluar")
        if operacion != "evaluar":
            self.valor_eval.clear()

        # Mostrar campo de variable solo para 'derivar'
        self.label_variable.setVisible(operacion == "derivar")
        self.campo_variable.setVisible(operacion == "derivar")
        if operacion != "derivar":
            self.campo_variable.clear()

        # Mostrar/ocultar campo Polinomio 2
        mostrar_2 = operacion in ["sumar", "restar", "multiplicar"]
        self.label2.setVisible(mostrar_2)
        self.entrada2.setVisible(mostrar_2)
        if not mostrar_2:
            self.entrada2.clear()

    # --- Ejecutar operación seleccionada ---
    def ejecutar_operacion(self):
        if not self.operacion_actual:
            QMessageBox.warning(self, "Falta seleccionar", "Selecciona primero una operación.")
            return

        if self.operacion_actual == "sumar":
            self.sumar()
        elif self.operacion_actual == "restar":
            self.restar()
        elif self.operacion_actual == "multiplicar":
            self.multiplicar()
        elif self.operacion_actual == "derivar":
            self.derivar()
        elif self.operacion_actual == "integrar":
            self.integrar()
        elif self.operacion_actual == "evaluar":
            self.evaluar()

    # --- Limpieza de campos ---
    def limpiar_campos(self):
        self.entrada1.clear()
        self.entrada2.clear()
        self.valor_eval.clear()
        self.campo_variable.clear()
        self.resultado.clear()

    # --- Validaciones ---
    def obtener_polinomios(self):
        texto1 = self.entrada1.text().strip()
        texto2 = self.entrada2.text().strip()

        # Validación avanzada de errores comunes
        for idx, txt in enumerate([texto1, texto2], start=1):
            if txt and (
                txt in ".-+*/" or
                txt.endswith((".", "+", "-", "*", "/", "^")) or
                re.search(r'[^\d\w\s+\-*/^().]', txt)  # caracteres inválidos
            ):
                QMessageBox.warning(self, "Entrada inválida", f"El Polinomio {idx} contiene una expresión no válida.")
                return None, None

        # Agregar multiplicación implícita (2x → 2*x)
        texto1 = re.sub(r'(?<=\d)(?=[a-zA-Z])', '*', texto1)
        texto2 = re.sub(r'(?<=\d)(?=[a-zA-Z])', '*', texto2)

        try:
            p1 = sympify(texto1)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Polinomio 1 inválido:\n{e}")
            return None, None

        p2 = None
        if texto2:
            try:
                p2 = sympify(texto2)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Polinomio 2 inválido:\n{e}")
                return None, None

        return p1, p2


    def obtener_dos_polinomios_obligatorios(self):
        texto1 = self.entrada1.text().strip()
        texto2 = self.entrada2.text().strip()

        if not texto1 or not texto2:
            QMessageBox.warning(self, "Faltan datos", "Debes ingresar ambos polinomios para esta operación.")
            return None, None

        for idx, txt in enumerate([texto1, texto2], start=1):
            if txt in ".-+*/" or txt.endswith((".","+","-","*","/")):
                QMessageBox.warning(self, "Entrada inválida", f"El Polinomio {idx} contiene una expresión incompleta.")
                return None, None

        # Insertar multiplicación implícita
        texto1 = re.sub(r'(?<=\d)(?=[a-zA-Z])', '*', texto1)
        texto2 = re.sub(r'(?<=\d)(?=[a-zA-Z])', '*', texto2)

        try:
            p1 = sympify(texto1)
            p2 = sympify(texto2)
            return p1, p2
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al interpretar los polinomios:\n{e}")
            return None, None


    # --- Operaciones ---
    def sumar(self):
        p1, p2 = self.obtener_dos_polinomios_obligatorios()
        if p1 and p2:
            resultado = PolinomioMayor.sumar(p1, p2)
            self.resultado.setText(f"<div align='center'>{resultado}</div>")
            self.resultado.moveCursor(self.resultado.textCursor().Start)

    def restar(self):
        p1, p2 = self.obtener_dos_polinomios_obligatorios()
        if p1 and p2:
            self.resultado.setText(str(PolinomioMayor.restar(p1, p2)))

    def multiplicar(self):
        p1, p2 = self.obtener_dos_polinomios_obligatorios()
        if p1 and p2:
            resultado = PolinomioMayor.multiplicar(p1, p2).expand()
            self.resultado.setText(str(resultado))

    def derivar(self):
        p1, _ = self.obtener_polinomios()
        if not p1:
            return

        variable = self.campo_variable.text().strip()
        if not variable:
            QMessageBox.warning(self, "Falta variable", "Debes ingresar la variable respecto a la cual derivar.")
            return

        try:
            simbolo = symbols(variable)
            resultado = PolinomioMayor.derivar(p1, simbolo)
            self.resultado.setText(str(resultado))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Variable inválida:\n{e}")

    def integrar(self):
        p1, _ = self.obtener_polinomios()
        if not p1:
            return  # Evita continuar si hubo error

        try:
            resultado = PolinomioMayor.integrar(p1)
            self.resultado.setText(str(resultado))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al integrar:\n{e}")


    def evaluar(self):
        p1, _ = self.obtener_polinomios()
        if not p1:
            return

        texto_valor = self.valor_eval.text().strip()
        if not texto_valor:
            QMessageBox.warning(self, "Falta el valor", "Debes ingresar un número para evaluar el polinomio.")
            return

        try:
            val = float(texto_valor)
            resultado = PolinomioMayor.evaluar(p1, val)
            if resultado.is_number:
                resultado = round(float(resultado), 3)
            self.resultado.setText(str(resultado))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Valor inválido:\n{e}")
