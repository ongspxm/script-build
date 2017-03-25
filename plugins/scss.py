import scss
import cssprefix

def encode(stri):
    return stri.encode('unicode_escape').replace('\\u', '\\\\')

def decode(stri):
    return stri.decode('unicode_escape')

def extScss(content):
    content = scss.Compiler(search_path=['./src']).compile_string(content)

    ### allow unicode characters in content field - content:'\236a'
    return cssprefix.process(decode(encode(content)), minify=True)

def init(funcs, convs):
    funcs['scss'] = extScss
    convs['scss'] = 'css'
