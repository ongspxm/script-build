import scss

def extScss(content):
    return scss.Compiler().compile_string(content)

def init(funcs, convs):
    funcs['scss'] = extScss
    convs['scss'] = 'css'
