import cssprefix

def extCss(content):
    return cssprefix.process(content, minify=True)

def init(funcs, convs):
    funcs['css'] = extCss
    convs['css'] = 'css'
