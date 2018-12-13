# -*- coding: utf-8 -*-
"""
@author: Team REOS

Módulo que contiene las integraciones del movimiento
"""

from numpy import inf, dot, arccos, degrees
from numpy.linalg import norm

from errores import TimeDictionaryError
from mecanica import numero_mach, altitud, aceleracion, resistencia, sustentacion, peso, ley_alfa
from modulos.aerodinamica.aero_misil import CoeficienteFuerza
from modulos.atmosfera.gravedad import RT
from inputs_iniciales import GAMMA_INY_MIN

DT = .05


def step(mas, tie, pos, vel, gasto, isp, coeficientes_fuerza, vloss=0,
         masa_minima=0, step_size=DT, perdidas=False, dic_tie={}):
    '''
    Paso de integración que se utiliza en las demás funciones de integración.
    Devuelve la masa, la velocidad, el tiempo y la posición habiendo
    transcurrido un diferencial de tiempo DT.
    También devuelve las pérdidas en el caso de que se tengan en cuenta.

    mas : float
        Masa.

    tie : float
        Tiempo.

    pos : array (3 componentes)
        Posición.

    vel : array (3 componentes)
        Velocidad.

    gasto : float
        Gasto másico.

    isp : float
        Impulso específico.
    
    coeficientes_fuerza : object
        Es un objeto en el cual está definida la aerodinámica del lanzador.

    vloss : float
        Pérdidas de velocidad. Por defecto es vloss=0.

    masa_minima : float
        Masa mínima. Por defecto es masa_minima=0.

    step_size : float
        Salto temporal. Por defecto es step_size=DT (DT=0.05).

    perdidas : bool
        Indica si deben computarse las pérdidas de velocidad o no. Por
        defecto es perdidas=False.
    dic_tie : dictionary
        Define el lanzamiento en función del tiempo inicial de lanzamiento y
        los tiempos característicos de cada etapa. Por defecto está vacío.
    '''
    
    dtl = step_size
    masa = mas - gasto * dtl
    if masa < masa_minima:
        masa = masa_minima
        dtl = (mas - masa_minima) / gasto
    tiempo = tie + dtl
    if coeficientes_fuerza._etapa == 1:
        coeficientes_fuerza._angulo_ataque = ley_alfa(tiempo, dic_tie)
        
    alfa = degrees(coeficientes_fuerza._angulo_ataque) # Valor en grados del ángulo de ataque
    
    acc = aceleracion(pos, vel, (mas + masa) / 2, gasto, isp,
                      coeficientes_fuerza)
    posicion = pos + vel * dtl + .5 * acc * dtl**2
    velocidad = vel + acc * dtl
    factor_carga = norm(sustentacion(posicion, velocidad, coeficientes_fuerza)) / norm(peso(posicion, masa))
    
    mach = numero_mach(posicion, velocidad)
    alt = altitud(posicion)

    cd = coeficientes_fuerza.cd_total(mach, alt)
    cn = coeficientes_fuerza.cn_total(mach)
    
    # Pérdida de velocidad
    if perdidas:
        pos_media = (pos + posicion) / 2
        vel_media = (vel + velocidad) / 2
        mas_media = (mas + masa) / 2
        loss_aero = (dtl*
                     norm(resistencia(pos_media, vel_media, coeficientes_fuerza))/
                     mas_media)
        loss_grav = -dtl * (dot(peso(pos_media, mas_media), vel_media)
                            / (norm(vel_media) * mas_media))
        vloss = vloss + loss_aero + loss_grav
        return masa, tiempo, posicion, velocidad, vloss, factor_carga, cd, cn, alfa
    return masa, tiempo, posicion, velocidad, factor_carga, cd, cn, alfa


