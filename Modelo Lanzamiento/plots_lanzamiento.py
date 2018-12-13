# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 08:29:07 2018

@author: Team REOS
"""

import matplotlib.pyplot as plt
from inputs_iniciales import GASTOS


def plot_graficas(nombre_archivo):

    # Definición de los vectores
    
    def desglose_etapas(variable, j): # La variable j indica la columna a leer en la hoja de datos  
        
        diccionario = {}
        paso_temporal = []
        paso_variable = []
        
        for i in range(len(GASTOS)+1):
            
            Lanzamiento = open(nombre_archivo, "r") # Lectura del archivo 
            HEAD = Lanzamiento.readline() # Lectura de la primera línea
            nom = variable + str(i)

            for line in Lanzamiento:
                s = line.strip() # Divide el string principal en strings por líneas
                s = s.split() # Elimina los espacios
                
                if i == 0 and s[8] == 'Off':
                    
                    paso_temporal.append(float(s[0]))
                    paso_variable.append(float(s[j]))  
                
                if i == float(s[7]) and s[8] == 'On':
                    
                    paso_temporal.append(float(s[0]))
                    paso_variable.append(float(s[j]))            
                    
                etapa = [paso_temporal, paso_variable]
                diccionario.update({nom:etapa})               
                
            Lanzamiento.close()
            diccionario.update({nom:etapa})
    
            paso_temporal = []
            paso_variable = []
            
        return diccionario

    ############## GRÁFICAS #############
    
    dicc_altura = desglose_etapas('Altura_', 1)
    
    Retardos_altura=dicc_altura['Altura_0']
    Altura_1=dicc_altura['Altura_1']
    Altura_2=dicc_altura['Altura_2']
    Altura_3=dicc_altura['Altura_3']

    plt.figure(1)
    plt.plot(Retardos_altura[0], Retardos_altura[1], '.')
    plt.plot(Altura_1[0], Altura_1[1], '.')
    plt.plot(Altura_2[0], Altura_2[1], '.')
    plt.plot(Altura_3[0], Altura_3[1], '.')
    plt.title('Altitud de vuelo')
    plt.ylabel('Altitud (m)')
    plt.xlabel('Tiempo (s)')
#    plt.xlim((-10,1000))
    plt.legend(("Retardos", "Etapa 1", "Etapa 2", "Etapa 3"))
    plt.grid(True)
    plt.savefig("./imagenes/Altitud vs t.pdf")
    plt.show()
    
    
    dicc_velocidad = desglose_etapas('Velocidad_', 2)
    
    Retardos_vel=dicc_velocidad['Velocidad_0']
    Velocidad_1=dicc_velocidad['Velocidad_1']
    Velocidad_2=dicc_velocidad['Velocidad_2']
    Velocidad_3=dicc_velocidad['Velocidad_3']

    plt.figure(2)
    plt.plot(Retardos_vel[0], Retardos_vel[1], '.')
    plt.plot(Velocidad_1[0], Velocidad_1[1], '.')
    plt.plot(Velocidad_2[0], Velocidad_2[1], '.')
    plt.plot(Velocidad_3[0], Velocidad_3[1], '.')
    plt.title('Velocidad de vuelo')
    plt.ylabel('Velocidad (m/s)')
    plt.xlabel('Tiempo (s)')
#    plt.xlim((-10,1000))
    plt.legend(("Retardos", "Etapa 1", "Etapa 2", "Etapa 3"))
    plt.grid(True)
    plt.savefig("./imagenes/Velocidad vs t.pdf")
    plt.show()
 
    
    dicc_masa = desglose_etapas('Masa_', 3)
    
    Retardos_mas=dicc_masa['Masa_0']
    Masa_1=dicc_masa['Masa_1']
    Masa_2=dicc_masa['Masa_2']
    Masa_3=dicc_masa['Masa_3']

    plt.figure(3)
    plt.plot(Retardos_mas[0], Retardos_mas[1], '.')
    plt.plot(Masa_1[0], Masa_1[1], '.')
    plt.plot(Masa_2[0], Masa_2[1], '.')
    plt.plot(Masa_3[0], Masa_3[1], '.')
    plt.title('Variación másica')
    plt.ylabel('Masa (kg)')
    plt.xlabel('Tiempo (s)')
    plt.xlim((-10,1000))
    plt.legend(("Retardos", "Etapa 1", "Etapa 2", "Etapa 3"))
    plt.grid(True)
    plt.savefig("./imagenes/Masa vs t.pdf")
    plt.show()


    dicc_gamma = desglose_etapas('Gamma_', 4)
    
    Retardos_gamma=dicc_gamma['Gamma_0']
    Gamma_1=dicc_gamma['Gamma_1']
    Gamma_2=dicc_gamma['Gamma_2']
    Gamma_3=dicc_gamma['Gamma_3']

    plt.figure(4)
    plt.plot(Retardos_gamma[0], Retardos_gamma[1], '.')
    plt.plot(Gamma_1[0], Gamma_1[1], '.')
    plt.plot(Gamma_2[0], Gamma_2[1], '.')
    plt.plot(Gamma_3[0], Gamma_3[1], '.')
    plt.title('Variación del ángulo de la trayectoria')
    plt.ylabel('Gamma (º)')
    plt.xlabel('Tiempo (s)')
    plt.xlim((-10,600))
    plt.legend(("Retardos", "Etapa 1", "Etapa 2", "Etapa 3"))
    plt.grid(True)
    plt.savefig("./imagenes/Gamma vs t.pdf")
    plt.show()


#    dicc_alfa = desglose_etapas('Alfa_', 5)
#    
#    Retardos=dicc_alfa['Alfa_0']
#    Alfa_1=dicc_alfa['Alfa_1']
#    Alfa_2=dicc_alfa['Alfa_2']
#    Alfa_3=dicc_alfa['Alfa_3']

#    fig, ax1 = plt.subplots()
#    ax1.set_xlabel('Tiempo (s)')
#    ax1.set_ylabel('Gamma (º)')
#    plt.plot(Retardos[0], Retardos[1], '.')
#    plt.plot(Gamma_1[0], Gamma_1[1], '.')
#    plt.plot(Gamma_2[0], Gamma_2[1], '.')
#    plt.plot(Gamma_3[0], Gamma_3[1], '.')
#    plt.xlim((0,500))
#    plt.ylim((-10,50))
#    ax2 = ax1.twinx()
#    ax2.set_ylabel('Alfa (º)')
##    plt.plot(Retardos[0], Retardos[1])
##    plt.plot(Alfa_1[0], Alfa_1[1])
##    plt.plot(Alfa_2[0], Alfa_2[1])
##    plt.plot(Alfa_3[0], Alfa_3[1])
#    plt.ylim((-1,5))
#    plt.grid(True)
#    plt.legend(("Retardos", "Etapa 1", "Etapa 2", "Etapa 3"))
##    fig.legend(("Gamma", "Alfa", "Factor Carga"), bbox_to_anchor=(0.9, 0.86))
#    plt.savefig("./imagenes/Angulos vs t.pdf")
#    plt.show()


