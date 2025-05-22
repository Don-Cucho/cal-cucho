from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt

class AcercaDeModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #CAD7E9;")

        # --- Título ---
        titulo = QLabel("<h2>📚 Acerca de la Calculadora Científica</h2>")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # --- Grupo: Información del Proyecto ---
        grupo_info = QGroupBox("ℹ️ Información del Proyecto")
        grupo_info.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 8px;
                padding: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        info_layout = QVBoxLayout()
        info_texto = QLabel("""
            <div style='line-height: 1.5;'>
                <b>🧠 Proyecto de Modelos Matemáticos</b><br>
                <b>Descripción:</b> Aplicación educativa desarrollada como proyecto integrador para resolver operaciones matemáticas complejas, incluyendo cálculo simbólico, álgebra lineal, vectores y gráficos.<br>
                <b>Versión:</b> 1.0<br>
                <b>Tecnologías:</b> PyQt5, SymPy, NumPy, Matplotlib
            </div>
        """)
        info_texto.setWordWrap(True)
        info_layout.addWidget(info_texto)
        grupo_info.setLayout(info_layout)
        layout.addWidget(grupo_info)

        # --- Grupo: Datos Académicos ---
        datos = QGroupBox("🎓 Datos Académicos")
        datos.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 8px;
                padding: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        layout_datos = QVBoxLayout()
        texto_datos = QLabel("""
            <div style='line-height: 1.5;'>
                <b>Materia:</b> Modelos Matemáticos<br>
                <b>Profesor:</b> Mg. Morales Torres Fabricio<br>
                <b>Carrera:</b> Ingeniería en Software<br>
                <b>Semestre:</b> 6to semestre<br>
                <b>Año Académico:</b> 2025-2026
            </div>
        """)

        texto_datos.setWordWrap(True)
        layout_datos.addWidget(texto_datos)
        datos.setLayout(layout_datos)
        layout.addWidget(datos)

        # --- Grupo: Autor del Proyecto ---
        autor = QGroupBox("👨‍💻 Autor del Proyecto")
        autor.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 8px;
                padding: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        layout_autor = QVBoxLayout()
        texto_autor = QLabel("""
            <div style='line-height: 1.5;'>
                <b>Nombre:</b> Marcelo Alberto Romero Jara<br>
                <b>Correo:</b> mromeroj4@unemi.edu.ec<br>
                <b>Institución:</b> Universidad Estatal de Milagro, UNEMI
            </div>
        """)

        texto_autor.setWordWrap(True)
        layout_autor.addWidget(texto_autor)
        autor.setLayout(layout_autor)
        layout.addWidget(autor)
