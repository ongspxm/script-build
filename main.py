'''
global ext_funcs stores the plugins function
global ext_convs stores the corresponding extensions (jade -> html, scss -> css)

keys of the dictionary is the targeted file extensions (.scss, .html, .jade)
'''

#!/usr/bin/env python
import os
import sys
import imp

path = '/'.join(sys.argv[0].split('/')[:-1])
sys.path.append(os.path.join(path, 'lib'))

import shutil
import pickle

import pyjade
from scss import Compiler as scss

src = './src'
dst = './build'
modification_db = 'spuild.db'
skipped = ''.split()

gitPath = os.path.join(dst, '.git')
tmpPath = './.gittmp'

ext_funcs = {}
ext_convs = {}
def loadPlugins():
    path_plugins = os.path.join(path, 'plugins')
    plugins = [f for f in os.listdir(path_plugins) if f.endswith('.py')]

    for plugin in plugins:
        path_plugin = os.path.join(path_plugins, plugin)
        plugin = imp.load_source(plugin[:-3], path_plugin)
        plugin.init(ext_funcs, ext_convs)

def cleanDst():
    pickle.dump({}, open(modification_db, 'wb'))

    if not os.path.isdir(dst):
        return

    # dun remove .git function
    if os.path.isdir(gitPath):
        shutil.move(gitPath, tmpPath)

    try: shutil.rmtree(dst)
    except: shutil.rmtree(dst)

def resetRepo():
    if os.path.isdir(tmpPath):
        shutil.move(tmpPath, gitPath)

def main(clean=False, concat=False):
    if clean: cleanDst()

    modification_times = {}
    if os.path.isfile(modification_db):
        modification_times = pickle.load(open(modification_db, 'rb'))

    concat_str = dict(js='', css='')

    for root, dirs, files in os.walk(src):
        for name in files:
            sname = os.path.join(root, name)
            dname = os.path.join(root.replace(src, dst, 1), name)
            ext = name.split('.')[-1]

            ### vim swap files
            if len(ext)==3 and ext[:2]=='sw': continue

            ### skipped files
            if ext in skipped: continue

            ### Skipped if modified time change pass
            time = modification_times.get(sname)
            modification_times[sname] = os.path.getmtime(sname)
            if time==modification_times[sname] and not concat:
                continue

            print 'Processing', sname

            content = None
            func = ext_funcs.get(ext)
            with open(sname, 'r') as fin:
                content = fin.read()
                if func:
                    content = func(content)
                ext = ext_convs.get(ext) or ext

            if dname[1:].count('.'):
                dname = '.'.join(dname.split('.')[:-1])+'.'+ext
            ddir = '/'.join(dname.split('/')[:-1])

            if ddir and not os.path.exists(ddir):
                os.makedirs(ddir)

            if content:
                with open(dname, 'w') as fout:
                    fout.write(content+'\n')

            if concat and (ext=='js' or ext=='css'):
                concat_str[ext] += '\n'+content+'\n'

    ### Concat function
    fname = os.path.join(dst, 'all.')
    for key in concat_str.keys():
        if concat_str[key]:
            with open(fname+key, 'w') as fout:
                fout.write(concat_str[key])

    pickle.dump(modification_times, open(modification_db, 'wb'))

    if clean: resetRepo()

_USAGE = '''
Use -c to clean build directory before building.
Use -a to concat .js and .css files.

Use -h to display this help message.
'''

if __name__=='__main__':
    clean = False
    concat = False

    args = sys.argv
    if '-c' in args:
        clean = True
    if '-a' in args:
        concat = True
    if '-h' in args:
        print _USAGE

    loadPlugins()
    main(clean, concat)
