from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mongoengine import MongoEngine

from flask_cors import CORS, cross_origin

import os

# Init app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1 per second"],
)
db_limit = limiter.shared_limit("10/minute", scope="db_limit")
fast_limit = limiter.shared_limit("100/minute", scope="fast_limit")

app.config['MONGODB_HOST'] = os.environ['DB_URL']
db = MongoEngine()
db.init_app(app)

