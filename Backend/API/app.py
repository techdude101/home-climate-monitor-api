from flask import Flask, request, jsonify, abort
from flask.helpers import make_response
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.operators import not_endswith_op
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from sqlalchemy import and_

import os
import datetime

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init marshmallow
ma = Marshmallow(app)

# Models


class Device(db.Model):
  __tablename__ = 'device'
  id = db.Column(db.Integer, primary_key=True)
  serial = db.Column(db.Integer, unique=True)
  description = db.Column(db.String(50))

  def __init__(self, serial, description):
    self.serial = serial
    self.description = description


class DeviceData(db.Model):
  __tablename__ = 'device_data'
  id = db.Column(db.Integer, primary_key=True)
  temperature = db.Column(db.Float)
  humidity = db.Column(db.Float)
  timestamp = db.Column(db.DateTime)
  device_id = db.Column(db.Integer, db.ForeignKey('device.serial'))

  def __init__(self, temperature, humidity, timestamp, device_id):
    self.temperature = temperature
    self.humidity = humidity
    self.device_id = device_id
    self.timestamp = timestamp

# Device Schema


class DeviceSchema(ma.Schema):
  class Meta:
    fields = ('id', 'serial', 'description')

# Device Data Schema


class DataSchema(ma.Schema):
  class Meta:
    fields = ('id', 'temperature', 'humidity', 'timestamp', 'device_id')


# Init Device Schema
device_schema = DeviceSchema()
devices_schema = DeviceSchema(many=True)

# Init Data Schema
data_schema = DataSchema()
datas_schema = DataSchema(many=True)


@app.route('/', methods=['GET'])
def get():
  return jsonify({'message': 'Home Climate Monitor API'})


@app.route('/device/create', methods=['POST'])
def create_device():
  serial = request.json['serial']
  description = request.json['description']

  new_device = Device(serial, description)

  db.session.add(new_device)
  db.session.commit()

  return device_schema.jsonify(new_device)

@app.route('/device/update', methods=['PUT', 'PATCH'])
def update_device():
  data = request.json
  #print(data)
  serial = None
  description = None
  if 'serial' in data:
    serial = data['serial']
  if 'description' in data:
    description = data['description']

  if serial != None and description != None:
    device = Device.query.filter(Device.serial == serial).first()
    device.description = description
    db.session.commit()
    return device_schema.jsonify(device)
  return make_response(jsonify("Error"), 404)

@app.route('/device/', methods=['GET'])
def get_devices():
  all_devices = Device.query.all()
  result = devices_schema.dump(all_devices)
  return jsonify(result)


@app.route('/device/<id>', methods=['GET'])
def get_device(id):
  device = Device.query.get(id)
  return device_schema.jsonify(device)


@app.route('/device/serial/<serial_num>', methods=['GET'])
def get_device_by_serial(serial_num):
  device = Device.query.filter(Device.serial == serial_num).first()
  return device_schema.jsonify(device)


@app.route('/data/', methods=['POST'])
def add_data():
  device_serial = request.json['serial']
  temperature = request.json['temperature']
  humidity = request.json['humidity']
  device = Device.query.filter(Device.serial == device_serial).first()
  timestamp = datetime.datetime.now()

  new_device_data = DeviceData(temperature, humidity, timestamp, device.id)

  db.session.add(new_device_data)
  db.session.commit()
  return data_schema.jsonify(new_device_data)


@app.route('/data/<serial>', methods=['GET'])
def get_all_data(serial):
  start_date_str = request.args.get('start', None)
  end_date_str = request.args.get('end', None)
  #print(f"Args: {request.args.get('start')}")
  device_serial = serial
  device = Device.query.filter(Device.serial == device_serial).first()
  data = DeviceData.query.filter(DeviceData.device_id == device.id).all()
  if start_date_str != None and end_date_str != None:
    start_date_time = datetime.datetime.fromisoformat(start_date_str)
    end_date_time = datetime.datetime.fromisoformat(end_date_str)
    
    #print(f"Start: {start_date_time}, End: {end_date_time}")
    
    data = DeviceData.query.filter(and_(DeviceData.device_id == device.id,
      DeviceData.timestamp > start_date_time,
      DeviceData.timestamp < end_date_time))
  return datas_schema.jsonify(data)


# Run server
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
