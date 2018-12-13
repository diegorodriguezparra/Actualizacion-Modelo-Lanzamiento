# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 09:45:53 2018

@author: Team REOS
"""

# GEOMETRÍA DEL LANZADOR
# ----------------------

DIAMETRO_M = .6  # Diámetro del misil (m)
DIAMETRO_S = [0.5, 0.5, 0.5]  # Diámetro salida de gases (m)
LONGITUD_CONO = 1.0  # Longitud del cono del misil (m)
LONGITUD_MISIL = [5.0, 2.5, 1.5, LONGITUD_CONO]  # Long. de misil por etapa(m)
TIPO_NARIZ = 0  # 0-Cono 1-Ojiva Circular Tangente
IYY= 10000 # Momento de inercia en el eje perpendicular al plano vertical

# GEOMETRÍA DE LAS ALETAS
# -----------------------

ESPESOR_ALETA = .02  # Espesor de la aleta (m)
CMEDIA_ALETA = .5  # Cuerda media de la aleta (m)
CRAIZ_ALETA = .5  # Cuerda raíz de la aleta (m)
NUM_ALETAS = 4  # Número de aletas
ENVERGADURA_ALETAS = 0.8 # Envergadura de dos aletas
FACTOR_ALETA = 1 # Depende del tipo de perfil de la aleta (apuntes misiles UPM)

# GEOMETRÍA DEL ALA
# -----------------

ESPESOR_ALA= 0.035 # Espesor del ala (m)
FACTOR_ALA= 1 # Depende del tipo de perfil del ala (apuntes misiles UPM)
CRAIZ_ALA= 1.4 # Cuerda en la raiz del ala del lanzador (m)
ENVERGADURA_ALA= 2.2 # Envergadura del ala del lanzador (m)
X_ALA= 4 # Posición del borde de salida del ala desde la proa del lanzador