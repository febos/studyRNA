from flask import Flask, jsonify, request, redirect, send_from_directory,render_template
import logging
import os

import parsefacts

# the main Flask application object
app = Flask(__name__)

# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

@app.route('/favicon.ico')
def favicon():
    """Handles browser's request for favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.png'
    )

@app.route('/', methods=['GET'])
def getroot():

    return render_template(
        'index.html'
    )


@app.route('/entry/<obj_name>', methods=['GET'])
def getobj(obj_name = None):

    if 'rnadata' not in globals():
        globals()['rnadata'] = parsefacts.parse(log=logger)

    if not obj_name or obj_name.lower() not in rnadata:
        return redirect('/')

    return render_template(
        'entry.html',
        facts = rnadata[obj_name.lower()]
    )

if __name__ == "__main__":

    rnadata = parsefacts.parse(log=logger)

    app.run(debug=True)


'''
# global variables to store the current state of our notebook
inputs = ['print("Type your code snippet here")']
outputs = ['']
execute_counters = [0]
current_execute_count = 0
globs = {}







@app.route('/execute_cell/<cell_id>', methods=['POST'])
def execute(cell_id=None):
    """Gets piece of code from cell_id and executes it"""
    try:
        cell_id = int(cell_id)
    except ValueError as e:
        logger.warning(e)
        return redirect('/')

    global current_execute_count
    try:
        current_execute_count += 1
        execute_counters[cell_id] = current_execute_count
        
        global globs
        
        inputs[cell_id] = request.form['input{}'.format(cell_id)]
        result = ipynb.execute_snippet(inputs[cell_id], globs)
    except BaseException as e:
        # anything could happen inside, even `exit()` call
        result = str(e)

    outputs[cell_id] = result
    return redirect('/')


@app.route('/add_cell', methods=['POST'])
def add_cell():
    """Appends empty cell data to the end"""
    inputs.append('')
    outputs.append('')
    execute_counters.append(0)
    return redirect('/')


@app.route('/remove_cell/<cell_id>', methods=['POST'])
def remove_cell(cell_id=0):
    """Removes a cell by number"""
    try:
        cell_id = int(cell_id)
        if len(inputs) < 2:
            raise ValueError('Cannot remove the last cell')
        if cell_id < 0 or cell_id >= len(inputs):
            raise ValueError('Bad cell id')
    except ValueError as e:
        # do not change internal info
        logger.warning(e)
        return redirect('/')

    # remove related data
    inputs.pop(cell_id)
    outputs.pop(cell_id)
    execute_counters.pop(cell_id)
    return redirect('/')


@app.route('/ipynb', methods=['GET', 'POST'])
def ipynb_handler():
    """
    Imports/exports notebook data in .ipynb format (a.k.a Jupyter Notebook)
    Docs: https://nbformat.readthedocs.io/en/latest/format_description.html
    """
    global inputs
    global outputs
    if request.method == 'GET':
        # return json representation of the notebook here
        return ipynb.export(inputs, outputs)
    elif request.method == 'POST':
        # update internal data
        imported = ipynb.import_from_json(request.get_json())
        # we can return None if json is not a valid ipynb
        if imported:
            inputs, outputs = imported
        # common practice for POST/PUT is returning empty json
        # when everything is 200 OK
        return jsonify({})
'''


