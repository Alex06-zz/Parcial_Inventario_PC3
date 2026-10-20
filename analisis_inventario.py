"""
analisis_inventario.py
Inspección del inventario con Pandas: estructura, tipos de datos y estadísticas básicas.
"""

import pandas as pd

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)


def cargar_datos(ruta: str = "datos.csv") -> pd.DataFrame:
    df = pd.read_csv(ruta, encoding="utf-8")
    df["Fecha_Ultimo_Ingreso"] = pd.to_datetime(df["Fecha_Ultimo_Ingreso"])
    return df


def titulo(texto: str) -> None:
    print("\n" + "=" * 80)
    print(texto)
    print("=" * 80)


def inspeccionar(df: pd.DataFrame) -> None:
    titulo("1. PRIMEROS Y ÚLTIMOS REGISTROS  -> head() / tail()")
    print(df.head())
    print(df.tail())

    titulo("2. ESTRUCTURA  -> shape / columns / info()")
    print(f"Filas: {df.shape[0]}   Columnas: {df.shape[1]}")
    print("Columnas:", list(df.columns))
    df.info()

    titulo("3. TIPOS DE DATOS  -> dtypes")
    print(df.dtypes)

    titulo("4. VALORES NULOS Y DUPLICADOS  -> isnull().sum() / duplicated()")
    print(df.isnull().sum())
    print("Registros duplicados:", df.duplicated().sum())

    titulo("5. VALORES ÚNICOS POR COLUMNA  -> nunique()")
    print(df.nunique())

    titulo("6. ESTADÍSTICAS DESCRIPTIVAS NUMÉRICAS  -> describe()")
    print(df.describe().round(2))

    titulo("7. ESTADÍSTICAS DE COLUMNAS CATEGÓRICAS  -> describe(exclude=...)")
    print(df.describe(exclude=["number", "datetime"]))

    titulo("8. FRECUENCIAS  -> value_counts()")
    for col in ["Sucursal", "Categoria", "Estado", "Proveedor"]:
        print(f"\n{col}:")
        print(df[col].value_counts())

    titulo("9. RESUMEN POR SUCURSAL  -> groupby().agg()")
    print(resumen_sucursal(df))

    titulo("10. RESUMEN POR CATEGORÍA  -> groupby().agg()")
    print(resumen_categoria(df))

    titulo("11. ESTADO DEL STOCK POR SUCURSAL  -> crosstab()")
    print(pd.crosstab(df["Sucursal"], df["Estado"], margins=True))

    titulo("12. CORRELACIÓN ENTRE VARIABLES NUMÉRICAS  -> corr()")
    print(df.select_dtypes("number").corr().round(2))

    titulo("13. RANGO DE FECHAS DE ÚLTIMO INGRESO")
    print("Más antigua:", df["Fecha_Ultimo_Ingreso"].min().date())
    print("Más reciente:", df["Fecha_Ultimo_Ingreso"].max().date())

    titulo("14. PRODUCTOS AGOTADOS O CON BAJO STOCK")
    criticos = df[df["Estado"] != "Disponible"]
    print(criticos[["Sucursal", "Producto", "Stock", "Stock_Minimo", "Estado"]].to_string(index=False))


def resumen_sucursal(df: pd.DataFrame) -> pd.DataFrame:
    res = df.groupby("Sucursal").agg(
        Productos=("ID_Producto", "count"),
        Unidades=("Stock", "sum"),
        Valor_Inventario=("Valor_Inventario", "sum"),
        Ventas_Mensuales=("Ventas_Mensuales", "sum"),
        Agotados=("Estado", lambda s: (s == "Agotado").sum()),
        Bajo_Stock=("Estado", lambda s: (s == "Bajo stock").sum()),
    )
    res["Cobertura_Meses"] = (res["Unidades"] / res["Ventas_Mensuales"]).round(2)
    return res.sort_values("Valor_Inventario", ascending=False).round(2)


def resumen_categoria(df: pd.DataFrame) -> pd.DataFrame:
    res = df.groupby("Categoria").agg(
        Unidades=("Stock", "sum"),
        Valor_Inventario=("Valor_Inventario", "sum"),
        Precio_Promedio=("Precio_Venta", "mean"),
        Ventas_Mensuales=("Ventas_Mensuales", "sum"),
    )
    res["Margen_Promedio_%"] = (
        df.assign(m=(df["Precio_Venta"] - df["Costo_Unitario"]) / df["Precio_Venta"] * 100)
        .groupby("Categoria")["m"].mean()
    )
    res["Participacion_Valor_%"] = res["Valor_Inventario"] / res["Valor_Inventario"].sum() * 100
    return res.sort_values("Valor_Inventario", ascending=False).round(2)


if __name__ == "__main__":
    inspeccionar(cargar_datos())
