import pyjade

def extJade(content):
    return pyjade.simple_convert(content)

def init(funcs, convs):
    funcs['jade'] = extJade
    convs['jade'] = 'html'
