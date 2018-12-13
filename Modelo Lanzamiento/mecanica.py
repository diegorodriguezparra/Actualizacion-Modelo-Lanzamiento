# -*- coding: utf-8 -*-
"""
@author: Team REOS

Este módulo contiene la mecánica del lanzamiento.
"""

from numpy import sqrt, cross, dot, cos, radians
from numpy.linalg import norm

from modulos.atmosfera.gravedad import gravity, MU, RT, vel_orbital
from modulos.atmosfera.modelo_msise00 import temperature, pressure, GAMMA, R_AIR
from modulos.velocidad_rotacional1 import OMEGA_R
from modulos.aerodinamica.aero_misil import SREF_MISIL
#from modulos.aerodinamica.aero_misil import CoeficienteFuerza

G0 = 9.81  # Constante de dimensionalización del impulso específico (m/s2)


def numero_mach(pos, vel):
    '''
    Calcula el número de Mach.

    pos : array (3 componentes)
        Vector posición.

    vel : array (3 componentes)
        Vector velocidad.
    '''
    altur = norm(pos) - RT
    tem = temperature(altur)
    vel_sonido = sqrt(GAMMA * R_AIR * tem)
    vel_aire = cross(OMEGA_R, pos)
    vel_relativa = vel - vel_aire
    
    return norm(vel_relativa) / vel_sonido


def altitud(pos):
    '''Calcula la altitud del lanzador.

    pos : array (3 componentes)	
        Vector posición.
    '''
    alt = norm(pos) - RT

    return  alt


def empuje(pos, vel, gasto, impulso, coeficientes_fuerza):
    '''
    Calcula el empuje del lanzador. En la dirección de la velocidad más el 
    ángulo de ataque del lanzador.

    pos : array (3 componentes)
        Vector posición.
        
    vel : array (3 componentes)
        Vector velocidad.
        
    gasto : float
        Gasto másico.

    impulso : float
        Impulso específico normalizado.
    
    coeficientes_fuerza : object
        Es un objeto en el cual está definida la aerodinámica del lanzador.
    '''
    # Calculo la dirección del empuje, suponiendo:
    #     - Forma un ángulo alfa con la velocidad
    #       (coeficientes_fuerza._angulo_ataque)
    #     - Está contenida en el plano que forman la velocidad y la posición
    #     - Se elige el sentido en el que el ángulo entre velocidad y empuje es
    #       alfa.
    if coeficientes_fuerza._angulo_ataque != 0:
        pos_un = pos/norm(pos)
        vel_un = vel/norm(vel)
        prod_vec = dot(pos_un, vel_un)
        if prod_vec == 0:
            t = cos(coeficientes_fuerza._angulo_ataque)
            s = sqrt(1 - t**2)
        else:
            # Ec. Segundo grado
            a = (1/prod_vec**2) - 1
            b = 2*cos(coeficientes_fuerza._angulo_ataque)*(1 - (1/prod_vec**2))
            c = (cos(coeficientes_fuerza._angulo_ataque))**2/prod_vec**2 - 1
            t = (-1*b - sqrt(b**2 - 4*a*c))/(2*a)
            s = (cos(coeficientes_fuerza._angulo_ataque) - t)/prod_vec
        dir_emp = s*pos_un + t*vel_un
        dir_emp_un = dir_emp/norm(dir_emp)
    else:
        dir_emp_un = vel/norm(vel)
    
    altur = norm(pos) - RT
    v_orb = vel_orbital(altur)
    v_nom = norm(vel)
    if v_nom >= v_orb:
        return 0
    
    return gasto * G0 * impulso * dir_emp_un


def resistencia(pos, vel, coeficientes_fuerza):
    '''
    Calcula la fuerza de resistencia del lanzador. En la dirección de la
    velocidad pero sentido contrario.

    pos : array (3 componentes)
        Vector posición.

    vel : array (3 componentes)
        Vector velocidad.

    coeficientes_fuerza : object
        Es un objeto en el cual está definida la aerodinámica del lanzador.
    '''
    altur = norm(pos) - RT
    mach = numero_mach(pos, vel)

    cd_lanzador = coeficientes_fuerza.cd_total(mach, altur)

    return -(.5 * GAMMA * pressure(altur) * mach**2 * SREF_MISIL * cd_lanzador
             * vel / norm(vel))