def etapa(masa_etapa, masa_total, gasto, isp, posicion_inicial,
          velocidad_inicial, coeficientes_fuerza, tiempo_inicial=0, vloss=0,
          step_size=DT, altura_maxima=inf, perdidas=False, imprimir=False,
          archivo2=False, dic_tie={}):
    '''
    Ejecuta todos los pasos de integración de una etapa.
    Devuelve la masa, la velocidad, el tiempo y la posición una vez haya
    llegado a una condición de parada:
        1- Que se supere la altura máxima
        2- Que el misil esté cayendo
        3- Que se haya consumido todo el propulsante
    También devuelve las pérdidas en el caso de que se tengan en cuenta.

    masa_etapa : float
        Masa inicial de la etapa.

    masa_total : float
        Masa total inicial del lanzador.

    gasto : float
        Gasto másico.

    isp : float
        Impulso específico.

    posicion_inicial : array (3 componentes)
        Posición inicial.

    velocidad_inicial : array (3 componentes)
        Velocidad inicial.
    
    coeficientes_fuerza : object
        Es un objeto en el cual está definida la aerodinámica del lanzador.

    tiempo_inicial : float
        Tiempo inicial. Por defecto es tiempo_inicial=0.

    vloss : float
        Pérdidas de velocidad. Por defecto es vloss=0.

    step_size : float
        Salto temporal. Por defecto es step_size=DT (DT=0.05).

    altura_maxima : float
        Altura máxima. Por defecto es altura_maxima=inf.

    perdidas : bool
        Indica si deben computarse las pérdidas de velocidad o no. Por
        defecto es perdidas=False.

    imprimir : string
        Nombre del archivo de escritura. Si imprimir=False, no se
        escribe. Por defecto es imprimir=False.
    dic_tie : dictionary
        Define el lanzamiento en función del tiempo inicial de lanzamiento y
        los tiempos característicos de cada etapa.
    '''
    mase = masa_etapa
    masa = masa_total
    resto = masa - mase  # Como si fuera la carga de pago
    pos = posicion_inicial
    vel = velocidad_inicial
    # Cuando empieza la etapa de combustión enciendo el motor, cuando termine
    # de correrse esta función volverá a su valor.
    encendido = True
    coeficientes_fuerza.set_propulsion(prop=encendido)

    consumido = mase <= 0
    altur = norm(pos) - RT
    tiempo = tiempo_inicial
    gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))

    while (altur < altura_maxima
           and not consumido):
        # Condiciones de parada:
        # 1) que se haya superado la altura máxima
        # 2) que se haya consumido todo el combustible de la etapa
        if perdidas:
            masa, tiempo, pos, vel, vloss, factor_carga, cd, cn, alfa = step(masa, tiempo, pos, vel, gasto,
                                                 isp, coeficientes_fuerza,
                                                 vloss=vloss,
                                                 masa_minima=resto,
                                                 step_size=step_size,
                                                 perdidas=perdidas,
                                                 dic_tie=dic_tie)
        else:
            masa, tiempo, pos, vel, factor_carga, cd, cn, alfa = step(masa, tiempo, pos, vel, gasto, isp,
                                          coeficientes_fuerza,
                                          masa_minima=resto,
                                          step_size=step_size,
                                          dic_tie=dic_tie)
        altur = norm(pos) - RT
        gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))
        mase = masa - resto
        consumido = mase <= 0

        if imprimir:
            imprimir.write('\n' + format(tiempo, '^12.3f')
                           + '\t' + format(altur, '^12.1f')
                           + '\t' + format(norm(vel), '^17.1f')
                           + '\t' + format(masa, '^11.1f')
                           + '\t' + format(gamma, '^13.3f')
                           + '\t' + format(alfa, '^14.3f')
                           + '\t' + format(factor_carga, '^14.3f')
                           + '\t' + format(coeficientes_fuerza._etapa, '^17.3f')
                           + '\t' + format('On', '^14'))
           
            archivo2.write('\n' + format(tiempo, '^17.3f')
                           + '\t' + format(cd, '^17.3f')
                           + '\t' + format(cn, '^17.3f')
                           + '\t' + format(alfa, '^17.3f'))
            
    if perdidas:
        gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))
        return masa, tiempo, pos, vel, gamma, vloss
    
    gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))
    return masa, tiempo, pos, vel, gamma


