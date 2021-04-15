import io
import json
import logging
import sys

from flask import jsonify, render_template


# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def resolve_syn(objs, edges, syns, facts):
    """resolve synonyms and provide synonym transitivity"""


    # tree: obj: [[ups], [downs]]
    # update factlist
    # syndict: syn: name | name: name
    
    return tree, syndict, facts



def resolve_tree(tree):
    """resolve transitive parents and childs"""

    return parents, childs



def resolve_rel(facts):
    """resolve relatives"""

    return relatives



def compile_rnadata(syns, parents, childs, relatives, facts):

    # rnadata: {name: {syns,parents,childs,relatives,facts}}

    return rnadata



def parse(tsvfiles='StudyRNA.tsv', log=logger):

    log.warning('rnadata is updated')

    if type(tsvfiles) == str:
        tsvfiles = [tsvfiles,]


    factlist = []
    objset   = set()
    edgeset  = set()
    synset   = set()
    

    for tsv in tsvfiles:

        with open(tsv) as file:
            for line in file:
                
                row = line.strip().split('\t')

    tree, syndict, factlist = resolve_syn(objset, edgeset, synset, factlist)
    parents, childs = resolve_tree(tree)
    relatives = resolve_rel(factlist)

    rnadata = compile_rnadata(syndict, parents, childs, relatives, factlist)

    return rnadata



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
