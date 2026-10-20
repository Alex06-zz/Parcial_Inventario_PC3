"""
generar_datos.py
Genera el inventario de la empresa (datos.csv) directamente con Pandas.
Cinco sucursales: San Salvador, Santa Ana, San Miguel, La Libertad y Sonsonate.
"""

import numpy as np
import pandas as pd

SEMILLA = 2026
rng = np.random.default_rng(SEMILLA)

SUCURSALES = ["San Salvador", "Santa Ana", "San Miguel", "La Libertad", "Sonsonate"]

# Factor de tamaño de cada sucursal (San Salvador es la más grande)
FACTOR_SUCURSAL = {
    "San Salvador": 1.45,
    "Santa Ana": 1.05,
    "San Miguel": 1.00,
    "La Libertad": 0.90,
    "Sonsonate": 0.70,
}

# Catálogo: producto -> (categoría, precio base USD, margen aproximado, proveedor)
CATALOGO = {
    "Laptop 15 pulgadas":        ("Electrónica", 649.00, 0.18, "TecnoCentro S.A. de C.V."),
    "Smartphone gama media":     ("Electrónica", 279.00, 0.20, "TecnoCentro S.A. de C.V."),
    "Audífonos inalámbricos":    ("Electrónica", 39.90, 0.35, "Distribuidora Digital"),
    "Televisor 50 pulgadas":     ("Electrónica", 429.00, 0.17, "TecnoCentro S.A. de C.V."),
    "Mouse inalámbrico":         ("Electrónica", 14.50, 0.40, "Distribuidora Digital"),
    "Refrigeradora 14 pies":     ("Electrodomésticos", 689.00, 0.15, "Hogar Total"),
    "Licuadora 10 velocidades":  ("Electrodomésticos", 49.90, 0.30, "Hogar Total"),
    "Microondas 1.1 pies":       ("Electrodomésticos", 99.00, 0.25, "Hogar Total"),
    "Ventilador de pedestal":    ("Electrodomésticos", 32.00, 0.32, "Importadora Cuscatlán"),
    "Plancha de vapor":          ("Electrodomésticos", 24.90, 0.33, "Importadora Cuscatlán"),
    "Arroz 5 lb":                ("Abarrotes", 4.25, 0.12, "Agroindustrias del Pacífico"),
    "Frijol rojo 2 lb":          ("Abarrotes", 2.60, 0.14, "Agroindustrias del Pacífico"),
    "Aceite vegetal 1 L":        ("Abarrotes", 3.10, 0.13, "Agroindustrias del Pacífico"),
    "Café molido 400 g":         ("Abarrotes", 5.75, 0.22, "Café de Altura S.A."),
    "Azúcar 5 lb":               ("Abarrotes", 3.40, 0.10, "Agroindustrias del Pacífico"),
    "Detergente 2 kg":           ("Limpieza", 6.90, 0.24, "Químicos del Valle"),
    "Desinfectante 1 galón":     ("Limpieza", 4.80, 0.28, "Químicos del Valle"),
    "Papel higiénico 12 rollos": ("Limpieza", 5.50, 0.20, "Químicos del Valle"),
    "Jabón de baño (3 und)":     ("Limpieza", 2.95, 0.26, "Químicos del Valle"),
    "Camiseta algodón":          ("Ropa", 9.99, 0.45, "Textiles Salvadoreños"),
    "Pantalón jean":             ("Ropa", 24.99, 0.42, "Textiles Salvadoreños"),
    "Zapatos deportivos":        ("Ropa", 44.90, 0.38, "Calzado Nacional"),
    "Gorra bordada":             ("Ropa", 8.50, 0.50, "Textiles Salvadoreños"),
    "Cuaderno universitario":    ("Papelería", 2.25, 0.35, "Librería y Papelería Central"),
    "Bolígrafos (caja 12)":      ("Papelería", 3.20, 0.38, "Librería y Papelería Central"),
    "Resma papel bond":          ("Papelería", 5.40, 0.20, "Librería y Papelería Central"),
    "Mochila escolar":           ("Papelería", 19.90, 0.40, "Importadora Cuscatlán"),
}

# Stock base según el tipo de categoría (productos baratos tienen más unidades)
STOCK_BASE = {
    "Electrónica": 18,
    "Electrodomésticos": 12,
    "Abarrotes": 160,
    "Limpieza": 110,
    "Ropa": 55,
    "Papelería": 90,
}


def generar_inventario() -> pd.DataFrame:
    filas = []
    correlativo = 1
    fecha_corte = pd.Timestamp("2026-10-15")

    for sucursal in SUCURSALES:
        factor = FACTOR_SUCURSAL[sucursal]
        for producto, (categoria, precio, margen, proveedor) in CATALOGO.items():
            base = STOCK_BASE[categoria] * factor
            stock = int(max(0, rng.normal(base, base * 0.45)))
            # Algunos productos agotados de forma aleatoria (~6 %)
            if rng.random() < 0.06:
                stock = 0

            stock_minimo = int(round(STOCK_BASE[categoria] * 0.30))
            # Variación de precio entre sucursales (±5 %)
            precio_venta = round(precio * rng.uniform(0.95, 1.05), 2)
            costo = round(precio_venta * (1 - margen), 2)

            if stock == 0:
                estado = "Agotado"
            elif stock < stock_minimo:
                estado = "Bajo stock"
            else:
                estado = "Disponible"

            dias = int(rng.integers(1, 120))
            filas.append({
                "ID_Producto": f"P{correlativo:04d}",
                "Producto": producto,
                "Categoria": categoria,
                "Sucursal": sucursal,
                "Proveedor": proveedor,
                "Stock": stock,
                "Stock_Minimo": stock_minimo,
                "Costo_Unitario": costo,
                "Precio_Venta": precio_venta,
                "Valor_Inventario": round(stock * costo, 2),
                "Ventas_Mensuales": int(max(0, rng.normal(base * 0.6, base * 0.25))),
                "Fecha_Ultimo_Ingreso": (fecha_corte - pd.Timedelta(days=dias)).date(),
                "Estado": estado,
            })
            correlativo += 1

    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = generar_inventario()
    df.to_csv("datos.csv", index=False, encoding="utf-8")
    print(f"Inventario generado: {len(df)} registros, {df.shape[1]} columnas -> datos.csv")
