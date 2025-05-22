from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QMessageBox, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
import numpy as np


class VectorMayor:
    @staticmethod
    def suma(v1, v2): return np.add(v1, v2)
    @staticmethod
    def resta(v1, v2): return np.subtract(v1, v2)
    @staticmethod
    def magnitud(v): return np.linalg.norm(v)
    @staticmethod
    def producto_punto(v1, v2): return np.dot(v1, v2)
    @staticmethod
    def producto_cruzado(v1, v2): return np.cross(v1, v2)

class VectoresModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #D5E5CF;")  # Fondo general
        self.operacion_actual = None
        self.botones = {}

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        estilo_boton = """
            QPushButton {
                background-color: #E56300;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #E6BE48;
            }
        """
        estilo_boton_activo = """
            QPushButton {
                background-color: #627AE5;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """
        self.estilo_boton = estilo_boton
        self.estilo_boton_activo = estilo_boton_activo

        # --- Entrada de vectores ---
        entrada_group = QGroupBox("🔢 Entrada de Vectores")
        entrada_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 6px;
                margin-top: 10px;
            }
        """)
        entrada_layout = QVBoxLayout()

        label1 = QLabel("Vector 1:")
        label1.setStyleSheet("font-weight: bold;")
        self.entrada1 = QLineEdit()
        self.entrada1.setPlaceholderText("Ej: 1, 2, 3")
        self.entrada1.setFixedWidth(200)
        self.entrada1.setStyleSheet("background-color: white;")

        self.label2 = QLabel("Vector 2:")
        self.label2.setStyleSheet("font-weight: bold;")
        self.entrada2 = QLineEdit()
        self.entrada2.setPlaceholderText("Ej: 4, 5, 6")
        self.entrada2.setFixedWidth(200)
        self.entrada2.setStyleSheet("background-color: white;")

        val_vector = QRegExpValidator(QRegExp(r"[0-9,\s\-\.]+"))
        self.entrada1.setValidator(val_vector)
        self.entrada2.setValidator(val_vector)

        entrada_layout.addWidget(label1)
        entrada_layout.addWidget(self.entrada1)
        entrada_layout.addWidget(self.label2)
        entrada_layout.addWidget(self.entrada2)
        entrada_group.setLayout(entrada_layout)

        # --- Operaciones ---
        operaciones_group = QGroupBox("⚙️ Operaciones")
        operaciones_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 6px;
                margin-top: 10px;
            }
        """)
        operaciones_layout = QHBoxLayout()
        operaciones = [
            ("Suma", "suma"),
            ("Resta", "resta"),
            ("Magnitud", "magnitud"),
            ("Producto punto", "punto"),
            ("Producto cruzado", "cruzado"),
        ]
        for texto, clave in operaciones:
            btn = QPushButton(texto)
            btn.setStyleSheet(estilo_boton)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, op=clave: self.set_operacion(op))
            self.botones[clave] = btn
            operaciones_layout.addWidget(btn)
        operaciones_group.setLayout(operaciones_layout)

        # --- Ejecutar ---
        self.boton_ejecutar = QPushButton("▶️ Ejecutar operación")
        self.boton_ejecutar.setStyleSheet(estilo_boton)
        self.boton_ejecutar.setFixedWidth(160)
        self.boton_ejecutar.clicked.connect(self.ejecutar)
        ejecutar_layout = QHBoxLayout()
        ejecutar_layout.addStretch()
        ejecutar_layout.addWidget(self.boton_ejecutar)
        ejecutar_layout.addStretch()

        # --- Limpiar ---
        self.boton_limpiar = QPushButton("🧽 Limpiar todo")
        self.boton_limpiar.setStyleSheet(estilo_boton)
        self.boton_limpiar.setFixedWidth(120)
        self.boton_limpiar.clicked.connect(self.limpiar)
        limpiar_layout = QHBoxLayout()
        limpiar_layout.addStretch()
        limpiar_layout.addWidget(self.boton_limpiar)

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


        # --- Resultado ---
        resultado_group = QGroupBox("📤 Resultado")
        resultado_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 6px;
                margin-top: 10px;
            }
        """)
        resultado_layout = QVBoxLayout()
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setFixedHeight(100)
        self.resultado.setFixedWidth(320)
        self.resultado.setStyleSheet("font-size: 14px; padding: 6px; background-color: white;")
        resultado_layout.addWidget(self.resultado, alignment=Qt.AlignCenter)
        resultado_group.setLayout(resultado_layout)

        # --- Añadir todo ---
        main_layout.addWidget(entrada_group)
        main_layout.addWidget(operaciones_group)
        main_layout.addLayout(ejecutar_layout)
        main_layout.addLayout(limpiar_layout)
        main_layout.addWidget(resultado_group)

    def set_operacion(self, operacion):
        self.operacion_actual = operacion

        necesita_vector2 = operacion in ["suma", "resta", "punto", "cruzado"]
        self.label2.setVisible(necesita_vector2)
        self.entrada2.setVisible(necesita_vector2)

        for clave, btn in self.botones.items():
            if clave == operacion:
                btn.setStyleSheet(self.estilo_boton_activo)
            else:
                btn.setStyleSheet(self.estilo_boton)


    def leer_vector(self, entrada: QLineEdit):
        entrada.setStyleSheet("")  # Reset visual
        texto = entrada.text().strip()

        if not texto:
            entrada.setStyleSheet("background-color: #ffcccc;")
            raise ValueError("No puede dejar el campo vacío.")

        if ",," in texto or texto.endswith(",") or texto.startswith(","):
            entrada.setStyleSheet("background-color: #ffcccc;")
            raise ValueError("Formato inválido: no uses comas duplicadas o al inicio/final.")

        try:
            valores = [float(x.strip()) for x in texto.split(",") if x.strip()]
            return np.array(valores)
        except:
            entrada.setStyleSheet("background-color: #ffcccc;")
            raise ValueError("Solo se permiten números separados por comas.")


    def ejecutar(self):
        if not self.operacion_actual:
            QMessageBox.warning(self, "Error", "Selecciona primero una operación.")
            return

        try:
            v1 = self.leer_vector(self.entrada1)

            if self.operacion_actual in ["suma", "resta", "punto", "cruzado"]:
                v2 = self.leer_vector(self.entrada2)

                # Validar longitud igual (excepto para producto cruzado)
                if self.operacion_actual != "cruzado" and len(v1) != len(v2):
                    self.entrada1.setStyleSheet("background-color: #ffcccc;")
                    self.entrada2.setStyleSheet("background-color: #ffcccc;")
                    raise ValueError("Los vectores deben tener la misma longitud.")

                # Validar que los vectores para cruzado sean 3D
                if self.operacion_actual == "cruzado":
                    if len(v1) != 3 or len(v2) != 3:
                        self.entrada1.setStyleSheet("background-color: #ffcccc;")
                        self.entrada2.setStyleSheet("background-color: #ffcccc;")
                        raise ValueError("El producto cruzado solo aplica a vectores 3D.")


            if self.operacion_actual == "suma":
                resultado = VectorMayor.suma(v1, v2)
            elif self.operacion_actual == "resta":
                resultado = VectorMayor.resta(v1, v2)
            elif self.operacion_actual == "magnitud":
                resultado = round(VectorMayor.magnitud(v1), 3)
            elif self.operacion_actual == "punto":
                resultado = VectorMayor.producto_punto(v1, v2)
            elif self.operacion_actual == "cruzado":
                if len(v1) != 3 or len(v2) != 3:
                    raise ValueError("El producto cruzado solo se puede aplicar a vectores 3D.")
                resultado = VectorMayor.producto_cruzado(v1, v2)

            self.resultado.setHtml(f"""
                <div align='center'>
                    <span style='font-size:16pt;'>{resultado}</span>
                </div>
            """)
            self.resultado.moveCursor(self.resultado.textCursor().Start)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def limpiar(self):
        self.entrada1.clear()
        self.entrada2.clear()
        self.resultado.clear()
