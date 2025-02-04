from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Meter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Float, nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/add-meter', methods=['POST'])
def add_meter():
    meter_data = request.json
    new_meter = Meter(name=meter_data['name'], data=meter_data['data'])
    db.session.add(new_meter)
    db.session.commit()
    return jsonify({'id': new_meter.id, 'name': new_meter.name, 'data': new_meter.data}), 201

@app.route('/meters', methods=['GET'])
def get_meters():
    meters = Meter.query.all()
    return jsonify([{ 'id': meter.id, 'name': meter.name, 'data': meter.data } for meter in meters])

if __name__ == '__main__':
    app.run(debug=True)