from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json

with open('config.json', 'r') as f:
	params = json.load(f)["params"]

local_server = True
app = Flask(__name__)
app.config.update(
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = '465',
	MAIL_USE_SSL = True,
	MAIL_USERNAME = params['email'],
	MAIL_PASSWORD = params['password']
)
mail = Mail(app)

if(local_server):
	app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return f"User {self.name}"

@app.route("/")
def index():
    return render_template('index.html', params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/posts")
def posts():
    return render_template('post.html', params=params)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
	if(request.method=='POST'):
		name = request.form.get('name')
		email = request.form.get('email')
		phone = request.form.get('phone')
		message = request.form.get('message')

		entry = Contacts(name=name, phone=phone, email=email, msg=message, date=datetime.now())
		db.session.add(entry)
		db.session.commit()
		mail.send_message(
			subject = f'New Message from {name}',
			sender = email,
			recipients = [params['email']],
			body = f'{message} \n Phone: {phone}'
		)
	return render_template('contact.html', params=params)

if __name__ == "__main__":
	app.run(debug=True)
