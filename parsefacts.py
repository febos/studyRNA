import io
import json
import logging
import sys
import networkx as nx

from flask import jsonify, render_template


# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def draw_graph(data, obj):

    print(data['obj'][obj]['relative'])
        

    edges = set()

    for v in data['obj'][obj]['relative']:
        edges.add((obj,v))

    for v in data['obj'][obj]['relative']:
        for w in data['obj'][obj]['relative']:
            if v in data['obj'][w]['relative'] or w in data['obj'][v]['relative']:
                edges.add((w, v))

    edges = list(edges)

    g=nx.Graph()
    g.add_edges_from(edges)
    p=nx.drawing.nx_pydot.to_pydot(g)
    p.write_png('static/{}_related.png'.format(obj))


def draw_tree(data, obj, mode = 'down'):

    typs = {'down':'child','up':'parent'}

    if mode in typs:
        objs = set(data['obj'][obj][typs[mode]] + [obj,])
    elif mode == "updown":
        objs = set(data['obj'][obj]["child"] +\
                   data['obj'][obj]["parent"] + [obj,])
        

    edges = set()

    tree = data['tree']

    for v in tree:

        for w in tree[v]['up']:

            if v in objs and w in objs:

                edges.add((w, v))

        for w in tree[v]['down']:

            if v in objs and w in objs:

                edges.add((v, w))

    edges = list(edges)

    g=nx.DiGraph()
    g.add_edges_from(edges)
    p=nx.drawing.nx_pydot.to_pydot(g)
    p.write_png('static/{}_{}.png'.format(obj, mode))

                

def resolve_syn(objs, edges, syns, facts):
    """resolve synonyms and provide synonym transitivity""" 


    '''create syndict'''

    syndict = {x:x for x in objs}

    for n,s in syns:

        syndict[s] = n   

    flag = 1

    while flag:

        flag = 0

        for k in syndict.keys():

            if syndict[k] != syndict[syndict[k]]:

                flag = 1
                syndict[k] = syndict[syndict[k]]

    objs = set(syndict.values())

    '''update facts'''

    for fact in facts:

        ks = tuple(fact['obj'].keys())

        for obj in ks:

            newobj = syndict[obj]

            if newobj != obj:
                
                fact['obj'][newobj] = fact['obj'][obj]
                fact['obj'].pop(obj)


        fact['obj_order'] = sorted(fact['obj'].keys())

    '''create tree'''

    tree = {x:{'up':set(),'down':set()} for x in objs}

    for v,w in edges:

        nv = syndict[v]
        nw = syndict[w]

        tree[nv]['down'].add(nw)
        tree[nw]['up'].add(nv)
    
    return tree, syndict, facts



def resolve_tree(tree):
    """resolve transitive parents and childs"""

    parents, childs = {}, {}

    for obj in tree.keys():

        parents[obj] = set()

        pars = list(tree[obj]['up'])

        k = 0

        while k < len(pars):

            parents[obj].add(pars[k])

            for np in tree[pars[k]]['up']:

                pars.append(np)

            k += 1

    for obj in tree.keys():

        childs[obj] = set()

        chs = list(tree[obj]['down'])

        k = 0

        while k < len(chs):

            childs[obj].add(chs[k])

            for nch in tree[chs[k]]['down']:

                chs.append(nch)

            k += 1

    return parents, childs



def resolve_rel(tree, facts):
    """resolve relatives"""

    relatives = {x:set() for x in tree.keys()}

    for fact in facts:

        for obj1 in fact['obj']:

            for obj2 in fact['obj']:

                if obj1 == obj2:
                    continue

                relatives[obj1].add(obj2)
                relatives[obj2].add(obj1)

    return relatives



def sort_fact(fact, is_ind = False, ind = 0):

    if is_ind:

        return (fact[ind]['year'], fact[ind]['doi'], fact[ind]['link'], int(fact[ind]['num']), fact[ind]['text'])

    return (fact['year'], fact['doi'], fact['link'], int(fact['num']), fact['text'])



