# Taller práctico proyecto integrador: calidad de datos para la retención estudiantil

Una institución de educación superior quiere entender qué factores están asociados a la deserción, para diseñar estrategias de retención tempranas. Antes de responder preguntas de análisis, el equipo de datos debe garantizar que la información sea confiable. Este taller trabaja justo ese paso: auditar, limpiar y documentar los datos, y después responder cinco preguntas con esos datos limpios.

Los datos son sintéticos. Fueron generados para el taller y no corresponden a estudiantes reales.

## Requisitos

- Python 3.10 o superior
- Git
- Lo visto en los talleres de Pandas y de limpieza de datos

## Cómo empezar

1. Clona el repositorio y entra a la carpeta del proyecto:

   ```
   git clone <URL-DEL-REPOSITORIO>
   cd <NOMBRE-DE-LA-CARPETA>
   ```

2. Crea y activa un ambiente virtual. Las instrucciones para Windows y Mac/Linux están en `LEEME_ambiente.txt`.

3. Instala las librerías:

   ```
   pip install -r requirements.txt
   ```

4. Ejecuta el script:

   ```
   python analisis_desercion.py
   ```

Ejecuta el comando desde la carpeta del proyecto.

## Estructura del proyecto

```
proyecto/
├── analisis_desercion.py   Script principal de auditoría, limpieza y análisis.
├── requirements.txt        Versiones de las librerías.
├── LEEME_ambiente.txt      Pasos para crear el ambiente virtual.
├── README.md               Este archivo.
├── .gitignore              Archivos que Git no debe subir.
└── Data/
    ├── raw/
    │   └── datos_estudiantes.csv   Dataset original. No lo modifiques.
    └── processed/
        ├── .gitkeep                Mantiene la carpeta en el repositorio.
        ├── dataset_limpio.csv      Lo genera el script. No se sube (está en .gitignore).
        ├── decisiones.csv          Lo genera el script. Sí se sube.
        └── graficos/               Lo genera el script. Sí se sube.
```

Lo que genera el script (`dataset_limpio.csv`, `decisiones.csv` y `graficos/`) aparece en `Data/processed/` al ejecutarlo. Los dos últimos se suben al repositorio, porque son parte de la entrega.

## Ejecución y resultados

El script completa los pasos del taller y registra cada decisión de limpieza con `registrar()`. Ejecútalo desde la carpeta del proyecto para regenerar los resultados:

Cuando termines, el script debe producir:

- `Data/processed/dataset_limpio.csv`: el dataset limpio.
- `Data/processed/decisiones.csv`: la tabla de decisiones.
- `Data/processed/graficos/`: los cuatro gráficos.

La guía del taller (`Taller_Retencion_Estudiantil.pdf`) explica cada método antes de usarlo, con ejemplos y errores frecuentes.

## Entrega

Sube tu código completo al repositorio y envía el enlace por el formulario de entrega. La entrega es individual.

El repositorio debe incluir:

- `analisis_desercion.py` con todos los TODO completados.
- `Data/processed/decisiones.csv` y la carpeta `Data/processed/graficos/`.
- Un `README.md` al final de este archivo, con una sección titulada **Mis decisiones y respuestas**. Debe incluir:
  0. El diccionario de datos: la tabla de las 23 columnas con tipo, descripción y rol, completada según el paso 1 de la guía.
  1. Tu diagnóstico de calidad: qué problemas encontraste y en qué columnas.
  2. Tus decisiones de limpieza, con su justificación.
  3. Las respuestas a las cinco preguntas, cada una con el número de estudiantes por grupo.
  4. Tu respuesta a la reflexión sobre asociación y causalidad.
  5. Tu respuesta a la reflexión sobre `motivo_retiro` y la predicción.
  6. Tu respuesta a la reflexión sobre el uso de variables sensibles.

El script debe ejecutarse sin errores desde cero. Cada decisión necesita una justificación, y cada conclusión debe apoyarse en un número del análisis.

## Mis decisiones y respuestas

### 0. Diccionario de datos

