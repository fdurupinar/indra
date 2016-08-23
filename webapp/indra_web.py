from indra import trips
from indra.assemblers import PysbAssembler
from indra.statements import Statement
from flask import Flask, render_template, request
from wtforms import Form
from wtforms.fields import StringField, SelectMultipleField
from wtforms.fields import TextField, SubmitField
from wtforms.widgets import TextArea

from indra.statements import *

app = Flask(__name__)

class TripsForm(Form):
    trips_input = StringField('TRIPS text', widget=TextArea())
    trips_process = SubmitField('>>')
    trips_stmts = SelectMultipleField('TRIPS Statements', choices=[])
    trips_select = SubmitField('>>')

class ReachForm(Form):
    reach_input = TextField('REACH PMID')
    reach_process = SubmitField('>>')
    reach_stmts = SelectMultipleField('REACH Statements', choices = [])

class BiopaxForm(Form):
    biopax_input = TextField('BioPax Genes')
    biopax_process = SubmitField('>>')
    biopax_stmts = SelectMultipleField('BioPAX Statements', choices = [])

class BelForm(Form):
    bel_input = TextField('BEL Genes')
    bel_process = SubmitField('>>')
    bel_stmts = SelectMultipleField('BEL Statements', choices = [])

class IndraForm(Form):
    indra_stmts = SelectMultipleField('INDRA Statements', choices = [])
    remove = SubmitField('Remove')
    select_all = SubmitField('Select all')
    select_none = SubmitField('Select none')
    pysb_assemble = SubmitField('PySB >>')
    graph_assemble = SubmitField('Graph >>')
    network_assemble = SubmitField('Network >>')

def get_pysb_model(stmts):
    if stmts is not None:
        pa = PysbAssembler()
        pa.add_statements(stmts)
        pa.make_model()
        return pa.print_model()
    else:
        return 'Blank model'

def get_statements(txt):
    stmts = [Complex([Agent('A'), Agent('B')]), Complex([Agent('C'), Agent('D')])]
    return stmts

    tp = trips.process_text(txt)
    if tp is not None:
        return tp.statements
    else:
        return None

def get_stmt_list(stmts):
    list_choices = []
    for i, st in enumerate(stmts):
        choice = ('%d' % i, '%s' % st)
        list_choices.append(choice)
    return list_choices

global trips_stmts
global indra_stmts
trips_stmts = []
indra_stmts = []

@app.route("/", methods=['POST', 'GET'])
def run():
    global trips_stmts
    global indra_stmts
    print trips_stmts
    trips_form = TripsForm(request.form)
    reach_form = ReachForm(request.form)
    biopax_form = BiopaxForm(request.form)
    bel_form = BelForm(request.form)
    indra_form = IndraForm(request.form)
    pysb_model = ''
    print request.form
    print trips_form.data
    if request.method == 'POST':
        #stmts = form.statements_list.choices
        if request.form.get('trips_process'):
            print 'Trips process'
            txt = request.form['trips_input']
            trips_stmts = get_statements(txt)
            trips_stmts_list = get_stmt_list(trips_stmts)
        if request.form.get('trips_select'):
            indra_stmts = trips_stmts
        if request.form.get('reach_process'):
            print 'Reach process'
        elif request.form.get('biopax_process'):
            print 'Biopax process'
        elif request.form.get('bel_process'):
            print 'BEL process'
        elif request.form.get('pysb_assemble'):
            print indra_stmts
            pysb_model = get_pysb_model(indra_stmts)
        else:
            print 'Other'
        trips_form.trips_stmts.choices = get_stmt_list(trips_stmts)
        indra_form.indra_stmts.choices = get_stmt_list(indra_stmts)
    args = {'trips_form': trips_form,
            'reach_form': reach_form,
            'biopax_form': biopax_form,
            'bel_form': bel_form,
            'indra_form': indra_form,
            'pysb_model': pysb_model}
    return render_template('canvas.html', **args)

if __name__ == "__main__":
    app.run(debug=True)
