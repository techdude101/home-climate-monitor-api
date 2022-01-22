
from flask import jsonify

def device_data_to_json(device_serial, data):
  return_data = []
  for row in data:
    return_data.append({'serial': device_serial, 'timestamp': row.timestamp.isoformat(), 'temperature': row.temperature, 'humidity': row.humidity})
  return jsonify(return_data)