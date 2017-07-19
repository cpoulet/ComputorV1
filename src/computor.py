#!/usr/bin/env python3

import re
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
        ('NB' , r'[0-9]+'),
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
        self._tab(self._prob())
        if self.next_token:
            raise Exception('Wrong token sequence busted. Processing stopped at : ' + self.next_token.value)
        

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
            return (int(self.current_token.value), 0)
        else:
            return (1, self._pow())

    def _pow(self):
        '''
        <pow>       ::= VAR {'^' NB}
        '''
        if self._accept('VAR'):
            if self._accept('POW'):
                self._expect('NB')
                return int(self.current_token.value)
            return 1
        else:
            raise Exception('Expected a VAR or a NB')

    def _tab(self, prob):
        self.poly = []
        i = 0
        while len(prob):
            if prob.get(i):
                self.poly.append(prob[i])
                del prob[i]
            else:
                self.poly.append(0)
            i += 1

    def small(self):
        print('Sous forme reduite :', ' + '.join([str(x) + 'x^'+str(i) if i > 1 else str(x) + 'x' if i > 0 else str(x) for i, x in enumerate(self.poly) if x]))

def main():
    PS = PolynomeSolveur()
    print('Entrez une equation : ', end='')
    equa = input().strip()
    PS.parse(equa)
    PS.small()

if __name__ == "__main__":
    try:
	    main()
    except Exception as e:
        print('Error : ' + str(e))
