#! -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
from decimal import Decimal, InvalidOperation
import enchant
from .dicts import digitos, decenas, centenas, exponentes


class Singer(object):

    def __init__(self):
        self._calcular_limite()

    def _calcular_limite(self):
        """
        Calcula el numero maximo que se puede imprimir
        """
        self.exponentes = sorted(list(exponentes.keys()), reverse=True)
        exp = self.exponentes[0]
        self.limite = 10 ** (exp * 2) - 1

    def sing(self, number, strict=False):
        """Interfaz publica para convertir numero a texto"""

        if type(number) != Decimal:
            number = Decimal(number)

        if number > self.limite:
            msg = "El maximo numero procesable es %s" % self.limite
            raise ValueError(msg)
        else:
            texto = self.__to_text(int(number), strict)
        texto += self.__calcular_decimales(number)

        return self.__agregar_tildes(texto)

    def __agregar_tildes(self, texto):
        con_tildes = ''
        d = enchant.Dict("es")

        for palabra in texto.split():
            if palabra == 'y':
                con_tildes += 'y '
            elif '/' in palabra or palabra in('seis', 'trillones'):
                con_tildes += palabra + ' '
            elif palabra == 'trillon':
                con_tildes += 'trillón' + ' '
            else:
                try:
                    con_tildes += d.suggest(palabra)[0] + ' '
                except:
                    print palabra

        return con_tildes.strip()

    def __calcular_decimales(self, number):

        try:
            dec = (number % 1).quantize(Decimal('0.01'))
        except InvalidOperation:
            #Usamos strings para obtener la parte decimal
            dec_tp = number.as_tuple()
            if dec_tp.exponent < 0:
                digit_list = [str(n) for n in dec_tp.digits[dec_tp.exponent:]]
                dec = Decimal('0.' + ''.join(digit_list))
            else:
                dec = 0

        if dec != 0:
            centavos = int(dec * 100)
            return ' con %s/100' % centavos
        else:
            return ''

    def __to_text(self, number, strict, indice=0, sing=False):
        """Convierte un numero a texto, recursivamente"""

        number = int(number)
        exp = self.exponentes[indice]
        indice += 1
        divisor = 10 ** exp
        if exp == 3:
            func = self.__numero_tres_cifras
        else:
            func = self.__to_text
        if divisor < number:
            division = number // divisor
            resto = number % divisor
            if resto:
                der = func(resto, strict, indice, sing)
            else:
                der = False

            if exp == 3 and division == 1:  # 1000
                return "%s %s" % (exponentes[exp], der)
            else:
                izq = func(division, strict, indice, True)
                if der:
                    if division == 1:
                        return "un %s %s" % (exponentes[exp], der)
                    elif exp > 3:
                        return "%s %ses %s" % (izq, exponentes[exp], der)
                    else:
                        return "%s %s %s" % (izq, exponentes[exp], der)
                else:
                    if division == 1:
                        return "un %s" % (exponentes[exp])
                    elif exp > 3:
                        return "%s %ses" % (izq, exponentes[exp])
                    else:
                        return "%s %s" % (izq, exponentes[exp])

        elif divisor == int(number):
            if exp == 3 and strict is False:
                return exponentes[exp]
            elif exp == 3 and strict is True:
                return 'un %s' % exponentes[exp]
            else:
                return 'un %s' % exponentes[exp]

        else:
            return func(number, strict, indice, sing)

    def __numero_tres_cifras(self, number, strict, indice=None, sing=False):
        """Convierte a texto numeros de tres cifras"""
        number = int(number)
        if sing and number == 1:
            return 'un'
        elif number <= 15:
            return digitos[number]

        elif number < 20:
            return 'dieci%s' % \
                    self.__numero_tres_cifras(number % 10, strict, None, sing)

        elif number == 20:
            return 'veinte'

        elif number < 30:
            return 'veinti%s' % \
                    self.__numero_tres_cifras(number % 10, strict, None, sing)

        elif number < 100:
            texto = decenas[number // 10]
            resto = number % 10
            if resto:
                texto += ' y %s' % self.__numero_tres_cifras(resto, strict, None, sing)
            return texto

        if number == 100:
            return 'cien'

        if number < 1000:
            texto = centenas[number // 100]
            resto = number % 100
            if resto:
                texto += ' %s' % self.__numero_tres_cifras(resto, strict, None, sing)
            return texto
