import rules

def getIdx(text, substring):
    try:
        return text.index(substring)
    except ValueError:
        return -1

def getRules(text):
    rules = []

    while text:
        i = getIdx(text, ':')
        name = text[:i].strip()
        text = text[i+1:]
        
        a = getIdx(text, ':')
        b = getIdx(text, ';')

        if b<0:
            raise Exception('error in phasing, missing ";"')
        elif a<0:
            value = ';'.join(text.split(';')[:-1]).strip()
            text = ''
        elif a>b and not text.split(';')[0].count('url('):
            temp = text.split(';') 
            value = temp[0].strip()
            text = ';'.join(temp[1:])
        else:
            temp = text.split(')')
            value = (temp[0]+')').strip()

            text = ')'.join(temp[1:])
            text = ';'.join(text.split(';')[1:]) 

        if name and value:
            rules += [[name, value]]
    
    return rules

def getBlock(text):
    a = text.index('{')
    b = text.index('}')
    
    return dict(
        name = text[:a].strip(),
        inner = text[a+1:b],
        content = text[b+1:]
    )

def getStyles(content):
    styles = [] 
    content = preProcess(content)

    while content.count('{'):
        info = getBlock(content)
        
        special = '@media @keyframes'.split()
        if sum([1 for name in special if info['name'].startswith(name)]):
            wrapper = []
            content = content[content.index('{')+1:]

            while content.count('{'):
                a = content.index('{')
                b = content.index('}')
                info2 = getBlock(content)

                if a<b:
                    wrapper.append(dict(
                        name = info2['name'],
                        rules = getRules(info2['inner'])
                    ))
                    content = info2['content']
                else:
                    break
            
            styles.append(dict(
                name = info['name'],
                wrapper = wrapper
            ))

            content = content[content.index('}')+1:]
        else:
            styles.append(dict(
                name = info['name'],
                rules = getRules(info['inner'])
            ))
            content = info['content']

    return styles

def generateBlock(block, minify=False):
    if not block: return []

    text = []
    text.append(block['name']+'{')
    
    if not block.get('rules'): block['rules'] = []
    for rule in block['rules']:
        fmt = '    %s: %s;'
        if minify: 
            fmt = '%s:%s;'
            rule[1] = ','.join(map(lambda x:x.strip(), rule[1].split(',')))
        text.append(fmt%tuple(rule))
    
    if not block.get('wrapper'): block['wrapper'] = []
    for block in block['wrapper']:
        text += generateBlock(block, minify)

    if minify: text.append('}')
    else: text.append('}\n')

    return text

def generateText(css, minify=False):
    text = []
    for block in css:
        text += generateBlock(block, minify)

    if minify:
        return ''.join(text)
    else:
        return '\n'.join(text).strip()

def processBlock(block):
    if block.get('rules'):
        rules2 = []
        for rule in block['rules']:
            rules2 += rules.process(rule)
        block['rules'] = rules2
        return block
    
    if not block.get('wrapper'):
        print block

    wrapper = []
    for sublock in block['wrapper']: 
        wrapper.append(processBlock(sublock))
    block['wrapper'] = wrapper
    
    return block
        
def preProcess(content):
    ### remove trailing
    content = '\n'.join(map(lambda x: x.strip(), content.split('\n')))

    ### remove multiline comments
    while content.count('/*'):
        a = content.index('/*')
        b = content.index('*/')
        content = content[:a] + content[b+2:]
   
    ### remove comments
    lines = content.split('\n')
    for i in range(len(lines)):
        line = lines[i]
        
        idx = line.rfind('//')
        
        ### dun remove :// links
        if idx==-1 or line[idx-1]==':':
            continue

        lines[i] = line[:idx]
    content = '\n'.join(lines)

    return content

def process(content, minify=False):  
    css = getStyles(content)
    css2 = []
    for block in css:
        css2.append(processBlock(block))

    return generateText(css2, minify)
