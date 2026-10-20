"""
generar_informe.py
Genera el informe de consultoría en PDF (Informe_Consultoria_Inventario.pdf)
a partir de datos.csv. Todas las cifras se calculan con Pandas.
"""

import os
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from analisis_inventario import cargar_datos, resumen_categoria, resumen_sucursal

# ------------------------------------------------------------------ portada
INTEGRANTES = ["William Alexander Valencia Rosa", "Abner Lemuel Pérez Medrano"]
DOCENTE = "Willian Alexis Montes Girón"
CARRERA = "Ingeniería en Sistemas y Redes Informáticas"
ASIGNATURA = "Programación Computacional III"
EMPRESA = "Comercializadora Salvadoreña, S.A. de C.V."

BASE = os.path.dirname(os.path.abspath(__file__))
DIR_GRAF = os.path.join(BASE, "graficos_informe")
SALIDA = os.path.join(BASE, "Informe_Consultoria_Inventario.pdf")
AZUL = colors.HexColor("#1d2b4f")
COLORES = ["#2a6fdb", "#e8833a", "#3aa76d", "#c94c4c", "#8a5cc2", "#d4a72c"]
COLORES_ESTADO = {"Disponible": "#3aa76d", "Bajo stock": "#e8a33a", "Agotado": "#c94c4c"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

# ------------------------------------------------------------------ estilos
est = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=est["Heading1"], textColor=AZUL, fontSize=16, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=est["Heading2"], textColor=AZUL, fontSize=12.5, spaceBefore=10, spaceAfter=4)
P = ParagraphStyle("P", parent=est["BodyText"], fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
VIN = ParagraphStyle("VIN", parent=P, leftIndent=14, bulletIndent=4)
PIE = ParagraphStyle("PIE", parent=P, fontSize=8.5, textColor=colors.grey, alignment=TA_CENTER)
CEN = ParagraphStyle("CEN", parent=P, alignment=TA_CENTER)


def usd(v):
    return f"${v:,.2f}"


def pct(v):
    return f"{v:.1f} %"


def fecha_larga(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def vinetas(items):
    return [Paragraph(t, VIN, bulletText="•") for t in items]


def tabla(datos, anchos=None, encabezado=True):
    t = Table(datos, colWidths=anchos, repeatRows=1 if encabezado else 0)
    estilo = [
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c7cfdd")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5fa")]),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]
    if encabezado:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), AZUL),
                   ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                   ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                   ("ALIGN", (0, 0), (-1, 0), "CENTER")]
    t.setStyle(TableStyle(estilo))
    return t


def figura(nombre, ancho_cm=15.5):
    ruta = os.path.join(DIR_GRAF, nombre)
    plt.savefig(ruta, dpi=170, bbox_inches="tight")
    plt.close()
    img = Image(ruta)
    escala = (ancho_cm * cm) / img.imageWidth
    img.drawWidth, img.drawHeight = img.imageWidth * escala, img.imageHeight * escala
    return img


def limpiar_ejes(ax):
    ax.spines[["top", "right"]].set_visible(False)