| Columna | Tipo | Descripción | Rol |
|---|---|---|---|
| `id_estudiante` | Texto | Código único para identificar cada registro de estudiante. | Identificación |
| `programa` | Categórica | Programa académico en el que está matriculado el estudiante. | Explicativa |
| `facultad` | Categórica | Facultad a la que pertenece el programa. | Explicativa |
| `jornada` | Categórica | Horario de estudio: diurna, nocturna o fin de semana. | Explicativa |
| `semestre` | Categórica ordinal | Semestre académico que cursa (1 a 10). | Explicativa |
| `promedio_acumulado` | Numérica | Promedio académico acumulado, en escala de 0 a 5. | Explicativa |
| `creditos_aprobados` | Numérica | Total de créditos aprobados por el estudiante. | Explicativa |
| `materias_reprobadas` | Numérica | Número de materias reprobadas. | Explicativa |
| `asistencia_pct` | Numérica | Porcentaje de asistencia a las actividades académicas. | Explicativa |
| `sesiones_tutoria` | Numérica | Número de sesiones de tutoría recibidas. | Explicativa |
| `cambios_programa` | Numérica | Indicador (0/1) de si el estudiante cambió de programa. | Explicativa |
| `estrato` | Categórica ordinal | Estrato socioeconómico registrado (1 a 6). | Explicativa |
| `beca` | Categórica | Indica si el estudiante recibe una beca. | Explicativa |
| `trabaja` | Categórica | Indica si el estudiante trabaja. | Explicativa |
| `horas_trabajo_semana` | Numérica | Horas de trabajo del estudiante por semana. | Explicativa |
| `distancia_km` | Numérica | Distancia entre el lugar de procedencia y la institución, en kilómetros. | Explicativa |
| `edad` | Numérica | Edad del estudiante en años. | Explicativa |
| `genero` | Categórica | Género reportado por el estudiante. | Explicativa |
| `ciudad_procedencia` | Categórica | Ciudad de procedencia del estudiante. | Explicativa |
| `tipo_colegio` | Categórica | Tipo de colegio de procedencia: público o privado. | Explicativa |
| `fecha_matricula` | Fecha | Fecha en que se registró la matrícula. | Explicativa |
| `estado` | Categórica | Situación académica: activo, graduado o desertor. | Resultado |
| `motivo_retiro` | Categórica | Motivo reportado cuando el estudiante se retiró; solo se conoce después de la deserción. | Resultado posterior |

### 1. Diagnóstico de calidad

El archivo original contiene 10.150 filas y 23 columnas; hay 10.000 identificadores únicos.

| Problema | Columnas y cantidad observada |
|---|---|
| Nulos reales | `promedio_acumulado`: 304; `distancia_km`: 199; `ciudad_procedencia`: 103; `tipo_colegio`: 152; `motivo_retiro`: 6.877. |
| Faltantes disfrazados | `asistencia_pct`: 202 guiones y 300 valores con `%`; `horas_trabajo_semana`: 2.822 guiones; `distancia_km`: 152 valores `999`. |
| Valores fuera de rango | `edad`: 12 (4 menores de 15 y 8 de 150 años); `promedio_acumulado`: 17 mayores a 5 (1 valor 45, 10 valores 62 y 6 valores 78); `horas_trabajo_semana`: 30 valores de 200 horas. |
| Duplicados | 150 filas idénticas, con IDs repetidos. |
| Variantes de escritura | `programa`: 260; `jornada`: 485; `genero`: 559; `ciudad_procedencia`: 542. |
| Formato mixto | `fecha_matricula`: 7.098 fechas AAAA-MM-DD y 3.052 fechas DD/MM/AAAA. |

Los 6.877 nulos de `motivo_retiro` son esperados porque la variable solo aplica a quienes desertaron. Los demás nulos afectan 304 notas, 199 distancias, 103 ciudades y 152 tipos de colegio; la limpieza registra también los faltantes marcados con guion o `999`.

### 2. Decisiones de limpieza

Todas las acciones, cantidades afectadas y justificaciones quedan registradas en `Data/processed/decisiones.csv`.

| Decisión | Filas afectadas | Justificación |
|---|---:|---|
| Convertir asistencia, horas laborales y distancia a número; tratar `-`, `%` y `999` según su significado. | 502, 2.822 y 152, respectivamente. | Permite calcular estadísticas con números y convertir los códigos de falta en nulos reales. |
| Unificar variantes de programa, jornada, género y ciudad. | 260, 485, 559 y 542, respectivamente. | Espacios, mayúsculas, abreviaturas y tildes distintas representaban categorías ya existentes. |
| Convertir fechas usando ambos formatos explícitos. | 3.052 en formato DD/MM/AAAA. | Evita interpretar el día como mes y permite tener una única columna de fechas. |
| Eliminar filas duplicadas y reiniciar el índice. | 150. | Las filas repetían el mismo ID y todos sus datos; contarlas duplicaría estudiantes. |
| Eliminar filas sin promedio; completar ciudad y tipo de colegio con «Sin dato». | 298; 96; 145. | No se inventan notas; las categorías desconocidas se conservan sin atribuirles un valor. |
| Conservar como nulos asistencia, distancia y motivo de retiro, sin imputar. | 197; 334; 6.562. | Son mediciones desconocidas o, en el caso de `motivo_retiro`, un dato que no aplica a quienes no desertaron. |
| Reemplazar edades fuera de 15–60 por la mediana de edades válidas (22). | 12. | Corrige extremos imposibles sin descartar los registros. |
| Eliminar filas con notas mayores a 5, después de marcarlas como faltantes. | 15. | La escala del promedio es 0–5 y no hay información para reconstruir las notas. |
| Asignar 0 horas a quienes no trabajan; reemplazar horas mayores a 100 por la mediana de quienes sí trabajan (24). | 2.703; 29. | Las horas de no trabajadores son cero; valores extremos no se toman como reales. |
| Crear el indicador `desertor` y los cuartiles de asistencia. | 9.687 filas; 9.490 asistencias válidas. | La variable booleana permite calcular tasas y los cuartiles comparan grupos de tamaño parecido. |

