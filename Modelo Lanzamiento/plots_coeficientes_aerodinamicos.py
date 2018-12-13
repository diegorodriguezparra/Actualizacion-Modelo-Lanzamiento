# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 12:28:38 2018

@author: Team REOS
"""

import matplotlib.pyplot as plt

def plot_coeficientes_aerodinamicos(nombre_archivo):
    
    plot = open(nombre_archivo, "r") # Lectura del archivo
    
    HEAD = plot.readline() # Lectura de la primera línea
    
    # Definición de los vectores
    TIEMPO = []
    CD = []
    CN = []
    ALFA = []
    
    for line in plot:
        s = line.strip() # Divide el string principal en strings por líneas
        s = s.split( ) # Elimina los espacios
        TIEMPO.append(float(s[0]))
        CD.append(float(s[1]))
        CN.append(float(s[2]))
        ALFA.append(float(s[3]))
        
    #### Gráficas ####
        
    plt.figure(6)
    plt.plot(TIEMPO, CD)
    plt.title('Evolución del coeficiente de resistencia')
    plt.ylabel('Cd (-)')
    plt.xlabel('Tiempo (s)')
    plt.xlim((0,400))
    plt.grid(True)
    plt.savefig("./imagenes/CD vs t.pdf")
    plt.show()
    
    plt.figure(7)
    plt.plot(TIEMPO, CN)
    plt.title('Evolución del coeficiente de la fuerza normal')
    plt.ylabel('Cn (-)')
    plt.xlabel('Tiempo (s)')
    plt.xlim((0,400))
    plt.grid(True)
    plt.savefig("./imagenes/CN vs t.pdf")
    plt.show()