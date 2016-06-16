import scss
import cssprefix

def extScss(content):
    content = scss.Compiler().compile_string(content).replace('\\\\', '\\')
    return cssprefix.process(content, minify=True) 

def init(funcs, convs):
    funcs['scss'] = extScss
    convs['scss'] = 'css'
