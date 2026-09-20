% ============================================================
% ARCHIVO 2: FUENTE CON ERRORES RECUPERABLES (8 ERRORES)
% ============================================================

% 1 y 2. Caracteres no admitidos ($ y #)
$valor = 100 # falso;

% 3. Otro caracter no admitido (tilde de la ñ o backtick)
`variable_invalida = 50;

% 4. Caracter no admitido en operador (~ no es operador de Prolog estándar)
~negacion_erronea = 10;

% 5. Real mal formado (exponente sin digito)
constante(3.1416e-).

% 6. Cadena sin cierre
mensaje("Esta cadena no tiene comilla de cierre
padre(carlos, maria).

% 7. Atomo entrecomillado sin cierre
persona('Juan sin cierre
edad(carlos, 30).

% 8. Comentario de bloque sin cierre (al final para no tragarse el archivo)
/* Comentario abierto sin asterisco ni barra