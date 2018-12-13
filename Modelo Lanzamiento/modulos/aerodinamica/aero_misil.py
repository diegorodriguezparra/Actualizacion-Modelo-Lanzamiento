# -*- coding: utf-8 -*-
"""
@author: Team REOS

En este módulo se incluye una clase que define los coeficientes de fuerzas de
un lanzador (resistencia, normal, momento).

Para ello previamente se realizan unos cálculos geométricos necesarios y se
definen ciertas funciones de apoyo, además del de intervalo de régimen
transónico.

Para corregir el régimen transónico se aproximan polinómicamente las funciones
globales:
    - cntotal()
    - cdtotal()
    - cmtotal()
"""

from math import log10, pi, degrees, atan, sqrt, cos, radians
from numpy import size, array, ndarray, dot

from inputs_iniciales import MASAS, GASTOS, N_ETAPAS
from modulos.modulo_aproximacion import aprox_pol
from modulos.atmosfera.modelo_msise00 import (GAMMA, density, temperature,
                                              R_AIR, viscosity)
from modulos.aerodinamica.geometria_misil import (DIAMETRO_M, LONGITUD_CONO,
                                                  LONGITUD_MISIL, TIPO_NARIZ,
                                                  DIAMETRO_S)
from modulos.aerodinamica.geometria_misil import (NUM_ALETAS, FACTOR_ALETA,
                                                  ESPESOR_ALETA, CMEDIA_ALETA,
                                                  CRAIZ_ALETA,
                                                  ENVERGADURA_ALETAS)
from modulos.aerodinamica.geometria_misil import (ESPESOR_ALA, FACTOR_ALA,
                                                  CRAIZ_ALA, X_ALA,
                                                  ENVERGADURA_ALA)
from errores import NoseError
import warnings


# CARACTERÍSTICAS GEOMÉTRICAS DEL MISIL
# -------------------------------------

# Ángulo del cuerpo(deg).
ANGULO_NARIZ = [degrees(atan(.5 * DIAMETRO_M / LONGITUD_CONO)),
                2*degrees(atan(.5 * DIAMETRO_M / LONGITUD_CONO))]

# Superficie exterior del cono (m2)
SUP_CONO = pi * DIAMETRO_M / 2 * sqrt(LONGITUD_CONO**2 + DIAMETRO_M**2 / 4)

# Superficie de referencia del misil (m2)
SREF_MISIL = pi * DIAMETRO_M**2 / 4

# Superficie de la base (m2)
SBASE = SREF_MISIL  # No tiene porque ser igual a la de referencia.

# Superficie del cilindro en cada etapa (m2)
SUP_CIL = []
for s in LONGITUD_MISIL:
    if s == LONGITUD_MISIL[-1]:
        break
    SUP_CIL.append(pi*DIAMETRO_M*(s - LONGITUD_CONO))

# Superficie salida de gases del cilindro en cada etapa (m2)
SGASES = []
for i in range(size(DIAMETRO_S)):
    sgases_aux = pi * (DIAMETRO_S[i])**2 / 4
    SGASES.append(sgases_aux)

# Superficie total de las aletas (m2)
SW_ALETA = ENVERGADURA_ALETAS*CMEDIA_ALETA/2
SWTOTAL_ALETAS = SW_ALETA * NUM_ALETAS 

# Superficie total del ala (m2)
SW_ALA= CRAIZ_ALA*ENVERGADURA_ALA/2 

FLECHA_ALETA = 0  # Se suponen aletas rectangulares
FLECHA_ALA = atan(CRAIZ_ALA/ENVERGADURA_ALA)  # rad
ESPESOR_MEDIO_ALA = ESPESOR_ALA/CRAIZ_ALA
ESPESOR_MEDIO_ALETA = ESPESOR_ALETA/CMEDIA_ALETA
A_ALA = 2*ENVERGADURA_ALA/CRAIZ_ALA
A_ALETAS = ENVERGADURA_ALETAS/CMEDIA_ALETA

# Factores de forma para el cono y el cilindro obtenidos de los apuntes UPM
# Se utiilzan para los coeficientes de fricción
FF_CONO = 4/sqrt(3)
FF_CILINDRO = 1.25

# Parámetros para el cálculo de del coeficiente normal
Kwb = 1+DIAMETRO_M/(ENVERGADURA_ALETAS+DIAMETRO_M)
Kbw = ((DIAMETRO_M/(DIAMETRO_M+ENVERGADURA_ALETAS))*
       (1+DIAMETRO_M/(ENVERGADURA_ALETAS+DIAMETRO_M)))
