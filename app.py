from flask import Flask, request, jsonify, abort
from flask.helpers import make_response

import datetime
import uuid
import os

from auth import authenticate
from config import db, app, db_limit, fast_limit, limiter, cors, cross_origin, MongoEngine
from models import Device, DeviceData
from auth import validate_api_key, add_api_key
from responses import generate_unauthorized, generate_bad_request

from helpers import device_data_to_json

# TODO: Insert serial # of zero and random uuidv4 into authentication DB
# Used to authenticate creating / updating / deleting devices

@app.route('/', methods=['GET'])
@cross_origin()
def get():
  return jsonify({'message': 'Home Climate Monitor API'})


@db_limit
@app.route('/device/create', methods=['POST'])
@authenticate
# @cross_origin()
def create_device():
  description = request.json['description']
  api_key = str(uuid.uuid4())

  # Get last device serial number
  last_device_serial = Device.objects().order_by('-serial').all()[0]
  serial = last_device_serial.serial + 1
  
  new_device = Device(serial=serial, description=description)

  try:
    new_device.save() # Store in DB
    add_api_key(api_key, serial)
  except Exception as ex:
    if "duplicate key error" in ex.args[0]:
      return generate_bad_request("Duplicate description")
    print(f"Device create error {ex}")    
    return generate_bad_request("Something went wrong")

  response = {"key": api_key, "serial": serial, "description": description}

  return response

@db_limit
@app.route('/device/update', methods=['PUT', 'PATCH'])
@authenticate
def update_device():
  data = request.json

  serial = None
  description = None
  if 'serial' in data:
    serial = data['serial']
  if 'description' in data:
    description = data['description']

  if serial != None and description != None:
    device = Device.objects(serial=serial).first()
    # TODO: Validate description
    device.description = description
    try:
      device.save()
      return jsonify(device)
    except Exception:
      return generate_bad_request("Something went wrong")
  else:
    return make_response(jsonify("Invalid or missing parameters"), 400)


@app.route('/device/', methods=['GET'])
def get_devices():
  all_devices = Device.objects().all()
  return jsonify(all_devices)


@app.route('/device/serial/<int:serial_num>', methods=['GET'])
def get_device_by_serial(serial_num=None):
  all_devices = Device.objects(serial=serial_num).all()
  return jsonify(all_devices)


@db_limit
@app.route('/data/<int:serial_num>', methods=['POST'])
@authenticate
def add_data(serial_num=None):
  data = request.json
  serial_num = None
  temperature = None
  humidity = None
  battery = None
  
  if data:
    if 'serial' in data:
      serial_num = data['serial']
    
    if 'temperature' in data:
      temperature = data['temperature']
    if 'humidity' in data:
      humidity = data['humidity']
    if 'battery' in data:
      battery = data['battery']
  else:
    return generate_bad_request("Invalid request parameters")  
  
  device = Device.objects(serial=serial_num).first()
  if device != None:
    timestamp = datetime.datetime.now()
    new_device_data = None

    # Temperature, humidity and battery
    if temperature != None and humidity != None and battery != None:
      new_device_data = DeviceData(temperature=temperature, humidity=humidity, battery=battery, timestamp=timestamp, device_id=device._id)  

    # Temperature and humidity
    if temperature != None and humidity != None and battery == None:
      new_device_data = DeviceData(temperature=temperature, humidity=humidity, timestamp=timestamp, device_id=device._id)  

    # Temperature only
    if temperature != None and humidity == None and battery == None:
      new_device_data = DeviceData(temperature=temperature, timestamp=timestamp, device_id=device._id)  
    
    # Temperature and battery
    if temperature != None and humidity == None and battery != None:
      new_device_data = DeviceData(temperature=temperature, battery=battery, timestamp=timestamp, device_id=device._id)  
    
    if new_device_data != None:
      new_device_data.save()
      return jsonify(new_device_data)
  return generate_bad_request("Error saving data")


@app.route('/data/<int:serial>', methods=['GET'])
def get_all_data(serial):
  start_date_str = request.args.get('start', None)
  end_date_str = request.args.get('end', None)

  device_serial = serial
  device = Device.objects(serial=device_serial).first_or_404()
  data = DeviceData.objects(device_id=device._id).order_by('-timestamp').all()

  # # TODO: Validate datetime
  if start_date_str != None and end_date_str != None:
    start_date_time = datetime.datetime.fromisoformat(start_date_str)
    end_date_time = datetime.datetime.fromisoformat(end_date_str)

    data = DeviceData.objects(device_id=device._id, timestamp__gte=start_date_time,
                                        timestamp__lte=end_date_time).order_by('-timestamp').all()
    return device_data_to_json(device.serial, data)
  return device_data_to_json(device.serial, data)

@limiter.exempt
@app.route('/data/<int:serial>/last', methods=['GET'])
def get_last(serial):
  device_serial = serial
  device = Device.objects(serial=device_serial).first()
  data = []
  data.append(DeviceData.objects(device_id=device._id).order_by('-timestamp').first())

  return device_data_to_json(device.serial, data)

# Run server
if __name__ == '__main__':
  app.run(threaded=True, port = int(os.environ.get('PORT', 5000)))
