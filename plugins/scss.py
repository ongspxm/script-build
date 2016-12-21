import scss
import cssprefix

def extScss(content):
    content = scss.Compiler(search_path=['./src']).compile_string(content)

    ### allow unicode characters in content field - content:'\236a'
    content = content.encode('unicode_escape').replace('\\u', '\\')
    return cssprefix.process(content.decode('unicode_escape'), minify=True)

def init(funcs, convs):
    funcs['scss'] = extScss
    convs['scss'] = 'css'
