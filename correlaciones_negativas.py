"""
Para cada matriz de correlacion generada en figuras/matrices_de_correlacion,
encuentra para cada variable el par con el que tiene la correlacion mas
negativa y guarda una tabla: Categoria, Par, Correlacion.

Se generan tablas para:
  1. General: correlacion_heatmap.png (todas las variables, todos los pacientes)
  2. correlacion_por_lesion: por lado (izquierdo/derecho) y tipo de lesion,
     sin las variables VNC
  3. correlacion_vnc_sensorial: por lado (izquierdo/derecho) y tipo de lesion,
     solo variables VNC y sensoriales
"""

from pathlib import Path

import pandas as pd

CSV_PATH = "tablas/baseDeDatosTesis.csv"
SALIDA_DIR = Path("tablas/correlaciones")

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

LESIONES = {1: "normal", 2: "neuropraxia", 3: "axonotmesis"}
LADOS = [("IZQUIERDO", "I", "izquierdo"), ("DERECHO", "D", "derecho")]


def cargar_datos(path):
    df = pd.read_csv(path, decimal=",")
    for columna in df.columns:
        if df[columna].dtype == object:
            limpio = df[columna].astype(str).str.replace(",", ".", regex=False)
            df[columna] = pd.to_numeric(limpio, errors="coerce")
    return df


def calcular_correlacion_general(df):
    numericas = df.select_dtypes(include="number").dropna(axis=1, how="all")
    numericas = numericas.loc[:, numericas.nunique(dropna=True) > 1]
    numericas = numericas.drop(columns=COLUMNAS_EXCLUIDAS, errors="ignore")
    return numericas.corr()


def obtener_columnas_lado(df, sufijo):
    todas = df.columns[6:34]  # columna G (idx 6) a AH (idx 33), 28 variables
    return [c for c in todas if c.endswith(sufijo) and "VNC" not in c]


def obtener_columnas_vnc_sensorial(df, sufijo):
    todas = df.columns[6:34]  # columna G (idx 6) a AH (idx 33), 28 variables
    return [
        c
        for c in todas
        if c.endswith(sufijo)
        and (c.startswith("VNC") or c.startswith("Latencia pico") or c.startswith("Amplitud sensory"))
    ]


def pares_mas_negativos(corr):
    filas = []
    for categoria in corr.columns:
        serie = corr[categoria].drop(index=categoria).dropna()
        if serie.empty:
            continue
        par = serie.idxmin()
        filas.append(
            {
                "Categoria": categoria,
                "Par": par,
                "Correlacion": serie[par],
            }
        )
    return pd.DataFrame(filas).sort_values("Correlacion").reset_index(drop=True)


def guardar_tabla(corr, archivo_salida):
    tabla = pares_mas_negativos(corr)
    archivo_salida.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(archivo_salida, index=False)
    print(f"Guardado: {archivo_salida}")


def generar_tablas_por_lado_y_lesion(df, obtener_columnas, columna_lesion, sufijo, nombre_lado, carpeta):
    columnas = obtener_columnas(df, sufijo)
    for valor_lesion, nombre_lesion in LESIONES.items():
        subset = df.loc[df[columna_lesion] == valor_lesion, columnas]
        corr = subset.corr()
        archivo_salida = SALIDA_DIR / carpeta / f"correlaciones_negativas_{nombre_lado}_{nombre_lesion}.csv"
        guardar_tabla(corr, archivo_salida)


def main():
    df = cargar_datos(CSV_PATH)

    guardar_tabla(calcular_correlacion_general(df), SALIDA_DIR / "correlaciones_negativas.csv")

    for columna_lesion, sufijo, nombre_lado in LADOS:
        generar_tablas_por_lado_y_lesion(
            df, obtener_columnas_lado, columna_lesion, sufijo, nombre_lado, "correlacion_por_lesion"
        )
        generar_tablas_por_lado_y_lesion(
            df, obtener_columnas_vnc_sensorial, columna_lesion, sufijo, nombre_lado, "correlacion_vnc_sensorial"
        )


if __name__ == "__main__":
    main()