# ------------------------------------------------------------------ gráficos
def graficos(df, suc, cat):
    os.makedirs(DIR_GRAF, exist_ok=True)
    g = {}

    fig, ax = plt.subplots(figsize=(8, 3.6))
    b = ax.bar(suc.index, suc["Valor_Inventario"], color=COLORES[0])
    ax.bar_label(b, labels=[f"${v:,.0f}" for v in suc["Valor_Inventario"]], fontsize=8, padding=2)
    ax.set_title("Figura 1. Valor del inventario por sucursal (USD)", fontsize=10)
    ax.margins(y=0.15)
    limpiar_ejes(ax)
    g["valor_suc"] = figura("valor_sucursal.png")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
    c = cat.sort_values("Valor_Inventario")
    axs[0].barh(c.index, c["Participacion_Valor_%"], color=COLORES[1])
    axs[0].set_title("Participación en el valor (%)", fontsize=9.5)
    c2 = cat.sort_values("Unidades")
    axs[1].barh(c2.index, c2["Unidades"], color=COLORES[2])
    axs[1].set_title("Unidades en stock", fontsize=9.5)
    for ax in axs:
        limpiar_ejes(ax)
        ax.tick_params(labelsize=8)
    fig.suptitle("Figura 2. Composición del inventario por categoría", fontsize=10)
    fig.tight_layout()
    g["categoria"] = figura("categoria.png")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
    conteo = df["Estado"].value_counts()
    axs[0].pie(conteo, autopct="%1.1f%%", startangle=90, pctdistance=0.75,
               colors=[COLORES_ESTADO[e] for e in conteo.index], wedgeprops={"edgecolor": "white"},
               textprops={"fontsize": 7.5})
    axs[0].legend(conteo.index, loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=7.5, frameon=False)
    ct = pd.crosstab(df["Sucursal"], df["Estado"])[["Agotado", "Bajo stock"]]
    ct.plot(kind="bar", ax=axs[1], color=[COLORES_ESTADO["Agotado"], COLORES_ESTADO["Bajo stock"]])
    axs[1].set_xlabel("")
    axs[1].tick_params(axis="x", rotation=25, labelsize=8)
    axs[1].legend(fontsize=8, frameon=False)
    limpiar_ejes(axs[1])
    fig.suptitle("Figura 3. Estado del stock y productos críticos por sucursal", fontsize=10)
    fig.tight_layout()
    g["estado"] = figura("estado.png")

    fig, ax = plt.subplots(figsize=(8, 3.6))
    x = range(len(cat))
    orden = cat.sort_index()
    ax.bar([i - 0.2 for i in x], orden["Unidades"], 0.4, label="Stock", color=COLORES[0])
    ax.bar([i + 0.2 for i in x], orden["Ventas_Mensuales"], 0.4, label="Ventas mensuales", color=COLORES[2])
    ax.set_xticks(list(x))
    ax.set_xticklabels(orden.index, fontsize=8)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Figura 4. Stock frente a ventas mensuales por categoría (unidades)", fontsize=10)
    limpiar_ejes(ax)
    g["stock_ventas"] = figura("stock_ventas.png")

    fig, ax = plt.subplots(figsize=(8, 3.4))
    m = cat["Margen_Promedio_%"].sort_values()
    b = ax.barh(m.index, m, color=COLORES[4])
    ax.bar_label(b, labels=[f"{v:.1f}%" for v in m], fontsize=8, padding=2)
    ax.set_title("Figura 5. Margen bruto promedio por categoría", fontsize=10)
    ax.margins(x=0.12)
    limpiar_ejes(ax)
    g["margen"] = figura("margen.png", 14)

    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.hist(df["Antiguedad_Dias"], bins=12, color=COLORES[5], edgecolor="white")
    ax.axvline(90, color="#c94c4c", ls="--", lw=1)
    ax.text(91, ax.get_ylim()[1] * 0.9, "90 días", color="#c94c4c", fontsize=8)
    ax.set_xlabel("Días desde el último ingreso", fontsize=8.5)
    ax.set_ylabel("Productos", fontsize=8.5)
    ax.set_title("Figura 6. Antigüedad del último ingreso de mercadería", fontsize=10)
    limpiar_ejes(ax)
    g["antiguedad"] = figura("antiguedad.png", 14)
    return g


