from API import api
from flask_restplus import fields

user = api.model('User',{
	'email': fields.String(required = True, description = 'User\'s email address'),
	'password': fields.String(required = True, description = 'Password hash'),
	'full_name': fields.String(required = True, description = 'User\'s full name')
	})

message = api.model('Message',{
	'title': fields.String(required = True, description = 'Message title'),
	'content': fields.String(required = True, description = 'Message content'),
	'magic_number': fields.Integer(required = True, description = 'Magic number')
	})