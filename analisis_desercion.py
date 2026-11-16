from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })


def explorar(df):
    """Paso 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    """
    print("\n=== Exploración inicial ===")
    print(f"Filas y columnas: {df.shape}")
    print("\nTipos y valores no nulos:")
    df.info()
    print("\nEstadísticas numéricas:")
    print(df.describe())
    for columna in ["programa", "jornada", "genero", "estado"]:
        print(f"\nValores de {columna}:")
        print(df[columna].value_counts(dropna=False))


def auditar(df):
    """Paso 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    """
    print("\n=== Auditoría de calidad ===")
    print("\nNulos reales por columna:")
    print(df.isnull().sum())
    print("\nFaltantes disfrazados:")
    print(f"Guiones en asistencia_pct: {df['asistencia_pct'].eq('-').sum()}")
    print(f"Guiones en horas_trabajo_semana: {df['horas_trabajo_semana'].eq('-').sum()}")
    print(f"999 en distancia_km: {df['distancia_km'].eq(999).sum()}")
    print(
        "Signos % en asistencia_pct: "
        f"{df['asistencia_pct'].str.contains('%', regex=False).sum()}"
    )
    print(f"Filas duplicadas: {df.duplicated().sum()}")
    edades_imposibles = (df["edad"] < 15) | (df["edad"] > 60)
    promedios_imposibles = df["promedio_acumulado"] > 5
    horas = pd.to_numeric(df["horas_trabajo_semana"].replace("-", np.nan), errors="coerce")
    print(f"Edades fuera del rango 15-60: {edades_imposibles.sum()}")
    print(f"Promedios mayores a 5: {promedios_imposibles.sum()}")
    print(f"Horas de trabajo mayores a 100: {horas.gt(100).sum()}")
    fechas_dmy = df["fecha_matricula"].str.contains("/", regex=False)
    print(f"Fechas en formato DD/MM/AAAA: {fechas_dmy.sum()}")
    print(f"Fechas en formato AAAA-MM-DD: {(~fechas_dmy).sum()}")


def convertir_numericos(df):
    """Paso 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
    asistencia = df["asistencia_pct"].astype("string")
    asistencia_con_porcentaje = asistencia.str.contains("%", regex=False, na=False)
    guiones_asistencia = asistencia.eq("-").sum()
    df["asistencia_pct"] = pd.to_numeric(
        asistencia.str.replace("%", "", regex=False).replace("-", np.nan),
        errors="coerce",
    )
    registrar(
        "conversión numérica",
        "asistencia_pct",
        "quitar % y convertir a numérico; guiones a nulo",
        int(asistencia_con_porcentaje.sum() + guiones_asistencia),
        "La asistencia debe ser numérica para calcular estadísticas y cuartiles; "
        "el guion representa un dato faltante que se conserva sin imputar para "
        "no inventar una medición.",
    )

    guiones_horas = df["horas_trabajo_semana"].eq("-").sum()
    df["horas_trabajo_semana"] = pd.to_numeric(
        df["horas_trabajo_semana"].replace("-", np.nan),
        errors="coerce",
    )
    registrar(
        "conversión numérica",
        "horas_trabajo_semana",
        "convertir a numérico; guiones a nulo",
        int(guiones_horas),
        "Las horas deben ser numéricas; el guion es un faltante disfrazado y se "
        "trata según trabaja en el paso de valores imposibles.",
    )

    distancia_invalida = df["distancia_km"].eq(999)
    df["distancia_km"] = pd.to_numeric(
        df["distancia_km"].mask(distancia_invalida),
        errors="coerce",
    )
    registrar(
        "conversión numérica",
        "distancia_km",
        "reemplazar 999 por nulo y convertir a numérico",
        int(distancia_invalida.sum()),
        "999 es un código de faltante, no una distancia real en kilómetros.",
    )
    return df


def unificar_categorias(df):
    """Paso 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    """
    variantes = {
        "programa": {
            "ingenieria de sistemas": "Ingeniería de Sistemas",
            "psicologia": "Psicología",
        },
        "jornada": {},
        "genero": {
            "f": "Femenino",
            "m": "Masculino",
        },
        "ciudad_procedencia": {
            "bogota": "Bogotá",
            "medellin": "Medellín",
        },
    }

    for columna in variantes:
        original = df[columna]
        normalizada = original.str.strip().str.lower()
        canonicos = {valor.lower(): valor for valor in VALIDOS[columna]}
        canonicos.update(variantes[columna])
        df[columna] = normalizada.map(lambda valor: canonicos.get(valor, valor))
        cambiaron = original.notna() & original.ne(df[columna])
        registrar(
            "unificación de categorías",
            columna,
            "quitar espacios, normalizar mayúsculas y unificar variantes",
            int(cambiaron.sum()),
            "Se consolidan diferencias de escritura que representan la misma "
            "categoría; no se mezclan categorías con significados distintos.",
        )
    return df


def convertir_fechas(df):
    """Paso 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    fecha_iso = pd.to_datetime(
        df["fecha_matricula"], format="%Y-%m-%d", errors="coerce"
    )
    fecha_dmy = pd.to_datetime(
        df["fecha_matricula"], format="%d/%m/%Y", errors="coerce"
    )
    df["fecha_matricula"] = fecha_iso.fillna(fecha_dmy)
    registrar(
        "conversión de fechas",
        "fecha_matricula",
        "convertir formatos AAAA-MM-DD y DD/MM/AAAA a fecha",
        int(fecha_dmy.notna().sum()),
        "La columna mezcla dos formatos; se intenta cada formato explícitamente "
        "y se combinan los resultados sin invertir día y mes.",
    )
    return df


