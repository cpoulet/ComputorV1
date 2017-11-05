#!/usr/bin/env python3

import re
import math
import collections
from color import Color

Token = collections.namedtuple('Token', ['type_', 'value'])

def tokenize(expr, tokens_spec):
    '''Token Generator'''
    token_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in tokens_spec))
    for item in re.finditer(token_regex, expr):
        if item.lastgroup == 'ERROR':
            raise Exception('Very wrong token.')
        if not item.lastgroup == 'WS':
            yield Token(item.lastgroup, item.group())

def ordi(nb):
    suff = ['rd', 'st', 'nd']
    if nb <= 0:
        return str(nb)
    if 0 < nb % 10 < 4 and nb not in [11, 12, 13]:
        return str(nb) + suff[nb % 10 % 3]
    else:
        return str(nb) + 'th'

class PolynomeSolveur:
    '''
    <prob>      ::= <equa> '=' <equa>
    <equa>      ::= <term> {('+' | '-') <term>}
    <term>      ::= <factor> {('*' <factor>)}
    <factor>    ::= NB | <pow>
    <pow>       ::= VAR {'^' NB}
    '''
    def __init__(self):
        self.TOKENS_SPEC = [
        ('NB' , r'[0-9]+\.?[0-9]*'),
        ('MINUS' , r'\-'),
        ('PLUS' , r'\+'),
        ('MULT' , r'\*'),
        ('POW' , r'\^'),
        ('EGA' , r'\='),
        ('VAR' , r'[Xx]'),
        ('WS' , r'\s'),
        ('ERROR' , r'[^0-9Xx\s+-^*=]')]

    def parse(self, equa):
        self.token_generator = tokenize(equa, self.TOKENS_SPEC)
        self.current_token = None
        self.next_token = None
        self._next()
        out = self._prob()
        if self.next_token:
            raise Exception('Wrong token sequence busted. Processing stopped at : ' + self.next_token.value)
        self._tab(out)
        

    def _next(self):
        self.current_token, self.next_token = self.next_token, next(self.token_generator, None)

    def _accept(self, token_type):
        if self.next_token and self.next_token.type_ == token_type:
            self._next()
            return True
        else:
            return False

    def _expect(self, token_type):
        if not self._accept(token_type):
            raise Exception('Wrong token sequence busted. Expected : ' + token_type)

    def _prob(self):
        '''
        <prob>      ::= <equa> '=' <equa>
        '''
        prob_val = self._equa()
        self._expect('EGA')
        equa_val = self._equa()
        for k in equa_val:
            if prob_val.get(k):
                prob_val[k] -= equa_val[k]
            else:
                prob_val[k] = equa_val[k] * -1
        return prob_val

    def _equa(self):
        '''
        <equa>      ::= <term> {('+' | '-') <term>}
        '''
        term_val = self._term()
        equa_val = {term_val[1]:term_val[0]}
        while self._accept('PLUS') or self._accept('MINUS'):
            if self.current_token.type_ == 'MINUS':
                term_val = self._term()
                term_val = (term_val[0] * -1, term_val[1])
            else:
                term_val = self._term()
            if equa_val.get(term_val[1]):
                equa_val[term_val[1]] += term_val[0]
            else:
                equa_val[term_val[1]] = term_val[0]
        return equa_val

    def _term(self):
        '''
        <term>      ::= <factor> {'*'? <factor>}
        '''
        term_val = self._factor()
        while self._accept('MULT') or (self.next_token and self.next_token.type_ == 'VAR'):
            term_add = self._factor()
            term_val = (term_val[0]*term_add[0], term_val[1]+term_add[1])
        return term_val

    def _factor(self):
        '''
        <factor>    ::= NB | <pow>
        '''
        if self._accept('NB'):
            return (float(self.current_token.value), 0)
        elif self._accept('MINUS'):
            if self._accept('NB'):
                return (float(self.current_token.value) * -1, 0)
            else:
                return (-1, self._pow())
        else:
            return (1, self._pow())

    def _pow(self):
        '''
        <pow>       ::= VAR {'^'? NB}
        '''
        if self._accept('VAR'):
            if self._accept('POW'):
                self._expect('NB')
                if '.' in self.current_token.value:
                    raise Exception('Power should be an integer')
                p = int(self.current_token.value)
                return p if p > 0 else -1
            elif self._accept('NB'):
                if '.' in self.current_token.value:
                    raise Exception('Power should be an integer')
                p = int(self.current_token.value)
                return p if p > 0 else -1
            return 1
        else:
            raise Exception('Expected a VAR or a NB')

    def _tab(self, prob):
        x0 = prob.pop(-1, None)
        self.poly = []
        i = 0
        while(len(prob)):
            val = self.poly.append(prob.pop(i, 0))
            i += 1
        while(len(self.poly)):
            if not self.poly[-1]:
                self.poly.pop()
            else:
                break
        if x0 != None:
            if self.poly != []:
                self.poly[0] += x0
            elif x0:
                self.poly.append(x0)
        self._reduce()

    def _reduce(self):
        if len(self.poly) == 1:
            if self.poly[0] == 0:
                self.degree = 0
                return
            else:
                self.degree = -1
                return
        if self.poly == []:
            self.degree = 0
            return
        self.degree = len(self.poly) - 1
        s1 = ''
        s2 = ''
        for i, x in enumerate(self.poly):
            s1 += ' - ' if x < 0 else ' + '
            if x != 0:
                s2 += ' - ' if x < 0  else ' + '
            s1 += str(abs(x)) + ' * ' if abs(x) != 1 else ''
            s2 += '{:g}'.format(abs(x)) if x else ''
            s1 += 'X^' + str(i)
            if i and x:
                s2 += 'x' + (str(i) if i != 1 else '')
        s1 = s1[3:] if s1[1] == '+' else '-' + s1[3:]
        s2 = s2[3:] if s2[1] == '+' else '-' + s2[3:]
        print('Reduce form : ' + s1 + ' = 0');
        print('Reduce form : ' + s2 + ' = 0');
        print('This is a', Color().red(ordi(self.degree)), 'degree equation.')

    def solve(self):
        if self.degree == -1:
            print(Color().red('There is no solution to this expression.'))
        elif self.degree == 0:
            print(Color().green('All reals are solution to this equation..'))
        elif self.degree == 1:
            self._first_degree()
        elif self.degree == 2:
            self._second_degree()
        else:
            print(Color().red('The equation is to complex to be solve.'))

    def _first_degree(self):
        print(Color().green('X = ' + str(-1 * self.poly[0] / self.poly[1])))

    def _second_degree(self):
        d = self._discriminant()
        a = self.poly[2]
        b = self.poly[1]
        c = self.poly[0]
        if d > 0:
            print('Its discriminant is strictly positive, then there is two distinct real roots :')
            print(Color().green('X1 = {:g}'.format((-1 * b - math.sqrt(d)) / (2 * a))))
            print(Color().green('X2 = {:g}'.format((-1 * b + math.sqrt(d)) / (2 * a))))
        elif d == 0:
            print('Its discriminant is null, then there is exactly one real root :')
            print(Color().green('X = ' + str((-1 * b) / (2 * a))))
        else:
            print('Its discriminant is strictly negative, then there is two distinct complex roots:')
            print(Color().green('X1 = ' + str((-1 * b) / (2 * a)) + ' + i * {:g}'.format((math.sqrt(d * -1)) / (2 * a))))
            print(Color().green('X2 = ' + str((-1 * b) / (2 * a)) + ' - i * {:g}'.format((math.sqrt(d * -1)) / (2 * a))))

    def _discriminant(self):
        return self.poly[1]**2 - 4 * self.poly[0] * self.poly[2]

def main():
    PS = PolynomeSolveur()
    while(1):
        print(Color().white('> Enter an equation : '), end='')
        equa = input().strip()
        if equa == 'Q':
            exit()
        try:
            PS.parse(equa)
            PS.solve()
        except Exception as e:
            print('Error : ' + str(e))
            print('Write \'Q\' to exit the program')

if __name__ == "__main__":
    try:
	    main()
    except Exception as e:
        print('Error : ' + str(e))
