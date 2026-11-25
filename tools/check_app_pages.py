#!/usr/bin/env python3
"""
check_app_pages - test only: the App Pages.incl the generator writes, linted with the runtime.

    check_app_pages.py [<path to FutureBasic_Documentation>]
    check_app_pages.py --help

The generator (App Generator.incl, AppPagesSource) builds App Pages.incl as text. FB does not
run here, so this check reads AppPagesSource from the generator's source and plays its string
building for two entities (Customer, Order): each MutableStringAppendString, StringWithFormat,
and the loop over the model's entities. It writes the result into a temporary project with the
real runtime (src/Runtime), the app templates (src/Templates/App) and small stand-in bindings,
then runs fblint on it, so a generated call to a function that does not exist, a keyword used
as a name or an unbalanced block fails here instead of in the author's build.
"""
import re,os,shutil,sys,subprocess,tempfile
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
if len(sys.argv)>1 and sys.argv[1] in ('-h','--help'):
    print(__doc__); sys.exit(0)
DOCS=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'..','FutureBasic_Documentation')
if not os.path.isdir(DOCS): DOCS=os.path.join(ROOT,'..','futurebasic_documentation')
gen=open(os.path.join(ROOT,'src','Generator','App Generator.incl'),newline='').read().replace('\r','\n')
src=gen[gen.index('local fn AppPagesSource('):]
src=src[:src.index('\nend fn = s\n')+len('\nend fn = s')]
body=src[src.index('long               index')+len('long               index'):src.rindex('end fn = s')]
D=tempfile.mkdtemp()
os.makedirs(D+'/genapp')
res=[{'name':'Customer','formNib':'CustomerForm','listNib':'CustomerList'},{'name':'Order','formNib':'OrderForm','listNib':'OrderList'}]
LIT=re.compile(r'@"((?:[^"\\]|\\.)*)"')
def unesc(t): return t.replace('\\n','\n').replace('\\"','"').replace('\\\\','\\')
out=[]
def pre(n): return n[0].lower()+n[1:]
def ev(e,env):
    e=e.strip()
    if e=='index': return str(env['index'])
    if e in('name','prefix'): return env[e]
    if 'XibResourcePrefix' in e: return pre(env['resource']['name'])
    if 'formNib' in e: return env['resource']['formNib']
    if 'listNib' in e: return env['resource']['listNib']
    if 'DictionaryObjectForKey( resource, @"name" )' in e: return env['resource']['name']
    if 'TypeMapDefaultTitle' in e: return env['name']+'s'
    if '@"icon"' in e: return 'person.2'
    if 'appSymbol' in e: return 'building.2'
    if 'tagline' in e: return 'Tag'
    if 'copyright' in e: return '(c) Co'
    raise Exception(e)
def split_args(t):
    a,d,c,q=[],0,'',False
    i=0
    while i<len(t):
        ch=t[i]
        if q:
            c+=ch
            if ch=='\\': c+=t[i+1]; i+=2; continue
            if ch=='"': q=False
        else:
            if ch=='"': q=True
            if ch=='(': d+=1
            if ch==')': d-=1
            if ch==',' and d==0: a.append(c); c=''; i+=1; continue
            c+=ch
        i+=1
    a.append(c); return a
lines=body.strip('\n').split('\n')
def run(lines,env):
    i=0
    while i<len(lines):
        l=lines[i].strip()
        if l.startswith('for resource in'):
            j=i+1
            while lines[j].strip()!='next': j+=1
            for r in res:
                env['resource']=r; run(lines[i+1:j],env)
            i=j+1; continue
        if l=='index = 0': env['index']=0
        elif l=='index++': env['index']+=1
        elif re.match(r'name\s*=',l): env['name']=env['resource']['name']
        elif re.match(r'prefix\s*=',l): env['prefix']=pre(env['resource']['name'])
        elif l.startswith('MutableStringAppendString( s, fn StringWithFormat('):
            inner=l[len('MutableStringAppendString( s, fn StringWithFormat('):l.rindex(') )')]
            args=split_args(inner)
            fmt=unesc(LIT.search(args[0]).group(1))
            vals=iter([ev(a,env) for a in args[1:]])
            out.append(re.sub(r'%(ld|@)',lambda m: next(vals),fmt))
        elif l.startswith('MutableStringAppendString( s, @"'):
            out.append(unesc(LIT.search(l).group(1)))
        elif l=='' or l.startswith('//'): pass
        else: raise Exception('?? '+l)
        i+=1
run(lines,{'index':0})
G=D+'/genapp'
open(G+'/App Pages.incl','w',newline='').write(''.join(out).replace('\n','\r'))
tags=''
for k,r in enumerate(res):
    p=pre(r['name'])
    tags+=f'_{p}View = {100+k*100}\r_{p}List = {101+k*100}\r_{p}ListTable = {102+k*100}\r_{p}ViewHeight = 300\r'
open(G+'/Model Tags.incl','w',newline='').write(tags)
for r in res:
    n=r['name']
    open(G+f'/{n} Binding.incl','w',newline='').write(f'void local fn {n}RecordToForm( aRecord as CFDictionaryRef )\rend fn\r\rlocal fn {n}FormToRecord as CFMutableDictionaryRef\rend fn = fn MutableDictionaryNew\r\rvoid local fn {n}RecordsToList( records as CFArrayRef )\rend fn\r'+f'\rvoid local fn {n}FormSetUp\rend fn\r\rlocal fn {n}Lookups as CFArrayRef\rend fn = @[]\r\rvoid local fn {n}FillLookup( lookupEntity as CFStringRef, records as CFArrayRef )\rend fn\r')
R=os.path.join(ROOT,'src')+'/'
for f in ['Data SQLite.incl','DataObject.glbl','DataObject_Super.incl','DataObject.incl','Data Model.incl','Data Records.incl','Logic Rules.incl','Logic Row.incl','Logic Engine.incl','App Data Lite.incl','App Shell.incl','Binding Support.incl']:
    shutil.copy(R+'Runtime/'+f,G)
for f in ['EventHandlers.incl','Menus.incl','Theme.incl','Rules.incl']:
    shutil.copy(R+'Templates/App/'+f,G)
open(G+'/Studio Rules.incl','w',newline='').write('void local fn DeclareStudioRules\rend fn\r')

run_ = subprocess.run([sys.executable, os.path.join(HERE,'fblint.py'), '--headers', os.path.join(DOCS,'Toolboxes','Headers'), G], capture_output=True, text=True)
print(run_.stdout.strip())
ok = run_.returncode == 0 and ' 0 problems' in run_.stdout
print('check_app_pages: ' + ('0 failed' if ok else '1 failed'))
shutil.rmtree(D)
sys.exit(0 if ok else 1)
