# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 09:55:46 2018

@author: Team REOS
Modulo que contiene las funciones necesarias para realizar una aproximación
polinómica y el cálculo de la regresión lineal de la aproximación.
"""
from numpy import transpose, zeros, matmul, array, size, dot
from numpy.linalg import cholesky, inv

def aprox_pol(x, y, k):
    """
    Realiza una aproximación por minimos cuadrados y devuelve el vector
    de coeficientes de un polinomio del grado requerido. Donde:
    x es el array de la variable independiente
    y es el array de la variable dependiente
    k es el grado del polinomio
    Así pues obtenemos un polinomio:
        p(x) = c0 + c1·x + c2·x**2 + c3·x**3 + c4·x**4 + ···
    La función devuelve el vector de coeficientes c (array).
    """
    # Entramos con listas y las convertimos en arrays
    x = array(x)
    y = array(y)

    n = size(x)
    M = zeros((n, k + 1))

    # Calculamos la matriz M
    for i in range(n):
        for j in range(k + 1):
            M[i, j] = x[i]**j

    Mt = transpose(M)  # Matriz traspuesta de M
    A = matmul(Mt, M)
    L = cholesky(A)  # Factorización de cholesky
    b = matmul(Mt, y)
    L_inv = inv(L)  # Invertimos la matriz
    y_sol = matmul(L_inv, b)
    Lt = transpose(L)
    Lt_inv = inv(Lt)
    c = matmul(Lt_inv, y_sol)  # Matriz de coeficientes del polinomio

    return c


def coef_det(y_r, y_a, y_m):
    """
    Cálculo del coeficiente de determinación (R**2) que resulta de utilizar el
    polinomio aproximado.
    y_m = lista del valor medio (con datos reales),
          mismo tamaño que y_1 y que y_2
    y_r = valores obtenidos interpolando (reales)
    y_a = valores obtenidos con el polinomio (aproximadas)
    """
    y_r = array(y_r)
    y_a = array(y_a)
    y_m = array(y_m)
    r_1 = y_a - y_r  # Error residual
    r_2 = y_a - y_m  # Variación de regresion
    R_2 = (dot(r_2, r_2))/(dot(r_1, r_1) + dot(r_2, r_2))  # Coef. determ.

    return R_2