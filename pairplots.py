"""
Genera pairplots a partir de las correlaciones negativas mas fuertes:

  1. General (figuras/pairplots/general/<lado>/): para cada par (fila) de
     tablas/correlaciones/correlaciones_negativas.csv, un pairplot usando
     todos los pacientes, coloreado por grupo de lesion (Normal/Neuropraxia/
     Axonotmesis). Se genera una vez por lado (IZQUIERDO y DERECHO), ya que
     la tabla general mezcla variables de ambos lados.
  2. Por lado + tipo de lesion, sin VNC (figuras/pairplots/correlacion_por_lesion/)
     y VNC+sensoriales (figuras/pairplots/correlacion_vnc_sensorial/): para
     cada fila de cada tabla en tablas/correlaciones/, un pairplot entre esa
     Categoria y su Par, usando el mismo subconjunto de pacientes con el que
     se calculo esa tabla.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

CSV_PATH = "tablas/baseDeDatosTesis.csv"
TABLAS_DIR = Path("tablas/correlaciones")
FIGURAS_DIR = Path("figuras/pairplots")

LESIONES = {1: "normal", 2: "neuropraxia", 3: "axonotmesis"}
LADOS = [("IZQUIERDO", "I", "izquierdo"), ("DERECHO", "D", "derecho")]
CARPETAS = ["correlacion_por_lesion", "correlacion_vnc_sensorial"]


def cargar_datos(path):
    df = pd.read_csv(path, decimal=",")
    for columna in df.columns:
        if df[columna].dtype == object:
            limpio = df[columna].astype(str).str.replace(",", ".", regex=False)
            df[columna] = pd.to_numeric(limpio, errors="coerce")
    return df


def nombre_archivo(categoria, par):
    return f"{categoria.replace(' ', '_')}_vs_{par.replace(' ', '_')}.png"


def generar_pairplot(datos, categoria, par, correlacion, carpeta_salida):
    subset = datos[[categoria, par]].dropna()
    if len(subset) < 2:
        print(f"Omitido (datos insuficientes): {categoria} vs {par}")
        return

    grid = sns.pairplot(subset)
    grid.fig.suptitle(f"{categoria} vs {par} (r={correlacion:.2f}, n={len(subset)})", y=1.02)

    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = carpeta_salida / nombre_archivo(categoria, par)
    grid.fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close(grid.fig)
    print(f"Guardado: {ruta_salida}")


def generar_pairplot_coloreado(df, categoria, par, correlacion, columna_lesion, nombre_lado, carpeta_salida):
    subset = df.loc[df[columna_lesion].isin(LESIONES.keys()), [categoria, par, columna_lesion]].dropna()
    if len(subset) < 2:
        print(f"Omitido (datos insuficientes): {categoria} vs {par} ({nombre_lado})")
        return
    subset["Grupo"] = subset[columna_lesion].map(LESIONES).str.capitalize()
    subset = subset.drop(columns=[columna_lesion])

    grid = sns.pairplot(
        subset,
        hue="Grupo",
        hue_order=[nombre.capitalize() for nombre in LESIONES.values()],
        plot_kws={"alpha": 0.6, "s": 20},
    )
    grid.fig.suptitle(
        f"{categoria} vs {par} - {nombre_lado.capitalize()} (r={correlacion:.2f}, n={len(subset)})", y=1.02
    )

    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = carpeta_salida / nombre_archivo(categoria, par)
    grid.fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close(grid.fig)
    print(f"Guardado: {ruta_salida}")


def procesar_tabla_general(tabla_path, df):
    tabla = pd.read_csv(tabla_path)
    pares_vistos = set()
    for _, fila in tabla.iterrows():
        categoria, par = fila["Categoria"], fila["Par"]
        clave = frozenset((categoria, par))
        if clave in pares_vistos:
            continue
        pares_vistos.add(clave)
        for columna_lesion, _sufijo, nombre_lado in LADOS:
            carpeta_salida = FIGURAS_DIR / "general" / nombre_lado
            generar_pairplot_coloreado(df, categoria, par, fila["Correlacion"], columna_lesion, nombre_lado, carpeta_salida)


def procesar_tabla(tabla_path, datos, carpeta_salida):
    tabla = pd.read_csv(tabla_path)
    pares_vistos = set()
    for _, fila in tabla.iterrows():
        categoria, par = fila["Categoria"], fila["Par"]
        clave = frozenset((categoria, par))
        if clave in pares_vistos:
            continue
        pares_vistos.add(clave)
        generar_pairplot(datos, categoria, par, fila["Correlacion"], carpeta_salida)


def main():
    df = cargar_datos(CSV_PATH)

    # General: un pairplot por par y por lado, coloreado por grupo de lesion
    procesar_tabla_general(TABLAS_DIR / "correlaciones_negativas.csv", df)

    # Tablas por lado + tipo de lesion
    for carpeta in CARPETAS:
        for columna_lesion, _sufijo, nombre_lado in LADOS:
            for valor_lesion, nombre_lesion in LESIONES.items():
                tabla_path = TABLAS_DIR / carpeta / f"correlaciones_negativas_{nombre_lado}_{nombre_lesion}.csv"
                subset_df = df.loc[df[columna_lesion] == valor_lesion]
                carpeta_salida = FIGURAS_DIR / carpeta / f"{nombre_lado}_{nombre_lesion}"
                procesar_tabla(tabla_path, subset_df, carpeta_salida)


if __name__ == "__main__":
    main()
