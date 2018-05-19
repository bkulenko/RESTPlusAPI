import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	DEBUG=False
	TESTING=False
	ENV='production'
	SECRET_KEY = 'Ym7eoamEoom149El0+w45wY0EcXkBRNw3gIoYVHTtMm6bnaCy5wYmbA3ykF4HUknfKgyAyDndqQmroKkO4rHIA=='
	RESTPLUS_VALIDATE = True
	STORAGE_NAME = ''
	STORAGE_KEY = ''
	STORAGE_STRING = ''
	SWAGGER_UI_DOC_EXPANSION = 'list'
	SWAGGER_UI_JSONEDITOR = False