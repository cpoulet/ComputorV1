#!/usr/bin/env python3

import re
import math
import collections

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
    <term>      ::= <factor> {'*' <factor>}
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
        <term>      ::= <factor> {'*' <factor>}
        '''
        term_val = self._factor()
        while self._accept('MULT'):
            term_add = self._factor()
            term_val = (term_val[0]*term_add[0], term_val[1]+term_add[1])
        return term_val

    def _factor(self):
        '''
        <factor>    ::= NB | <pow>
        '''
        if self._accept('NB'):
            return (float(self.current_token.value), 0)
        else:
            return (1, self._pow())

    def _pow(self):
        '''
        <pow>       ::= VAR {'^' NB}
        '''
        if self._accept('VAR'):
            if self._accept('POW'):
                self._expect('NB')
                if '.' in self.current_token.value:
                    raise Exception('Power should be an integer')
                p = int(self.current_token.value)
                return p if p > 0 else -1
            return 1
        else:
            raise Exception('Expected a VAR or a NB')

    def _procede(self, prob):
        print(prob)
        print(len(prob))
        if 0 in prob:
            print(prob[0])
        if -1 in prob and len(prob) == 1:
            self.degree =0
            return False
        if -1 in prob and len(prob) == 2 and 0 in prob:
            if prob[0] == 1:
                self.degree = 0
                return False
            else:
                return {}
        return prob

    def _tab(self, prob):
        prob = self._procede(prob)
        if not prob:
            return
        self.poly = []
        i = 0
        while len(prob):
            if prob.get(i) != None:
                self.poly.append(prob[i])
                del prob[i]
            else:
                self.poly.append(0)
            i += 1
        if len(self.poly) > 1:
            while not self.poly[-1]:
                self.poly.pop()
        self._small()

    def _small(self):
        self.degree = len(self.poly) - 1
        if not self.degree:
            raise Exception('This is not an equation.')
        s = ''
        for i, x in enumerate(self.poly):
            s += ' - ' if x < 0 else ' + '
            if abs(x) != 1:
                s += str(abs(x)) + ' * '
            s += 'X^' + str(i)
        s = s[3:] if s[1] == '+' else '-' + s[3:]
        print('Reduce form : ' + s + ' = 0');
        print('This is a', ordi(self.degree), 'degree equation.')

    def solve(self):
        if self.degree == 0:
            print('All reals are solution to this equation..')
        elif self.degree == 1:
            self._first_degree()
        elif self.degree == 2:
            self._second_degree()
        else:
            print('The equation is to complex to be solve.')

    def _first_degree(self):
        print('X =', -1 * self.poly[0] / self.poly[1])

    def _second_degree(self):
        d = self._discriminant()
        a = self.poly[2]
        b = self.poly[1]
        c = self.poly[0]
        if d > 0:
            print('Its discriminant is strictly positive, then there is two distinct real roots :')
            print('{:.6f}'.format((-1 * b - math.sqrt(d)) / (2 * a)))
            print('{:.6f}'.format((-1 * b + math.sqrt(d)) / (2 * a)))
        elif d == 0:
            print('Its discriminant is null, then there is exactly one real root :')
            print((-1 * b) / (2 * a))
        else:
            print('Its discriminant is strictly negative, then there is two distinct complex roots:')
            print((-1 * b) / (2 * a), '+ i * {:.6f}'.format((math.sqrt(d * -1)) / (2 * a)))
            print((-1 * b) / (2 * a), '- i * {:.6f}'.format((math.sqrt(d * -1)) / (2 * a)))

    def _discriminant(self):
        return self.poly[1]**2 - 4*self.poly[0]*self.poly[2]

def main():
    PS = PolynomeSolveur()
    while(1):
        print('Enter an equation : ', end='')
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
