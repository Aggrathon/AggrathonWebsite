import app
from flask_login import login_required
from database import Text, db
from flask import request
from model import RETURN_SUCCESS

app.add_hook(app.HOOK_ADMIN_WIDGET, lambda : (False, "Admin Notes", "modules/notes/widget.html", Text.query.get('ADMIN_NOTES')))
app.add_hook(app.HOOK_TEST_CONTENT, lambda : add_admin_notes("Remember to remove all test data"))

@app.app.route('/admin/', methods=['POST'])
@login_required
def admin_notes():
	action = request.form.get('action')
	if action == 'notes':
		return set_admin_notes(request.form.get('notes'))
	else:
		return "Unrecognized Action"

def set_admin_notes(notes):
	dbn = Text.query.get('ADMIN_NOTES')
	if dbn:
		if notes == "":
			db.session.delete(dbn)
		else:
			dbn.text = notes
		db.session.commit()
	elif notes != "":
		db.session.add(Text('ADMIN_NOTES', notes))
		db.session.commit()
	return RETURN_SUCCESS

def add_admin_notes(notes):
	dbn = Text.query.get('ADMIN_NOTES')
	if dbn:
		dbn.text = dbn.text +"<br />"+notes
		db.session.commit()
	else:
		db.session.add(Text('ADMIN_NOTES', notes))
		db.session.commit()
	return RETURN_SUCCESS