def eliminar_duplicados(df):
    """Paso 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Pista: duplicated() y drop_duplicates(), con reset_index(drop=True).
    """
    duplicados = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    registrar(
        "duplicados",
        "todas las columnas",
        "eliminar filas duplicadas y reiniciar índice",
        duplicados,
        "Las filas repetidas contienen el mismo identificador y todos los datos; "
        "conservar ambas inflaría los conteos del análisis.",
    )
    return df


def tratar_faltantes(df):
    """Paso 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    sin_promedio = int(df["promedio_acumulado"].isna().sum())
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar(
        "faltantes",
        "promedio_acumulado",
        "eliminar filas sin promedio",
        sin_promedio,
        "No es válido inventar o imputar una nota; estas filas no pueden aportar "
        "a análisis que requieren el promedio.",
    )

    for columna in ["ciudad_procedencia", "tipo_colegio"]:
        faltantes = int(df[columna].isna().sum())
        df[columna] = df[columna].fillna("Sin dato")
        registrar(
            "faltantes",
            columna,
            "reemplazar nulos por Sin dato",
            faltantes,
            "La categoría desconocida no impide conservar al estudiante y evita "
            "atribuirle una procedencia o tipo de colegio inventados.",
        )

    for columna in ["asistencia_pct", "distancia_km", "motivo_retiro"]:
        faltantes = int(df[columna].isna().sum())
        if columna == "motivo_retiro":
            justificacion = (
                "El motivo solo aplica a quienes desertaron; el nulo de estudiantes "
                "activos o graduados es esperado y se conserva."
            )
        else:
            justificacion = (
                "No hay información para reconstruir el valor; se conserva como "
                "nulo en lugar de inventar una medición."
            )
        registrar(
            "faltantes",
            columna,
            "conservar nulos sin imputar",
            faltantes,
            justificacion,
        )
    return df


def tratar_imposibles(df):
    """Paso 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    edades_invalidas = (df["edad"] < 15) | (df["edad"] > 60)
    cantidad_edades_invalidas = int(edades_invalidas.sum())
    if cantidad_edades_invalidas:
        mediana_edad = df.loc[~edades_invalidas, "edad"].median()
        df.loc[edades_invalidas, "edad"] = mediana_edad
    else:
        mediana_edad = df["edad"].median()
    registrar(
        "valores imposibles",
        "edad",
        f"reemplazar edades fuera de 15-60 por la mediana ({mediana_edad:g})",
        cantidad_edades_invalidas,
        "Las edades fuera del rango definido por la guía son errores; la mediana "
        "de edades válidas evita perder esas filas y no se distorsiona por extremos.",
    )

    promedios_invalidos = df["promedio_acumulado"] > 5
    cantidad_promedios_invalidos = int(promedios_invalidos.sum())
    df.loc[promedios_invalidos, "promedio_acumulado"] = np.nan
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar(
        "valores imposibles",
        "promedio_acumulado",
        "marcar notas mayores a 5 como nulas y eliminar esas filas",
        cantidad_promedios_invalidos,
        "La escala va de 0 a 5; no hay información para reconstruir una nota "
        "válida, por lo que no se imputa.",
    )

    no_trabaja = df["trabaja"].str.strip().str.lower().eq("no")
    horas_no_cero = no_trabaja & df["horas_trabajo_semana"].ne(0)
    cantidad_horas_ajustadas = int(horas_no_cero.sum())
    df.loc[no_trabaja, "horas_trabajo_semana"] = 0
    registrar(
        "valores imposibles",
        "horas_trabajo_semana",
        "asignar 0 horas a quienes no trabajan",
        cantidad_horas_ajustadas,
        "Si trabaja es no, las horas laborales semanales son cero; se evita "
        "interpretar el guion como una cantidad.",
    )

    horas_invalidas = df["horas_trabajo_semana"] > 100
    cantidad_horas_invalidas = int(horas_invalidas.sum())
    df.loc[horas_invalidas, "horas_trabajo_semana"] = np.nan
    trabaja = df["trabaja"].str.strip().str.lower().isin(["sí", "si"])
    mediana_horas = df.loc[
        trabaja & df["horas_trabajo_semana"].notna(), "horas_trabajo_semana"
    ].median()
    df.loc[horas_invalidas, "horas_trabajo_semana"] = mediana_horas
    registrar(
        "valores imposibles",
        "horas_trabajo_semana",
        f"reemplazar valores mayores a 100 por la mediana laboral ({mediana_horas:g})",
        cantidad_horas_invalidas,
        "Más de 100 horas semanales excede un límite razonable; se usa la mediana "
        "de quienes trabajan, no la de toda la población.",
    )
    return df


