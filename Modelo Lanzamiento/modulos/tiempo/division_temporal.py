# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 09:37:18 2018

@author: Team REOS

En éste módulo se calcula la división temporal del lanzamiento, en función del
instante inicial, los tiempos de retardos, masas y gastos de cada etapa.
"""

# ORGANIZACIÓN TEMPORAL DEL LANZAMIENTO.
# --------------------------------------

from inputs_iniciales import GASTOS, ESTRUCTURAS, MASAS
#from numpy import size

# Tiempos de combustión
T_COMBUSTION = []

for i, gas in enumerate(GASTOS):
    t_c = (1 - ESTRUCTURAS[i])*MASAS[i]/gas
    T_COMBUSTION.append(t_c)


# Tiempos característicos de lanzamiento
def tiempos_lanzamiento(t0, RETARDOS):
    '''
    División temporal en tiempos característicos.
        - t0 : float
            tiempo inicial del lanzamiento
        - RETARDOS : list
            lista que contiene los valores de retardo de cada etapa
    Esta función devuelve un diccionario con n + 1 entradas (n = etapas), cada
    una incluye los tiempos ideales de retardo y de combustión de cada etapa en
    un entorno global, es decir, teniendo en cuenta el tiempo inicial de
    lanzamiento.
    
    T_LANZAMIENTO = [[tr1, tc1], [tr2, tc2], ..., [tri, tci]]
    dicc_temp = {'t_inicial': t0, 'etapa_1': [tr1, tc1],
                 'etapa_2': [tr2, tc2], ...}
    '''
    t = t0
    T_LANZAMIENTO = []
    dicc_temp = {'t_inicial': t0}
    
    for i, gas in enumerate(GASTOS):
        nom = 'etapa_' + str(i + 1)
        a = RETARDOS[i] + t
        b = a + T_COMBUSTION[i]
        t = b
        T_LANZAMIENTO.append([a, b])
        dicc_temp.update({nom:T_LANZAMIENTO[i]})

    return dicc_temp
