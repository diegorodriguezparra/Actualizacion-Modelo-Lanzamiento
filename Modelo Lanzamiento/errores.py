# -*- coding: utf-8 -*-
"""
@author: Team REOS

Clases para excepciones en los códigos del proyecto REOS.
"""


class ValorInadmisibleError(Exception):
    '''
    Error que se produce cuando un valor no tiene sentido real,
    aunque matemáticamente siga siendo válido.

    Parámetros
    ----------
    diccionario : dictionary
        Variable cuyo valor es inadmisible.  Debe introducirse como
        dict(nombre_variable=nombre_variable).

    formato : string, opcional
        Código de formato con el que se representa el valor inadmisible
        de la variable. Por defecto, es un string vacío.

    deberia_ser : string, opcional
        Condición que el valor en cuestión no cumple y que lo hace
        inadmisible. Por defecto es None.

    Atributos
    ---------
    message : string
        Mensaje de error.

    Ejemplos
    --------
    >>> valor_negativo = 2
    >>> raise ValorInadmisibleError(dict(valor_negativo=valor_negativo))

    ValorInadmisibleError: La variable valor_negativo tiene un valor
    inadmisible: 2.

    >>> raise ValorInadmisibleError(dict(valor_negativo=valor_negativo))

    ValorInadmisibleError: La variable valor_negativo tiene un valor
    inadmisible: 2. Debería ser negativo.


    '''
    def __init__(self, diccionario, formato='', deberia_ser=None):
        variable = [str(var) for var in diccionario.keys()]
        variable = variable[0]

        if deberia_ser is None:
            deberia_ser = ''
        else:
            deberia_ser = ' Debería ser ' + deberia_ser + '.'

        self.message = ("La variable '" + variable +
                        "' tiene un valor inadmisible: "
                        + format(diccionario[variable], formato) + '.'
                        + deberia_ser)
        Exception.__init__(self, self.message)


class IteracionError(Exception):
    '''
    Error que se produce cuando una iteración en un bucle produce una
    excepción e identifica dicha iteración.

    Parámetros
    ----------
    iteracion
        Valor de la variable de iteración cuando se produce la
        excepción.

    Atributos
    ---------
    message : string
        Mensaje de error.
    '''
    def __init__(self, iteracion, error=None):

        if error is not None:
            error_type = str(type(error))
            error_type = error_type[:error_type.find('Error')+5]
            error_type = error_type.split(sep='.')[1]

            error_msg = error.message

        else:
            error_type = ''
            error_msg = ''

        self.message = ('El valor de la variable de iteración en el error es '
                        + str(iteracion) + '.\n\n' + error_type + ': '
                        + error_msg)

        Exception.__init__(self, self.message)


class NoseError(Exception):
    '''
    Error que se produce cuando se asigna un valor inadmisible a la variable
    tipo en la geometría del misil.
    
    Parámetros
    ----------
    tipo
        Valor que se le ha dado al tipo de nariz.
    
    Atributos
    ---------
    message : string
        Mensaje de error.
    '''
    def __init__(self, tipo):
        tipo = str(tipo)
        self.message = ('El tipo de nariz seleccionado para el lanzador, ' +
                        tipo + ', no existe.\n Ha de ser:' +
                        '\n\t0: Cono\n\t1:Ojiva Circular Tangente')
        
        Exception.__init__(self, self.message)


class TimeDictionaryError(Exception):
    '''
    Error que se produce cuando no se define un diccionario temporal en el
    programa principal.
    
    Atributos
    ---------
    message : string
        Mensaje de error.
    '''
    def __init__(self):
        self.message = ('No se ha introducido un diccionario válido.')
        
        Exception.__init__(self, self.message)