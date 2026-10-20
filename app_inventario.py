"""
app_inventario.py
Aplicación gráfica (PyQt5 + Matplotlib) para visualizar el inventario de las
cinco sucursales de la empresa.

Ejecutar:  python app_inventario.py
"""

import os
import sys

import matplotlib
matplotlib.use("Qt5Agg")
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

RUTA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos.csv")
TODAS = "Todas las sucursales"
COLORES = ["#2a6fdb", "#e8833a", "#3aa76d", "#c94c4c", "#8a5cc2", "#d4a72c"]
COLORES_ESTADO = {"Disponible": "#3aa76d", "Bajo stock": "#e8a33a", "Agotado": "#c94c4c"}


class Grafico(QWidget):
    """Lienzo de Matplotlib con barra de herramientas, embebido en PyQt5."""

    def __init__(self):
        super().__init__()
        self.figura = Figure(figsize=(8, 5), tight_layout=True)
        self.canvas = FigureCanvas(self.figura)
        layout = QVBoxLayout(self)
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)

    def nuevo_eje(self):
        self.figura.clear()
        return self.figura.add_subplot(111)

    def dibujar(self):
        self.canvas.draw_idle()


class TarjetaKPI(QFrame):
    def __init__(self, titulo: str):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("QFrame{background:#ffffff;border:1px solid #d0d7e2;border-radius:8px;}")
        layout = QVBoxLayout(self)
        etiqueta = QLabel(titulo)
        etiqueta.setStyleSheet("color:#5b6475;border:none;font-size:11px;")
        self.valor = QLabel("-")
        self.valor.setStyleSheet("color:#1d2b4f;border:none;font-size:20px;font-weight:bold;")
        layout.addWidget(etiqueta)
        layout.addWidget(self.valor)


