# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 13:06:14 2018

@author: Team REOS

Modelo atmosférico: NRL-MSISE00
Funciones de temperatura (temperature), densidad (density), presión
(pressure) y viscosidad (viscosity).  Sólo requieren una variable de
entrada: la altitud, que no ha de ser superior a 1000 km.
Los datos se obtienen del archivo modelo_considerado.reos
Este archivo se ha obtenido del módulo modelo_atmosfera.py
"""

from errores import ValorInadmisibleError
import numpy as np

# Constantes atmosféricas.
R_AIR = 287  # Constante de los gases ideales (J/Kkg).
RHO_SL = 101325 / (R_AIR * 288.15)  # Densidad a nivel del mar (kg/m3).
GAMMA = 1.4  # Coeficiente de dilatación adiabática.
BETA_VISC = 1.458e-6  # Viscosidad de referencia (Pa s/K.5).
S_VISC = 110.4  # Temperatura de referencia para la viscosidad (K).

TEMPER = []
DENSIT = []

FILE = open('./modulos/atmosfera/modelo_atmosferico.reos', 'r')
for i in range(3):
    HEAD = FILE.readline()
for i, line in enumerate(FILE):
    if i == 16:
        break
    s = line.strip()
    s = s.split()
    TEMPER_AUX = []
    for n in range(np.size(s)):
        TEMPER_AUX.append(float(s[n]))
    TEMPER.append(TEMPER_AUX)
for i in range(2):
    BETWEEN_LINES = FILE.readline()
for i, line in enumerate(FILE):
    if i == 16:
        break
    s = line.strip()
    s = s.split()
    DENSIT_AUX = []
    for n in range(np.size(s)):
        DENSIT_AUX.append(float(s[n]))
    DENSIT.append(DENSIT_AUX)
FILE.close()
    
def interval_msise00(alt):
    '''División de tramos del modelo atmosférico MSISE00.
    La variable de entrada alt es la altitud (m).  Debe ser menor o
    igual que 800000 (8e5) metros.
    '''
    if alt < 0:
        raise ValorInadmisibleError(dict(alt=alt), '.0f', 'positivo')
    elif alt > 10e5:
        raise ValorInadmisibleError(dict(alt=alt), '.0f', 'menor que 1000 km')
    i = -1
    tramos = [0, 11e3, 20e3, 32e3, 47e3, 51e3, 71e3, 85e3, 105e3, 125e3, 180e3,
              300e3, 315.5e3, 390e3, 550e3, 600e3, 999.5e3]
    en_tramo = False
    while not en_tramo:
        i = i + 1
        en_tramo = tramos[i] <= alt and alt <= tramos[i+1]
    return i


def temperature(alt):
    '''Cálculo de la temperatura en función de la altura dada por el
    modelo MSISE00.
    La variable de entrada alt es la altitud (m).  Debe ser menor o
    igual que 1000000(10e5) metros.
    La variable de salida es un float con la temperatura (K).
    '''
    tem = 0
    i = interval_msise00(alt)
    for j, k in enumerate(TEMPER[i]):
        tem = tem + k * alt**j
    return tem


def density(alt):
    '''Cálculo de la densidad en función de la altura dada por el modelo
    MSISE00.
    La variable de entrada alt es la altitud (m).  Debe ser menor o
    igual que 1000000 (10e5) metros.
    La variable de salida es un float con la densidad (kg/m3).
    '''
    den = 0
    i = interval_msise00(alt)
    for j, k in enumerate(DENSIT[i]):
        den = den + k * alt**j
    return den


def pressure(alt):
    '''Cálculo de la presión en función de la altura dada por el modelo
    MSISE00.  Se implementa la ley de los gases ideales.
    La variable de entrada alt es la altitud (m).  Debe ser menor o
    igual que 1000000 (10e5) metros.
    La variable de salida es un float con la presión (Pa).
    '''
    return density(alt) * R_AIR * temperature(alt)


def viscosity(alt):
    '''Cálculo de la viscosidad en función de la altura dada por el
    modelo MSISE00.  Se implementa la ley de Sutherland.
    La variable de entrada alt es la altitud (m).  Debe ser menor o
    igual que 1000000 (10e5) metros.
    La variable de salida es un float con la presión (Pa).
    '''
    tem = temperature(alt)
    return BETA_VISC * tem**(3 / 2) / (tem + S_VISC)