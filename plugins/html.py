import pyjade

def extHTML(content):
    return ''.join(map(lambda x: x.strip(), content.split('\n')))

def init(funcs, convs):
    funcs['html'] = extHTML
    convs['html'] = 'html'
