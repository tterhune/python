#!/usr/bin/env python

import functools

def dec_gen(*args, **kwargs):
    print 'Enter dec_gen(): args = {}, kwargs = {}'.format(args, kwargs)

    def dec(f):
        print 'Enter dec f = {}'.format(f)

        @functools.wraps(f)
        def wrapper(self):
            print 'Enter wrapper()'
            print 'wrapper(): self._a = {}'.format(self._a)
            print 'wrapper(): self._d = {}'.format(self._d)
            print 'wrapper(): args = {}, kwargs = {}'.format(args, kwargs)
            f(self)
            post_func = kwargs.get('post')
            if post_func: 
                post_func()
            # raise ValueError('fake error')
            print 'Exit wrapper() return {}'.format(wrapper)
        return wrapper

    print 'Exit dec() return {}'.format(dec)
    return dec

def post_work(*args, **kwargs):
    print 'post_work(): {}, {}'.format(args, kwargs)

class A(object):
    def __init__(self, d1):
        print '__init__ class A'
        self._a = 2
        self._d = d1

    @dec_gen(post=post_work)
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
