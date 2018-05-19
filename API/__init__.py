from flask import Flask
from flask_restplus import Api
from config import Config



app = Flask(__name__)
api = Api(app, doc='/swagdoc/', title = 'Flask-restplus API', description = 'A test REST API. \
	It allows to get, post and delete both users and their messages in Microsoft Azure tables. \
	It accepts and outputs JSON only. Message entities contain their contents in form of a Protobuf message.')
app.config.from_object(Config)





import API.views
import API.models
