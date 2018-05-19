from API import app, api, models
from flask_restplus import Resource
from flask import request, jsonify, redirect
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity, EntityProperty, EdmType
from azure.common import AzureMissingResourceHttpError as Azure404
from json import dumps, loads
import message_pb2
from google.protobuf.json_format import MessageToJson
from werkzeug.exceptions import NotFound

table_service = TableService(account_name=app.config['STORAGE_NAME'],
                             account_key=app.config['STORAGE_KEY'],
                             connection_string=app.config['STORAGE_STRING'])

usr = api.namespace('Users', description='Operations on user objects')
msg = api.namespace('Messages', description='Operations on message objects')


@app.errorhandler(NotFound)
def redirect_404(request):
    return redirect('/swagdoc')


@usr.route('/users')
class UsersAll(Resource):
    @usr.expect(models.user)
    @api.response(201, 'User successfully added.')
    def post(self):
        """
        Inserts user into an Azure table.
        """
        if request.is_json:
            try:
                user = Entity()
                user.PartitionKey = request.json["email"]
                user.RowKey = ''
                user.info = EntityProperty(EdmType.BINARY, dumps(request.json))
                table_service.insert_or_replace_entity('users', user)
            except(KeyError):
                return 'Please provide a json object conforming to \
                the following pattern: {\"email\":\"example@email.com\",\
                \"password\":\"xxx\", \"full_name\":\"Foo Bar\"}', 400

            return None, 201
        else:
            return 'Please supply a json object in order to add a user.', 400

    def get(self):
        '''
        Fetches a list of all users.
        '''
        ret = []
        for u in table_service.query_entities('users'):
            ret.append(loads(u.info.value.decode('utf-8')))
        return jsonify(ret)


@usr.route('/users/<mail>')
@usr.doc(params={'mail': "A user\'s e-mail address."})
@api.response(404, 'User does not exist')
class UserOne(Resource):
    @api.response(204, 'User successfully deleted')
    def delete(self, mail):
        '''
        Deletes user with specified e-mail, as well as user\'s messages
        '''
        try:
            for message in table_service.query_entities('messages',filter="PartitionKey eq '{}'".format(mail)):
                table_service.delete_entity('messages', message.PartitionKey, message.RowKey)
            table_service.delete_entity('users', mail, '')
        except Exception:
            return None, 404
        return None, 204

    def get(self, mail):
        '''
        Fetches user with specified e-mail.
        '''
        if len(list(table_service.query_entities('users', filter="PartitionKey eq '{}'".format(mail)))) == 0:
            return None, 404
        else:
            return loads(table_service.get_entity('users', mail, '').info.value.decode('utf-8'))


@api.response(404, 'User does not exist')
@msg.doc(params={'mail': "A user\'s e-mail address."})
@msg.route('/users/<mail>/messages')
class MessagesAll(Resource):
    def get(self, mail):
        '''
        Lists user\'s messages
        '''
        if len(list(table_service.query_entities('users', filter="PartitionKey eq '{}'".format(mail)))) == 0:
            return None, 404
        else:
            ret = []
            for message in table_service.query_entities('messages', filter="PartitionKey eq '{}'".format(mail)):
                ret.append(loads(message.details.value.decode('utf-8')))
            return jsonify(ret)

    @msg.expect(models.message)
    def post(self, mail):
        '''
        Adds a message
        '''
        if request.is_json:
            try:
                try:
                    table_service.get_entity('users', mail, '')
                    message = Entity()
                    details = message_pb2.Message()
                    details.title = request.json["title"]
                    details.content = request.json["content"]
                    details.magic_number = request.json["magic_number"]
                    message.PartitionKey = mail
                    message.RowKey = str(len(list(table_service.query_entities('messages'))) + 1)
                    message.details = EntityProperty(EdmType.BINARY, MessageToJson(details))
                    table_service.insert_entity('messages', message)
                    return None, 201
                except(Azure404):
                    return None, 404
            except(KeyError):
                return 'Please provide a json object conforming to the \
                following pattern: {\"title\": \"Message title\", \
                \"content\":\"Message content\", \
                \"magic_number\": a number}', 400


@usr.route('/users/page=<int:page>')
@api.doc(params={'page': 'Page number'})
class UserPagination(Resource):
    def get(self, page):
        '''
        Paginates users, 10 per page
        '''
        ret = []
        for u in table_service.query_entities('users'):
            ret.append(loads(u.info.value.decode('utf-8')))
        return jsonify(ret[((page - 1) * 10):(page * 10 - 1)])


@msg.route('/users/<mail>/messages/page=<int:page>')
@api.doc(params={'page': 'Page number', 'mail': 'A user\'s email address'})
class MessagePagination(Resource):
    def get(self, mail, page):
        '''
        Paginates messages of a specified user, 10 per page
        '''
        ret = []
        for message in table_service.query_entities('messages', filter="PartitionKey eq '{}'".format(mail)):
            ret.append(loads(message.details.value.decode('utf-8')))
        return jsonify(ret[((page - 1) * 10):(page * 10)])