kbm = DIAMETRO_M/(ENVERGADURA_ALETAS+DIAMETRO_M)
kmb = 1

# Centros de presión de cada parte del lanzador. Como referencia se toma la
# proa del misil, es decir, se miden las distancias desde la punta del lanzador
xcp_cono=2/3*LONGITUD_CONO
xcp_cil = []
for xlan in LONGITUD_MISIL:
    if xlan == LONGITUD_MISIL[-1]:
        break
    xcp_cilindro_aux=(xlan+LONGITUD_CONO)/2
    xcp_cil.append(xcp_cilindro_aux)
xcp_aletas=LONGITUD_MISIL[0]-CMEDIA_ALETA/2
xcp_ala=X_ALA-CRAIZ_ALA/2

# Distancias de la punta del cono al centro de gravedad de cada etapa por
# separado: payload, etapa 1, etapa 2, ..., etapa n.
MAT = ndarray(shape=(N_ETAPAS + 1,N_ETAPAS + 1), dtype=float)
L_ETAPAS = []
for i in range(N_ETAPAS + 1):
    for j in range(N_ETAPAS + 1):
        if i == j:
            MAT[i,j] = 1/2
        elif i < j:
            MAT[i,j] = 1
        else:
            MAT[i,j] = 0
    if i != N_ETAPAS:
        L_ETAPAS.append(LONGITUD_MISIL[i] - LONGITUD_MISIL[i + 1])
    else:
        L_ETAPAS.append(LONGITUD_MISIL[i])
X_ETAPAS = dot(MAT, L_ETAPAS)

# INTERVALO DE RÉGIMEN TRANSÓNICO
# -------------------------------
inicio_transonico = 0.85
fin_transonico = 1.15
def condicion_transonico(mach):
    a = (inicio_transonico < mach < fin_transonico)
    return a

# FUNCIONES DE APOYO PARA EL CÁLCULO DE COEFICIENTES
# --------------------------------------------------

def posicion_cg(diccionario_tiempo, t):
    '''
    Calculo de la posición del centro de gravedad en función de:
        - t : float
              tiempo global del problema.
        - diccionario_tiempo : dictionary
              diccionario con tiempo inicial de lanzamiento y tiempos
              característicos de cada etapa.
    '''
    
    
    def funcion_heaviside(t, t0):
        '''
        Función que determina el escalón en las masas del lanzador. Donde:
            - t : float
                  tiempo global transcurrido
            - t0 : float
                  tiempo global para el que se consume el combustible. Vendrá
                  definido por el diccionario de tiempos.
        '''
        if t < t0:
            return 1
        else:
            return 0
        
        
    pesos_etapas = []
    for n in range(N_ETAPAS):
        key = 'etapa_' + str(n + 1)
        var_etapa = diccionario_tiempo[key]
        if t <= var_etapa[0]:
            w_i = MASAS[n]
        else:
            w_i = ((MASAS[n] - GASTOS[n]*
                   (t - var_etapa[0]))*funcion_heaviside(t, var_etapa[1]))
        pesos_etapas.append(w_i)
    w_p = MASAS[-1]  # Carga de pago
    pesos_etapas.append(w_p)
    pesos_etapas = array(pesos_etapas)
    sum_w = sum(pesos_etapas)
    x_cdg_p = dot(pesos_etapas, X_ETAPAS)/sum_w
    return x_cdg_p


def factor_Q(mach, flecha):
    '''
    Función que determina el factor de correlación de la superficie
    sustentadora en función de una gráfica con 4 rectas y de:
        - mach : float
                 número de mach
        - flecha : float
                 ángulo de flecha para el elemento sustentador (rad)
    '''
    Mach_Int = [0.25, 0.6, 0.8, 0.9]
    y0 = (-2.2663*cos(flecha)**3 + 4.111*cos(flecha)**2 -
          1.697*cos(flecha) + 0.9131)
    y1 = (-2.2*cos(flecha)**3 + 3.9006*cos(flecha)**2 
          - 1.4746*cos(flecha) + 0.916)
    y2 = (-1.8612*cos(flecha)**3 + 3.3174*cos(flecha)**2 -
          1.2067*cos(flecha) + 1.0065)
    y3 = (-1.9902*cos(flecha)**3 + 3.7697*cos(flecha)**2 -
          1.6533*cos(flecha) + 1.2311)
    y = [y0, y1, y2, y3]
    
    if mach<= 0.25:
        return y[0]
    elif 0.25 < mach < 0.6:
        return (y[0]+(y[1]-y[0])/(Mach_Int[1]-Mach_Int[0])*(mach-Mach_Int[0]))
    elif mach == 0.6:
        return y[1]
    elif 0.6 < mach < 0.8:
        return (y[1]+(y[2]-y[1])/(Mach_Int[2]-Mach_Int[1])*(mach-Mach_Int[1]))
    elif mach == 0.8:
        return y[2]
    elif 0.8 < mach < 0.9:
        return (y[2]+(y[3]-y[2])/(Mach_Int[3]-Mach_Int[2])*(mach-Mach_Int[2]))
    elif mach == 0.9:
        return y[3]
    elif 0.9 < mach < 1:
        return (y[3]+(y[3]-y[2])/(Mach_Int[3]-Mach_Int[2])*(mach-Mach_Int[3]))