def compile_rnadata(syns, parents, childs, relatives, facts):

    rnadata = {'obj':{}}

    for obj in relatives.keys():

        rnadata['obj'][obj] = {'syn':[],
                               'parent':list(parents[obj]),
                               'child':list(childs[obj]),
                               'relative':list(relatives[obj]),
                               'fact':[]}

    for ss in syns.keys():

        if ss != syns[ss]:

            rnadata['obj'][syns[ss]]['syn'].append(ss)

    for fact in facts:

        for obj in fact['obj']:

            rnadata['obj'][obj]['fact'].append(fact)


    for obj in rnadata['obj']:

        rnadata['obj'][obj]['fact'].sort(key = sort_fact)
        rnadata['obj'][obj]['syn'].sort(key = lambda x: x.lower())
        rnadata['obj'][obj]['parent'].sort(key = lambda x: x.lower())
        rnadata['obj'][obj]['child'].sort(key = lambda x: x.lower())
        rnadata['obj'][obj]['relative'].sort(key = lambda x: x.lower())

    return rnadata

def clean_obj(obj):

    return obj.replace(':','_').replace('/','_')

def descr_fact(fact):

    tps = set()
    for x in fact['obj'].values():
        for y in x:
            tps.add(y)

    return ''.join([''.join(list(tps)),fact['year'],fact['doi'],fact['link'],fact['ref'],
            fact['text'],''.join(fact['obj_order'])]).lower()

def parse(tsvfiles='StudyRNA.tsv', log=logger):

    log.warning('rnadata is updated')

    if type(tsvfiles) == str:
        tsvfiles = [tsvfiles,]


    factlist = []
    objset   = set()
    edgeset  = set()
    synset   = set()
    

    facttypes = set()
    
    for tsv in tsvfiles:

        with open(tsv) as file:
            for line in file:
                
                row = line.strip().split('\t')

                if row[0] in ('tree','syn'):

                    objset.add(clean_obj(row[1]))
                    objset.add(clean_obj(row[2]))

                    edgeset.add((clean_obj(row[1]),clean_obj(row[2]))) if row[0] == 'tree' else synset.add((clean_obj(row[1]),
                                                                                                            clean_obj(row[2])))

                elif row[0] == 'fact':

                    fact = {'year': row[1],
                            'doi': row[2],
                            'link':row[3],
                            'ref': row[4],
                            'num': row[5],
                            'pic': row[6],
                            'text':row[7],
                            'obj' : {}}

                    for i in range(8,len(row),2):

                        fact['obj'][clean_obj(row[i])] = [x.strip() for x in row[i+1].split(',')]
                        objset.add(clean_obj(row[i]))

                        for fctp in fact['obj'][clean_obj(row[i])]:

                            facttypes.add(fctp)

                    factlist.append(fact)

    tree, syndict, factlist = resolve_syn(objset, edgeset, synset, factlist)
    parents, childs = resolve_tree(tree)
    relatives = resolve_rel(tree, factlist)

    rnadata = compile_rnadata(syndict, parents, childs, relatives, factlist)

    rnadata['facttypes'] = sorted(list(facttypes))
    rnadata['lowersyn'] = {x.lower():y.lower() for x,y in syndict.items()}

    for i in range(len(factlist)):
        factlist[i]['desc'] = descr_fact(factlist[i])

    lowers = {x.lower():x for x in rnadata['obj'].keys()}
    rnadata['lower']    = lowers
    rnadata['tree']     = tree
    rnadata['facts']    = factlist

    return rnadata


def fact_token(fact):

    return '-'.join([fact['year'],fact['doi'],fact['link'],fact['num']])

