# Inventario por sucursal: consultoría de datos

**Universidad Gerardo Barrios**, Programación Computacional III, Parcial Segundo Cómputo

## Integrantes

- William Alexander Valencia Rosa
- Abner Lemuel Pérez Medrano

**Docente:** Willian Alexis Montes Girón

Facultad de Ciencia y Tecnología, Ingeniería en Sistemas y Redes Informáticas

## Descripción

Una empresa salvadoreña con locales en **San Salvador, Santa Ana, San Miguel, La Libertad y Sonsonate**
solicitó a un consultor de datos:

1. Un inventario con lo que contiene cada sucursal (`datos.csv`).
2. Una aplicación gráfica para visualizar ese inventario (`app_inventario.py`).
3. Un informe de consultoría en PDF (`Informe_Consultoria_Inventario.pdf`).

## Contenido del repositorio

| Archivo | Descripción |
|---------|-------------|
| `datos.csv` | Inventario: 135 registros y 13 columnas (27 productos × 5 sucursales) |
| `generar_datos.py` | Genera `datos.csv` con Pandas (semilla fija, reproducible) |
| `analisis_inventario.py` | Inspección con Pandas: `head`, `info`, `dtypes`, `describe`, `isnull`, `value_counts`, `groupby`, `crosstab`, `corr` |
| `app_inventario.py` | Interfaz gráfica en PyQt5 con gráficos de Matplotlib |
| `generar_informe.py` | Genera el informe de consultoría en PDF |
| `Informe_Consultoria_Inventario.pdf` | Informe de consultoría |
| `requirements.txt` | Dependencias del proyecto |
| `.gitignore` | Archivos excluidos del repositorio |

### Columnas del inventario

`ID_Producto`, `Producto`, `Categoria`, **`Sucursal`**, `Proveedor`, `Stock`, `Stock_Minimo`,
`Costo_Unitario`, `Precio_Venta`, `Valor_Inventario`, `Ventas_Mensuales`, `Fecha_Ultimo_Ingreso`, `Estado`

## Instalación y uso

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

python generar_datos.py        # (opcional) vuelve a generar datos.csv
python analisis_inventario.py  # inspección del inventario con Pandas
python app_inventario.py       # abre la aplicación gráfica
python generar_informe.py      # (opcional) vuelve a generar el informe PDF
```

## Aplicación gráfica

- Filtros por **sucursal** y **categoría**.
- Indicadores: registros, unidades, valor del inventario, ventas mensuales y productos críticos.
- Pestañas de gráficos (Matplotlib): valor por sucursal, stock por categoría, estado del stock,
  stock frente a ventas, y precios y márgenes. Cada gráfico tiene la barra de herramientas de Matplotlib (zoom y guardar imagen).
- Tabla de inventario ordenable y botón para abrir otro archivo CSV.

## Tecnologías

Python 3 · Pandas · NumPy · Matplotlib · PyQt5 · ReportLab
