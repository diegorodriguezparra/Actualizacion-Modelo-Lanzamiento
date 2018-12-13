# -*- coding: utf-8 -*-
"""
@author: TeamREOS
Módulo que contiene los inputs del programa.
"""

from numpy import radians, array

# Inputs de altura, posición, velocidad y masa del avión
Z0 = 11000  # Altitud inicial del misil (m)
Zmax = 800001 # Altitud maxima limitada por modelo_msise00 de momento
AZ = radians(90)  # Azimut de lanzamiento dirección
LAT = radians(0)  # Latitud inicial del avión
LON = radians(0)  # Longitud inicial del avión
INC = radians(0) # Inclinación de lanzamiento
M_inicial = 0.8  # Número de Mach inicial
V_inicial = 280  # m/s
N = 3.5  # Factor de carga máximo
V_ANGULAR = 0  # Se considera 0 la velocidad angular


# Caracteristicas del Lanzador
GASTOS = array([18.57, 5.33, 1.75])  # Gasto másico (kg/s)
ISPS = array([285, 285, 285])  # Impulso específico (s)
N_ETAPAS = len(GASTOS)  # Número de etapas del lanzador
MASA_DE_PAGO = 10.0  # Masa de la carga de pago (kg)
MASAS = array([830.0, 280.0, 80.0, MASA_DE_PAGO]) # Masa total de cada etapa
MASA_TOTAL = float(sum(MASAS))
ESTRUCTURAS = array([0.1416, 0.1480, 0.1117])  # Razón estructural de cada etapa
RETARDOS_IN = array([4.0, 0.0, 385.0])  # Retardos iniciales de encendido de etapas (s)
GAMMA_INY_MIN = 0.025  # Gamma de inyección mínima en órbita (deg).
