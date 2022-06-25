from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for, flash
#from werkzeug.utils import secure_filename
from flask_cors import CORS
import config
from config import Config
from ledger import Ledger

# Python program to find SHA256 hash string of a file
import hashlib

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Submit')
    
#https://flask-wtf.readthedocs.io/en/1.0.x/quickstart/#creating-forms   
class MyForm1(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    domain = StringField('domain', validators=[DataRequired()])
    
class set_key_value_form(FlaskForm):
    account = StringField('Account Id:', validators=[DataRequired()])
    key = StringField('Key:', validators=[DataRequired()])
    value = StringField('Value:', validators=[DataRequired()])
    

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

ledger = Ledger()
history = []

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = MyForm1()
    return render_template('signup.html', form=form)
    
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = MyForm1()
    if form.validate_on_submit():
        username_input = form.name.data
        domain_input = form.domain.data
        ledger.create_account(username_input, domain_input)
        return redirect('/submit')
    return render_template('submit.html', form=form)
    
@app.route('/set_key_value', methods=['GET', 'POST'])
def set_key_value():
    form = set_key_value_form()
    return render_template('set_key_value.html', form=form)
    
@app.route('/submit_key_value', methods=['GET', 'POST'])
def submit_key_value():
    form = set_key_value_form()
    if form.validate_on_submit():
        account_input = form.account.data
        key_input = form.key.data
        value_input = form.value.data
        ledger.set_key_pair_to_user(account_input, key_input, value_input)
        return redirect('/submit_key_value')
    return render_template('submit_key_value.html', form=form)

@app.route('/', methods=['GET'])  # Decorator
def iroha_admin():
    return send_from_directory('templates', 'iroha_admin.html')

@app.route('/iroha_user', methods=['GET'])  # Decorator
def iroha_user():
    return send_from_directory('templates', 'iroha_user.html')
    
@app.route('/iroha_user_assets', methods=['GET'])  # Decorator
def iroha_user_assets():
    return send_from_directory('templates', 'iroha_user_assets.html')
    
@app.route('/iroha_admin_assets', methods=['GET'])  # Decorator
def iroha_admin_assets():
    return send_from_directory('templates', 'iroha_admin_assets.html')
 
@app.route('/admin_details', methods=['GET'])
def admin_details():
    details = ledger.get_admin_details()
    print("details= ", details)
    response = {
            'message': details,
            'message2': 'Details loaded.'            
        }
    return jsonify(response), 200

@app.route('/user_details', methods=['GET'])
def user_details():
    details = ledger.get_user_details()
    print("details= ", details)
    response = {
            'message': details,
            'message2': 'Details loaded.'            
        }
    return jsonify(response), 200
      
@app.route('/user_assets', methods=['GET'])
def user_assets():
    details = ledger.get_user_account_assets()
    print("details= ", details)
    response = {
            'message': details,
            'message2': 'Details loaded.'            
        }
    return jsonify(response), 200
    
@app.route('/admin_assets', methods=['GET'])
def admin_assets():
    details = ledger.get_admin_account_assets()
    print("details= ", details)
    response = {
            'message': details,
            'message2': 'Details loaded.'            
        }
    return jsonify(response), 200 
    
@app.route('/upload', methods=['GET', 'POST'])
def index():
	global value_1
	if request.method == 'POST':
		uploaded_file = request.files['file']
		if uploaded_file.filename != '':
			uploaded_file.save(uploaded_file.filename)
		filename = uploaded_file.filename
		sha256_hash = hashlib.sha256()
		with open(filename,"rb") as f:
			# Read and update hash string value in blocks of 4K
			for byte_block in iter(lambda: f.read(4096),b""):
				sha256_hash.update(byte_block)
			print(sha256_hash.hexdigest())
			#key = 'hash_1'
			value_1 = sha256_hash.hexdigest()
			#print (value_1)
			ledger.set_key_pair_to_userone(value_1)
		return redirect(url_for('index'))
	return render_template('upload.html')

if __name__ == '__main__':
    #ledger.init_ledger()
    app.run('0.0.0.0')
