# -*- coding: utf-8 -*-
"""
@author: Team REOS
Cálculo de la velocidad rotacional de la Tierra.
"""

from numpy import cos, sin, pi, array
from modulos.atmosfera.gravedad import RT

# LATtitudes del mundo (ciudades).

# 90º Polo Norte.
# 66.57º Circulo Polar Artico.
# 50º Bruselas.
# 40º Madrid y Nueva York.
# 34º Los Angeles y Tokio.
# 27º Isla del Hierro.
# 23.43º Trópico de Cáncer.
# 19º Ciudad de México.
# 0º Ecuador Quito.
# -1º Nairobi (Kenia).
# -15.5º Brasilia.
# -16º La Paz (Bolivia).
# -23.43º Trópico de Capricornio.
# -34º Buenos Aires, Ciudad del Cabo y Sydney.
# -66.57º Circulo Polar Antartico.
# -90º Polo Sur.


ANO_MEDIO = (365 * 400 + 100 - 1) / 400  # Año calendario medio en días
PERIODO = ANO_MEDIO / (ANO_MEDIO + 1) * 24 * 60 * 60
# Periodo de rotación de la Tierra
V_ANGULAR = 0 # 2 * pi / PERIODO  Velocidad angular rotacional
OMEGA_R = array([0, 0, V_ANGULAR])  # Velocidad angular (rad/s)


def vel_rot_lon(altitud, latitud, azimut):
    '''Componente longitudinal (paralela a la velocidad de vuelo) de la
    velocidad rotacional en m/s.
    altitud : float
        Altitud (m)
    latitud : float
        Latitud (rad)
    azimut : float
        Azimut (rad)
    '''

    return V_ANGULAR * (RT + altitud) * cos(latitud) * sin(azimut)


def vel_rot_tra(altitud, latitud, azimut):
    '''Componente transversal (perpendicular a la velocidad de vuelo) de la
    velocidad rotacional en m/s.
    altitud : float
        Altitud (m)
    latitud : float
        Latitud (rad)
    azimut : float
        Azimut (rad)
    '''

    return V_ANGULAR * (RT + altitud) * cos(latitud) * cos(azimut)


def vel_rot(altitud, latitud):
    '''Módulo de la velocidad rotacional en m/s.
    altitud : float
        Altitud (m)
    latitud : float
        Latitud (rad)
    azimut : float
        Azimut (rad)
    '''

    return V_ANGULAR * (RT + altitud) * cos(latitud)