def crear_variables(df):
    """Paso 9 del Word: variables nuevas para el análisis.

    Crea:
    - desertor: True si estado es 'desertor', False si no.
    - cuartil_asistencia: divide asistencia_pct en cuatro grupos iguales con pd.qcut.
    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    """
    df["desertor"] = df["estado"].eq("desertor")
    registrar(
        "variables nuevas",
        "desertor",
        "crear indicador booleano a partir de estado",
        len(df),
        "Permite calcular directamente la proporción de estudiantes cuyo estado "
        "es desertor.",
    )
    df["cuartil_asistencia"] = pd.qcut(
        df["asistencia_pct"],
        q=4,
        labels=["Q1 (baja)", "Q2", "Q3", "Q4 (alta)"],
    )
    registrar(
        "variables nuevas",
        "cuartil_asistencia",
        "crear cuatro grupos de igual tamaño con qcut",
        int(df["asistencia_pct"].notna().sum()),
        "Los cuartiles facilitan comparar grupos de tamaño parecido sin depender "
        "de cada valor exacto de asistencia.",
    )
    return df


def mostrar_grafico():
    if plt.get_backend().lower() != "agg":
        plt.show()


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original.

    Pista: sns.heatmap(df.isnull(), cbar=False)
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False, ax=ax)
    ax.set_title("Mapa de faltantes del dataset original")
    ax.set_xlabel("Columnas")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "mapa_faltantes.png", dpi=150)
    mostrar_grafico()
    plt.close(fig)


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar.

    Pregunta: ¿qué cambió en cada distribución? ¿Por qué?
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    sns.boxplot(y=antes["promedio_acumulado"], ax=axes[0, 0])
    axes[0, 0].set_title("Promedio acumulado antes")
    sns.boxplot(y=despues["promedio_acumulado"], ax=axes[0, 1])
    axes[0, 1].set_title("Promedio acumulado después")
    sns.boxplot(y=antes["edad"], ax=axes[1, 0])
    axes[1, 0].set_title("Edad antes")
    sns.boxplot(y=despues["edad"], ax=axes[1, 1])
    axes[1, 1].set_title("Edad después")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "distribuciones_antes_despues.png", dpi=150)
    mostrar_grafico()
    plt.close(fig)


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa.

    Pista: df.groupby("programa")["desertor"].mean()
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    tasa = df.groupby("programa", observed=True)["desertor"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(x=tasa.values, y=tasa.index, ax=ax, color="steelblue")
    ax.set_title("Tasa de deserción por programa")
    ax.set_xlabel("Proporción de estudiantes desertores")
    ax.set_ylabel("Programa")
    ax.set_xlim(0, 1)
    fig.tight_layout()
    fig.savefig(GRAFICOS / "tasa_desercion_por_programa.png", dpi=150)
    mostrar_grafico()
    plt.close(fig)


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia.

    Pista: df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    tasa = df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=tasa.index, y=tasa.values, ax=ax, color="darkorange")
    ax.set_title("Tasa de deserción por cuartil de asistencia")
    ax.set_xlabel("Cuartil de asistencia")
    ax.set_ylabel("Proporción de estudiantes desertores")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(GRAFICOS / "tasa_desercion_por_asistencia.png", dpi=150)
    mostrar_grafico()
    plt.close(fig)