def vuelo_libre(masa, posicion_inicial, velocidad_inicial, coeficientes_fuerza,
                t_de_vuelo=inf, tiempo_inicial=0, vloss=0, step_size=DT,
                altura_maxima=inf, perdidas=False, imprimir=False,
                archivo2=False, dic_tie={}):
    '''
    Ejecuta todos los pasos de integración del vuelo sin propulsión.
    Funciona de la misma manera que la función anterior etapa(), pero al usar
    la función step(), el isp y el gasto son nulos.

    Tiene una variable booleana que se llama 'encendido' que se activa si se
    supera el tiempo de vuelo libre (retardo) y el programa termina la función

    Devuelve lo mismo que etapa()

    masa : float
        Masa.

    posicion_inicial : array (3 componentes)
        Posición inicial.

    velocidad_inicial : array (3 componentes)
        Velocidad inicial.
    
    coeficientes_fuerza : object
        Es un objeto en el cual está definida la aerodinámica del lanzador.

    t_de_vuelo : float

    tiempo_inicial : float
        Tiempo inicial. Por defecto es tiempo_inicial=0.

    vloss : float
        Pérdidas de velocidad. Por defecto es vloss=0.

    step_size : float
        Salto temporal. Por defecto es step_size=DT (DT=0.05).

    altura_maxima : float
        Altura máxima. Por defecto es altura_maxima=inf.

    perdidas : bool
        Indica si deben computarse las pérdidas de velocidad o no. Por
        defecto es perdidas=False.

    imprimir : string
        Nombre del archivo de escritura. Si imprimir=False, no se
        escribe. Por defecto es imprimir=False.
    dic_tie : dictionary
        Define el lanzamiento en función del tiempo inicial de lanzamiento y
        los tiempos característicos de cada etapa.
    '''
    t_vuelo = 0
    tiempo = tiempo_inicial
    pos = posicion_inicial
    vel = velocidad_inicial
    altur = norm(pos) - RT
    gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))
    encendido = False

    while (altur < altura_maxima
           and t_vuelo <= t_de_vuelo
           and gamma > -5.0):
        # Condiciones de parada:
        # 1) que se haya superado la altura máxima
        # 2) que se haya superado el tiempo de vuelo libre
        # 3) que esté cayendo a más de 5º
        # 4) El misil se choca con la tierra.
        if (tiempo > 300) and altur < 100:
            print('El misil choca con la tierra')
            break
        if t_de_vuelo < step_size + t_vuelo:
            step_size = t_de_vuelo - t_vuelo
            encendido = True
        if perdidas:
            masa, t_vuelo, pos, vel, vloss, factor_carga, cd, cn, alfa = step(masa, t_vuelo, pos, vel, 0,
                                                  0, coeficientes_fuerza,
                                                  vloss=vloss,
                                                  step_size=step_size,
                                                  perdidas=perdidas,
                                                  dic_tie=dic_tie)
        else:
            masa, t_vuelo, pos, vel, factor_carga, cd, cn, alfa = step(masa, t_vuelo, pos, vel, 0, 0,
                                           coeficientes_fuerza,
                                           step_size=step_size,
                                           dic_tie=dic_tie)
        altur = norm(pos) - RT
        tiempo = t_vuelo + tiempo_inicial
        gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))
        if imprimir:
            imprimir.write('\n' + format(tiempo, '^12.3f')
                           + '\t' + format(altur, '^12.1f')
                           + '\t' + format(norm(vel), '^17.1f')
                           + '\t' + format(masa, '^11.1f')
                           + '\t' + format(gamma, '^13.3f')
                           + '\t' + format(alfa, '^14.3f')
                           + '\t' + format(factor_carga, '^14.3f')
                           + '\t' + format(coeficientes_fuerza._etapa, '^17.3f')
                           + '\t' + format('Off', '^14'))
            
            
            archivo2.write('\n' + format(tiempo, '^17.3f')
                           + '\t' + format(cd, '^17.3f')
                           + '\t' + format(cn, '^17.3f')
                           + '\t' + format(alfa, '^17.3f'))
            
        if encendido:
            break

    if perdidas:
        gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))
        return masa, tiempo, pos, vel, gamma, vloss
    
    gamma = 90 - degrees(arccos(dot(vel, pos)/(norm(vel)*norm(pos))))
    return masa, tiempo, pos, vel, gamma


