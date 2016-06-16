import pyjade

def extJade(content):
    content = pyjade.simple_convert(content)
    return ''.join(map(lambda x: x.strip(), content.split('\n')))



def init(funcs, convs):
    funcs['jade'] = extJade
    convs['jade'] = 'html'
