from flask import Flask, request, render_template, redirect,session
from flask_sqlalchemy import SQLAlchemy
import bcrypt


app = Flask(__name__)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_meter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'secret_key'



# Smart Meter Model
class SmartMeter(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Meter ID
    key= db.Column(db.String(100), nullable=False)  # Public Key
    di= db.Column(db.String(100), nullable=False)  # Device Info

def __init__(self,id,key,di):
        self.id = id
        self.di=di
        self.key = bcrypt.hashpw(key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
def check_key(self,key):
        return bcrypt.checkpw(key.encode('utf-8'),self.key.encode('utf-8'))



# Fog Node Model
class FogNode(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Fog Node ID
    key = db.Column(db.String(100), nullable=False)  # Public Key
def __init__(self,id,key):
        self.id = id
        self.key = bcrypt.hashpw(key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
def check_key(self,key):
        return bcrypt.checkpw(key.encode('utf-8'),self.key.encode('utf-8'))




# Initialize the Database
with app.app_context():
    db.create_all()



# API Endpoint to Add Smart Meter
@app.route('/addm', methods=['POST'])
def add_meter():
    data = request.json
    new_meter = SmartMeter(id=data['newIDM'], hpbm=data['newHPBM'], di=data['DI'])
    db.session.add(new_meter)
    db.session.commit()
    return jsonify({"message": "Smart meter added successfully!"})

