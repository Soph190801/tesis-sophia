"""
Histogramas de las variables de conduccion nerviosa (columnas G:AH) con curva
de distribucion normal ajustada, comparando Sano vs Patologico.

Reglas de clasificacion (columnas IZQUIERDO=AI y DERECHO=AJ; valores 1/2/3):
  - Sano       -> valor == 1
  - Patologico -> valor in {2, 3}

Se generan tres figuras:
  1. Izquierda : variables del lado izquierdo (NMI/NUI), agrupadas por IZQUIERDO
  2. Derecha   : variables del lado derecho (NMD/NUD), agrupadas por DERECHO
  3. Bilateral : las 28 variables (G:AH), agrupadas por IZQUIERDO y DERECHO a la vez
                 (Sano = ambos lados sanos, Patologico = ambos lados patologicos;
                 los casos mixtos se excluyen)
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

CSV_PATH = "tablas/baseDeDatosTesis.csv"
SALIDA_DIR = Path("figuras/histogramas")

SANO_COLOR = "#4C72B0"
PATOLOGICO_COLOR = "#DD8452"
N_BINS = 20


def cargar_datos(path):
    df = pd.read_csv(path, decimal=",")
    columnas_valores = df.columns[6:34]  # columna G (idx 6) a AH (idx 33)
    for columna in columnas_valores:
        if df[columna].dtype == object:
            limpio = df[columna].astype(str).str.replace(",", ".", regex=False)
            df[columna] = pd.to_numeric(limpio, errors="coerce")
    return df


def obtener_columnas_valores(df):
    todas = df.columns[6:34]  # columna G (idx 6) a AH (idx 33), 28 variables
    izquierda = [c for c in todas if c.endswith("I")]
    derecha = [c for c in todas if c.endswith("D")]
    return list(todas), izquierda, derecha


def clasificar(serie):
    sano = serie == 1
    patologico = serie.isin([2, 3])
    return sano, patologico


def graficar_grupo(ax, valores, color, etiqueta):
    valores = valores.dropna()
    n = len(valores)
    if n == 0:
        return
    ax.hist(
        valores,
        bins=N_BINS,
        density=True,
        alpha=0.45,
        color=color,
        label=f"{etiqueta} (n={n})",
    )
    if n >= 2 and valores.std() > 0:
        mu, sigma = stats.norm.fit(valores)
        x = np.linspace(valores.min(), valores.max(), 200)
        ax.plot(x, stats.norm.pdf(x, mu, sigma), color=color, linewidth=2)


def graficar_variable(ax, columna, datos_sano, datos_patologico):
    graficar_grupo(ax, datos_sano, SANO_COLOR, "Sano")
    graficar_grupo(ax, datos_patologico, PATOLOGICO_COLOR, "Patologico")
    ax.set_title(columna, fontsize=10)
    ax.set_xlabel(columna)
    ax.set_ylabel("Densidad")
    ax.legend(fontsize=7)


def generar_figura(df, columnas, mask_sano, mask_patologico, titulo, archivo_salida):
    ncols = 4
    nrows = math.ceil(len(columnas) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    axes = np.atleast_2d(axes).reshape(nrows, ncols)

    for i, columna in enumerate(columnas):
        fila, col = divmod(i, ncols)
        ax = axes[fila][col]
        graficar_variable(
            ax,
            columna,
            df.loc[mask_sano, columna],
            df.loc[mask_patologico, columna],
        )

    for i in range(len(columnas), nrows * ncols):
        fila, col = divmod(i, ncols)
        axes[fila][col].axis("off")

    fig.suptitle(titulo, fontsize=16)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    ruta_salida = SALIDA_DIR / archivo_salida
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)
    print(f"Guardado: {ruta_salida}")


def main():
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    df = cargar_datos(CSV_PATH)
    _, columnas_izquierda, columnas_derecha = obtener_columnas_valores(df)
    columnas_todas = list(df.columns[6:34])

    sano_izq, pat_izq = clasificar(df["IZQUIERDO"])
    sano_der, pat_der = clasificar(df["DERECHO"])

    sano_bilateral = sano_izq & sano_der
    pat_bilateral = pat_izq & pat_der

    generar_figura(
        df,
        columnas_izquierda,
        sano_izq,
        pat_izq,
        "Distribuciones - Lado Izquierdo | Sano vs Patologico",
        "histograma_normal_izquierdo.png",
    )
    generar_figura(
        df,
        columnas_derecha,
        sano_der,
        pat_der,
        "Distribuciones - Lado Derecho | Sano vs Patologico",
        "histograma_normal_derecho.png",
    )
    generar_figura(
        df,
        columnas_todas,
        sano_bilateral,
        pat_bilateral,
        "Distribuciones - Bilateral | Sano vs Patologico",
        "histograma_normal_bilateral.png",
    )


if __name__ == "__main__":
    main()