def responder_preguntas(df):
    """Paso 10 del Word: las cinco preguntas de la institución.

    Cada pregunta debe imprimir el resultado con el número de estudiantes por grupo.
    Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
    Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
    Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
    Pregunta 4: ¿Cuántas materias reprobadas tienen en promedio los desertores frente a los activos?
                (Excluye a los graduados.)
    Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
                (Usa cuartil_asistencia.)
    """
    print("\n=== Respuestas a las preguntas ===")
    por_programa = (
        df.groupby("programa", observed=True)
        .agg(tasa_desercion=("desertor", "mean"), estudiantes=("desertor", "size"))
        .sort_values("tasa_desercion", ascending=False)
    )
    print("\n1. Tasa de deserción por programa (tasa y estudiantes):")
    print(por_programa.to_string(float_format=lambda valor: f"{valor:.3f}"))

    por_beca = (
        df.groupby("beca", observed=True)
        .agg(tasa_desercion=("desertor", "mean"), estudiantes=("desertor", "size"))
        .sort_values("tasa_desercion", ascending=False)
    )
    print("\n2. Tasa de deserción por beca (tasa y estudiantes):")
    print(por_beca.to_string(float_format=lambda valor: f"{valor:.3f}"))

    por_jornada = (
        df.groupby("jornada", observed=True)
        .agg(promedio=("promedio_acumulado", "mean"), estudiantes=("id_estudiante", "size"))
        .sort_values("promedio")
    )
    print("\n3. Promedio acumulado por jornada (promedio y estudiantes):")
    print(por_jornada.to_string(float_format=lambda valor: f"{valor:.3f}"))

    por_estado = (
        df.loc[df["estado"].isin(["desertor", "activo"])]
        .groupby("estado", observed=True)
        .agg(
            promedio_materias_reprobadas=("materias_reprobadas", "mean"),
            estudiantes=("id_estudiante", "size"),
        )
    )
    print("\n4. Materias reprobadas en promedio (graduados excluidos):")
    print(por_estado.to_string(float_format=lambda valor: f"{valor:.3f}"))

    por_asistencia = (
        df.groupby("cuartil_asistencia", observed=True)
        .agg(
            tasa_desercion=("desertor", "mean"),
            asistencia_promedio=("asistencia_pct", "mean"),
            estudiantes=("desertor", "size"),
        )
    )
    print("\n5. Deserción por cuartil de asistencia:")
    print(por_asistencia.to_string(float_format=lambda valor: f"{valor:.3f}"))


def guardar(df):
    """Paso 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)


if __name__ == "__main__":
    main()