def get_facts(dic, objj, incchld, incpar, fctps, yearfrom, yearto, query):

    res = []

    objs = [objj,]

    if incchld == 'checked':

        objs += dic[objj]['child']

    if incpar == 'checked':

        objs += dic[objj]['parent']

    seen = set()

    for ob in objs:

        for fct in dic[ob]['fact']:

            if any(fctps[x] == 'checked' for x in fct['obj'][ob]) and yearfrom <= int(fct['year']) < yearto and\
               (not query or all(any(x.lower() in y.lower() for y in (fct['ref'],fct['text'],fct['link'],
                                                                      fct['doi'],' '.join(fct['obj'].keys()))) for x in query.split())) :

                token = fact_token(fct)

                if token not in seen:

                    seen.add(token)
                    res.append((ob, fct))

    result = sorted(res, key = lambda x: sort_fact(x,is_ind=True,ind=1))

    return result

def search_facts(data,yearfrom,yearto,query):


    facts, objects, objset = [], [], set()

    query = query.lower().split()

    for fact in data['facts']:

        if yearfrom <= int(fact['year']) <= yearto:

            hits = sum(1 for word in query if word in fact['desc'])

            if hits > 0:
                facts.append((hits,int(fact['year']),fact))
                for obj in fact['obj_order']:
                    objset.add(obj)

    for x in objset:
        objects.append((len(data['obj'][x]['child']),x))

    resf = [x[2] for x in sorted(facts,key=lambda x: (x[0],x[1]),reverse=True)]
    reso = [x[1] for x in sorted(objects,key= lambda x: (-x[0],x[1]))]       

    return resf,reso

if __name__ == '__main__':

    rnadata = parse()




'''
def render_notebook(inputs, outputs, execute_counters):
    """"""
    return render_template(
        'jupyter.html',
        cells=zip(range(len(inputs)), inputs, outputs, execute_counters)
    )


def execute_snippet(snippet, globs):
    """Temporary changes the standard output stream to capture exec output"""
    temp_buffer = io.StringIO()
   
    sys.stdout = temp_buffer
    exec(snippet, globs)   
    
    res = None

    for line in snippet.split('\n'):

        try:
            res = eval(line, globs)
            
        except:
            pass
    
    if res:
        print(res)   
    
    sys.stdout = sys.__stdout__
    
    return temp_buffer.getvalue()


def export(inputs, outputs, filename='ipynb.json'):
    """Export current state to ipynb format"""
    with open(filename, 'r') as f:  # json file with basic jupyter metadata
        ipynb_json = json.loads(f.read())

    # add cell data in jupyter-like format
    for in_cell, out_cell in zip(inputs, outputs):
        cell_json = {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {
                'collapsed': False,
                'scrolled': False,
            },
            'source': in_cell,
            'outputs': [{
                'output_type': 'stream',
                'name': 'stdout',
                'text': out_cell
            }]
        }
        ipynb_json['cells'].append(cell_json)

    return jsonify(ipynb_json)


def _get_cell_output(cell_json):
    """Get plain-text output of the cell"""
    cell_stdouts = [
        output for output in cell_json['outputs']
        if output.get('name', '') == 'stdout'
    ]
    return '\n'.join(
        [''.join(out['text']) for out in cell_stdouts]
    )


def _is_valid_ipynb(ipynb_json):
    return (
        ipynb_json.get('cells') is not None and
        ipynb_json.get('metadata') is not None and
        ipynb_json.get('nbformat', -1) > 0 and
        ipynb_json.get('nbformat_minor', -1) > 0
    )


def import_from_json(ipynb_json):
    if not _is_valid_ipynb(ipynb_json):
        logger.warning('Bad ipynb')
        return None
    inputs = []
    outputs = []
    for cell in ipynb_json['cells']:
        try:
            # We handle only code-contatining cells
            # No Markdown, HTML etc
            if cell['cell_type'] != 'code':
                continue
            cell_input = ''.join(cell['source'])
            cell_output = _get_cell_output(cell)
        except KeyError as e:
            logger.error(e)
            continue

        inputs.append(cell_input)
        outputs.append(cell_output)

    logger.info('Imported {} inputs, {} outputs'.format(len(inputs), len(outputs)))
    return inputs, outputs
'''