def f_comp(mach):
    '''
    Factor de compresibilidad de flujo en función del mach.
    '''
    # SUBSÓNICO
    if mach < 1:
        return sqrt(1 - mach**2)
    # SUPERSÓNICO
    else:
        return sqrt(mach**2 - 1)
  

# CLASE QUE DEFINE LOS COEFICIENTES DE FUERZA
# -------------------------------------------

class CoeficienteFuerza(object):
    '''
    Clase que define los atributos y métodos de coeficientes de fuerzas
    del lanzador.
    
    Parámetros
    ----------
    etapa : int
           Indica la etapa del lanzador, con la que queda definida su longitud.
           
    delta : float
           Ángulo de deflexión de mando (rad).
           
    alpha : float
           Ángulo de ataque del lanzador (rad).
           
    aletas, ala, prop : boolean
           Indican si existen o no las aletas, ala y la propulsión.
    
    Atributos
    ---------
    _etapa : int
            Etapa del lanzador.
            
    _deflexion_mando : float
            Ángulo de deflexión de mando (rad).
            
    _angulo_ataque : float
            Ángulo de ataque del lanzador (rad).
            
    _aletas, _ala, _prop : bool
            Indican si existen o no las aletas, el ala y propulsión.
            
    cdtotal : float
            Valor del coeficiente de resistencia total.
            
    cntotal : float
            Valor del coeficiente normal total.
            
    cmtotal : float
            Valor del coeficiente de momento total.
    '''
    def __init__(self, etapa=1, delta=0, alpha=0, propulsion=False,
                 aletas=False, ala=False):
        self._etapa = etapa
        self._deflexion_mando = delta
        self._angulo_ataque = alpha
        self._prop = propulsion
        self._aletas = aletas
        self._ala = ala

        return None  # __init__ retorna None por defecto, no debe devolver otra cosa.
    
    
    # MÉTODOS QUE PERMITEN LA VARIACIÓN DE ATRIBUTOS
    # ----------------------------------------------
    
    
    def set_etapa(self, etapa):
        '''
        Asigna un valor al atributo '_etapa'. Éste ha de ser como máximo el
        número de etapas que haya y como mínimo 1.
        '''
        if etapa > size(LONGITUD_MISIL):
            if size(LONGITUD_MISIL) == 1:
                raise ValueError('El número de etapa ha de ser 1')
            raise ValueError('El número de la etapa ha de estar entre 1 y ' +
                             str(size(LONGITUD_MISIL)) + '.')
        if etapa < 1:
            raise ValueError('La etapa del lanzador no puede ser menor que 1.')

        self._etapa = etapa
    
    
    def set_delta(self, delta):
        '''
        Asigna un valor al atributo '_deflexion_mando'.
        '''
        if delta >= radians(30):
            warnings.warn('Cuidado: El valor de la deflexión ' +
                          'de mando supera 30º (deg)')
        self._deflexion_mando = delta
    
    
    def set_alpha(self, alpha):
        '''
        Asigna un valor al atributo '_angulo_ataque'.
        '''
        if alpha >= radians(30):
            warnings.warn('Cuidado: El valor del ángulo de ataque' +
                          ' supera 30º (deg)')
        self._angulo_ataque = alpha
    
    
    def set_aletas(self, aletas=True):
        '''
        Define si hay aletas o no.
        '''
        if type(aletas) is not bool:
            nom = 'set_aletas()'
            nom_var = 'aletas'
            raise ValueError('El argumento ' + nom_var + ' de la función ' +
                             nom + ' ha de ser un booleano y no: ' +
                             str(aletas) + ', lo que es ' + str(type(aletas)))
        self._aletas = aletas
    
    
    def set_ala(self, ala=True):
        '''
        Define si hay ala o no.
        '''
        if type(ala) is not bool:
            nom = 'set_ala()'
            nom_var = 'ala'
            raise ValueError('El argumento ' + nom_var + ' de la función ' +
                             nom + ' ha de ser un booleano y no: ' +
                             str(ala) + ', lo que es ' + str(type(ala)))
        self._ala = ala
    
    
    def set_propulsion(self, prop=True):
        '''
        Define si hay propulsión o no.
        '''
        if type(prop) is not bool:
            nom = 'set_propulsion()'
            nom_var = 'prop'
            raise ValueError('El argumento ' + nom_var + ' de la función ' +
                             nom + ' ha de ser un booleano y no: ' +
                             str(prop) + ', lo que es ' + str(type(prop)))
        self._prop = prop
    
    
    # MÉTODOS QUE CALCULAN LOS COEFICIENTES DE RESISTENCIA
    # ----------------------------------------------------
    
    def cb_misil(self, mach):
        '''
        Esta función define la resistencia de base del misil en función del
        Mach. Para su definición se ha utilizado la figura 12 del documento
        'Misiles - Parte II.pdf' de los apuntes de la UPM.
        Los demás parámetros son:
            - PROP: Es un booleano que indica si hay propulsión o no.
            - n_etapa: Indica el numero de la etapa en la que estamos, pues es
                       necesario para la superficie de salida de gases
        '''
        if self._prop == False:
            if mach < 0.8:
                Cdb_prima = 0.14026
                Cdb = Cdb_prima*SBASE/SREF_MISIL
            elif 0.8 <= mach < 1:
                Cdb_prima = (3.2751*mach**3 - 8.1789*mach**2 +
                             6.8665*mach - 1.7954)
                Cdb = Cdb_prima*SBASE/SREF_MISIL
            elif 1 <= mach < 1.095:
                Cdb_prima = (-150.3*mach**3 + 466.52*mach**2 -
                             481.64*mach + 165.59)
                Cdb = Cdb_prima*SBASE/SREF_MISIL
            elif 1.095 <= mach <= 1.5:
                Cdb_prima = 0.2226*mach**2 - 0.7103*mach + 0.7391
                Cdb = Cdb_prima*SBASE/SREF_MISIL
            elif mach > 1.5:
                Cdb_prima = 0.0076*mach**2 - 0.0854*mach + 0.2846
                Cdb = Cdb_prima*SBASE/SREF_MISIL
        else:
            if mach < 0.8:
                Cdb_prima = 0.14026
                Cdb = Cdb_prima*(SBASE-SGASES[self._etapa - 1])/SREF_MISIL
            elif 0.8 <= mach < 1:
                Cdb_prima = (3.2751*mach**3 - 8.1789*mach**2 +
                             6.8665*mach - 1.7954)
                Cdb = Cdb_prima*(SBASE-SGASES[self._etapa - 1])/SREF_MISIL
            elif 1 <= mach < 1.095:
                Cdb_prima = (-150.3*mach**3 + 466.52*mach**2 -
                             481.64*mach + 165.59)
                Cdb = Cdb_prima*(SBASE-SGASES[self._etapa - 1])/SREF_MISIL
            elif 1.095 <= mach <= 1.5:
                Cdb_prima = 0.2226*mach**2 - 0.7103*mach + 0.7391
                Cdb = Cdb_prima*(SBASE-SGASES[self._etapa - 1])/SREF_MISIL
            elif mach > 1.5:
                Cdb_prima = 0.0076*mach**2 - 0.0854*mach + 0.2846
                Cdb= Cdb_prima*(SBASE-SGASES[self._etapa - 1])/SREF_MISIL
    
        return Cdb
    

    def cf_cono(self, mach, alt):
        '''
        Coeficiente de fricción del cono.
        
        Para una primera aproximación solo se tiene en cuenta que el flujo
        alrededor del cono es laminar, para ello se impone una condición en
        el Reynolds que es irreal: es laminar para Re < 1e10.
        '''
        vel = mach*sqrt(GAMMA * R_AIR * temperature(alt))  # velocidad respecto al aire
        re_cono = density(alt)*vel*LONGITUD_CONO/viscosity(alt)
        # LAMINAR
        if re_cono < 1e10:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE
            cfi_cono = .664 * re_cono**(-1 / 2) * FF_CONO
            # CÁLCULO COEFICIENTE DE FRICCIÓN TOTAL
            cfm_cono = cfi_cono / (1 + .17 * mach**2)**.1295
        # TURBULENTO
        else:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE
            cfi_cono = .288 / log10(re_cono)**2.45 * FF_CONO
            # CÁLCULO COEFICIENTE DE FRICCIÓN TOTAL
            cfm_cono = cfi_cono / (1 + (GAMMA - 1) / 2 * mach**2)**.467
        return cfm_cono * SUP_CONO / SREF_MISIL


    def cf_cil(self, mach, alt):
        '''
        Coeficiente de fricción del cilindro.
        
        En este caso se considera que el flujo es siempre turbulento y se usa
        el método inverso que para el cono: es laminar para Re < 1e5.
        
        Los parámetros que se utilizan son:
            - mach : float
                  número de mach.
            - alt : float
                  altitud del lanzador (m).
        '''
        vel = mach*sqrt(GAMMA * R_AIR * temperature(alt))  # velocidad respecto al aire
        re_cil = (density(alt)*vel*
                  ((LONGITUD_MISIL[self._etapa - 1] - LONGITUD_CONO)/
                   viscosity(alt)))
        # LAMINAR
        if re_cil < 1e5:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE
            cfi_cil = .664 * re_cil**(-1 / 2) * FF_CILINDRO
            # CÁLCULO COEFICIENTE DE FRICCIÓN TOTAL
            cfm_cil = cfi_cil / (1 + .17 * mach**2)**.1295
        # TURBULENTO
        else:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE
            cfi_cil = .288 / log10(re_cil)**2.45 * FF_CILINDRO
            # CÁLCULO COEFICIENTE DE FRICCIÓN TOTAL
            cfm_cil = cfi_cil / (1 + (GAMMA - 1) / 2 * mach**2)**.467
        return cfm_cil * SUP_CIL[self._etapa - 1] / SREF_MISIL    
    
    
    def cf_aletas(self, mach, alt):
        '''
        Coeficiente de fricción de las aletas. En función de:
            - mach : float
                  número de mach.
            - alt : float
                  altitud del lanzador (m).
        '''
        vel = mach*sqrt(GAMMA * R_AIR * temperature(alt))  # velocidad respecto al aire
        re_aleta = density(alt)*vel*CRAIZ_ALETA/viscosity(alt)
        # LAMINAR.
        if re_aleta < 1e5:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE.
            cfialetas = .664 / re_aleta**.5
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL MEDIO.
            cf1aletas = 2 * cfialetas
            # CÁLCULO COEFICIENTE DE FRICCIÓN COMPRESIBLE.
            cfmaletas = cf1aletas * (0.0001*mach**3 - 0.0031*mach**2 -
                                     0.0011*mach + 1.0021)
        # TURBULENTO.
        else:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE.
            cfialetas = .288 * (log10(re_aleta))**(-2.45)
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL COMPRESIBLE.
            cf1aletas = 1.25 * cfialetas
            # CÁLCULO COEFICIENTE DE FRICCIÓN MEDIO.
            cfmaletas = cf1aletas *(-0.0002*mach**4 + 0.005*mach**3 -
                                    0.0387*mach**2 + 0.0203*mach + 0.9933)
        return cfmaletas * SWTOTAL_ALETAS / SREF_MISIL


    def cf_ala(self, mach, alt):
        '''
        Coeficiente de fricción del ala. En función de:
            - mach : float
                  número de mach.
            - alt : float
                  altitud del lanzador (m).
        '''
        vel = mach*sqrt(GAMMA * R_AIR * temperature(alt))  # velocidad respecto al aire
        re_ala = density(alt)*vel*CRAIZ_ALA/viscosity(alt)
        # LAMINAR.
        if re_ala < 1e5:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE.
            cfiala = .664 / re_ala**.5
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL MEDIO.
            cf1ala = 2 * cfiala
            # CÁLCULO COEFICIENTE DE FRICCIÓN COMPRESIBLE.
            cfmala = cf1ala * (0.0001*mach**3 - 0.0031*mach**2 - 0.0011*mach +
                               1.0021)
        # TURBULENTO.
        else:
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL INCOMPRESIBLE.
            cfiala = .288 * (log10(re_ala))**(-2.45)
            # CÁLCULO COEFICIENTE DE FRICCIÓN LOCAL COMPRESIBLE.
            cf1ala = 1.25 * cfiala
            # CÁLCULO COEFICIENTE DE FRICCIÓN MEDIO.
            cfmala = cf1ala *(-0.0002*mach**4 + 0.005*mach**3 - 0.0387*mach**2 +
                              0.0203*mach + 0.9933)
        return cfmala * SW_ALA / SREF_MISIL
    

    def cw_misil(self, mach, alt, tipo=0):
        '''
        Coeficiente de onda del misil (Apuntes UPM). Se considera que la
        resistencia de onda del misil ocurre en el cono, por lo tanto, el 
        coeficiente de fricción que se utiliza es sólo el del cono.
        
        Depende de:
            - mach : float
                     número de mach.
            - alt : float
                     altitud del lanzador (m).
            - tipo : int
                     tipo de nariz, 0-cono, 1-ojiva. Por defecto es cono.
        '''
        ratio = LONGITUD_CONO / DIAMETRO_M
        
        if tipo == 0:
            if mach >= 1:
            # RÉGIMEN SUPERSÓNICO.
                return (.083 + .096/mach**2)*(ANGULO_NARIZ[tipo]/10)**1.69
            # RÉGIMEN SUBSÓNICO: Fórmula semiempírica - Resistencia de presión
            return 0
        
        elif tipo == 1:
            # Se le aplica una corrección a la resistencia debida al cono.
            if mach >= 1:
            # RÉGIMEN SUPERSÓNICO.
                cd_cono = (.083 + .096/mach**2)*(ANGULO_NARIZ[tipo]/10)**1.69
                cd_correccion = (1 - (392*ratio**2 - 32)/(28*(mach + 18)*ratio**2))
                return cd_cono*cd_correccion
            # RÉGIMEN SUBSÓNICO: Fórmula semiempírica - Resistencia de presión
            return 0
        
        else:
            raise NoseError(tipo)


    def cw_aletas(self, mach, alt):
        '''
        Coeficiente de resistencia de onda de las aletas.
        Coefiente m: posición del espesor máximo.
        
        Parámetros:
            - mach : float
                     número de mach
            - alt : float
                     altitud de vuelo (m).
        '''
        m = 0.5
        if m >= 3:
            parametro_L = 1.2
        else:
            parametro_L = 2
    
        # RÉGIMEN SUBSÓNICO.
        if mach < 1:
            cd_w_aleta = ((parametro_L*ESPESOR_MEDIO_ALETA +
                           100*ESPESOR_MEDIO_ALETA**4)*
                          ((2*self.cf_aletas(mach, alt))*
                           factor_Q(mach, FLECHA_ALETA)))
            
            return cd_w_aleta*SWTOTAL_ALETAS/SREF_MISIL
        # RÉGIMEN SUPERSÓNICO
        else:
            cdw = (4*FACTOR_ALETA*
                   atan(ESPESOR_MEDIO_ALETA)**2/(sqrt(mach**2 - 1)))
            return cdw
    

    def cw_ala(self, mach, alt):
        '''
        Coeficiente de resistencia de onda del ala.
        Coefiente m: posición del espesor máximo.
        Parámetros:
            - mach : float
                     número de mach
            - alt : float
                     altitud de vuelo (m).
        '''
        m = 0.5
        if m >= 3:
            parametro_L = 1.2
        else:
            parametro_L = 2
        
        # SUBSÓNICO
        if mach < 1:
            cd_w_ala = (parametro_L*
                        (ESPESOR_MEDIO_ALA + 100*ESPESOR_MEDIO_ALA**4)*
                        (2/SREF_MISIL*self.cf_ala(mach, alt))*
                        ENVERGADURA_ALA*CRAIZ_ALA/2*factor_Q(mach, FLECHA_ALA))
        # SUPERSÓNICO
        else:
            cd_w_ala = (FACTOR_ALA*4*atan(ESPESOR_MEDIO_ALA)**2/
                        (sqrt(mach**2-1)))
            
        return (cd_w_ala * SW_ALA/SREF_MISIL)
    
    
    def cd_total(self, mach, alt):
        '''
        Coeficiente de resistencia total del misil.
        Además crea el atributo cdtotal.
        
        Definido por:
            - mach : float
                     número de mach de vuelo.
            - alt : float
                     altitud de vuelo (m).
        '''
        # CASO TRANSÓNICO
        ev = condicion_transonico(mach)  # Evaluación de régimen transónico
        if ev:
            self.cdtotal = self.cd_transonico(mach, alt)
            return self.cdtotal
        
        # CÁLCULO DEL COEFICIENTE DE RESISTENCIA BASE.
        cd_base_misil = self.cb_misil(mach)
        
        # CÁLCULO DEL COEFICIENTE DE FRICCIÓN
        CD_F = [self.cf_cono(mach, alt), self.cf_cil(mach, alt)]
        if self._aletas:
            CD_F.append(self.cf_aletas(mach, alt))
        if self._ala:
            CD_F.append(self.cf_ala(mach, alt))
        
        cd_friccion = sum(CD_F)
        
        # CÁLCULO DEL COEFICIENTES DE ONDA.
        CD_W = [self.cw_misil(mach, alt, tipo=TIPO_NARIZ)]
        if self._aletas:
            CD_W.append(self.cw_aletas(mach, alt))
        if self._ala:
            CD_W.append(self.cw_ala(mach, alt))

        cd_onda = sum(CD_W)
        
        # Coeficiente de resistencia parásita.
        cd0 = cd_base_misil + cd_friccion + cd_onda
        
        # Coeficiente de resistencia inducida.
        cnal = self.cnalpha(mach)
        cndel = 0
        if self._aletas:
            cndel = self.cndelta_aletas(mach)
        cdi = cnal*self._angulo_ataque**2 + cndel*self._deflexion_mando**2
        
        self.cdtotal = cd0 + cdi
        
        if self._etapa > 2:
            self.cdtotal = 2.52 # Cd del satélite (atmósfera a muy baja densidad)
        
        return self.cdtotal
    
    
    def cd_transonico(self, mach, alt):
        '''
        Corrección del coeficiente de resistencia para régimen transónico.
        
        La corrección consiste en elegir 2 puntos entre el mach de inicio y el
        de fin de régimen, a continuación se dan 2 valores (tomados por prueba
        y error) para realizar una aproximación polinómica de grado 3.
        Estos 2 puntos y valores se han tomado mediante prueba y error.
        '''
        mach_1 = (0.3 + 0.7*inicio_transonico)
        mach_2 = (0.5 + 0.5*fin_transonico)
        mach_list = [inicio_transonico, mach_1, mach_2, fin_transonico]
        cd_1 = self.cd_total(inicio_transonico, alt)
        cd_2 = self.cd_total(fin_transonico, alt)
        cd_list = [cd_1, (cd_1 + 0.04), (cd_2 - 0.05), cd_2]
        coef = aprox_pol(mach_list, cd_list, 3)
        
        res = 0
        for i, ci in enumerate(coef):
            res = res + ci*mach**i
        
        return res


    # MÉTODOS QUE CALCULAN LOS COEFICIENTES NORMALES DE ALPHA Y DELTA
    # ---------------------------------------------------------------
    
    def cnalpha_cono(self):
        '''
        Coeficiente normal de alfa del cono.
        Es constante y vale 2 (Apuntes UPM).
        '''
        return 2
    
    
    def cnalpha_cil(self):
        '''
        Coeficiente normal de alfa del cilindro en función de:
            - alpha : float
                    ángulo de ataque del misil (rad)
            - lon : float
                    longitud del cilindro que depende de cada etapa (m)
        '''
        longitud_cil = LONGITUD_MISIL[self._etapa - 1] - LONGITUD_MISIL[-1]
        return 1.1*self._angulo_ataque*2*longitud_cil/(pi*DIAMETRO_M/2)
    
    
    def cnalpha_ala(self, mach):
        '''
        Coeficiente normal de alfa del ala en función del mach.
        '''
        cni_ala = 4/f_comp(mach)*(1-1/(2*A_ALA*f_comp(mach)))
        return (cni_ala*(Kwb+Kbw)*SW_ALA/SREF_MISIL)
    
    
    def cnalpha_aletas(self, mach):
        '''
        Coeficiente normal de alfa de las aletas dependiente del mach.
        '''
        F_deflexion = 0.6  # Factor de deflexión de la estela.
        
        cni_aletas = 4/f_comp(mach)*(1-1/(2*A_ALETAS*f_comp(mach)))
        return (cni_aletas*(kbm+kmb)*F_deflexion*(2*SW_ALETA)/SREF_MISIL)
    
    
    def cnalpha(self, mach):
        '''
        Coeficiente normal de alfa total.
        '''
        CNALPHA = [self.cnalpha_cono(), self.cnalpha_cil()]
        if self._ala:
            CNALPHA.append(self.cnalpha_ala(mach))
        if self._aletas:
            CNALPHA.append(self.cnalpha_aletas(mach))
        
        cnalpha_total = sum(CNALPHA)
        return cnalpha_total


    def cndelta_aletas(self, mach):
        '''
        Coeficiente normal delta debida a la deflexión de mando dependiente del
        mach.
        Se diferencia de cnalpha_aletas() en que no se tiene en cuenta el
        factor de deflexión.
        '''
        if self._aletas:
            cni_mando = 4/f_comp(mach)*(1-1/(2*A_ALETAS*f_comp(mach)))
            cndelta = cni_mando*(Kwb+Kbw)*2*SW_ALETA/SREF_MISIL
            return cndelta
        else:
            return 0
    
    
    def cn_total(self, mach):
        '''
        Cálculo del coeficiente normal total en función del mach.
        Además crea el atributo cntotal.
        '''
        # CASO TRANSÓNICO
        ev = condicion_transonico(mach)
        if ev:
            self.cntotal = self.cn_transonico(mach)
            return self.cntotal
        
        # CASO NO TRANSÓNICO
        self.cntotal = (self.cnalpha(mach)*self._angulo_ataque +
                        self.cndelta_aletas(mach)*self._deflexion_mando)
        return self.cntotal
    
    
    def cn_transonico(self, mach):
        '''
        Corrección del coeficiente normal para régimen transónico.
        
        La corrección consiste en suponer un valor de cn para M = 1
        para realizar una aproximación polinómica de grado 2. 
        Este valor se ha tomado por prueba y error.
        '''
        mach_list = [inicio_transonico, 1, fin_transonico]
        cn_1 = self.cn_total(inicio_transonico)
        cn_2 = self.cn_total(fin_transonico)
        cn_list = [cn_1, cn_1*0.95, cn_2]
        coef = aprox_pol(mach_list, cn_list, 2)
        
        res = 0
        for i, ci in enumerate(coef):
            res = res + ci*mach**i
        
        return res


    # MÉTODO QUE CALCULA EL COEFICIENTE DE MOMENTO DE ALFA Y DELTA.
    # -----------------------------------------------------
    
    def cmalpha(self, mach, x_cdg):
        '''
        Cálculo del coeficiente de momento de alfa en función del mach y la 
        posición del centro del gravedad, para lo cual se usará la función 
        posicion_cg() que depende del instante de tiempo.
        '''
        lon_lanz = LONGITUD_MISIL[self._etapa - 1]
        d_cono = x_cdg - xcp_cono
        d_cil = x_cdg - xcp_cil[self._etapa - 1]
        cm_alpha_cono = self.cnalpha_cono()*d_cono
        cm_alpha_cil = self.cnalpha_cil()*d_cil
        cm_alpha_total = cm_alpha_cono + cm_alpha_cil
        
        if self._aletas:
            d_aletas = x_cdg - xcp_aletas
            cm_alpha_total = (cm_alpha_total + 
                              self.cnalpha_aletas(mach)*d_aletas)
        if self._ala:
            d_ala = x_cdg - xcp_ala
            cm_alpha_total = cm_alpha_total + self.cnalpha_ala(mach)*d_ala
        
        return cm_alpha_total/lon_lanz
    
    
    def cmdelta(self, mach, x_cdg):
        '''
        Cálculo del coeficiente de momento de delta en función del mach y de la
        posición del centro de gravedad para cierto instante.
        Devuelve 0 para el caso en el que no haya aletas.
        '''
        if self._aletas:
            lon_lanz = LONGITUD_MISIL[self._etapa - 1]
            d_aletas = x_cdg - xcp_aletas
            return self.cndelta_aletas(mach)*d_aletas/lon_lanz
        else:    
            return 0
    
    
    def cm_total(self, mach, x_cdg):
        '''
        Calcula el coeficiente de momentos total en función de los coef. de
        alfa y delta, así como del ángulo de ataque y de deflexión.
        Además crea el atributo cmtotal.
        '''
        # CASO TRANSÓNICO
        ev = condicion_transonico(mach)
        if ev:
            self.cmtotal = self.cm_transonico(mach, x_cdg)
            return self.cmtotal
        
        # CASO NO TRANSÓNICO
        self.cmtotal = (self.cmalpha(mach, x_cdg)*self._angulo_ataque +
                         self.cmdelta(mach, x_cdg)*self._deflexion_mando)
        return self.cmtotal
    
    
    def cm_transonico(self, mach, x_cdg):
        '''
        Corrección del coeficiente de momentos para régimen transónico.
        
        La corrección consiste en suponer un valor de cm para M = 1, en función
        del valor que éste toma para M = inicio_transonico para realizar una
        aproximación polinómica de grado 2.
        Este valor se ha tomado por prueba y error.
        '''
        mach_list = [inicio_transonico, 1, fin_transonico]
        cm_1 = self.cm_total(inicio_transonico, x_cdg)
        cm_2 = self.cm_total(fin_transonico, x_cdg)
        cm_list = [cm_1, cm_1*0.95, cm_2]
        coef = aprox_pol(mach_list, cm_list, 2)
        
        res = 0
        for i, ci in enumerate(coef):
            res = res + ci*mach**i
        
        return res
