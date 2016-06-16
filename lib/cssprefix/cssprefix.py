import rules

def getRules(text):
    rules = []
    inner = text.split(';')
    for rule in inner:
        if not rule.count(':'): continue
        rule = map(lambda x:x.strip(), rule.split(':'))
        rules.append([rule[0], ':'.join(rule[1:])])

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
    
    ### remove comments
    while content.count('/*'):
        a = content.index('/*')
        b = content.index('*/')
        content = content[:a] + content[b+2:]

    while content.count('{'):
        info = getBlock(content)

        if info['name'].startswith('@media'):
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

    wrapper = []
    for sublock in block['wrapper']: 
        wrapper.append(processBlock(sublock))
    block['wrapper'] = wrapper
    return block
        

def process(content, minify=False):
    css = getStyles(content)
    css2 = []
    for block in css:
        css2.append(processBlock(block))

    return generateText(css2, minify)
