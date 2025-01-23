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
    meterId = db.Column(db.String(50), primary_key=True)  # Meter ID
    state = db.Column(db.String(100), nullable=False)  # State
    city = db.Column(db.String(100), nullable=False)  # City
    house_number = db.Column(db.String(50), nullable=False)  # House Number
    phone_number = db.Column(db.Integer, nullable=False)  # Phone Number
    password = db.Column(db.String(100), nullable=False)  # Password
    fog_node = db.Column(db.String(100), nullable=False)  # Fog Node Connection




class FogNode(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Fog Node ID
    location = db.Column(db.String(100), nullable=False)  # Location

# Initialize the Database
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/next')
def next():
    return render_template('next.html')

@app.route('/addMeter')
def index():
    fog_nodes = FogNode.query.all()
    return render_template('addMeter.html', fog_nodes=fog_nodes)



@app.route('/addFogNode')
def addFogNode():
    return render_template('addFogNode.html')

@app.route('/removeMeter')
def removeMeter():
    return render_template('removeMeter.html')

@app.route('/removeFogNode')
def removeFogNode():
    return render_template('removeFogNode.html')

# API Endpoint to Add Smart Meter
# API Endpoint to Add Smart Meter



@app.route('/addMeter', methods=['POST'])
def add_meter():
    data = request.json
    new_meter = SmartMeter(
        meterId=data['meter_ID'],
        state=data['state'],
        city=data['city'],
        house_number=data['house_number'],
        phone_number=data['phone_number'],
        password=data['password'],
        fog_node=data['fog_node']
    )
    db.session.add(new_meter)
    db.session.commit()


    # algo to generate signature (id , fog_node) 
    # OR 
    # send meter id to trusted authority to generate signature
    # trusted_authority(meter_id):
    #     search meter_id in database
    #     generate a signature for that meter and fog_node
    #     return signature (store signature in cloud database)
    return jsonify({"message": "Smart meter added successfully!"})


# API Endpoint to Add Fog Node
@app.route('/addFogNode', methods=['POST'])
def add_fog_node():
    data = request.json
    if not data.get('node_id') or not data.get('location'):
        return jsonify({"message": "Invalid data"}), 400

    new_fog = FogNode(id=data['node_id'], location=data['location'])
    db.session.add(new_fog)
    db.session.commit()
    return jsonify({"message": "Fog node added successfully!"}), 200



# API Endpoint to Remove Smart Meter
@app.route('/removeMeter', methods=['POST'])
def remove_meter():
    data = request.json
    meter = SmartMeter.query.get(data['meterId'])
    if meter:
        db.session.delete(meter)
        db.session.commit()
        return jsonify({"message": "Smart meter removed successfully!"})
    return jsonify({"error": "Meter not found"}), 404

# API Endpoint to Remove Fog Node
@app.route('/removeFogNode', methods=['POST'])
def remove_fog_node():
    data = request.json
    fog_node = FogNode.query.get(data['node_id'])
    if fog_node:
        db.session.delete(fog_node)
        db.session.commit()
        return jsonify({"message": "Fog node removed successfully!"})
    return jsonify({"error": "Fog node not found"}), 404

# API Endpoint to Update Smart Meter
@app.route('/updateMeter', methods=['POST'])
def update_meter():
    data = request.json
    meter = SmartMeter.query.get(data['meterId'])
    if meter:
        meter.hpbm = data['newHPBM']
        db.session.commit()
        return jsonify({"message": "Smart meter updated successfully!"})
    return jsonify({"error": "Meter not found"}), 404

# API Endpoint to Update Fog Node
@app.route('/updateFogNode', methods=['POST'])
def update_fog_node():
    data = request.json
    fog_node = FogNode.query.get(data['node_id'])
    if fog_node:
        fog_node.hpbf = data['newHPBF']
        db.session.commit()
        return jsonify({"message": "Fog node updated successfully!"})
    return jsonify({"error": "Fog node not found"}), 404





@app.route('/get-power', methods=['POST'])
def get_power():
    data = request.json
    meter = SmartMeter.query.get(data['meterId'])
    if meter:
        # fog node will send power to meter and store that data consumption for that specific meter in database
        # if the same meter requests more power than it should get added to the row of that meter
        return jsonify({"message": "Power data sent successfully!"})
    return jsonify({"error": "Meter not found"}), 404

@app.route('/get-bill', methods=['GET'])
def get_bill():
    data = request.json
    meter_id = data['meterId']
    # fetch the power consumed by the meter from the database
    # for example
    power_consumed = "1000"
    # algo to calculate the bill
    bill = 100
    
    return jsonify({"message": "Bill generated successfully!", bill : bill, power_consumed : power_consumed})

@app.route('/login-meter', methods=['POST'])
def login_meter():
    data = request.json
    meter = SmartMeter.query.get(data['meterId'])
    if meter:
        # algo to verify the signature
        # if signature is valid then return success
        # else return error
        # if success then send {meter_id, success_message} to meter
        return jsonify({"message": "Meter logged in successfully!"})
    return jsonify({"error": "Meter not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
