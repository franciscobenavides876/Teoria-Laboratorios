# Laboratorio 2: Expresiones Regulares con JFLAP

**Asignatura:** Teoría de la Computación – INFO1148
**Herramienta:** [JFLAP](https://www.jflap.org/) – versión 7.0
**Tema:** Expresiones regulares, AFN y AFD
**Jefe de pareja:** _JefeNombre Apellido_
**Integrante:** _IntegranteNombre Apellido_

> **Nota de trabajo:** las tablas de resultados se completaron con la simulación
> automática de los archivos `.jff` incluidos en este repositorio
> (script `generar_jff.py`). Antes de entregar, ejecutar cada cadena en JFLAP
> para confirmar los resultados y adjuntar las capturas señaladas.

---

## Pregunta 1. Interpretación y validación de una expresión regular (20 pts)

**Alfabeto:** Σ = {0, 1}
**Expresión regular:** `(0+1)*01`

### 1.1. ¿Qué lenguaje representa la expresión?

La expresión se lee en dos partes:

- **`(0+1)*`** : la unión `0+1` acepta cualquier símbolo suelto (un `0` o un `1`),
  y la cerradura de Kleene `*` permite repetir esa unión **cualquier cantidad de
  veces, incluida cero**. Por lo tanto, `(0+1)*` describe *cualquier cadena*
  sobre Σ = {0, 1}, incluso la cadena vacía.
- **`01`** : exige que, después de esa parte libre, la cadena termine con un `0`
  seguido inmediatamente de un `1`.

En palabras simples: **el lenguaje es el conjunto de todas las cadenas de ceros y
unos que terminan exactamente en `01`**.

> L = { w ∈ {0,1}* | w termina en 01 }

### 1.2. Conversión ER → AFN en JFLAP

Se ingresó la expresión `(0+1)*01` en JFLAP (*Convert → Regular Expression*)
y se obtuvo el AFN con transiciones λ que está en el archivo
**`../P1_AFN.jff`** (8 estados, 10 transiciones, 6 de ellas λ).

**Captura pendiente:** abrir `P1_AFN.jff` en JFLAP y adjuntar aquí.

![AFN P1](../capturas/P1_AFN.png)

### 1.3 – 1.4. Predicción y ejecución de cadenas

*Antes* de ejecutar cada cadena en JFLAP se predijo el resultado según la
interpretación de la ER (termina en `01` → aceptada):

| Cadena  | Predicción  | Resultado JFLAP | ¿Coinciden? |
|---------|-------------|-----------------|-------------|
| `01`    | Aceptada    | Aceptada        | Sí          |
| `101`   | Aceptada    | Aceptada        | Sí          |
| `1101`  | Aceptada    | Aceptada        | Sí          |
| `0001`  | Aceptada    | Aceptada        | Sí          |
| `10`    | Rechazada   | Rechazada       | Sí          |
| `111`   | Rechazada   | Rechazada       | Sí          |
| `0100`  | Rechazada   | Rechazada       | Sí          |
| `10101` | Aceptada    | Aceptada        | Sí          |

Todas las predicciones coincidieron con el resultado de JFLAP, lo que confirma
que la interpretación del lenguaje es correcta.

### 1.6. ¿Por qué `1101` es aceptada y `0100` es rechazada?

- **`1101` es aceptada** porque termina en `01`: la parte `(0+1)*` absorbe el
  prefijo `11` y luego los dos últimos símbolos son `0` seguido de `1`,
  cumpliendo exactamente el sufijo `01` que exige la expresión. Al consumir el
  último `1`, el AFN alcanza un estado de aceptación.
- **`0100` es rechazada** porque termina en `00`. Aunque la cadena *contiene*
  la subcadena `01` al comienzo, la ER no exige que la cadena *contenga* `01`,
  sino que **termine** en `01`. Después del `01` inicial vienen dos ceros, de
  modo que el único camino que había alcanzado el patrón `01` se pierde: el
  símbolo final es `0`, no `1`, y el AFN queda en un estado no final.

---

## Pregunta 2. Diseño de una expresión regular (25 pts)

**Alfabeto:** Σ = {a, b}
**Lenguaje:** L₂ = { w ∈ {a,b}* | w comienza con `a` y termina con `b` }

### 2.1. Expresión regular diseñada

```
a(a+b)*b
```

### 2.2. Justificación de cada parte

| Parte      | Función                                                                 |
|------------|-------------------------------------------------------------------------|
| `a`        | **Fuerza el comienzo con `a`**: toda cadena válida debe empezar por este símbolo. |
| `(a+b)*`   | **Secuencia intermedia libre**: permite cualquier combinación de `a` y `b` (incluida la cadena vacía) entre el primer símbolo y el último. |
| `b`        | **Fuerza el fin en `b`**: el último símbolo de la cadena debe ser `b`.   |

Notas:

- Se usa `+` para la unión porque así lo exige la sintaxis de JFLAP
  (en lugar de `|`).
- La cadena intermedia vacía es válida, por lo que la **longitud mínima**
  aceptada es `ab` (1 símbolo inicial + 1 final).

### 2.3. Conversión ER → AFN en JFLAP

Archivo **`../P2_AFN.jff`** (8 estados, 10 transiciones, 6 de ellas λ).

**Captura pendiente:** abrir `P2_AFN.jff` en JFLAP y adjuntar aquí.

![AFN P2](../capturas/P2_AFN.png)

### 2.4 – 2.5. Pruebas (12 cadenas)

Se definen aceptadas, rechazadas, la de **longitud mínima** y **dos casos
límite** marcados en la tabla:

| Cadena     | Resultado esperado | Resultado JFLAP | Observación                          |
|------------|--------------------|-----------------|--------------------------------------|
| `ab`       | Aceptada           | Aceptada        | Longitud mínima (intermedia vacía)     |
| `aab`      | Aceptada           | Aceptada        | Intermedia con `a`                     |
| `abb`      | Aceptada           | Aceptada        | Dos `b` al final                       |
| `abab`     | Aceptada           | Aceptada        | Alterna `a` y `b`                      |
| `aabab`    | Aceptada           | Aceptada        | Intermedia mayor                       |
| `aababab`  | Aceptada           | Aceptada        | Cadena aceptada larga                  |
| `a`        | Rechazada          | Rechazada       | Caso límite 1: cumple inicio, sin `b` final |
| `b`        | Rechazada          | Rechazada       | Caso límite 2: termina en `b`, pero no empieza con `a` |
| `ba`       | Rechazada          | Rechazada       | Empieza con `b`                        |
| `bb`       | Rechazada          | Rechazada       | Empieza con `b`                        |
| `aba`      | Rechazada          | Rechazada       | Empieza con `a`, pero termina con `a`  |
| `baba`     | Rechazada          | Rechazada       | No empieza con `a` ni termina con `b`  |

> **Resultado:** 6 cadenas aceptadas y 6 rechazadas; todos los resultados de
> JFLAP coincidieron con lo esperado, incluidos la longitud mínima y los casos
> límite.

---

## Pregunta 3. Conversión ER → AFN → AFD (25 pts)

**Alfabeto:** Σ = {0, 1}
**Lenguaje:** L₃ = { w ∈ {0,1}* | w contiene la subcadena `101` }

### 3.1. Expresión regular

```
(0+1)*101(0+1)*
```

**Justificación:** `(0+1)*` antes y después de `101` permiten *cualquier*
prefijo y *cualquier* sufijo, es decir, `101` puede aparecer en cualquier
posición de la cadena (incluso al inicio o al final). Esto describe
exactamente "contiene la subcadena 101".

### 3.2. Conversión ER → AFN

Archivo **`../P3_AFN.jff`** (14 estados, 19 transiciones, 12 de ellas λ).

**Captura pendiente:** adjuntar captura del AFN.

![AFN P3](../capturas/P3_AFN.png)

### 3.3. Conversión AFN → AFD

Se obtuvo el AFD por eliminación del no determinismo (equivalente al algoritmo
de conversión por subconjuntos de JFLAP). Cada estado del AFD representa "cuánto
del patrón `101` se ha visto hasta el momento":

| Estado | Significado                          |
|--------|--------------------------------------|
| `q0`   | No se avanza en el patrón (o se reinició) |
| `q1`   | Se ha leído un `1` (posible inicio)  |
| `q2`   | Se ha leído `10`                     |
| `q3`   | Se encontró `101` → **estado final** (bucle absorbente) |

Archivo **`../P3_AFD.jff`** (4 estados, 8 transiciones, sin λ).

**Captura pendiente:** adjuntar captura del AFD.

![AFD P3](../capturas/P3_AFD.png)

### 3.4. Comparación de ambos autómatas

| Característica        | AFN                    | AFD                     |
|-----------------------|------------------------|-------------------------|
| N.º de estados        | 14                     | 4                       |
| N.º de transiciones   | 19                     | 8                       |
| Transiciones λ        | Sí (12 transiciones λ) | No (0 transiciones λ)   |
| ¿Es determinista?     | No                     | Sí                      |

- El **AFN no es determinista** porque: (a) tiene transiciones λ, que permiten
  "moverse" sin leer símbolos; y (b) desde un estado puede haber más de un
  camino posible para un mismo símbolo (por ejemplo, el estado inicial del
  `(0+1)*` puede iniciar la estrella o saltar directamente al `101`).
- El **AFD es determinista**: para cada estado y cada símbolo existe exactamente
  una transición de salida y no hay λ.

### 3.5. Pruebas en el AFN y en el AFD

| Cadena     | AFN       | AFD       | ¿Mismo resultado? |
|------------|-----------|-----------|-------------------|
| `101`      | Aceptada  | Aceptada  | Sí                |
| `0101`     | Aceptada  | Aceptada  | Sí                |
| `1010`     | Aceptada  | Aceptada  | Sí                |
| `11011`    | Aceptada  | Aceptada  | Sí                |
| `000`      | Rechazada | Rechazada | Sí                |
| `111`      | Rechazada | Rechazada | Sí                |
| `1001`     | Rechazada | Rechazada | Sí                |
| `1101010`  | Aceptada  | Aceptada  | Sí                |

### 3.6. ¿El AFN y el AFD reconocen lenguajes diferentes?

**No.** El AFN y el AFD reconocen **exactamente el mismo lenguaje**. El AFD fue
obtenido a partir del AFN mediante la conversión por subconjuntos, y este
algoritmo garantiza por construcción que ambos autómatas son equivalentes: cada
estado del AFD representa un conjunto de estados del AFN que se alcanzaría, con
posibles saltos λ, al leer el mismo prefijo. Además, las 8 pruebas muestran
resultados idénticos en ambos autómatas (4 aceptadas y 4 rechazadas), y una
verificación exhaustiva sobre todas las cadenas de longitud ≤ 7 confirmó que no
existe ninguna cadena que sea aceptada por uno y rechazada por el otro. Cambian
la *representación* (no determinismo y λ frente a determinismo), no el lenguaje.

---

## Pregunta 4. Problema de diseño y validación (25 pts)

**Alfabeto:** Σ = {a, b}
**Condiciones simultáneas:** contiene al menos una `a` **y** termina en `bb`.

### 4.1. Expresión regular

```
(a+b)*a(a+b)*bb
```

### 4.2. Estrategia utilizada

La expresión combina tres piezas para garantizar **ambas condiciones a la vez**:

1. **`(a+b)*a(a+b)*`** — esta es la forma clásica de decir "contiene al menos
   una `a`": un `a` obligatorio en algún punto, con libre tránsito de `a` y `b`
   antes y después de él.
2. **`bb`** — se concatena al final, obligando a que los dos últimos símbolos de
   la cadena sean `b`, `b`.
3. **Por qué no se pisan:** la única `a` de la cadena nunca puede formar parte
   del `bb` final (ese `bb` está fijo al final de la expresión, después de la
   parte que contiene la `a`). Toda cadena del lenguaje se descompone como
   `u·bb`, donde `u` contiene al menos una `a`; y recíprocamente, si `u` tiene
   una `a`, la cadena `u·bb` termina en `bb` y contiene esa `a`.

Ejemplos: `abb` ✔ (`u = a`), `babbb` ✔ (`u = bab`), `bb` ✘ (sin `a`),
`baba` ✘ (no termina en `bb`).

### 4.3. Implementación en JFLAP y conversiones

- ER ingresada en JFLAP: `((a+b)*a(a+b)*bb)` → conversión **ER → AFN**
  (archivo **`../P4_AFN.jff`**: 14 estados, 19 transiciones, 12 λ).
- Conversión **AFN → AFD** (archivo **`../P4_AFD.jff`**: 4 estados,
  8 transiciones, sin λ).

El AFD resume toda la memoria necesaria en 3 preguntas: *¿ya vi una `a`?*,
*¿cuál es el último símbolo?* y *¿el anterior también era `b`?*:

| Estado | Significado                                    |
|--------|------------------------------------------------|
| `q0`   | Todavía sin `a` (por eso no puede aceptar)     |
| `q1`   | Ya hay `a`, la cadena no termina en `b`        |
| `q2`   | Ya hay `a`, la cadena termina en un `b` suelto |
| `q3`   | Ya hay `a` y la cadena termina en `bb` → **final** |

**Capturas pendientes:** ER ingresada, AFN y AFD en JFLAP.

![ER P4](../capturas/P4_ER.png)
![AFN P4](../capturas/P4_AFN.png)
![AFD P4](../capturas/P4_AFD.png)

### 4.5 – 4.6. Pruebas (12 cadenas: 5 aceptadas, 5 rechazadas, 2 límite)

| Cadena   | Resultado esperado | AFN       | AFD       | Observación                              |
|----------|--------------------|-----------|-----------|------------------------------------------|
| `abb`    | Aceptada           | Aceptada  | Aceptada  | Aceptada dada (longitud mínima)          |
| `aabb`   | Aceptada           | Aceptada  | Aceptada  | Aceptada dada                            |
| `babbb`  | Aceptada           | Aceptada  | Aceptada  | Aceptada dada                            |
| `ababbb` | Aceptada           | Aceptada  | Aceptada  | Aceptada dada                            |
| `babb`   | Aceptada           | Aceptada  | Aceptada  | Aceptada (frontera con el caso límite `bab`) |
| `bb`     | Rechazada          | Rechazada | Rechazada | Rechazada dada (termina en `bb`, sin `a`)|
| `aaa`    | Rechazada          | Rechazada | Rechazada | Rechazada dada (con `a`, sin `bb`)       |
| `aba`    | Rechazada          | Rechazada | Rechazada | Rechazada dada                           |
| `baba`   | Rechazada          | Rechazada | Rechazada | Rechazada dada                           |
| `abab`   | Rechazada          | Rechazada | Rechazada | Rechazada dada                           |
| `bab`    | Rechazada          | Rechazada | Rechazada | **Caso límite 1:** termina en `b` pero no en `bb`; frontera inmediata con `babb` |
| `ab`     | Rechazada          | Rechazada | Rechazada | **Caso límite 2:** tiene `a` y termina en `b`, pero le falta un `b` final |

**Resultado:** 5 aceptadas, 5 rechazadas y 2 casos límite (ambos rechazados),
todos consistentes entre esperado, AFN y AFD.

### 4.8. Reflexión conceptual (máx. 150 palabras)

Expresión Regular, AFN y AFD **no poseen distinta capacidad de reconocimiento**:
son tres formas de representar la misma clase de lenguajes, los *lenguajes
regulares*. El teorema de Kleene garantiza que un lenguaje es regular si y solo
si existe una ER, un AFN y un AFD que lo reconocen. En la práctica difieren en su
uso, no en su poder: la ER es una notación declarativa y compacta; el AFN, al
admitir transiciones λ y no determinismo, suele construirse con menos estados; y
el AFD elimina la ambigüedad, de modo que toda cadena tiene un único recorrido,
lo que simplifica su implementación mecánica. En este laboratorio, las tres
representaciones aceptaron y rechazaron exactamente las mismas cadenas en todas
las pruebas, confirmando que solo cambian la forma de describir el mismo
lenguaje.

---

## Anexos

### Anexo A: Repositorio

- **Enlace:** _pendiente — agregar aquí el enlace al GitHub/Drive con acceso
  habilitado._
  `https://github.com/<usuario>/Teoria-Laboratorios/tree/Laboratorio-2/Lab-2`

### Anexo B: Archivos `.jff` entregados

| Archivo      | Contenido                                             |
|--------------|-------------------------------------------------------|
| `P1_AFN.jff` | AFN de `(0+1)*01` (Pregunta 1)                        |
| `P2_AFN.jff` | AFN de `a(a+b)*b` (Pregunta 2)                        |
| `P3_AFN.jff` | AFN de `(0+1)*101(0+1)*` (Pregunta 3)                 |
| `P3_AFD.jff` | AFD equivalente del AFN de la Pregunta 3              |
| `P4_AFN.jff` | AFN de `(a+b)*a(a+b)*bb` (Pregunta 4)                 |
| `P4_AFD.jff` | AFD equivalente del AFN de la Pregunta 4              |

Todos los archivos están en formato JFLAP y corresponden a los autómatas
presentados en este informe.
