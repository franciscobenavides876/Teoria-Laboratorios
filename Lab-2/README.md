# Laboratorio 2 – Expresiones Regulares con JFLAP

**Asignatura:** Teoría de la Computación – INFO1148
**Herramienta:** [JFLAP](https://www.jflap.org/)
**Tema:** Expresiones regulares, AFN y AFD
**Puntaje:** 100 puntos
**Modalidad:** Trabajo práctico de laboratorio de parejas

Esta carpeta (`Lab-2/`) es el área de trabajo del laboratorio. Aquí se guardan los
archivos `.jff` generados en JFLAP, las capturas y el informe final.

## Estructura

```
Lab-2/
├── README.md              ← este archivo (plan de trabajo)
├── capturas/              ← capturas legibles de JFLAP (AFN, AFD, expresiones)
├── P1_AFN.jff             ← Pregunta 1: AFN de (0+1)*01
├── P2_AFN.jff             ← Pregunta 2: AFN de L₂ (comienza con a, termina con b)
├── P3_AFN.jff             ← Pregunta 3: AFN de L₃ (contiene la subcadena 101)
├── P3_AFD.jff             ← Pregunta 3: AFD obtenido del AFN
├── P4_AFN.jff             ← Pregunta 4: AFN (al menos una a y termina en bb)
├── P4_AFD.jff             ← Pregunta 4: AFD obtenido del AFN
└── Lab02_jefe_nombre_apellido.pdf   ← informe final
```

## Entrega

- Informe en formato PDF con el desarrollo de las cuatro preguntas, tablas,
  explicaciones y capturas de JFLAP.
- Archivos `.jff` correspondientes a los autómatas generados (deben abrir
  correctamente y corresponder con los autómatas del informe).
- En anexos: el enlace al GitHub/Drive con acceso habilitado.
- Nombre del informe: `Lab02_jefe_nombre_apellido.pdf`.

## Reglas de JFLAP a recordar

- Unión: `+` (no `|`).
- Cerradura de Kleene: `*`.
- Las ER deben diseñarse por nosotros y escritas con sintaxis compatible con JFLAP.
- Antes de ejecutar una cadena en JFLAP, indicar la predicción esperada.
- Cada captura debe acompañarse de una breve explicación (no solo capturas).

## Actividades

### Pregunta 1 – Interpretación y validación de una ER (20 pts)
- Alfabeto `Σ = {0, 1}`, ER: `(0+1)*01`
- Explicar el lenguaje, convertir ER → AFN en JFLAP.
- Predecir y luego ejecutar: `01, 101, 1101, 0001, 10, 111, 0100, 10101`.
- Explicar por qué `1101` se acepta y `0100` se rechaza.

### Pregunta 2 – Diseño de una ER (25 pts)
- `L₂ = { w ∈ {a,b}* | w comienza con a y termina con b }`
- Diseñar la ER sin JFLAP, justificar cada parte, convertir a AFN.
- Probar ≥ 10 cadenas (aceptadas, rechazadas, longitud mínima y 2 casos límite).

### Pregunta 3 – Conversión ER → AFN → AFD (25 pts)
- `L₃ = { w ∈ {0,1}* | w contiene la subcadena 101 }`
- Diseñar la ER, ER → AFN → AFD.
- Registrar: nº de estados, nº de transiciones, presencia de transiciones λ,
  determinismo.
- Ejecutar en ambos: `101, 0101, 1010, 11011, 000, 111, 1001, 1101010`.
- Responder si AFN y AFD reconocen lenguajes diferentes (justificar).

### Pregunta 4 – Diseño y validación (25 pts)
- `Σ = {a, b}`: cadenas que contienen al menos una `a` Y terminan en `bb`.
  - Aceptados: `abb, aabb, babbb, ababbb` / Rechazados: `bb, aaa, aba, baba`
- Diseñar la ER, explicar la estrategia, ER → AFN → AFD.
- Probar ≥ 12 cadenas (5 aceptadas, 5 rechazadas, 2 casos límite).
- Tabla comparativa: esperado vs AFN vs AFD.
- Reflexión (máx. 150 palabras): ¿ER, AFN y AFD tienen distinta capacidad de
  reconocimiento o son formas distintas de representar la misma clase de lenguajes?

## Checklist de avance

- [ ] P1: ER explicada + AFN + predicciones/verificación + captura
- [ ] P2: ER diseñada + justificación + AFN + ≥10 pruebas + captura
- [ ] P3: ER + AFN + AFD + tabla de características + ≥8 pruebas + capturas
- [ ] P4: ER + AFN + AFD + ≥12 pruebas + reflexión + capturas
- [ ] Archivos `.jff` con los nombres indicados
- [ ] Informe PDF `Lab02_jefe_nombre_apellido.pdf`
- [ ] Enlace en anexos con acceso habilitado
