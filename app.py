import os
import re
import uuid
import numpy as np
from cv2 import *
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask import send_from_directory
from datetime import datetime
from fusions import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy()
bcrypt = Bcrypt(app)  # Initialize Flask-Bcrypt

login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    boards = db.relationship('Board', back_populates='user')

class Board(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    filename = db.Column(db.String(250), unique=True, nullable=False)
    fusions = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', back_populates='boards')


db.init_app(app)


with app.app_context():
	db.create_all()


@login_manager.user_loader
def loader_user(user_id):
	return Users.query.get(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8')
        user = Users(username=request.form.get("username"), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
def logout():
	logout_user()  
	return redirect(url_for("home"))

@app.route("/")
def home():
	return render_template("home.html")

@app.route('/create', methods=["GET", "POST"])
def create():
	if request.method == "POST":
		board = Board(name=request.form.get("name"))
		db.session.add(board)
		db.session.commit()
		return redirect(url_for("BOARD"))
	return render_template("create_board.html")

if __name__ == "__main__":
	app.run()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser also
        # submits an empty part without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Generate a unique filename
            unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            boardname = "Board-" + current_time
            print("START FUSIONS")
            path = f"{app.config['UPLOAD_FOLDER']}/{unique_filename}"
            print(path)
            fusion_results = showFusions(path)
            analyzed_image = fusion_results[1]
            print(type(analyzed_image))
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], ("analyzed" + unique_filename)), analyzed_image) 
            fusions = f"{fusion_results[0]}"
            fusions = fusions[1:-1]
            fusions = re.sub("'", "", fusions)
            print("FINISHED FUSIONS")
            # Create a new board associated with the current user
            board = Board(name=boardname, filename=unique_filename, user=current_user, fusions=fusions)
            db.session.add(board)
            db.session.commit()
            
            return redirect(url_for('boards', filename=unique_filename))
    return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/boards')
def boards():
    boards = Board.query.all() 
    return render_template('boards.html', boards=boards)

@app.route('/boards/<id>')
def board(id):
    board = Board.query.filter_by(id=id).first_or_404()
    fusions = board.fusions
    fusions = re.sub("\],", "].", fusions)
    fusions = re.sub(" ", "", fusions)
    fusions_array = fusions.split(".")
    for i in range(0,len(fusions_array)):
        fusion = re.sub("\]", "", fusions_array[i])
        fusion = re.sub("\[", "", fusion)
        fusion = fusion.split(",")
        fusions_array[i] = fusion

    # fusions = re.sub("\]", "", fusions)
    # fusions = re.sub(" ", "", fusions)
    # fusions_array = fusions.split(",")
    return render_template('board.html', board=board, fusions=fusions_array)