Después de limpiar quedan 9.687 filas y 25 columnas (las 23 originales y las variables `desertor` y `cuartil_asistencia`). Las asistencias con guion y las distancias faltantes se mantienen como nulos: quedan 197 y 333, respectivamente. Los cálculos por asistencia excluyen sus 197 faltantes. Los 6.551 nulos de `motivo_retiro` también se conservan porque son estructurales. Las cantidades de la decisión de conservar nulos se registraron antes de retirar las 15 notas imposibles.

### 3. Respuestas a las cinco preguntas

Las tasas son proporciones dentro de cada grupo. Se reportan también los tamaños de grupo para contextualizarlas.

**1. ¿Qué programa presenta la tasa de deserción más alta?**

| Programa | Tasa de deserción | Estudiantes |
|---|---:|---:|
| Ingeniería Industrial | 40,2 % | 1.271 |
| Ingeniería de Sistemas | 38,2 % | 1.386 |
| Diseño Gráfico | 35,6 % | 848 |
| Enfermería | 31,3 % | 1.132 |
| Derecho | 30,5 % | 1.447 |
| Administración de Empresas | 29,7 % | 1.304 |
| Contaduría Pública | 27,0 % | 1.162 |
| Psicología | 26,0 % | 1.137 |

Ingeniería Industrial tiene la tasa más alta: 40,2 % de sus 1.271 estudiantes.

**2. ¿Hay diferencia entre becados y no becados?**

| Beca | Tasa de deserción | Estudiantes |
|---|---:|---:|
| No | 36,4 % | 7.004 |
| Sí | 21,9 % | 2.683 |

En estos datos, la tasa de deserción es 14,5 puntos porcentuales menor entre quienes reciben beca.

**3. ¿Qué jornada tiene el menor promedio acumulado?**

| Jornada | Promedio acumulado | Estudiantes |
|---|---:|---:|
| Nocturna | 3,464 | 2.666 |
| Fin de semana | 3,704 | 949 |
| Diurna | 3,725 | 6.072 |

La jornada nocturna presenta el promedio más bajo.

**4. ¿Cuántas materias reprobadas tienen en promedio desertores y activos?**

| Estado | Promedio de materias reprobadas | Estudiantes |
|---|---:|---:|
| Desertor | 3,066 | 3.136 |
| Activo | 0,623 | 5.692 |

Se excluyeron los 859 graduados porque no pertenecen a los grupos comparados.

**5. ¿Aumenta la deserción conforme baja la asistencia?**

| Cuartil de asistencia | Asistencia promedio | Tasa de deserción | Estudiantes |
|---|---:|---:|---:|
| Q1 (baja) | 73,905 % | 61,9 % | 2.385 |
| Q2 | 84,406 % | 36,7 % | 2.386 |
| Q3 | 91,336 % | 20,7 % | 2.348 |
| Q4 (alta) | 98,660 % | 9,4 % | 2.371 |

La asociación es monotónica en estos grupos: la tasa observada baja de 61,9 % en Q1 a 9,4 % en Q4. No demuestra que la asistencia por sí sola cause permanencia.

### 4. Reflexión: asociación y causalidad

La diferencia observada entre becados (21,9 %, 2.683 estudiantes) y no becados (36,4 %, 7.004) muestra asociación, no prueba que la beca cause permanencia. Las personas becadas pueden diferir en necesidad económica, rendimiento, criterios de selección, apoyo familiar u otras variables que también se relacionan con continuar estudiando. Para estimar un efecto causal se necesitaría un diseño que haga comparables los grupos (por ejemplo, asignación aleatoria o un estudio cuasiexperimental) y controlar factores de confusión.

### 5. Reflexión: `motivo_retiro` y predicción

`motivo_retiro` no debe usarse para predecir la deserción antes de que ocurra: es información posterior al resultado y solo está registrada para desertores. Usarla causaría fuga de información y daría una evaluación engañosamente optimista. También deben revisarse `estado` y otras variables posteriores al evento o medidas después del momento en que se haría la predicción, como cambios de programa, materias reprobadas o asistencia, según su fecha de medición. La selección de predictores debe fijar primero el momento real de predicción.

### 6. Reflexión: variables sensibles

Una asociación con género, estrato o ciudad no justifica por sí sola decidir quién recibe apoyo. Usarlas como criterio de asignación puede reproducir o agravar desigualdades, discriminar grupos y afectar la confianza. La institución debería priorizar indicadores de necesidad y ofrecer apoyo con criterios transparentes; evaluar equidad por grupo, minimizar datos sensibles y limitar su uso a auditorías de sesgo con controles de privacidad y supervisión humana.
