# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 12:28:38 2018

@author: Team REOS
"""
from math import radians
import matplotlib.pyplot as plt
from modulos.aerodinamica.aero_misil import CoeficienteFuerza
from mecanica import altitud
from inputs_iniciales import LAT, LON, AZ, Z0, INC, V_inicial
from apoyo import condiciones_iniciales

t0, x0, v0 = condiciones_iniciales(Z0, LAT, LON, AZ, INC, V_inicial)
alt = altitud(x0)
mach=0.01
x_cdg=3

mach_lanzador=[]
cd_lanzador=[]
cn_lanzador=[]
cm_lanzador=[]

coef_fuerzas=CoeficienteFuerza()
coef_fuerzas.set_alpha(radians(5))
coef_fuerzas.set_delta(radians(0))
coef_fuerzas.set_propulsion(prop=True)
coef_fuerzas.set_ala(ala=True)
coef_fuerzas.set_aletas(aletas=True)

while mach<5:
    mach_lanzador.append(mach)
    cd_lanzador.append(coef_fuerzas.cd_total(mach, alt))
    cn_lanzador.append(coef_fuerzas.cn_total(mach))
    cm_lanzador.append(coef_fuerzas.cm_total(mach,x_cdg))
    mach += 0.01
    
#### Gráficas ####
    
plt.figure(1)
plt.plot(mach_lanzador, cd_lanzador)
plt.title('Evolución del coeficiente de resistencia')
plt.ylabel('Cd (-)')
plt.xlabel('Mach (-)')
plt.xlim((0,5))
plt.grid(True)
plt.savefig("CD vs Mach.pdf")
plt.show(1)

plt.figure(2)
plt.plot(mach_lanzador, cn_lanzador)
plt.title('Evolución del coeficiente de la fuerza normal')
plt.ylabel('Cn (-)')
plt.xlabel('Mach (-)')
plt.xlim((0,5))
plt.grid(True)
plt.savefig("CN vs Mach.pdf")
plt.show(1)

plt.figure(3)
plt.plot(mach_lanzador, cm_lanzador)
plt.title('Evolución del coeficiente del momento de cabeceo')
plt.ylabel('Cm (-)')
plt.xlabel('Mach (-)')
plt.xlim((0,5))
plt.grid(True)
plt.savefig("Cm vs Mach.pdf")
plt.show(1)
