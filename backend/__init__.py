from flask import Flask
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__, static_folder='../frontend/dist/static', template_folder='../frontend/dist')
app.config.from_object('backend.config')
app.config['SESSION_TYPE'] = 'filesystem'
app.config["JSON_AS_ASCII"] = False

Session(app)
# logging configuration for CORS
# import sys,logging, logging.handlers
# logging.getLogger('flask_cors').level = logging.DEBUG
# logging.getLogger('flask_cors').addHandler(logging.StreamHandler(sys.stdout))
CORS(app, supports_credentials=True)  # supports_credentials=True: APIアクセスにてセッションCookieを受け付けるようにする

import backend.views
