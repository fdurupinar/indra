from indra.trips import trips_api
from indra.pysb_assembler import PysbAssembler
from flask import Flask, render_template, request
from wtforms import Form
from wtforms.fields import StringField, SelectMultipleField
from wtforms.widgets import TextArea
app = Flask(__name__)

class IndraForm(Form):
    trips_input = StringField('TRIPS input', widget=TextArea())
    reach_input = StringField('REACH input', widget=TextArea())
    statements_list = SelectMultipleField('Statements', choices = [])

def get_pysb_model(stmts):
    if stmts is not None:
        pa = PysbAssembler()
        pa.add_statements(stmts)
        pa.make_model()
        return pa.print_model()
    else:
        return 'Blank model'

def get_statements(txt):
    tp = trips_api.process_text(txt)
    if tp is not None:
        return tp.statements
    else:
        return None

@app.route("/", methods=['POST', 'GET'])
def run():
    form = IndraForm(request.form)
    if request.method == 'POST':
        print request.__dict__
        txt = form.trips_input.data
        if txt:
            stmts = get_statements(txt)
            stmt_list = [(str(i), str(stmts[i])) for i in range(len(stmts))]
            form.statements_list.choices = stmt_list
            pysb_model = get_pysb_model(stmts)
        else:
            stmts = None
            pysb_model = 'No input text'
    else:
        stmts = None
        pysb_model = 'Let\'s start!'
    args = {'form': form,
            'statements': stmts,
            'pysb_model': pysb_model}
    return render_template('canvas.html', **args)

if __name__ == "__main__":
    app.run(debug=True)
