#!/usr/bin/env python

import functools

def dec(f):
    print 'Enter dec() f = {}'.format(f)

    @functools.wraps(f)
    def wrapper(self):
        print 'Enter wrapper()'
        print 'wrapper(): self._a = {}'.format(self._a)
        print 'wrapper(): self._d = {}'.format(self._d)
        f(self)
        # raise ValueError('fake error')
        print 'Exit wrapper()'
        
    print 'Exit dec()'
    return wrapper


class A(object):
    def __init__(self, d1):
        print '__init__ class A'
        self._a = 2
        self._d = d1

    @dec
    def func(self):
        print 'Enter: func()'
        print 'func: self._a = {}'.format(self._a)
        print 'Exit: func()'

def main():
    print 'Enter main()'
    d = dict(one=1)
    a = A(d)

    print 'main: a = {}'.format(a)
    print 'main: a.func = {}'.format(a.func)

    print 'Calling a.func()'
    a.func()
    print 'Exit main()'
    

if __name__ == "__main__":
    main()
