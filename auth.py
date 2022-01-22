from functools import wraps
from config import db, app
from models import Auth
from flask import request
from responses import generate_unauthorized
from flask_mongoengine import DoesNotExist
from mongoengine.connection import _get_db


from uuid import uuid4

def add_api_key(key, serial):
  try:
    # TODO: Add validation of key and serial
    data = Auth(key=key, device_serial=serial)
    data.save()
  except Exception as e:
    print(e)
    return False
  return True


def validate_api_key(key, serial):
  try:
    result = Auth.objects(key=key, device_serial=serial).get()
    # False if None, True if record is returned from DB
    return result != None
  except Exception as e:
    return False


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      try:
        serial_num = 0
        if 'serial_num' in kwargs:
          serial_num = kwargs['serial_num']
        api_key = request.headers.get('X-API-KEY', None)
      except KeyError as e:
        return generate_unauthorized()

      if api_key == None:
        return generate_unauthorized()
      if validate_api_key(api_key, serial_num):
        return f(*args, **kwargs)
      else:
        return generate_unauthorized()
    return wrapper

def add_root():
    uuid = str(uuid4())
    print(f"#### Admin api key = {uuid} ####")
    app.logger.info('Root api key %s', uuid)
    success = add_api_key(uuid, 0)
    if success:
        app.logger.info('Added root api key to DB')
    else:
        app.logger.error('Error adding root api key to DB')

# Check if authentication table has root / serial number zero

try:
  collections_names = _get_db().list_collection_names()
  if 'auth' not in collections_names:
    add_root()
  if 'auth' in collections_names:
    root_exists = Auth.objects(device_serial=0).get()
except DoesNotExist:
  add_root()
