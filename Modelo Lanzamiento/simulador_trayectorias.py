# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 08:20:44 2018

@author: Team REOS
"""

from time import time
from numpy import sign, log
from numpy.linalg import norm
from inputs_iniciales import LAT, LON, AZ, Z0, INC, V_inicial, Zmax
from inputs_iniciales import GASTOS, MASAS, ISPS, ESTRUCTURAS, RETARDOS_IN
from inputs_iniciales import GAMMA_INY_MIN
from modulos.atmosfera.gravedad import vel_orbital, RT
from modulos.tiempo.division_temporal import tiempos_lanzamiento
from apoyo import condiciones_iniciales
from integracion import lanzamiento, DT
from plots_lanzamiento import plot_graficas
from plots_coeficientes_aerodinamicos import plot_coeficientes_aerodinamicos
import matplotlib.pyplot as plt

plt.close('all')

TIME = time()
NOM = 'Lanzamiento_REOS_Datos'
MASA_TOTAL = float(sum(MASAS))
V0 = V_inicial
string_masa = 'Masa del lanzador por etapas'
string_linea = '----------------------------'
print(string_masa + '\n' + string_linea)
for i, masa in enumerate(MASAS):
    if masa == MASAS[-1]:
        print('Carga de pago:\t{0:6.2f} kg'.format(masa))
    else:
        print('Etapa {0}:\t{1:6.2f} kg'.format((i + 1), masa))
print('Masa Total:\t{0:6.2f} kg'.format(MASA_TOTAL))
print('\nVelocidad inicial del lanzador: {0:.2f} m/s'.format(V0))

# Condiciones que cambiarán en el bucle.
gamma_inyec = -1
retardos = RETARDOS_IN

# COMIENZA LA SIMULACIÓN DE LANZAMIENTO.
# --------------------------------------
i = 1
while abs(gamma_inyec) > GAMMA_INY_MIN:
    print('\nIteración {0}\n------------'.format(i))
    print('RETARDOS: {0}'.format(retardos))
    t0, x0, v0 = condiciones_iniciales(Z0, LAT, LON, AZ, INC, V0)
    DIC_TIE = tiempos_lanzamiento(t0, retardos)  # Diccionario que divide el lanzamiento

    m, t, x, v, gamma, gamma_inyec, vloss = lanzamiento(MASAS, ESTRUCTURAS, GASTOS,
                                                        ISPS, x0, v0, INC,
                                                        retardos,
                                                        diccionario_tiempo=DIC_TIE,
                                                        step_size=DT,
                                                        alt_maxima=Zmax,
                                                        perdidas=True,
                                                        imprimir=NOM)
    if abs(gamma_inyec) > 0.1:
        retardos[2] = round((retardos[2] + sign(gamma_inyec)*log(abs(gamma_inyec) + 1)/log(1.1)), 2)
    else:
        retardos[2] = round((retardos[2] + sign(gamma_inyec)*(10*gamma_inyec)**2), 2)
        
    print('Ángulo de inyección: ' + format(gamma_inyec, '.2f') + ' deg')
    i += 1
print('\nVelocidad final: '
      + format(norm(v) / vel_orbital(norm(x) - RT), '.3%')
      + ' de la velocidad orbital')
print('Altitud final: ' + format((norm(x) - RT) / 1000, '.3f') + ' km')

plot_graficas(NOM)
plot_coeficientes_aerodinamicos('caracteristicas_aerodinamicas')

print('\nTiempo de ejecución: ' + format(time() - TIME, '.4f') + ' s')
