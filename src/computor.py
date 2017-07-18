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
        ('VAR' , r'X'),
        ('WS' , r'\s'),
        ('ERROR' , r'[^0-9X\s+-^*=]')]

    def parse(self, equa):
        self.token_generator = tokenize(equa, self.TOKENS_SPEC)
        self.current_token = None
        self.next_token = None
        self._next()
        self._prob()
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
        self._equa()
        self._expect('EGA')
        self._equa()

    def _equa(self):
        '''
        <equa>      ::= <term> {('+' | '-') <term>}
        '''
        self._term()
        while self._accept('PLUS') or self._accept('MINUS'):
            self._term()

    def _term(self):
        '''
        <term>      ::= <factor> {'*' <factor>}
        '''
        self._factor()
        if self._accept('MULT'):
            self._factor()

    def _factor(self):
        '''
        <factor>    ::= NB | <pow>
        '''
        if self._accept('NB'):
            return
        else:
            self._pow()

    def _pow(self):
        '''
        <pow>       ::= VAR {'^' NB}
        '''
        if self._accept('VAR'):
            if self._accept('POW'):
                self._expect('NB')
            return
        else:
            raise Exception('Expected a VAR')

def main():
    PS = PolynomeSolveur()
    print('Entrez une equation : ', end='')
    equa = input().strip()
    PS.parse(equa)

if __name__ == "__main__":
    try:
	    main()
    except Exception as e:
        print('Error : ' + str(e))
