# Análisis de neuroconducción

Scripts en Python para el análisis exploratorio de un estudio de neuroconducción
(nervios mediano y cubital, lado izquierdo y derecho), clasificado por tipo de
lesión: **Normal**, **Neuropraxia** y **Axonotmesis**.

## Datos

- `tablas/baseDeDatosTesis.csv`: base de datos original. Cada fila es un
  paciente, con variables demográficas, comorbilidades, mediciones de
  neuroconducción motora y sensorial (slatencia, amplitud, velocidad de
  conducción) para los nervios mediano (NM) y cubital (NU) de ambos lados, y
  la clasificación de lesión por lado (`IZQUIERDO` / `DERECHO`, valores 1/2/3).

### Códigos de la base de datos

**Sexo**

| Código | Valor   |
|--------|---------|
| 1      | Mujer   |
| 2      | Hombre  |

**Servicio de referencia**

| Código | Valor              | Código | Valor            |
|--------|--------------------|--------|-------------------|
| 1      | Rehabilitación     | 13     | Hematología       |
| 2      | Ortopedia          | 14     | No dice           |
| 3      | Neurología         | 15     | Cirugía general   |
| 4      | Clínica del dolor  | 16     | Ginecología       |
| 5      | Medicina interna   | 17     | Medicina familiar |
| 6      | Cirugía plástica   | 18     | Angiología        |
| 7      | Neurocirugía       | 19     | Urología          |
| 8      | Infectología       | 20     | Nefrología        |
| 9      | Medicina general   | 21     | Neumología        |
| 10     | Genética           | 22     | Alergia           |
| 11     | Reumatología       | 21     | Audiología*       |
| 12     | Caído              | 24     | Gastroenterología |

\* código duplicado (21) tal como está en la fuente original.

**Comorbilidades**

| Código | Valor                        |
|--------|-------------------------------|
| 0      | Ninguna                      |
| 1      | Diabetes tipo II              |
| 2      | Artritis reumatoide            |
| 3      | Cáncer de mama                 |
| 4      | VIH                             |
| 5      | Secuelas fractura de muñeca     |
| 6      | Hipertensión                   |
| 7      | Sjögren                        |
| 8      | Fibromialgia                   |
| 9      | Lupus                          |
| 10     | OA                              |
| 11     | Hipotiroidismo                 |

**Tipo de lesión** (columnas `IZQUIERDO` / `DERECHO`)

| Código | Valor        |
|--------|--------------|
| 1      | Normal       |
| 2      | Neuropraxia  |
| 3      | Axonotmesis  |

**Localización**

| Código | Valor      |
|--------|------------|
| 1      | Derecha    |
| 2      | Izquierda  |
| 3      | Bilateral  |

## Scripts

- `histogramas.py` — histogramas de las variables de conducción nerviosa
  (lado izquierdo, derecho y bilateral), comparando Sano vs Patológico con
  curva de distribución normal ajustada.
- `correlacion.py` — matriz de correlación (heatmap) entre todas las
  variables numéricas relevantes.
- `correlacion_por_lesion.py` — mapas de correlación por lado y tipo de
  lesión, excluyendo las variables VNC.
- `correlacion_vnc_sensorial.py` — mapas de correlación por lado y tipo de
  lesión, solo con las variables VNC y sensoriales.
- `correlaciones_negativas.py` — para cada matriz de correlación generada,
  identifica el par de variables con la correlación más negativa y guarda
  una tabla (Categoría, Par, Correlación).
- `pairplots.py` — genera pairplots (dispersión + distribución) para los
  pares de variables identificados en `correlaciones_negativas.py`,
  coloreados por grupo de lesión.

## Salidas

- `figuras/histogramas/`
- `figuras/matrices_de_correlacion/` (general, `correlacion_por_lesion/`,
  `correlacion_vnc_sensorial/`)
- `figuras/pairplots/` (`general/`, `correlacion_por_lesion/`,
  `correlacion_vnc_sensorial/`)
- `tablas/correlaciones/` (tablas de correlaciones negativas, misma
  estructura de carpetas que `figuras/matrices_de_correlacion/`)

## Uso

Cada script se corre de forma independiente desde la raíz del repositorio:

```bash
python3 histogramas.py
python3 correlacion.py
python3 correlacion_por_lesion.py
python3 correlacion_vnc_sensorial.py
python3 correlaciones_negativas.py   # genera las tablas que usa pairplots.py
python3 pairplots.py                 # depende de las tablas anteriores
```

Requiere `pandas`, `numpy`, `scipy`, `matplotlib` y `seaborn`.
