from flask_mongoengine import MongoEngine

from config import db

class Device(db.Document):
  _id = db.ObjectIdField()
  serial = db.IntField(required=True, unique=True)
  description = db.StringField(max_length=50, required=True)



class DeviceData(db.Document):
  _id = db.ObjectIdField()
  temperature = db.FloatField(min_value=-55, max_value=125)
  humidity = db.FloatField(default=0, min_value=0, max_value=100)
  battery = db.IntField(default=0, min_value=0, max_value=100)
  timestamp = db.DateTimeField(required=True)
  device_id = db.ReferenceField(Device, required=True)

class Auth(db.Document):
  _id = db.ObjectIdField()
  key = db.UUIDField(binary=False, required=True)
  device_serial = db.IntField(required=True, unique=True)

if __name__ == '__main__':
  print("Updating battery in DB")
  DeviceData.objects().update(battery=100)
  DeviceData.objects().update(humidity=0)