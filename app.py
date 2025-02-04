from flask import Flask, request, jsonify, render_template, redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func
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
    password = db.Column(db.String(100), nullable=False)  # Password



# Database Model
class Meter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    voltage = db.Column(db.Float, nullable=False)
    power = db.Column(db.Float, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    consumption = db.Column(db.Float, nullable=False)  # kWh (Units)
    bill = db.Column(db.Float, nullable=False)  # Amount
    appliance = db.Column(db.String(100), nullable=False)  # E.g., AC, fridge, light


# Initialize the Database
with app.app_context():
    db.create_all()

# @app.route('/remote-table', methods=['GET'])
# def remove_fog_node_table():
#     FogNode.__table__.drop(db.engine)
#     return jsonify({"message": "Fog node table removed successfully!"}), 200


# Route for Dashboard

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/contact')
def contact():
    return render_template('contactus.html')



# Route for Data Entry Page
@app.route('/current_meter_data')
def entry_page():
    return render_template('current_meter_data.html')

# API to Submit Data
@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json.get('data', [])
    if not data:
        return jsonify({'error': 'Missing data'}), 400
    
    for entry in data:
        voltage = entry.get('voltage')
        power = entry.get('power')
        hours = entry.get('hours')
        appliance = entry.get('appliance')

        if not (voltage and power and hours and appliance):
            continue

        consumption = (float(power) * float(hours)) / 1000  # Convert Watts to kWh
        bill = consumption * 5  # Assuming $5 per kWh

        new_entry = Meter(
            voltage=float(voltage),
            power=float(power),
            hours=float(hours),
            consumption=consumption,
            bill=bill,
            appliance=appliance
        )
        db.session.add(new_entry)
    
    db.session.commit()
    return jsonify({'message': 'Data stored successfully!'}), 201

# API to Get Consumption Data
@app.route('/consumption', methods=['GET'])
def get_consumption():
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    data = {
        "today": db.session.query(func.sum(Meter.consumption)).filter(func.date(Meter.date) == today).scalar() or 0,
        "yesterday": db.session.query(func.sum(Meter.consumption)).filter(func.date(Meter.date) == (today - timedelta(days=1))).scalar() or 0,
        "this_month": db.session.query(func.sum(Meter.consumption)).filter(Meter.date >= start_of_month).scalar() or 0,
        "last_month": db.session.query(func.sum(Meter.consumption)).filter(Meter.date < start_of_month, Meter.date >= start_of_month - timedelta(days=30)).scalar() or 0,
        "this_year": db.session.query(func.sum(Meter.consumption)).filter(Meter.date >= start_of_year).scalar() or 0,
        "last_year": db.session.query(func.sum(Meter.consumption)).filter(Meter.date < start_of_year, Meter.date >= start_of_year - timedelta(days=365)).scalar() or 0,
    }
    return jsonify(data)

# API to Get Billing Data
@app.route('/billing', methods=['GET'])
def get_billing():
    start_of_month = datetime.utcnow().replace(day=1)
    
    data = {
        "this_month": db.session.query(func.sum(Meter.bill)).filter(Meter.date >= start_of_month).scalar() or 0,
        "last_month": db.session.query(func.sum(Meter.bill)).filter(Meter.date < start_of_month, Meter.date >= start_of_month - timedelta(days=30)).scalar() or 0,
    }
    return jsonify(data)

# API to Get Appliance-Wise Consumption
@app.route('/appliance-consumption', methods=['GET'])
def get_appliance_consumption():
    start_of_month = datetime.utcnow().replace(day=1)
    
    appliances = db.session.query(Meter.appliance, func.sum(Meter.consumption)).filter(
        Meter.date >= start_of_month
    ).group_by(Meter.appliance).all()
    
    data = {appliance: consumption for appliance, consumption in appliances}
    return jsonify(data)


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
def fog_Node():
    return render_template('addFogNode.html')

@app.route("/login-meter")
def smart_meter_login():
    return render_template('meterlogin.html')


@app.route("/meter_entry")
def meter_entry_login():
    return render_template('meter_entry.html')


@app.route("/login-fog")
def fog_login():
    return render_template('nodelogin.html')


@app.route('/removeMeter')
def removeMeter():
    return render_template('removeMeter.html')

@app.route('/removeFogNode')
def removeFogNode():
    return render_template('removeFogNode.html')

@app.route('/meter-dashboard')
def meter_dashboard():
    return render_template('meterDashboard.html')

@app.route('/fog-dashboard')
def fog_dashboard():
    return render_template('fogDashboard.html')

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
    return jsonify({"message": "Smart meter added successfully!"}), 200


# API Endpoint to Add Fog Node
@app.route('/addFogNode', methods=['POST'])
def add_fog_node():
    data = request.json
    if not data.get('node_id') or not data.get('location'):
        return jsonify({"message": "Invalid data"}), 400
    new_fog = FogNode(id=data['node_id'], location=data['location'], password=data['password'])
    db.session.add(new_fog)
    db.session.commit()
    return jsonify({"message":"Fog node added successfully!"}), 200



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

@app.route('/login-meter', methods=['GET'])
def login_meter():
    data = request.json
    meter = SmartMeter.query.get(data['meterId'])
    
    if meter:
        if(meter.password == data['password']):
            return jsonify({"message": "Meter logged in successfully!", "status": 200}), 200
        # algo to verify the signature
        # if signature is valid then return success
        # else return error
        # if success then send {meter_id, success_message} to meter
        # return jsonify({"message": "Meter logged in successfully!"})
    return jsonify({"error": "Meter not found"}), 404



@app.route('/login-fog', methods=['POST'])
def login_fog():
    data = request.json
    fog_node = FogNode.query.get(data['node_id'])
    
    if fog_node:
        if(fog_node.password == data['password']):
            return jsonify({"message": "node logged in successfully!", "status": 200}), 200
        # algo to verify the signature
        # if signature is valid then return success
        # else return error
        # if success then send {meter_id, success_message} to meter
        # return jsonify({"message": "Meter logged in successfully!"})
    return jsonify({"error": "fog not found"}), 404



if __name__ == '__main__':
    app.run(debug=True)