# ------------------------------------------------------------------ pie de página
def pie_pagina(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Informe de consultoría – Inventario por sucursal")
    canvas.drawRightString(letter[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


# ------------------------------------------------------------------ informe
def construir():
    df = cargar_datos(os.path.join(BASE, "datos.csv"))
    corte = pd.Timestamp("2026-10-15")
    df["Antiguedad_Dias"] = (corte - df["Fecha_Ultimo_Ingreso"]).dt.days
    df["Margen_%"] = (df["Precio_Venta"] - df["Costo_Unitario"]) / df["Precio_Venta"] * 100
    suc = resumen_sucursal(df)
    cat = resumen_categoria(df)
    cat["Cobertura_Meses"] = cat["Unidades"] / cat["Ventas_Mensuales"]
    g = graficos(df, suc, cat)

    total_valor = df["Valor_Inventario"].sum()
    total_und = int(df["Stock"].sum())
    total_ventas = int(df["Ventas_Mensuales"].sum())
    criticos = df[df["Estado"] != "Disponible"]
    agotados = df[df["Estado"] == "Agotado"]
    bajo = df[df["Estado"] == "Bajo stock"]
    s_max, s_min = suc.index[0], suc.index[-1]
    rot = suc.sort_values("Cobertura_Meses")
    prov = df.groupby("Proveedor")["Valor_Inventario"].sum().sort_values(ascending=False)
    prov_pct = prov / prov.sum() * 100
    viejos = df[df["Antiguedad_Dias"] > 90]
    corr = df[["Stock", "Stock_Minimo", "Costo_Unitario", "Precio_Venta",
               "Valor_Inventario", "Ventas_Mensuales"]].corr()
    top_valor = df.nlargest(5, "Valor_Inventario")
    elec_elec = cat.loc[["Electrónica", "Electrodomésticos"], "Participacion_Valor_%"].sum()
    precio_var = df.groupby("Producto")["Precio_Venta"].agg(lambda s: (s.max() - s.min()) / s.mean() * 100)

    h = []

    # ---------------- a) Portada formal
    h += [Spacer(1, 1.2 * cm),
          Paragraph("UNIVERSIDAD GERARDO BARRIOS", ParagraphStyle("u", parent=CEN, fontSize=17, textColor=AZUL, fontName="Helvetica-Bold")),
          Spacer(1, 0.2 * cm),
          Paragraph(f"Facultad de Ciencia y Tecnología<br/>{CARRERA}", ParagraphStyle("f", parent=CEN, fontSize=12, leading=17)),
          Spacer(1, 0.2 * cm),
          Paragraph(f"Asignatura: {ASIGNATURA}<br/>Parcial – Segundo Cómputo", ParagraphStyle("a", parent=CEN, fontSize=11)),
          Spacer(1, 2.2 * cm),
          Paragraph("INFORME DE CONSULTORÍA DE DATOS", ParagraphStyle("t", parent=CEN, fontSize=22, leading=28, textColor=AZUL, fontName="Helvetica-Bold")),
          Spacer(1, 0.4 * cm),
          Paragraph("Análisis del inventario de las sucursales de San Salvador, Santa Ana, San Miguel, La Libertad y Sonsonate",
                    ParagraphStyle("st", parent=CEN, fontSize=13, leading=18)),
          Spacer(1, 0.4 * cm),
          Paragraph(f"Preparado para: <b>Gerencia General – {EMPRESA}</b>", ParagraphStyle("pp", parent=CEN, fontSize=11)),
          Spacer(1, 2.4 * cm),
          Paragraph("<b>Consultores (integrantes):</b><br/>" + "<br/>".join(INTEGRANTES), ParagraphStyle("i", parent=CEN, fontSize=11.5, leading=17)),
          Spacer(1, 0.6 * cm),
          Paragraph(f"<b>Docente:</b> {DOCENTE}" if DOCENTE else "", ParagraphStyle("d", parent=CEN, fontSize=11.5)),
          Spacer(1, 2.2 * cm),
          Paragraph(f"San Miguel, El Salvador<br/>{fecha_larga(date.today())}", ParagraphStyle("l", parent=CEN, fontSize=11, leading=16)),
          PageBreak()]

    # ---------------- Resumen ejecutivo
    h += [Paragraph("1. Resumen ejecutivo", H1),
          Paragraph(
              f"La gerencia solicitó un diagnóstico del inventario de sus cinco sucursales. Se construyó un inventario de "
              f"<b>{len(df)} registros</b> ({df['Producto'].nunique()} productos en {df['Categoria'].nunique()} categorías por sucursal) "
              f"con un valor total a costo de <b>{usd(total_valor)}</b> y <b>{total_und:,} unidades</b> en existencia, frente a "
              f"ventas de {total_ventas:,} unidades mensuales. Los hallazgos principales son:", P)]
    h += vinetas([
        f"<b>{s_max}</b> concentra el mayor valor de inventario ({usd(suc.loc[s_max, 'Valor_Inventario'])}) y "
        f"<b>{s_min}</b> el menor ({usd(suc.loc[s_min, 'Valor_Inventario'])}).",
        f"Electrónica y Electrodomésticos representan el <b>{pct(elec_elec)}</b> del capital invertido en inventario, "
        f"aunque solo el {pct((cat.loc[['Electrónica','Electrodomésticos'],'Unidades'].sum()) / total_und * 100)} de las unidades.",
        f"<b>{len(criticos)} registros ({pct(len(criticos) / len(df) * 100)})</b> están en situación crítica: "
        f"{len(agotados)} agotados y {len(bajo)} con stock por debajo del mínimo.",
        f"La cobertura global es de {total_und / total_ventas:.2f} meses; {rot.index[0]} es la sucursal con mayor rotación "
        f"({rot['Cobertura_Meses'].iloc[0]:.2f} meses) y {rot.index[-1]} la de menor ({rot['Cobertura_Meses'].iloc[-1]:.2f} meses).",
        f"{len(viejos)} productos ({pct(len(viejos) / len(df) * 100)}) no reciben mercadería desde hace más de 90 días.",
    ])

    # ---------------- Metodología
    h += [Paragraph("2. Alcance y metodología", H1),
          Paragraph(
              "El conjunto de datos fue generado con Python y Pandas (script <i>generar_datos.py</i>) simulando el "
              "inventario real de la empresa con una semilla fija para que los resultados sean reproducibles. "
              "El archivo resultante, <i>datos.csv</i>, se inspeccionó con Pandas (<i>analisis_inventario.py</i>) y se "
              "visualizó con una aplicación de escritorio desarrollada en PyQt5 con gráficos de Matplotlib "
              "(<i>app_inventario.py</i>). Las funciones de inspección empleadas fueron:", P)]
    h += vinetas([
        "<b>head() / tail()</b>: revisión de los primeros y últimos registros.",
        "<b>shape, columns, info(), dtypes</b>: estructura y tipos de datos de cada columna.",
        "<b>isnull().sum(), duplicated()</b>: calidad de datos (nulos y duplicados).",
        "<b>nunique(), value_counts()</b>: cardinalidad y frecuencias de las variables categóricas.",
        "<b>describe()</b>: estadísticas básicas (media, desviación estándar, mínimo, cuartiles, máximo).",
        "<b>groupby().agg(), crosstab(), corr()</b>: resúmenes por sucursal y categoría, tablas cruzadas y correlaciones.",
    ])

    # ---------------- Estructura
    h += [Paragraph("3. Estructura y calidad de los datos", H1),
          Paragraph(
              f"El inventario tiene <b>{df.shape[0] - 0} filas y 13 columnas</b> originales. No se encontraron valores nulos "
              f"({int(df.isnull().sum().sum())}) ni registros duplicados ({int(df.duplicated().sum())}). Cada sucursal "
              f"tiene exactamente {int(df['Sucursal'].value_counts().iloc[0])} productos registrados, lo que permite "
              f"comparaciones equilibradas.", P)]
    descripcion = {
        "ID_Producto": "Código único del registro", "Producto": "Nombre del artículo",
        "Categoria": "Línea de producto", "Sucursal": "Local donde se encuentra",
        "Proveedor": "Empresa que abastece", "Stock": "Unidades en existencia",
        "Stock_Minimo": "Punto de reorden", "Costo_Unitario": "Costo de compra (USD)",
        "Precio_Venta": "Precio al público (USD)", "Valor_Inventario": "Stock × costo (USD)",
        "Ventas_Mensuales": "Unidades vendidas al mes", "Fecha_Ultimo_Ingreso": "Última recepción",
        "Estado": "Disponible / Bajo stock / Agotado",
    }
    filas = [["Columna", "Tipo (dtype)", "Únicos", "Nulos", "Descripción"]]
    for col in descripcion:
        filas.append([col, str(df[col].dtype), str(df[col].nunique()), str(int(df[col].isnull().sum())), descripcion[col]])
    t = tabla(filas, [3.6 * cm, 2.6 * cm, 1.4 * cm, 1.2 * cm, 6.2 * cm])
    t.setStyle(TableStyle([("ALIGN", (1, 1), (3, -1), "CENTER"), ("ALIGN", (4, 1), (4, -1), "LEFT")]))
    h += [KeepTogether([t, Spacer(1, 0.3 * cm), Paragraph("Tabla 1. Estructura del inventario (df.info() / df.dtypes / df.nunique()).", PIE)])]

    d = df[["Stock", "Costo_Unitario", "Precio_Venta", "Valor_Inventario", "Ventas_Mensuales"]].describe()
    filas = [["Estadístico"] + list(d.columns)]
    for idx in d.index:
        filas.append([idx] + [f"{v:,.2f}" for v in d.loc[idx]])
    h += [Spacer(1, 0.3 * cm), KeepTogether([tabla(filas, [2.4 * cm, 2.4 * cm, 2.9 * cm, 2.7 * cm, 3.3 * cm, 3.3 * cm]),
          Spacer(1, 0.2 * cm), Paragraph("Tabla 2. Estadísticas descriptivas de las variables numéricas (df.describe()).", PIE)]),
          PageBreak()]

    # ---------------- b) Hallazgos
    h += [Paragraph("4. Análisis de hallazgos", H1),
          Paragraph("4.1 Inventario por sucursal", H2),
          Paragraph(
              f"{s_max} es la sucursal con mayor inversión en inventario ({pct(suc.loc[s_max, 'Valor_Inventario'] / total_valor * 100)} "
              f"del total) y también la de mayores ventas ({int(suc.loc[s_max, 'Ventas_Mensuales']):,} unidades/mes). "
              f"{s_min} tiene el inventario más pequeño ({pct(suc.loc[s_min, 'Valor_Inventario'] / total_valor * 100)}). "
              f"La diferencia entre la sucursal de mayor y menor valor es de "
              f"{usd(suc.loc[s_max, 'Valor_Inventario'] - suc.loc[s_min, 'Valor_Inventario'])}.", P),
          g["valor_suc"]]
    filas = [["Sucursal", "Unidades", "Valor (USD)", "Ventas/mes", "Cobertura (meses)", "Agotados", "Bajo stock"]]
    for s, r in suc.iterrows():
        filas.append([s, f"{int(r['Unidades']):,}", usd(r["Valor_Inventario"]), f"{int(r['Ventas_Mensuales']):,}",
                      f"{r['Cobertura_Meses']:.2f}", str(int(r["Agotados"])), str(int(r["Bajo_Stock"]))])
    h += [tabla(filas, [3 * cm, 1.9 * cm, 2.8 * cm, 2 * cm, 2.8 * cm, 1.8 * cm, 2 * cm]),
          Spacer(1, 0.2 * cm), Paragraph("Tabla 3. Resumen por sucursal (groupby('Sucursal').agg()).", PIE),
          Paragraph(
              f"La cobertura (unidades en stock ÷ ventas mensuales) muestra que {rot.index[0]} vende su inventario más rápido "
              f"({rot['Cobertura_Meses'].iloc[0]:.2f} meses), mientras que {rot.index[-1]} mantiene más mercadería inmovilizada "
              f"respecto a lo que vende ({rot['Cobertura_Meses'].iloc[-1]:.2f} meses).", P)]

    h += [KeepTogether([Paragraph("4.2 Inventario por categoría", H2),
          Paragraph(
              f"Electrónica es la categoría más costosa: acumula {usd(cat.loc['Electrónica', 'Valor_Inventario'])} "
              f"({pct(cat.loc['Electrónica', 'Participacion_Valor_%'])} del valor) con apenas {int(cat.loc['Electrónica', 'Unidades'])} unidades. "
              f"En contraste, Abarrotes tiene el mayor volumen físico ({int(cat.loc['Abarrotes', 'Unidades']):,} unidades) "
              f"pero solo el {pct(cat.loc['Abarrotes', 'Participacion_Valor_%'])} del valor, y es la categoría más vendida "
              f"({int(cat.loc['Abarrotes', 'Ventas_Mensuales']):,} unidades/mes).", P),
          g["categoria"]])]

    h += [PageBreak(), Paragraph("4.3 Estado del stock", H2),
          Paragraph(
              f"El {pct((df['Estado'] == 'Disponible').mean() * 100)} de los registros está disponible. Sin embargo, "
              f"{len(agotados)} productos están agotados y {len(bajo)} se encuentran bajo el stock mínimo. "
              f"Las sucursales con más agotados son "
              f"{', '.join(suc[suc['Agotados'] == suc['Agotados'].max()].index)} ({int(suc['Agotados'].max())} cada una), "
              f"y {suc['Bajo_Stock'].idxmax()} es la que acumula más productos en bajo stock ({int(suc['Bajo_Stock'].max())}).", P),
          g["estado"]]
    filas = [["Sucursal", "Producto", "Categoría", "Stock", "Mínimo", "Estado"]]
    for _, r in criticos.sort_values(["Estado", "Sucursal"]).iterrows():
        filas.append([r["Sucursal"], r["Producto"], r["Categoria"], str(r["Stock"]), str(r["Stock_Minimo"]), r["Estado"]])
    t = tabla(filas, [2.8 * cm, 4.6 * cm, 3.2 * cm, 1.4 * cm, 1.5 * cm, 2.2 * cm])
    t.setStyle(TableStyle([("ALIGN", (1, 1), (2, -1), "LEFT"), ("ALIGN", (5, 1), (5, -1), "LEFT")]))
    h += [KeepTogether([t, Spacer(1, 0.2 * cm), Paragraph("Tabla 4. Productos agotados o con bajo stock.", PIE)]), PageBreak()]

    h += [Paragraph("4.4 Stock frente a ventas", H2),
          Paragraph(
              f"Al comparar existencias con ventas mensuales, {cat['Cobertura_Meses'].idxmin()} tiene la menor cobertura "
              f"({cat['Cobertura_Meses'].min():.2f} meses), lo que indica alta rotación y riesgo de quiebre de stock, mientras "
              f"que {cat['Cobertura_Meses'].idxmax()} tiene la mayor cobertura ({cat['Cobertura_Meses'].max():.2f} meses). "
              f"La correlación entre Stock y Ventas_Mensuales es positiva (r = {corr.loc['Stock', 'Ventas_Mensuales']:.2f}): "
              f"en general, la empresa mantiene más existencias de los productos que más se venden.", P),
          g["stock_ventas"]]

    h += [Paragraph("4.5 Precios, costos y márgenes", H2),
          Paragraph(
              f"El precio de venta va de {usd(df['Precio_Venta'].min())} a {usd(df['Precio_Venta'].max())}, con una media de "
              f"{usd(df['Precio_Venta'].mean())} y una mediana de {usd(df['Precio_Venta'].median())}; la gran diferencia entre "
              f"media y mediana indica una distribución sesgada a la derecha por los artículos de alto valor. "
              f"Ropa tiene el mayor margen bruto ({pct(cat['Margen_Promedio_%'].max())}) y Abarrotes el menor "
              f"({pct(cat['Margen_Promedio_%'].min())}). Un mismo producto varía en promedio "
              f"{pct(precio_var.mean())} de precio entre sucursales (máximo {pct(precio_var.max())} en "
              f"{precio_var.idxmax()}).", P),
          g["margen"], PageBreak()]

    h += [Paragraph("4.6 Concentración de proveedores", H2),
          Paragraph(
              f"{prov.index[0]} abastece el {pct(prov_pct.iloc[0])} del valor del inventario y, junto con {prov.index[1]} "
              f"({pct(prov_pct.iloc[1])}), concentra el {pct(prov_pct.iloc[:2].sum())}. Esta dependencia expone a la empresa "
              f"a riesgos de abastecimiento y de negociación de precios.", P)]
    filas = [["Proveedor", "Valor (USD)", "% del valor"]]
    for p, v in prov.items():
        filas.append([p, usd(v), pct(prov_pct[p])])
    t = tabla(filas, [7 * cm, 3.5 * cm, 3 * cm])
    h += [KeepTogether([t, Spacer(1, 0.2 * cm), Paragraph("Tabla 5. Valor del inventario por proveedor.", PIE)])]

    h += [Paragraph("4.7 Antigüedad de los ingresos de mercadería", H2),
          Paragraph(
              f"Las fechas de último ingreso van del {fecha_larga(df['Fecha_Ultimo_Ingreso'].min())} al "
              f"{fecha_larga(df['Fecha_Ultimo_Ingreso'].max())}. La antigüedad promedio es de "
              f"{df['Antiguedad_Dias'].mean():.0f} días y {len(viejos)} registros superan los 90 días sin reabastecimiento, "
              f"con un valor inmovilizado de {usd(viejos['Valor_Inventario'].sum())}.", P),
          g["antiguedad"]]

    titulo_48 = Paragraph("4.8 Productos de mayor valor", H2)
    filas = [["Sucursal", "Producto", "Stock", "Costo unit.", "Valor (USD)"]]
    for _, r in top_valor.iterrows():
        filas.append([r["Sucursal"], r["Producto"], str(r["Stock"]), usd(r["Costo_Unitario"]), usd(r["Valor_Inventario"])])
    t = tabla(filas, [3.2 * cm, 4.8 * cm, 1.8 * cm, 2.8 * cm, 3 * cm])
    t.setStyle(TableStyle([("ALIGN", (1, 1), (1, -1), "LEFT")]))
    h += [KeepTogether([titulo_48, t, Spacer(1, 0.2 * cm),
          Paragraph(f"Tabla 6. Cinco registros con mayor valor de inventario ({pct(top_valor['Valor_Inventario'].sum() / total_valor * 100)} del total).", PIE)]),
          PageBreak()]

    # ---------------- c) Conclusiones por columna
    est_stock = df["Stock"].describe()
    h += [Paragraph("5. Conclusiones por variable", H1)]
    conclusiones = [
        ("ID_Producto", f"Identificador único: {df['ID_Producto'].nunique()} valores distintos para {len(df)} filas, sin duplicados. "
                        "Garantiza la trazabilidad de cada registro y es apto como llave primaria."),
        ("Producto", f"{df['Producto'].nunique()} artículos distintos, cada uno presente en las 5 sucursales. El catálogo es homogéneo, "
                     "lo que facilita comparar el desempeño de un mismo producto entre locales."),
        ("Categoria", f"6 categorías. Electrónica domina el valor ({pct(cat.loc['Electrónica', 'Participacion_Valor_%'])}) y Abarrotes "
                      f"el volumen ({pct(cat.loc['Abarrotes', 'Unidades'] / total_und * 100)} de las unidades). El riesgo financiero "
                      "se concentra en pocas categorías de alto valor."),
        ("Sucursal", f"5 sucursales con 27 registros cada una. {s_max} es la más fuerte en valor y ventas; {s_min} la más pequeña. "
                     f"{rot.index[0]} tiene la mejor rotación."),
        ("Proveedor", f"{df['Proveedor'].nunique()} proveedores. Existe alta concentración: los dos principales suman el "
                      f"{pct(prov_pct.iloc[:2].sum())} del valor del inventario."),
        ("Stock", f"Media de {est_stock['mean']:.1f} unidades, mediana de {est_stock['50%']:.0f} y desviación estándar de "
                  f"{est_stock['std']:.1f}; el rango va de {int(est_stock['min'])} a {int(est_stock['max'])}. La alta dispersión se "
                  "explica por la mezcla de productos de consumo masivo y artículos de alto valor."),
        ("Stock_Minimo", f"Toma {df['Stock_Minimo'].nunique()} valores fijos por categoría. Está bien correlacionado con las ventas "
                         f"(r = {corr.loc['Stock_Minimo', 'Ventas_Mensuales']:.2f}), pero no distingue entre sucursales grandes y pequeñas."),
        ("Costo_Unitario", f"Entre {usd(df['Costo_Unitario'].min())} y {usd(df['Costo_Unitario'].max())}; mediana "
                           f"{usd(df['Costo_Unitario'].median())}. Determina casi por completo el valor del inventario "
                           f"(r = {corr.loc['Costo_Unitario', 'Valor_Inventario']:.2f})."),
        ("Precio_Venta", f"Media {usd(df['Precio_Venta'].mean())} frente a mediana {usd(df['Precio_Venta'].median())}: distribución "
                         f"asimétrica. Los precios varían en promedio {pct(precio_var.mean())} entre sucursales para un mismo producto."),
        ("Valor_Inventario", f"Total de {usd(total_valor)}. Cinco registros concentran el "
                             f"{pct(top_valor['Valor_Inventario'].sum() / total_valor * 100)} del valor; la gestión debe priorizar estos artículos."),
        ("Ventas_Mensuales", f"{total_ventas:,} unidades al mes en total. Abarrotes aporta el "
                             f"{pct(cat.loc['Abarrotes', 'Ventas_Mensuales'] / total_ventas * 100)} de las unidades vendidas; "
                             f"la correlación negativa con el precio (r = {corr.loc['Precio_Venta', 'Ventas_Mensuales']:.2f}) confirma que "
                             "los productos más caros rotan menos."),
        ("Fecha_Ultimo_Ingreso", f"Antigüedad promedio de {df['Antiguedad_Dias'].mean():.0f} días; {len(viejos)} registros superan "
                                 "los 90 días, lo que sugiere reabastecimiento irregular en parte del catálogo."),
        ("Estado", f"{(df['Estado'] == 'Disponible').sum()} disponibles, {len(bajo)} en bajo stock y {len(agotados)} agotados. "
                   f"El {pct(len(criticos) / len(df) * 100)} de registros críticos representa ventas potencialmente perdidas."),
    ]
    filas = [[Paragraph("<b>Variable</b>", ParagraphStyle("hh", parent=P, textColor=colors.white, fontSize=9)),
              Paragraph("<b>Conclusión</b>", ParagraphStyle("hh2", parent=P, textColor=colors.white, fontSize=9))]]
    celda = ParagraphStyle("cel", parent=P, fontSize=9, leading=12, spaceAfter=0)
    for var, texto in conclusiones:
        filas.append([Paragraph(f"<b>{var}</b>", celda), Paragraph(texto, celda)])
    t = tabla(filas, [3.8 * cm, 12.6 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "LEFT")]))
    h += [t, PageBreak()]

    # ---------------- d) Recomendaciones
    h += [Paragraph("6. Recomendaciones estratégicas", H1)]
    recomendaciones = [
        ("Reposición inmediata de productos agotados",
         f"Emitir órdenes de compra para los {len(agotados)} productos agotados y los {len(bajo)} en bajo stock (Tabla 4), "
         f"priorizando abarrotes y limpieza en {', '.join(suc[suc['Agotados'] == suc['Agotados'].max()].index)}, donde un "
         "quiebre de stock significa pérdida directa de clientes."),
        ("Stock mínimo diferenciado por sucursal",
         f"Recalcular el punto de reorden según las ventas de cada local. {s_max} vende "
         f"{suc.loc[s_max, 'Ventas_Mensuales'] / suc.loc[s_min, 'Ventas_Mensuales']:.1f} veces más que {s_min}, "
         "pero ambas usan el mismo mínimo."),
        ("Transferencias entre sucursales",
         f"Trasladar mercadería desde {rot.index[-1]} (cobertura de {rot['Cobertura_Meses'].iloc[-1]:.2f} meses) hacia "
         f"{rot.index[0]} ({rot['Cobertura_Meses'].iloc[0]:.2f} meses) antes de realizar nuevas compras."),
        ("Control del capital en electrónica y electrodomésticos",
         f"Estas categorías inmovilizan el {pct(elec_elec)} del capital. Se recomienda compra bajo pedido o consignación con "
         "proveedores y revisión mensual de los artículos de mayor valor (Tabla 6)."),
        ("Impulsar categorías de alto margen",
         f"Ropa ({pct(cat.loc['Ropa', 'Margen_Promedio_%'])}) y Papelería ({pct(cat.loc['Papelería', 'Margen_Promedio_%'])}) "
         "tienen los mejores márgenes con baja inversión: conviene ampliar su exhibición y promoverlas en temporada escolar."),
        ("Diversificación de proveedores",
         f"Negociar con proveedores alternos para reducir la dependencia de {prov.index[0]} ({pct(prov_pct.iloc[0])} del valor)."),
        ("Unificar la política de precios",
         f"Los precios del mismo producto varían hasta {pct(precio_var.max())} entre sucursales; definir una lista de precios "
         "corporativa evita inconsistencias y reclamos de clientes."),
        ("Rotación de inventario antiguo",
         f"Aplicar promociones o liquidaciones a los {len(viejos)} registros con más de 90 días sin reabastecerse, revisando "
         "si se trata de productos de baja demanda."),
        ("Monitoreo continuo con la aplicación desarrollada",
         "Utilizar la aplicación PyQt5 entregada como tablero de control semanal, actualizando el archivo CSV desde el "
         "sistema de facturación para dar seguimiento a los indicadores de este informe."),
    ]
    for i, (tit, txt) in enumerate(recomendaciones, 1):
        h += [Paragraph(f"<b>6.{i} {tit}.</b> {txt}", P)]

    h += [Paragraph("7. Entregables del proyecto", H1)]
    h += vinetas([
        "<b>datos.csv</b>: inventario de las cinco sucursales.",
        "<b>generar_datos.py</b>: generación del inventario con Pandas.",
        "<b>analisis_inventario.py</b>: inspección de estructura, tipos de datos y estadísticas básicas.",
        "<b>app_inventario.py</b>: aplicación gráfica en PyQt5 con gráficos de Matplotlib.",
        "<b>generar_informe.py</b>: generación de este informe en PDF.",
        "<b>README.md, requirements.txt y .gitignore</b>: documentación y configuración del repositorio.",
    ])

    doc = SimpleDocTemplate(SALIDA, pagesize=letter, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Informe de Consultoría - Inventario por Sucursal",
                            author=", ".join(INTEGRANTES))
    doc.build(h, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    print(f"Informe generado: {SALIDA}")


if __name__ == "__main__":
    construir()