def sustentacion(pos, vel, coeficientes_fuerza):
    '''
    Calcula la fuerza normal o sustentación del lanzador. En dirección
    perpendicular a la velocidad.
    pos : array (3 componentes)
        Vector posición.
    vel : array (3 componentes)
        Vector velocidad.
    coeficientes_fuerza : object
        Es un objeto en el cual está definida la aerodinámica del lanzador.
    '''
    altur = norm(pos) - RT
    mach = numero_mach(pos, vel)
    cn_lanzador = coeficientes_fuerza.cn_total(mach)
    
    # Calculo la dirección de la sustentación, suponiendo:
    #     - Es perpendicular a la velocidad
    #     - Está contenida en el plano que forman la velocidad y la posición
    #     - Se elige el sentido en el que el ángulo entre velocidad y
    #       sustentación forman 90º partiendo desde vel. a sus.
    pos_un = pos/norm(pos)
    vel_un = vel/norm(vel)
    prod_vec = dot(pos_un, vel_un)
    if prod_vec == 0:
        t = 0
        s = 1
    elif prod_vec == 1:
        raise ValueError('Error: la posición y la velocidad están' +
                         'en la misma dirección y no está definida la' +
                         'dirección de la sustentación')
    else:
        t = -1*prod_vec/sqrt(1 - prod_vec**2)
        s = 1/sqrt(1 - prod_vec**2)
    n = s*pos_un + t*vel_un # Define un vector coplanario a la posición y la velocidad,
    # combinación lineal de estos dos vectores.
    n_un = n/norm(n)

    return (.5*GAMMA*pressure(altur)*mach**2*SREF_MISIL*cn_lanzador*n_un)


def peso(pos, mas):
    '''
    Calcula el peso del lanzador. Va en la dirección del peso.

    pos : array (3 componentes)
        Vector posición.

    mas : float
        Masa.
    '''
    altur = norm(pos) - RT

    return -mas * gravity(altur) * pos / norm(pos)

    
def aceleracion(pos, vel, mas, gasto, isp, coeficientes_fuerza):
    '''Calcula la aceleración total del lanzador.

    pos : array (3 componentes)
        Vector posición.

    vel : array (3 componentes)
        Vector velocidad.

    mas : float
        Masa.

    gasto : float
        Gasto másico.

    isp : float
        Impulso específico.

    coeficientes_fuerza : object
        Es un objeto en el cual está definida la aerodinámica del lanzador.
    '''
    
    emp = empuje(pos, vel, gasto, isp, coeficientes_fuerza)  # Empuje
    res = resistencia(pos, vel, coeficientes_fuerza)  # Resistencia
    nor = sustentacion(pos, vel, coeficientes_fuerza)  # Sustentación o Normal
    pes = peso(pos, mas)  # Peso

    fuerza = emp + res + pes + nor  # Fuerza resultante total

    return fuerza / mas


def energia_mecanica(mas, pos, vel):
    '''
    Calcula la energía mecánica del lanzador.

    mas : float
        Masa.

    pos : array (3 componentes)
        Vector posición.

    vel : array (3 componentes)
        Vector velocidad.
    '''
    cin = .5 * mas * dot(vel, vel)
    pot = -MU * mas / norm(pos)
    mec = cin + pot

    return mec


def ley_alfa(t, diccionario_tiempo):
    '''
    Ley de control del ángulo de ataque en función del tiempo. Devuelve el
    ángulo de ataque en radianes.
    
    t : float
        tiempo global.
    diccionario_tiempo : dictionary
        diccionario con tiempos inicial de lanzamiento y tiempos
        característicos de cada etapa.
    '''
    key_inicio = 't_inicial'
    key = 'etapa_1'
    var_inicio = diccionario_tiempo[key_inicio]
    var_key = diccionario_tiempo[key]
    
    if var_inicio < t < var_key[0]:
        alfa = radians(2.5/4)*(t - var_inicio)
    elif var_key[0] <= t <= (var_key[1] - 0.0):
        alfa = radians(2.5)
    else:
        alfa = 0
    return alfa