class VentanaInventario(QMainWindow):
    def __init__(self, ruta_csv: str):
        super().__init__()
        self.setWindowTitle("Inventario por Sucursal - Consultoría de Datos")
        self.resize(1200, 780)
        self.df = pd.DataFrame()

        central = QWidget()
        self.setCentralWidget(central)
        principal = QVBoxLayout(central)

        # Encabezado y filtros
        encabezado = QHBoxLayout()
        titulo = QLabel("Panel de Inventario")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        encabezado.addWidget(titulo)
        encabezado.addStretch()
        encabezado.addWidget(QLabel("Sucursal:"))
        self.combo_sucursal = QComboBox()
        self.combo_sucursal.setMinimumWidth(190)
        self.combo_sucursal.currentTextChanged.connect(self.actualizar)
        encabezado.addWidget(self.combo_sucursal)
        encabezado.addWidget(QLabel("Categoría:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.setMinimumWidth(160)
        self.combo_categoria.currentTextChanged.connect(self.actualizar)
        encabezado.addWidget(self.combo_categoria)
        boton_abrir = QPushButton("Abrir CSV...")
        boton_abrir.clicked.connect(self.abrir_csv)
        encabezado.addWidget(boton_abrir)
        principal.addLayout(encabezado)

        # Indicadores
        kpis = QHBoxLayout()
        self.kpi_productos = TarjetaKPI("Registros de producto")
        self.kpi_unidades = TarjetaKPI("Unidades en stock")
        self.kpi_valor = TarjetaKPI("Valor del inventario (USD)")
        self.kpi_ventas = TarjetaKPI("Ventas mensuales (und)")
        self.kpi_criticos = TarjetaKPI("Agotados / bajo stock")
        for k in (self.kpi_productos, self.kpi_unidades, self.kpi_valor, self.kpi_ventas, self.kpi_criticos):
            kpis.addWidget(k)
        principal.addLayout(kpis)

        # Pestañas con gráficos y tabla
        self.tabs = QTabWidget()
        self.g_valor = Grafico()
        self.g_categoria = Grafico()
        self.g_estado = Grafico()
        self.g_ventas = Grafico()
        self.g_precios = Grafico()
        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSortingEnabled(True)
        self.tabs.addTab(self.g_valor, "Valor por sucursal")
        self.tabs.addTab(self.g_categoria, "Stock por categoría")
        self.tabs.addTab(self.g_estado, "Estado del stock")
        self.tabs.addTab(self.g_ventas, "Stock vs ventas")
        self.tabs.addTab(self.g_precios, "Precios y márgenes")
        self.tabs.addTab(self.tabla, "Tabla de inventario")
        principal.addWidget(self.tabs)

        self.estado = self.statusBar()
        self.cargar(ruta_csv)

    # ---------------------------------------------------------------- datos
    def cargar(self, ruta: str):
        try:
            df = pd.read_csv(ruta, encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo:\n{e}")
            return
        requeridas = {"Sucursal", "Categoria", "Producto", "Stock", "Valor_Inventario",
                      "Ventas_Mensuales", "Estado", "Precio_Venta", "Costo_Unitario"}
        faltantes = requeridas - set(df.columns)
        if faltantes:
            QMessageBox.warning(self, "Archivo no válido", f"Faltan columnas: {', '.join(sorted(faltantes))}")
            return
        self.df = df
        for combo, col, todos in ((self.combo_sucursal, "Sucursal", TODAS),
                                  (self.combo_categoria, "Categoria", "Todas")):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems([todos] + sorted(df[col].unique()))
            combo.blockSignals(False)
        self.estado.showMessage(f"Archivo cargado: {ruta}  ({len(df)} registros)")
        self.actualizar()

    def abrir_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir inventario", "", "CSV (*.csv)")
        if ruta:
            self.cargar(ruta)

    def filtrado(self) -> pd.DataFrame:
        df = self.df
        suc = self.combo_sucursal.currentText()
        cat = self.combo_categoria.currentText()
        if suc and suc != TODAS:
            df = df[df["Sucursal"] == suc]
        if cat and cat != "Todas":
            df = df[df["Categoria"] == cat]
        return df

    # ---------------------------------------------------------- refresco
    def actualizar(self):
        if self.df.empty:
            return
        df = self.filtrado()
        self.actualizar_kpis(df)
        self.graf_valor_sucursal()
        self.graf_categoria(df)
        self.graf_estado(df)
        self.graf_stock_ventas(df)
        self.graf_precios(df)
        self.llenar_tabla(df)

    def actualizar_kpis(self, df):
        self.kpi_productos.valor.setText(f"{len(df):,}")
        self.kpi_unidades.valor.setText(f"{int(df['Stock'].sum()):,}")
        self.kpi_valor.valor.setText(f"${df['Valor_Inventario'].sum():,.2f}")
        self.kpi_ventas.valor.setText(f"{int(df['Ventas_Mensuales'].sum()):,}")
        criticos = (df["Estado"] != "Disponible").sum()
        self.kpi_criticos.valor.setText(f"{criticos}")

    def graf_valor_sucursal(self):
        # Compara todas las sucursales (solo aplica el filtro de categoría)
        df = self.df
        cat = self.combo_categoria.currentText()
        if cat and cat != "Todas":
            df = df[df["Categoria"] == cat]
        datos = df.groupby("Sucursal")["Valor_Inventario"].sum().sort_values(ascending=False)
        seleccion = self.combo_sucursal.currentText()
        colores = [COLORES[0] if (seleccion == TODAS or s == seleccion) else "#b8c4d9" for s in datos.index]
        ax = self.g_valor.nuevo_eje()
        barras = ax.bar(datos.index, datos.values, color=colores)
        ax.bar_label(barras, labels=[f"${v:,.0f}" for v in datos.values], padding=3, fontsize=9)
        ax.set_title(f"Valor del inventario por sucursal ({cat})")
        ax.set_ylabel("USD")
        ax.spines[["top", "right"]].set_visible(False)
        ax.margins(y=0.12)
        self.g_valor.dibujar()

    def graf_categoria(self, df):
        datos = df.groupby("Categoria")["Stock"].sum().sort_values()
        ax = self.g_categoria.nuevo_eje()
        barras = ax.barh(datos.index, datos.values, color=COLORES[1])
        ax.bar_label(barras, padding=3, fontsize=9)
        ax.set_title(f"Unidades en stock por categoría - {self.combo_sucursal.currentText()}")
        ax.set_xlabel("Unidades")
        ax.spines[["top", "right"]].set_visible(False)
        ax.margins(x=0.12)
        self.g_categoria.dibujar()

    def graf_estado(self, df):
        fig = self.g_estado.figura
        fig.clear()
        ax1 = fig.add_subplot(121)
        conteo = df["Estado"].value_counts()
        ax1.pie(conteo.values, labels=conteo.index, autopct="%1.1f%%", startangle=90,
                colors=[COLORES_ESTADO.get(e, "#999") for e in conteo.index],
                wedgeprops={"edgecolor": "white"})
        ax1.set_title("Distribución del estado del stock")

        ax2 = fig.add_subplot(122)
        tabla = pd.crosstab(df["Sucursal"], df["Estado"])
        orden = [e for e in ["Disponible", "Bajo stock", "Agotado"] if e in tabla.columns]
        tabla[orden].plot(kind="bar", stacked=True, ax=ax2,
                          color=[COLORES_ESTADO[e] for e in orden], edgecolor="white")
        ax2.set_title("Estado por sucursal")
        ax2.set_xlabel("")
        ax2.set_ylabel("Productos")
        ax2.tick_params(axis="x", rotation=30)
        ax2.spines[["top", "right"]].set_visible(False)
        self.g_estado.dibujar()

    def graf_stock_ventas(self, df):
        datos = df.groupby("Categoria")[["Stock", "Ventas_Mensuales"]].sum()
        ax = self.g_ventas.nuevo_eje()
        x = range(len(datos))
        ancho = 0.4
        ax.bar([i - ancho / 2 for i in x], datos["Stock"], ancho, label="Stock actual", color=COLORES[0])
        ax.bar([i + ancho / 2 for i in x], datos["Ventas_Mensuales"], ancho, label="Ventas mensuales", color=COLORES[2])
        ax.set_xticks(list(x))
        ax.set_xticklabels(datos.index, rotation=20)
        ax.set_ylabel("Unidades")
        ax.set_title("Stock disponible frente a ventas mensuales por categoría")
        ax.legend(frameon=False)
        ax.spines[["top", "right"]].set_visible(False)
        self.g_ventas.dibujar()

    def graf_precios(self, df):
        fig = self.g_precios.figura
        fig.clear()
        ax1 = fig.add_subplot(121)
        cats = sorted(df["Categoria"].unique())
        ax1.boxplot([df.loc[df["Categoria"] == c, "Precio_Venta"] for c in cats])
        ax1.set_xticks(range(1, len(cats) + 1))
        ax1.set_xticklabels(cats)
        ax1.set_yscale("log")
        ax1.set_title("Distribución de precios de venta")
        ax1.set_ylabel("USD (escala logarítmica)")
        ax1.tick_params(axis="x", rotation=30)

        ax2 = fig.add_subplot(122)
        margen = ((df["Precio_Venta"] - df["Costo_Unitario"]) / df["Precio_Venta"] * 100)
        datos = margen.groupby(df["Categoria"]).mean().sort_values()
        barras = ax2.barh(datos.index, datos.values, color=COLORES[4])
        ax2.bar_label(barras, labels=[f"{v:.1f}%" for v in datos.values], padding=3, fontsize=9)
        ax2.set_title("Margen bruto promedio")
        ax2.set_xlabel("%")
        ax2.margins(x=0.15)
        for ax in (ax1, ax2):
            ax.spines[["top", "right"]].set_visible(False)
        self.g_precios.dibujar()

    def llenar_tabla(self, df):
        self.tabla.setSortingEnabled(False)
        self.tabla.clear()
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(list(df.columns))
        for i, fila in enumerate(df.itertuples(index=False)):
            for j, valor in enumerate(fila):
                item = QTableWidgetItem()
                if isinstance(valor, (int, float)):
                    item.setData(Qt.DisplayRole, valor)
                else:
                    item.setText(str(valor))
                self.tabla.setItem(i, j, item)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.setSortingEnabled(True)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = VentanaInventario(RUTA_CSV)
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
