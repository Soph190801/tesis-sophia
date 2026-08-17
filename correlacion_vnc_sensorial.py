"""
Mapas de correlacion entre las variables VNC (Velocidad de Neuro Conducción) 
y las variables sensoriales (Latencia pico, Amplitud sensory),
separados por lado (izquierdo/derecho) y por tipo de lesion.

Tipos de lesion:
  1 -> Normal (sin lesion)
  2 -> Neuropraxia
  3 -> Axonotmesis
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

CSV_PATH = "tablas/baseDeDatosTesis.csv"
SALIDA_DIR = Path("figuras/matrices_de_correlacion/correlacion_vnc_sensorial")

LESIONES = {1: "Normal", 2: "Neuropraxia", 3: "Axonotmesis"}


def cargar_datos(path):
    df = pd.read_csv(path, decimal=",")
    columnas_valores = df.columns[6:34]  # columna G (idx 6) a AH (idx 33)
    for columna in columnas_valores:
        if df[columna].dtype == object:
            limpio = df[columna].astype(str).str.replace(",", ".", regex=False)
            df[columna] = pd.to_numeric(limpio, errors="coerce")
    return df


def obtener_columnas_vnc_sensorial(df, sufijo):
    todas = df.columns[6:34]  # columna G (idx 6) a AH (idx 33), 28 variables
    return [
        c
        for c in todas
        if c.endswith(sufijo)
        and (c.startswith("VNC") or c.startswith("Latencia pico") or c.startswith("Amplitud sensory"))
    ]


def generar_figura_lado(df, columnas, columna_lesion, titulo_lado, archivo_salida):
    fig, axes = plt.subplots(1, 3, figsize=(6 * 3, 5.5))

    for ax, (valor_lesion, nombre_lesion) in zip(axes, LESIONES.items()):
        subset = df.loc[df[columna_lesion] == valor_lesion, columnas]
        corr = subset.corr()
        sns.heatmap(
            corr,
            ax=ax,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            center=0,
            annot=True,
            fmt=".2f",
            annot_kws={"fontsize": 7},
            square=True,
            cbar=False,
        )
        ax.set_title(f"{nombre_lesion} (n={len(subset)})", fontsize=11)
        ax.tick_params(axis="x", labelsize=8, rotation=90)
        ax.tick_params(axis="y", labelsize=8, rotation=0)

    fig.suptitle(f"Correlacion VNC y Sensoriales - Lado {titulo_lado}", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    ruta_salida = SALIDA_DIR / archivo_salida
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)
    print(f"Guardado: {ruta_salida}")


def main():
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    df = cargar_datos(CSV_PATH)

    columnas_izquierda = obtener_columnas_vnc_sensorial(df, "I")
    columnas_derecha = obtener_columnas_vnc_sensorial(df, "D")

    generar_figura_lado(
        df,
        columnas_izquierda,
        "IZQUIERDO",
        "Izquierdo",
        "correlacion_vnc_sensorial_izquierdo.png",
    )
    generar_figura_lado(
        df,
        columnas_derecha,
        "DERECHO",
        "Derecho",
        "correlacion_vnc_sensorial_derecho.png",
    )


if __name__ == "__main__":
    main()
