# -*- coding: utf-8 -*-
"""
@author: Team REOS

Este módulo contiene las funciones matemáticas necesarias para la
función <lanzamiento> del módulo integracion.py.
"""

from numpy import (arctan, sqrt, pi, sign, array, cos, sin, arctan2, radians,
                   cross)
from numpy.linalg import norm

from modulos.atmosfera.gravedad import RT
from modulos.velocidad_rotacional1 import OMEGA_R

DT = 0.05


def esfericas(vector):
    '''Calcula las coordenadas esféricas de un vector de posición dado
    en coordenadas cartesianas.

    vector : array (3 componentes)
        vector[0] : float
            Componente x.
        vector[1] : float
            Componente y.
        vector[2] : float
            Componente z.
    '''
    # Cartesianas
    x_esf = vector[0]
    y_esf = vector[1]
    z_esf = vector[2]

    # Esféricas
    r_esf = norm(vector)
    if z_esf < 0:
        theta_esf = arctan(sqrt(x_esf**2 + y_esf**2) / z_esf) + pi
    elif z_esf == 0:
        theta_esf = pi / 2
    else:
        theta_esf = arctan(sqrt(x_esf**2 + y_esf**2) / z_esf)

    if x_esf > 0 and y_esf > 0:
        phi_esf = arctan(y_esf / x_esf)
    elif x_esf > 0 and y_esf < 0:
        phi_esf = arctan(y_esf / x_esf) + 2 * pi
    elif x_esf == 0:
        phi_esf = pi * sign(y_esf) / 2
    else:
        phi_esf = arctan(y_esf / x_esf) + pi

    return array([r_esf, theta_esf, phi_esf])


def cartesianas(vector):
    '''Calcula las coordenadas cartesianas de un vector de posición dado
    en coordenadas esféricas.

    vector : array (3 componentes)
        vector[0] : float
            Componente r. r > 0.
        vector[1] : float
            Componente theta (rad). 0 <= theta <= pi.
        vector[2] : float
            Componente phi (rad). 0 <= phi < 2*pi.
    '''
    # Cartesianas
    r_car = vector[0]
    theta_car = vector[1]
    phi_car = vector[2]

    # Esféricas
    x_car = r_car * round(sin(theta_car), 15) * round(cos(phi_car), 15)
    y_car = r_car * round(sin(theta_car), 15) * round(sin(phi_car), 15)
    z_car = r_car * round(cos(theta_car), 15)

    return array([x_car, y_car, z_car])


def vector_esf(modulo, inc, azimut, pos):
    '''Calcula las componentes cartesianas de un vector.

    modulo : float
        Módulo del vector. modulo > 0.

    inc : float
        Ángulo sobre la horizontal local (rad). -pi/2 <= inc <= pi/2.

    azimut : float
        Azimut (rad). -pi < azimut <= pi.

    pos : array (3 componentes)
        Vector posición en coordenadas cartesianas.
    '''
    posi = esfericas(pos)
    thet = posi[1]
    phip = posi[2]
    r_vec = modulo * round(sin(inc), 15)
    t_vec = modulo * round(cos(inc), 15) * round(cos(azimut), 15)
    p_vec = modulo * round(cos(inc), 15) * round(sin(azimut), 15)
#    print(r_vec, t_vec, p_vec)

    x_1 = (r_vec * round(sin(thet), 15) * round(cos(phip), 15)
           + t_vec * round(cos(thet), 15) * round(cos(phip), 15)
           - p_vec * round(sin(phip), 15))
#    print(x_1, thet, phip)
    x_2 = (r_vec * round(sin(thet), 15) * round(sin(phip), 15)
           + t_vec * round(cos(thet), 15) * round(sin(phip), 15)
           + p_vec * round(cos(phip), 15))
    x_3 = (r_vec * round(cos(thet), 15)
           - t_vec * round(sin(thet), 15))

    return array([x_1, x_2, x_3])


def vel_cart(V, theta, phi, psi, alfa):
    '''
    Función que calcula las componentes cartesianas de la velocidad respecto a
    un sistema de referencia fijo en el centro de la tierra. En función de:
        
        V: módulo de la velocidad (m/s)
        
        theta: longitud (rad)
        
        phi: latitud (rad)
        
        psi: inclinación de lanzamiento (rad)
        
        alfa: ángulo de azimut (rad)
    '''
    vz = V*(sin(psi)*sin(phi) + cos(psi)*cos(phi)*cos(alfa))
    vy = (V*(sin(theta)*(sin(psi)*cos(phi) - cos(psi)*cos(alfa)*sin(phi))
          + cos(psi)*sin(alfa)*cos(theta)))
    vx = (V*(cos(theta)*(sin(psi)*cos(phi) - cos(psi)*cos(alfa)*sin(phi))
          - cos(psi)*sin(alfa)*sin(theta)))
    V_cartesianas = [vx, vy, vz]
    return V_cartesianas


def condiciones_iniciales(alt, lat, lon, az, inc, vel, t=0):
    '''Define las condiciones iniciales (tiempo <tiempo>, posición
    <posicion> y velocidad <velocidad>) de lanzamiento del lanzador.

    alt : float
        Altura de lanzamiento (m)

    lat : float
        Latitud inicial del avión (rad).

    lon : float
        Longitud inicial del avión (rad).

    az : float
        Azimut inicial del avión (rad).

    inc : float
        Inclinación del lanzamiento (rad).

    vel : float
        Velocidad desde la que lanza el avión (m/s)

    t : float
        Tiempo inicial de lanzamiento (s)
    '''
    tiempo = t
    r_inicial = RT + alt
    phi_c = pi/2 - lat  # Colatitud que en coor. esf. es theta
    # Paso la posición a coordenadas cartesianas
    posicion = cartesianas([r_inicial, phi_c, lon])
    velocidad = (vel_cart(vel, lon, lat, inc, az)
                 + cross(OMEGA_R, posicion))
#    print(velocidad)

    return tiempo, posicion, velocidad
