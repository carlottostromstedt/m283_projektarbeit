from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

db = SQLAlchemy()

class Trees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude  = db.Column(db.Float, nullable=False)
    kategorie = db.Column(db.String(250), nullable=True)
    baumartlat = db.Column(db.String(250), nullable=True)
    baumgattunglat = db.Column(db.String(250), nullable=True)
    baumnamedeu = db.Column(db.String(250), nullable=True)
    baumnamelat = db.Column(db.String(250), nullable=True)
    baumnummer = db.Column(db.String(250), nullable=True)
    baumtyptext = db.Column(db.String(250), nullable=True)


db.init_app(app)

def fill_db():
    # Specify the full path if the file is in a different directory.
    file_path = 'opendata/trees-04-10-2023.json'

    with open(file_path, 'r') as file:
        data = json.load(file)

    for baum in data['features']:
        tree = Trees(longitude=baum['geometry']['coordinates'][0],
         latitude=baum['geometry']['coordinates'][1],
         kategorie=baum['properties']['kategorie'],
         baumartlat=baum['properties']['baumartlat'],
         baumgattunglat=baum['properties']['baumgattunglat'],
         baumnamedeu=baum['properties']['baumnamedeu'],
         baumnamelat=baum['properties']['baumnamelat'],
         baumnummer=baum['properties']['baumnummer'],
         baumtyptext=baum['properties']['baumtyptext'])

        db.session.add(tree)
        db.session.commit()

with app.app_context():
    db.create_all()

with app.app_context():
    fill_db()

@app.route("/")
def hello_baum():
    return "<p>Hello, Baum!</p>"
