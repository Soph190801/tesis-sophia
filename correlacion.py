"""
Matriz de correlacion (heatmap) entre todas las variables numericas de
baseDeDatosTesis.csv.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

CSV_PATH = "tablas/baseDeDatosTesis.csv"
SALIDA_DIR = Path("figuras/matrices_de_correlacion")
SALIDA = SALIDA_DIR / "correlacion_heatmap.png"

COLUMNAS_EXCLUIDAS = [
    "ID",
    "Edad",
    "Sexo",
    "Servicio de referencia",
    "Comorbilidaes",
    "IZQUIERDO",
    "DERECHO",
    "Año",
]


def cargar_datos(path):
    df = pd.read_csv(path, decimal=",")
    for columna in df.columns:
        if df[columna].dtype == object:
            limpio = df[columna].astype(str).str.replace(",", ".", regex=False)
            df[columna] = pd.to_numeric(limpio, errors="coerce")
    return df


def main():
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    df = cargar_datos(CSV_PATH)
    numericas = df.select_dtypes(include="number").dropna(axis=1, how="all")
    numericas = numericas.loc[:, numericas.nunique(dropna=True) > 1]
    numericas = numericas.drop(columns=COLUMNAS_EXCLUIDAS, errors="ignore")

    corr = numericas.corr()

    fig, ax = plt.subplots(figsize=(0.5 * len(corr.columns) + 2, 0.5 * len(corr.columns) + 2))
    sns.heatmap(
        corr,
        ax=ax,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        center=0,
        annot=True,
        fmt=".2f",
        annot_kws={"fontsize": 6},
        square=True,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Matriz de correlacion")
    fig.tight_layout()
    fig.savefig(SALIDA, dpi=150)
    plt.close(fig)
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
