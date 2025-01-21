from flask import Flask, request, jsonify, render_template, redirect,session
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
    hpbm = db.Column(db.String(100), nullable=False)  # Public Key
    di = db.Column(db.String(100), nullable=False)  # Device Info



# Fog Node Model
class FogNode(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Fog Node ID
    hpbf = db.Column(db.String(100), nullable=False)  # Public Key

# Initialize the Database
with app.app_context():
    db.create_all()

# API Endpoint to Add Smart Meter
# API Endpoint to Add Smart Meter
@app.route('/addMeter', methods=['POST'])
def add_meter():
    data = request.json
    new_meter = SmartMeter(id=data['newIDM'], hpbm=data['newHPBM'], di=data['DI'])
    db.session.add(new_meter)
    db.session.commit()
    return jsonify({"message": "Smart meter added successfully!"})


# API Endpoint to Add Fog Node
@app.route('/addFogNode', methods=['POST'])
def add_fog_node():
    data = request.json
    new_fog = FogNode(id=data['newIDF'], hpbf=data['newHPBF'])
    db.session.add(new_fog)
    db.session.commit()
    return jsonify({"message": "Fog node added successfully!"})

# API Endpoint to Remove Smart Meter
@app.route('/removeMeter', methods=['POST'])
def remove_meter():
    data = request.json
    meter = SmartMeter.query.get(data['IDM'])
    if meter:
        db.session.delete(meter)
        db.session.commit()
        return jsonify({"message": "Smart meter removed successfully!"})
    return jsonify({"error": "Meter not found"}), 404

# API Endpoint to Remove Fog Node
@app.route('/removeFogNode', methods=['POST'])
def remove_fog_node():
    data = request.json
    fog_node = FogNode.query.get(data['IDF'])
    if fog_node:
        db.session.delete(fog_node)
        db.session.commit()
        return jsonify({"message": "Fog node removed successfully!"})
    return jsonify({"error": "Fog node not found"}), 404

# API Endpoint to Update Smart Meter
@app.route('/updateMeter', methods=['POST'])
def update_meter():
    data = request.json
    meter = SmartMeter.query.get(data['IDM'])
    if meter:
        meter.hpbm = data['newHPBM']
        db.session.commit()
        return jsonify({"message": "Smart meter updated successfully!"})
    return jsonify({"error": "Meter not found"}), 404

# API Endpoint to Update Fog Node
@app.route('/updateFogNode', methods=['POST'])
def update_fog_node():
    data = request.json
    fog_node = FogNode.query.get(data['IDF'])
    if fog_node:
        fog_node.hpbf = data['newHPBF']
        db.session.commit()
        return jsonify({"message": "Fog node updated successfully!"})
    return jsonify({"error": "Fog node not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
