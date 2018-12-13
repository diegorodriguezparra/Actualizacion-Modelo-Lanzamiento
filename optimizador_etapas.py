# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 09:58:20 2018

@author: carlos.galanmorales
"""

"Optimización de etapas"

from sympy.solvers import solve
import sympy
import math
from inputs_iniciales import (V1, ESTRUCTURAS, ISPS, MASS)

#DATOS
altitud_orbita = 567000 # Altitud de la órbita en metros
gravedad = 9.81 # m/s**2
mu_tierra = 3.986 * 10**14 # Parámetro gravitacional estandar en m**3/s**2 (mu_tierra=G*(Masa de la Tierra))
radio_tierra = 6378140 # Radio de la Tierra en metros
V_perdidas = 1200 # Velocidad por pérdidas aerodinámicas y gravitatorias en m/s.
                    # El objetivo será calcular este valor y no meterlo como un input
numero_etapas = 2
 # Número de etapas de 1 a 5


#Cáculo de velocidades para obtener la velocidad total que hay que darle al lanzador y 
#calcular la masa de propulsante para ello

V_orbita = math.sqrt( mu_tierra / (radio_tierra + altitud_orbita) )
V_lanzamiento = V1

V_inyeccion = V_orbita - V_lanzamiento + V_perdidas # Velocidad total que tiene que ser capaz de dar nuestro propulsante
print("Velocidad de inyección =", V_inyeccion)

#Iteración para conseguir lambda, parámetro de optimización

if numero_etapas == 1:
    lamda = sympy.Symbol("lamda")
    sol=solve((1+lamda*gravedad*ISPS[0])/(ESTRUCTURAS[0]*lamda*gravedad*ISPS[0]) - math.e**(V_inyeccion/(gravedad*ISPS[0])), lamda)
    print("lambda 1 etapa =", sol[0])
    
    variable = sol[0]
    print((1+variable*gravedad*ISPS[0])/(ESTRUCTURAS[0]*variable*gravedad*ISPS[0]) - math.e**(V_inyeccion/(gravedad*ISPS[0])))
    
elif numero_etapas == 2:
    lamda = sympy.Symbol("lamda")
    sol=solve(((1+lamda*gravedad*ISPS[0])/(ESTRUCTURAS[0]*lamda*gravedad*ISPS[0]))*((1+lamda*gravedad*ISPS[1])/(ESTRUCTURAS[1]*lamda*gravedad*ISPS[1]))**(ISPS[1]/ISPS[0]) - math.e**(V_inyeccion/(gravedad*ISPS[0])), lamda)
    print("lambda 2 etapas =", sol[0])
    
elif numero_etapas == 3:
    lamda = sympy.Symbol("lamda")
    sol=solve(((1+lamda*gravedad*ISPS[0])/(ESTRUCTURAS[0]*lamda*gravedad*ISPS[0]))*((1+lamda*gravedad*ISPS[1])/(ESTRUCTURAS[1]*lamda*gravedad*ISPS[1]))**(ISPS[1]/ISPS[0])*((1+lamda*gravedad*ISPS[2])/(ESTRUCTURAS[2]*lamda*gravedad*ISPS[2]))**(ISPS[2]/ISPS[0]) - math.e**(V_inyeccion/(gravedad*ISPS[0])), lamda)
    print(sol)
    print("lambda 3 etapas =", sol[0])
#    variable = sol[0]
#    print(((1+lamda*gravedad*ISPS[0])/(ESTRUCTURAS[0]*lamda*gravedad*ISPS[0]))*((1+lamda*gravedad*ISPS[1])/(ESTRUCTURAS[1]*lamda*gravedad*ISPS[1]))**(ISPS[1]/ISPS[0])*((1+lamda*gravedad*ISPS[2])/(ESTRUCTURAS[2]*lamda*gravedad*ISPS[2]))**(ISPS[2]/ISPS[0]) - math.e**(V_inyeccion/(gravedad*ISPS[0])))

elif numero_etapas == 4:
    lamda = sympy.Symbol("lamda")
    sol=solve(((1+lamda*gravedad*ISPS[0])/(ESTRUCTURAS[0]*lamda*gravedad*ISPS[0]))*((1+lamda*gravedad*ISPS[1])/(ESTRUCTURAS[1]*lamda*gravedad*ISPS[1]))**(ISPS[1]/ISPS[0])*((1+lamda*gravedad*ISPS[2])/(ESTRUCTURAS[2]*lamda*gravedad*ISPS[2]))**(ISPS[2]/ISPS[0])*((1+lamda*gravedad*ISPS[3])/(ESTRUCTURAS[3]*lamda*gravedad*ISPS[3]))**(ISPS[3]/ISPS[0]) - math.e**(V_inyeccion/(gravedad*ISPS[0])), lamda)
    print("lambda 4 etapas =", sol[0])
    
elif numero_etapas == 5:
    lamda = sympy.Symbol("lamda")
    sol=solve(((1+lamda*gravedad*ISPS[0])/(ESTRUCTURAS[0]*lamda*gravedad*ISPS[0]))*((1+lamda*gravedad*ISPS[1])/(ESTRUCTURAS[1]*lamda*gravedad*ISPS[1]))**(ISPS[1]/ISPS[0])*((1+lamda*gravedad*ISPS[2])/(ESTRUCTURAS[2]*lamda*gravedad*ISPS[2]))**(ISPS[2]/ISPS[0])*((1+lamda*gravedad*ISPS[3])/(ESTRUCTURAS[3]*lamda*gravedad*ISPS[3]))**(ISPS[3]/ISPS[0])*((1+lamda*gravedad*ISPS[4])/(ESTRUCTURAS[4]*lamda*gravedad*ISPS[4]))**(ISPS[4]/ISPS[0]) - math.e**(V_inyeccion/(gravedad*ISPS[0])), lamda)
    print("lambda 5 etapas =", sol[0])

# rn = relación de masas de escalón en función de la relación de masa de etapa y relación estructural
# xn = relación de masas de etapa en función de masas escalón
# m_escalonn = masa de escalon de la etapa n

r1=(1+sol[0]*gravedad*ISPS[0])/(ESTRUCTURAS[0]*sol[0]*gravedad*ISPS[0])
x1=r1*(1-ESTRUCTURAS[0])/(1-r1*ESTRUCTURAS[0])
m_escalon1=MASS
m_escalon2=m_escalon1/x1
if numero_etapas >= 2:
    r2=(1+sol[0]*gravedad*ISPS[1])/(ESTRUCTURAS[1]*sol[0]*gravedad*ISPS[1])
    x2=r2*(1-ESTRUCTURAS[1])/(1-r1*ESTRUCTURAS[1])
    m_escalon3=m_escalon2/x2
    if numero_etapas >= 3:
        r3=(1+sol[0]*gravedad*ISPS[2])/(ESTRUCTURAS[2]*sol[0]*gravedad*ISPS[2])
        x3=r3*(1-ESTRUCTURAS[2])/(1-r1*ESTRUCTURAS[2])
        m_escalon4=m_escalon3/x3
        if numero_etapas >= 4:
            r4=(1+sol[0]*gravedad*ISPS[3])/(ESTRUCTURAS[3]*sol[0]*gravedad*ISPS[3])
            x4=r4*(1-ESTRUCTURAS[3])/(1-r1*ESTRUCTURAS[3])
            m_escalon5=m_escalon4/x4
            if numero_etapas >= 5:
                r5=(1+sol[0]*gravedad*ISPS[4])/(ESTRUCTURAS[4]*sol[0]*gravedad*ISPS[4])
                x5=r5*(1-ESTRUCTURAS[4])/(1-r1*ESTRUCTURAS[4])

# m_payload = masa de la carga de pago
if numero_etapas == 1:
    m_payload=m_escalon2
if numero_etapas == 2:
    m_payload=m_escalon3
if numero_etapas == 3:
    m_payload=m_escalon4
if numero_etapas == 4:
    m_payload=m_escalon5
if numero_etapas == 5:
    m_payload=m_escalon5/x5

# m_etapan = masa de la etapa n
# m_propulsanten = masa de propulsante de la etapa n

m_etapa1=m_escalon1-m_escalon2
m_propulsante1=m_etapa1*(1-ESTRUCTURAS[0])
print("Masa escalón de la primera etapa:", m_escalon1)
print("Masa de la primera etapa:", m_etapa1)
print("Masa de propulsante de la primera etapa:", m_propulsante1)
if numero_etapas >= 2:
    m_etapa2=m_escalon2-m_escalon3
    m_propulsante2=m_etapa2*(1-ESTRUCTURAS[1])
    print("Masa escalón de la segunda etapa:", m_escalon2)
    print("Masa de la segunda etapa:", m_etapa2)
    print("Masa de propulsante de la segunda etapa:", m_propulsante2)
    if numero_etapas >= 3:
        m_etapa3=m_escalon3-m_escalon4
        m_propulsante3=m_etapa3*(1-ESTRUCTURAS[2])
        print("Masa escalón de la tercera etapa:", m_escalon3)
        print("Masa de la tercera etapa:", m_etapa3)
        print("Masa de propulsante de la tercera etapa:", m_propulsante3)
        if numero_etapas >= 4:
            m_etapa4=m_escalon4-m_escalon5
            m_propulsante4=m_etapa4*(1-ESTRUCTURAS[3])
            print("Masa escalón de la cuarta etapa:", m_escalon4)
            print("Masa de la cuarta etapa:", m_etapa4)
            print("Masa de propulsante de la cuarta etapa:", m_propulsante4)
            if numero_etapas >= 5:
                m_etapa5=m_escalon5-m_payload
                m_propulsante5=m_etapa5*(1-ESTRUCTURAS[4])
                print("Masa escalón de la quinta etapa:", m_escalon5)
                print("Masa de la quinta etapa:", m_etapa5)
                print("Masa de propulsante de la quinta etapa:", m_propulsante5)

print("Masa de carga de pago:", m_payload)
                


       














