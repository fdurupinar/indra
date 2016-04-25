from indra.trips import trips_api
from indra.pysb_assembler import PysbAssembler
from flask import Flask, render_template, request
from wtforms import Form
from wtforms.fields import StringField, SelectMultipleField
from wtforms.fields import TextField, SubmitField
from wtforms.widgets import TextArea

from indra.statements import *

app = Flask(__name__)

class TripsForm(Form):
    trips_input = StringField('TRIPS text', widget=TextArea())
    trips_process = SubmitField('TRIPS process')
    statements_list = SelectMultipleField('TRIPS Statements', choices = [])

class ReachForm(Form):
    reach_input = TextField('REACH PMID')
    reach_process = SubmitField('REACH process')
    statements_list = SelectMultipleField('REACH Statements', choices = [])

class BiopaxForm(Form):
    biopax_input = TextField('BioPax Genes')
    biopax_process = SubmitField('BioPAX process')
    statements_list = SelectMultipleField('BioPAX Statements', choices = [])

class BelForm(Form):
    bel_input = TextField('BEL Genes')
    bel_process = SubmitField('BEL process')
    statements_list = SelectMultipleField('BEL Statements', choices = [])

class IndraForm(Form):
    statements_list = SelectMultipleField('INDRA Statements', choices = [])
    remove = SubmitField('Remove')
    select_all = SubmitField('Select all')
    select_none = SubmitField('Select none')
    pysb_assemble = SubmitField('PySB')
    graph_assemble = SubmitField('Graph')
    network_assemble = SubmitField('Network')

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

    tp = trips_api.process_text(txt)
    if tp is not None:
        return tp.statements
    else:
        return None

stmts = []
txt = ''

@app.route("/", methods=['POST', 'GET'])
def run():
    trips_form = TripsForm(request.form)
    reach_form = ReachForm(request.form)
    biopax_form = BiopaxForm(request.form)
    bel_form = BelForm(request.form)
    indra_form = IndraForm(request.form)
    stmts = []
    pysb_model = ''
    if request.method == 'POST':
        stmts = form.statements_list.choices
        print request.__dict__
        button = request.form.get('form_button')
        if button == 'stmt':
            txt = form.trips_input.data
            if txt:
                stmts = get_statements(txt)
                stmt_list = [(str(i), str(stmts[i])) for i in range(len(stmts))]
            else:
                stmts = []
            form.statements_list.choices = stmt_list
        elif button == 'pysba':
            print  form.statements_list.__dict__
            pysb_model = get_pysb_model(stmts)
            # pysb_model = 'No input text'
        else:
            stmts = None
            pysb_model = ''
    args = {'trips_form': trips_form,
            'indra_form': indra_form,
            'statements': stmts,
            'pysb_model': pysb_model}
    return render_template('canvas.html', **args)

if __name__ == "__main__":
    app.run(debug=True)
