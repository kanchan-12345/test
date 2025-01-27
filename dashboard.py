from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func

# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_meter.db'  # Use PostgreSQL/MySQL in production
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Database
db = SQLAlchemy(app)

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

# Route for Dashboard
@app.route('/result')
def dashboard():
    return render_template('result.html')

# Route for Data Entry Page
@app.route('/')
def entry_page():
    return render_template('index.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
