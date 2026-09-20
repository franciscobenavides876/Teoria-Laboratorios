% ============================================================
% ARCHIVO 1: CODIGO FUENTE PROLOG SIN ERRORES
% ============================================================

% Base de hechos
padre(juan, ana).
padre(juan, pedro).
edad(juan, 45).
factor_escala(1.25e+2).

% Reglas logicas y operadores
abuelo(X, Z) :-
    padre(X, Y),
    padre(Y, Z).

% Operadores aritmeticos, unificacion y control
calcular(R, Limite) :-
    R is (10 // 2) ** 3,
    R =< Limite,
    \+ (R == 0),
    !.

% Literales de cadena y atomos especiales
configuracion('Ruta Principal', "C:\\archivos\\datos.txt").