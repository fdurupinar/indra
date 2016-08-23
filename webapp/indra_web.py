from indra import trips, reach, biopax, bel, literature
from indra.assemblers import PysbAssembler
from indra.assemblers import GraphAssembler
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
    reach_select = SubmitField('>>')

class BiopaxForm(Form):
    biopax_input = TextField('BioPax Genes')
    biopax_process = SubmitField('>>')
    biopax_stmts = SelectMultipleField('BioPAX Statements', choices = [])
    biopax_select = SubmitField('>>')

class BelForm(Form):
    bel_input = TextField('BEL Genes')
    bel_process = SubmitField('>>')
    bel_stmts = SelectMultipleField('BEL Statements', choices = [])
    bel_select = SubmitField('>>')

class IndraForm(Form):
    indra_stmts = SelectMultipleField('INDRA Statements', choices = [])
    remove = SubmitField('Remove')
    select_all = SubmitField('Select all')
    select_none = SubmitField('Select none')
    pysb_assemble = SubmitField('PySB >>')
    graph_assemble = SubmitField('Graph >>')

def get_pysb_model(stmts):
    if stmts is not None:
        pa = PysbAssembler()
        pa.add_statements(stmts)
        pa.make_model()
        return pa.print_model()
    else:
        return 'Blank model'

def get_graph_model(stmts):
    if stmts is not None:
        ga = GraphAssembler()
        ga.add_statements(stmts)
        ga.make_model()
        return ga.get_string()
    else:
        return 'Blank model'

def trips_process_text(txt):
    tp = trips.process_text(txt)
    if tp is not None:
        return tp.statements
    return None

def reach_process_pmid(pmid):
    pmid = pmid.strip()
    txt, txt_format = literature.get_full_text(pmid, 'pmid')
    if txt_format == 'nxml':
        rp = reach.process_nxml_str(txt)
    elif txt_format in ('txt', 'abstract'):
        rp = reach.process_text(txt)
    else:
        return None
    if rp is not None:
        return rp.statements
    return None

def biopax_process_neighborhood(genes_str):
    genes = genes_str.split(',')
    genes = [g.strip() for g in genes]
    if len(genes) == 1:
        bp = biopax.process_pc_neighborhood(genes)
    else:
        bp = biopax.process_pc_pathsbetween(genes)
    if bp is not None:
        bp.get_phosphorylation()
        bp.get_dephosphorylation()
        return bp.statements
    return None

def bel_process_neighborhood(genes_str):
    genes = genes_str.split(',')
    genes = [g.strip() for g in genes]
    bp = bel.process_ndex_neighborhood(genes)
    if bp is not None:
        return bp.statements
    return None

def get_stmt_list(stmts):
    list_choices = []
    for i, st in enumerate(stmts):
        choice = ('%d' % i, '%s' % st)
        list_choices.append(choice)
    return list_choices

global trips_stmts
global trips_txt
global reach_stmts
global reach_txt
global biopax_stmts
global biopax_txt
global bel_stmts
global bel_txt
global indra_stmts
trips_stmts = []
trips_txt = ''
reach_stmts = []
reach_txt = ''
indra_stmts = []
biopax_stmts = []
biopax_txt = ''
bel_stmts = []
bel_txt = ''

@app.route("/", methods=['POST', 'GET'])
def run():
    global trips_stmts
    global trips_txt
    global reach_stmts
    global reach_txt
    global biopax_stmts
    global biopax_txt
    global bel_stmts
    global bel_txt
    global indra_stmts
    trips_form = TripsForm(request.form)
    reach_form = ReachForm(request.form)
    biopax_form = BiopaxForm(request.form)
    bel_form = BelForm(request.form)
    indra_form = IndraForm(request.form)
    model = ''
    print request.form
    print trips_form.data
    print indra_form.data
    if request.method == 'POST':
        #stmts = form.statements_list.choices
        if request.form.get('trips_process'):
            print 'Trips process'
            trips_txt = trips_form.data.get('trips_input')
            trips_stmts = trips_process_text(trips_txt)
            trips_stmts_list = get_stmt_list(trips_stmts)
        elif request.form.get('reach_process'):
            reach_txt = reach_form.data.get('reach_input')
            reach_stmts = reach_process_pmid(reach_txt)
            reach_stmts_list = get_stmt_list(reach_stmts)
        elif request.form.get('biopax_process'):
            biopax_txt = biopax_form.data.get('biopax_input')
            biopax_stmts = biopax_process_neighborhood(biopax_txt)
        elif request.form.get('bel_process'):
            bel_txt = bel_form.data.get('bel_input')
            bel_stmts = bel_process_neighborhood(bel_txt)
        elif request.form.get('trips_select'):
            indra_stmts += trips_stmts
        elif request.form.get('reach_select'):
            indra_stmts += reach_stmts
        elif request.form.get('biopax_select'):
            indra_stmts += biopax_stmts
        elif request.form.get('bel_select'):
            indra_stmts += bel_stmts
        elif request.form.get('pysb_assemble'):
            model = get_pysb_model(indra_stmts)
        elif request.form.get('graph_assemble'):
            model = get_graph_model(indra_stmts)
        elif request.form.get('remove'):
            stmts_to_remove = indra_form.data.get('indra_stmts')
        else:
            print 'Other'
        trips_form.trips_stmts.choices = get_stmt_list(trips_stmts)
        trips_form.trips_input.data = trips_txt
        reach_form.reach_stmts.choices = get_stmt_list(reach_stmts)
        reach_form.reach_input.data = reach_txt
        biopax_form.biopax_stmts.choices = get_stmt_list(biopax_stmts)
        biopax_form.biopax_input.data = biopax_txt
        bel_form.bel_stmts.choices = get_stmt_list(bel_stmts)
        bel_form.bel_input.data = bel_txt
        indra_form.indra_stmts.choices = get_stmt_list(indra_stmts)
    args = {'trips_form': trips_form,
            'reach_form': reach_form,
            'biopax_form': biopax_form,
            'bel_form': bel_form,
            'indra_form': indra_form,
            'pysb_model': model}
    return render_template('canvas.html', **args)

if __name__ == "__main__":
    app.run(debug=True)