def lanzamiento(masas, estructuras, gastos, isps, posicion_inicial,
                velocidad_inicial, inc_inicial, retardos,
                diccionario_tiempo={}, step_size=DT, alt_maxima=inf,
                perdidas=False, imprimir=False, aletas=True, ala=True):
    '''
    Ejecuta todos los pasos de integración del lanzamiento.
    Utiliza las condiciones iniciales para iniciarse. En función de las
    variables calcula la trayectoria de lanzamiento step a step.

    Devuelve la masa, el tiempo, la posición y la velocidad finales.
    En el caso de que se tengan en cuenta las pérdidas, también las devuelve.

    masas : array
        Masas de las distintas etapas, incluyendo la masa de la carga de
        pago como último elemento.

    estructuras : array
        Razones estructurales de las distintas etapas.

    gastos : array
        Gastos másicos de las distintas etapas.

    isps : array
        Impulsos específicos de las distintas etapas.

    posicion_inicial : array (3 componentes)
        Posición inicial.

    velocidad_inicial : array (3 componentes)
        Velocidad inicial.
    
    inc_inicial : escalar (rad)
        Ángulo que forma el lanzador con el horizonte local en radianes.

    retardos : array
        Tiempos de retardo de encendido de las distintas etapas.

    diccionario_tiempo : dictionary
        Define el lanzamiento en función del tiempo inicial de lanzamiento y
        los tiempos característicos de cada etapa.

    step_size : float
        Salto temporal. Por defecto es step_size=DT (DT=0.05).

    altura_maxima : float
        Altura máxima. Por defecto es altura_maxima=inf.

    perdidas : bool
        Indica si deben computarse las pérdidas de velocidad o no. Por
        defecto es perdidas=False.

    imprimir : string
        Nombre del archivo de escritura. Si imprimir=False, no se
        escribe. Por defecto es imprimir=False.
    '''
    # Condiciones iniciales
    mas = sum(masas)
    pos = posicion_inicial
    vel = velocidad_inicial
    gamma = degrees(inc_inicial)
    altur = norm(pos) - RT
    archivo = False
    coef_fuerzas = CoeficienteFuerza()
    v_iny = False
    gam_iny = False

    try:
        tie = diccionario_tiempo['t_inicial']
    except(KeyError):
        raise TimeDictionaryError()

    coef_fuerzas.set_aletas()
    coef_fuerzas.set_ala()
    if perdidas:
        per = 0

    if imprimir:
        archivo = open(imprimir, 'w')
        archivo.write(format('Tiempo (s)','^12')
                      + '\t' + format('Altura (m)','^12')
                      + '\t' + format('Velocidad (m/s)','^17')
                      + '\t' + format('Masa (kg)', '^11')
                      + '\t' + format('Gamma (º)','^13')
                      + '\t' + format('Alfa (º)','^17')
                      + '\t' + format('Factor de Carga (-)','^13')
                      + '\t' + format('Etapa (-)','^13')
                      + '\t' + format('Propulsión (-)','^15')
                      + '\n' + format(tie, '^12.3f')
                      + '\t' + format(altur, '^12.1f')
                      + '\t' + format(norm(vel), '^17.1f')
                      + '\t' + format(mas, '^11.1f')
                      + '\t' + format(gamma, '^13.3f')
                      + '\t' + format(0, '^14.3f')
                      + '\t' + format(1, '^14.3f')
                      + '\t' + format(1, '^17.3f')
                      + '\t' + format('Off', '^14'))
        
        archivo2 = open('caracteristicas_aerodinamicas', 'w')
        archivo2.write(format('Tiempo (s)','^17')
                      + '\t' + format('CD (-)','^17')
                      + '\t' + format('CN (-)','^17')
                      + '\t' + format('Alfa (º)','^17'))

    for i, gas in enumerate(gastos):
        coef_fuerzas.set_etapa(i + 1)
        if coef_fuerzas._etapa != 1:  # Si etapa no es 1 quita ala y aletas
            coef_fuerzas.set_ala(ala=False)
            coef_fuerzas.set_aletas(aletas=False)
        # Retardos de encendido
        if retardos[i] != 0:
            if perdidas:
                mas, tie, pos, vel, gamma, per = vuelo_libre(mas, pos, vel,
                                                             coef_fuerzas,
                                                             t_de_vuelo=retardos[i],
                                                             tiempo_inicial=tie,
                                                             vloss=per,
                                                             step_size=step_size,
                                                             altura_maxima=alt_maxima,
                                                             perdidas=perdidas,
                                                             imprimir=archivo,
                                                             archivo2=archivo2,
                                                             dic_tie=diccionario_tiempo)
            else:
                mas, tie, pos, vel, gamma = vuelo_libre(mas, pos, vel,
                                                        coef_fuerzas,
                                                        t_de_vuelo=retardos[i],
                                                        tiempo_inicial=tie,
                                                        step_size=step_size,
                                                        altura_maxima=alt_maxima,
                                                        imprimir=archivo,
                                                        archivo2=archivo2,
                                                        dic_tie=diccionario_tiempo)
            altur = norm(pos) - RT
            if altur >= alt_maxima:
                if imprimir:
                    archivo.close()
                    archivo2.close()
                if perdidas:
                    return mas, tie, pos, vel, gamma, gam_iny, per
                return mas, tie, pos, vel, gamma, gam_iny
        # Etapas
        if perdidas:
            mas, tie, pos, vel, gamma, per = etapa(masas[i]*(1 - estructuras[i]),
                                                   mas, gas, isps[i], pos, vel,
                                                   coef_fuerzas,
                                                   tiempo_inicial=tie,
                                                   vloss=per,
                                                   step_size=step_size,
                                                   altura_maxima=alt_maxima,
                                                   perdidas=perdidas,
                                                   imprimir=archivo,
                                                   archivo2=archivo2,
                                                   dic_tie=diccionario_tiempo)
        else:
            mas, tie, pos, vel, gamma = etapa(masas[i] * (1 - estructuras[i]),
                                              mas, gas, isps[i], pos, vel,
                                              coef_fuerzas,
                                              tiempo_inicial=tie,
                                              step_size=step_size,
                                              altura_maxima=alt_maxima,
                                              imprimir=archivo,
                                              archivo2=archivo2,
                                              dic_tie=diccionario_tiempo)
        altur = norm(pos) - RT
        if altur >= alt_maxima:
            if imprimir:
                archivo.close()
                archivo2.close()
            if perdidas:
                return mas, tie, pos, vel, gamma, gam_iny, per
            return mas, tie, pos, vel, gamma, gam_iny
        mas = mas - masas[i] * estructuras[i]
    v_iny = norm(vel)
    gam_iny = gamma
    
    # Condición que sale de la integración si el gamma de inyección no está
    # dentro de un valor estipulado.
    if abs(gam_iny) > GAMMA_INY_MIN:
        if perdidas:
            return mas, tie, pos, vel, gamma, gam_iny, per
        return mas, tie, pos, vel, gamma, gam_iny
    
    # Vuelo libre tras haberse consumido las etapas (maximo 3000 segundos)
    if perdidas:
        mas, tie, pos, vel, gamma, per = vuelo_libre(mas, pos, vel,
                                                     coef_fuerzas,
                                                     tiempo_inicial=tie,
                                                     t_de_vuelo=3000,
                                                     vloss=per,
                                                     step_size=step_size,
                                                     altura_maxima=alt_maxima,
                                                     perdidas=perdidas,
                                                     imprimir=archivo,
                                                     archivo2=archivo2,
                                                     dic_tie=diccionario_tiempo)
    else:
        mas, tie, pos, vel, gamma = vuelo_libre(mas, pos, vel,
                                                coef_fuerzas,
                                                tiempo_inicial=tie,
                                                t_de_vuelo=3000,
                                                step_size=step_size,
                                                altura_maxima=alt_maxima,
                                                imprimir=archivo,
                                                archivo2=archivo2,
                                                dic_tie=diccionario_tiempo)
    
    if imprimir:
        archivo.close()
        archivo2.close()
    if perdidas:
        print('\nVelocidad de inyección: {0:.2f} m/s'.format(v_iny))
        return mas, tie, pos, vel, gamma, gam_iny, per
    return mas, tie, pos, vel, gamma, gam_iny
